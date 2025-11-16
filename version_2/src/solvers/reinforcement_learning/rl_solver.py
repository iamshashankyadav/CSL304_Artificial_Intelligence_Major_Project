"""
Reinforcement Learning solver for Wordle.
"""

from typing import List, Dict, Optional
from solvers.base_solver import BaseSolver
from core.feedback import Feedback
from core.word_list import WordList
import numpy as np
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class RLSolver(BaseSolver):
    """Wordle solver using Reinforcement Learning (simplified Q-learning)."""

    def __init__(self, word_list: WordList, config: dict = None):
        super().__init__(word_list, config)
        self.config = config or {}
        self.epsilon = float(self.config.get("epsilon", 0.1))

        # Q-values placeholder (not used in this simplified version)
        self.q_values = {}

        # Ensure possible_words exists (BaseSolver may set it; be safe)
        valid_words = list(self.word_list.get_valid_words() or [])
        self.possible_words = set(valid_words)

        # Track history (BaseSolver may set these; ensure they exist)
        self.guess_history = getattr(self, "guess_history", [])
        self.feedback_history = getattr(self, "feedback_history", [])

        # Letter position preferences learned over time
        self.position_preferences = self._initialize_preferences()

    def _initialize_preferences(self) -> List[Dict[str, float]]:
        """Initialize position preferences from word frequency."""
        preferences = [{} for _ in range(5)]

        try:
            common_words = list(self.word_list.get_common_words() or [])
        except Exception:
            common_words = []

        if not common_words:
            # Fall back to some commonly recommended starters if no list
            common_words = ["slate", "crane", "stare", "raise", "arise"]

        for word in common_words:
            for i, letter in enumerate(word):
                preferences[i][letter] = preferences[i].get(letter, 0) + 1

        for i in range(5):
            total = sum(preferences[i].values())
            if total > 0:
                preferences[i] = {k: v / total for k, v in preferences[i].items()}
            else:
                preferences[i] = {}

        return preferences

    def get_next_guess(self) -> str:
        """Get next guess using epsilon-greedy policy with safe fallbacks."""
        # Ensure possible_words is not empty; if it is, recover
        if not self.possible_words:
            logger.warning("possible_words empty at get_next_guess(); attempting recovery.")
            self._recover_possible_words()
            if not self.possible_words:
                # As a final fallback, return a safe common word or first valid word
                fallback = self._fallback_guess()
                logger.error("Recovery failed; returning fallback guess: %s", fallback)
                return fallback

        try:
            if not self.guess_history:
                return self._get_first_guess()

            if len(self.possible_words) == 1:
                return next(iter(self.possible_words))

            # Epsilon-greedy action selection
            if np.random.random() < self.epsilon:
                # Explore: random valid word from possible_words
                return np.random.choice(list(self.possible_words))
            else:
                # Exploit: use learned policy
                return self._select_best_action()
        except Exception:
            logger.exception("Exception in get_next_guess; using fallback.")
            return self._fallback_guess()

    def _get_first_guess(self) -> str:
        """Get first guess based on learned preferences."""
        starting_words = ["slate", "crane", "stare", "raise", "arise"]
        for word in starting_words:
            if word in self.possible_words:
                return word
        # fallback to any common/valid word
        return self._fallback_guess()

    def _fallback_guess(self) -> str:
        """Safe fallback guess (prefer common words, else any valid)."""
        commons = list(self.word_list.get_common_words() or [])
        valids = list(self.word_list.get_valid_words() or [])
        if commons:
            return commons[0]
        if valids:
            return valids[0]
        return "raise"

    def _select_best_action(self) -> str:
        """Select best action based on current policy."""
        # Fail-safe: if no possible words remain
        if not self.possible_words:
            logger.error("RL Solver Error: No possible words remaining in _select_best_action.")
            # try to recover
            self._recover_possible_words()
            if not self.possible_words:
                return self._fallback_guess()

        scores = {}
        for word in list(self.possible_words):
            try:
                score = self._evaluate_word(word)
                scores[word] = score
            except Exception:
                logger.exception("Error evaluating word %s; skipping.", word)

        if not scores:
            logger.warning("No scores computed in _select_best_action; using fallback.")
            return self._fallback_guess()

        # Return highest scoring word
        return max(scores.items(), key=lambda x: x[1])[0]

    def _evaluate_word(self, word: str) -> float:
        """Evaluate a word using learned preferences."""
        score = 0.0
        for i, letter in enumerate(word):
            score += self.position_preferences[i].get(letter, 0) * 10
        unique_letters = len(set(word))
        score += unique_letters * 2
        if len(self.guess_history) < 2:
            score += unique_letters * 3
        return score

    def update_state(self, guess: str, feedback: Feedback) -> None:
        """Update learned policy based on feedback."""
        if guess:
            self.guess_history.append(guess)
        self.feedback_history.append(feedback)

        try:
            self._update_preferences(guess, feedback)
        except Exception:
            logger.exception("Error in _update_preferences")

        # Filtering possible words may reduce set size
        before = len(self.possible_words)
        try:
            # Use BaseSolver's filtering if available, else attempt a simple filter
            if hasattr(super(), "_filter_words_by_feedback"):
                # If BaseSolver implements it, call it. Protect with try/except.
                try:
                    super()._filter_words_by_feedback(guess, feedback)
                    # assume BaseSolver updates self.possible_words
                except Exception:
                    logger.exception("BaseSolver._filter_words_by_feedback failed, attempting local filter.")
                    self._local_filter(guess, feedback)
            else:
                # fallback local filter
                self._local_filter(guess, feedback)
        except Exception:
            logger.exception("Filtering step failed for guess %r", guess)

        after = len(self.possible_words)
        logger.info("RL update_state: possible_words before=%d after=%d", before, after)

        if not self.possible_words:
            logger.warning("possible_words became empty after filtering - attempting recovery")
            self._recover_possible_words()

    def _local_filter(self, guess: str, feedback: Feedback) -> None:
        """
        Conservative local filtering as a backup when BaseSolver filtering is unavailable or fails.
        This will attempt only to remove words that contradict GREEN (correct) letters and ABSENT with
        certainty, and will be intentionally lenient for YELLOW-like feedback to avoid over-pruning.
        """
        from core.feedback import LetterStatus

        keep = set(self.possible_words)
        if not guess or not feedback:
            return

        # If feedback.feedback is a sequence of statuses or tuples, attempt to interpret it.
        statuses = getattr(feedback, "feedback", None)
        if statuses is None:
            # unknown format; skip aggressive filtering
            logger.debug("Feedback object missing .feedback attribute; skipping local filter")
            return

        for i, status in enumerate(statuses):
            letter = guess[i]
            if status == LetterStatus.CORRECT:
                keep = {w for w in keep if len(w) > i and w[i] == letter}
            elif status == LetterStatus.ABSENT:
                # If letter occurs multiple times in guess, conservative: remove words that have letter
                keep = {w for w in keep if letter not in w}
            elif status == LetterStatus.PRESENT:
                # YELLOW-ish: ensure letter present but not at position i
                keep = {w for w in keep if (letter in w and (len(w) <= i or w[i] != letter))}
            else:
                # unknown status: be conservative
                pass

        if keep:
            self.possible_words = keep
        else:
            logger.debug("Local filter would remove all words; keeping previous set to avoid empty set.")

    def _recover_possible_words(self) -> None:
        """Attempt to recover possible_words set when it becomes empty."""
        logger.info("Attempting to recover possible_words.")
        try:
            valids = set(self.word_list.get_valid_words() or [])
            commons = set(self.word_list.get_common_words() or [])
        except Exception:
            valids = set()
            commons = set()

        # Strategy: prefer commons intersect valids, else valids, else commons, else last-known words
        candidates = (commons & valids) or valids or commons
        if candidates:
            # try to remove words already guessed (to avoid repetition)
            candidates = {w for w in candidates if w not in set(self.guess_history)}
            if candidates:
                self.possible_words = set(candidates)
                logger.info("Recovered possible_words with %d candidates.", len(self.possible_words))
                return

        # Last resort: allow previously guessed words (to allow completion)
        all_candidates = set(self.guess_history) | set(valids) | set(commons)
        if all_candidates:
            self.possible_words = all_candidates
            logger.info("Recovered possible_words from history/valids/commons; size=%d", len(self.possible_words))
            return

        # Nothing available; keep possible_words empty (caller will fallback)
        logger.error("Unable to recover any possible words.")

    def _update_preferences(self, guess: str, feedback: Feedback) -> None:
        """Update position preferences based on feedback (simple learning)."""
        from core.feedback import LetterStatus

        learning_rate = 0.1

        statuses = getattr(feedback, "feedback", None)
        if statuses is None:
            logger.debug("Feedback object missing .feedback; skipping preference update.")
            return

        for i, status in enumerate(statuses):
            letter = guess[i]
            if status == LetterStatus.CORRECT:
                current = self.position_preferences[i].get(letter, 0)
                self.position_preferences[i][letter] = current + learning_rate
            elif status == LetterStatus.ABSENT:
                current = self.position_preferences[i].get(letter, 0)
                self.position_preferences[i][letter] = max(0, current - learning_rate * 0.5)

        # Re-normalize
        for i in range(5):
            total = sum(self.position_preferences[i].values())
            if total > 0:
                self.position_preferences[i] = {k: v / total for k, v in self.position_preferences[i].items()}

    def reset(self) -> None:
        """Reset solver state."""
        super().reset()
        valid_words = list(self.word_list.get_valid_words() or [])
        self.possible_words = set(valid_words)
        self.guess_history = []
        self.feedback_history = []
        # keep learned preferences across games (optional) - do not reset position_preferences here
