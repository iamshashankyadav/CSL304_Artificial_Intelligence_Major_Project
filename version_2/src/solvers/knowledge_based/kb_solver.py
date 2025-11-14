"""
Knowledge-based solver using rule-based reasoning.
"""

from typing import List, Dict, Set
from ..base_solver import BaseSolver
from ...core.feedback import Feedback, LetterStatus
from ...core.word_list import WordList
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class KnowledgeBasedSolver(BaseSolver):
    """Wordle solver using knowledge-based rules and inference."""

    def __init__(self, word_list: WordList, config: dict = None):
        super().__init__(word_list, config)
        self.confirmed_letters: Dict[int, str] = {}  # position -> letter
        self.present_letters: Set[str] = set()  # letters in word but position unknown
        self.absent_letters: Set[str] = set()  # letters not in word
        self.excluded_positions: Dict[str, Set[int]] = (
            {}
        )  # letter -> positions to avoid

        # Letter frequency analysis
        self.letter_freq = self._analyze_letter_frequency()
        self.position_freq = self._analyze_position_frequency()

    def _analyze_letter_frequency(self) -> Dict[str, float]:
        """Analyze frequency of letters across all words."""
        freq = Counter()
        total = 0

        for word in self.word_list.get_common_words():
            for letter in set(word):
                freq[letter] += 1
                total += 1

        return {letter: count / total for letter, count in freq.items()}

    def _analyze_position_frequency(self) -> List[Dict[str, float]]:
        """Analyze frequency of letters at each position."""
        position_freq = [{} for _ in range(5)]

        for word in self.word_list.get_common_words():
            for i, letter in enumerate(word):
                position_freq[i][letter] = position_freq[i].get(letter, 0) + 1

        # Normalize
        for i in range(5):
            total = sum(position_freq[i].values())
            position_freq[i] = {k: v / total for k, v in position_freq[i].items()}

        return position_freq

    def get_next_guess(self) -> str:
        """Get next guess using knowledge-based rules."""
        if not self.guess_history:
            return self._get_first_guess()

        # Apply rules to filter candidates
        candidates = self._apply_rules()

        if not candidates:
            logger.warning("No candidates found, using fallback")
            return self._get_fallback_guess()

        if len(candidates) == 1:
            return list(candidates)[0]

        # Score and select best candidate
        return self._score_candidates(candidates)

    def _get_first_guess(self) -> str:
        """Get optimal first guess based on letter frequency."""
        # Use words with most common letters in optimal positions
        best_words = ["slate", "crane", "stare", "arise", "raise"]

        for word in best_words:
            if word in self.possible_words:
                return word

        return list(self.possible_words)[0]

    def _apply_rules(self) -> Set[str]:
        """Apply knowledge-based rules to filter candidates."""
        candidates = set(self.possible_words)

        # Rule 1: Must have confirmed letters at correct positions
        for pos, letter in self.confirmed_letters.items():
            candidates = {w for w in candidates if w[pos] == letter}

        # Rule 2: Must contain all present letters
        for letter in self.present_letters:
            candidates = {w for w in candidates if letter in w}

        # Rule 3: Must not contain absent letters
        for letter in self.absent_letters:
            candidates = {w for w in candidates if letter not in w}

        # Rule 4: Present letters must not be in excluded positions
        for letter, positions in self.excluded_positions.items():
            for pos in positions:
                candidates = {w for w in candidates if w[pos] != letter}

        return candidates

    def _score_candidates(self, candidates: Set[str]) -> str:
        """Score candidates using multiple heuristics."""
        scores = {}

        for word in candidates:
            score = 0

            # Heuristic 1: Letter frequency
            for letter in set(word):
                score += self.letter_freq.get(letter, 0) * 100

            # Heuristic 2: Position-specific frequency
            for i, letter in enumerate(word):
                score += self.position_freq[i].get(letter, 0) * 50

            # Heuristic 3: Number of unique letters (exploration)
            unique_letters = len(set(word))
            if len(self.guess_history) < 2:
                score += unique_letters * 30  # Prefer diverse letters early

            # Heuristic 4: Avoid repeated letters if we have knowledge
            if len(self.confirmed_letters) > 0:
                repeated = len(word) - len(set(word))
                score -= repeated * 20

            scores[word] = score

        # Return highest scoring word
        return max(scores.items(), key=lambda x: x[1])[0]

    def _get_fallback_guess(self) -> str:
        """Fallback when no candidates found."""
        if self.possible_words:
            return list(self.possible_words)[0]
        return "slate"

    def update_state(self, guess: str, feedback: Feedback) -> None:
        """Update knowledge base with new information."""
        self.guess_history.append(guess)
        self.feedback_history.append(feedback)

        # Extract knowledge from feedback
        for i, (letter, status) in enumerate(zip(guess, feedback.feedback)):
            if status == LetterStatus.CORRECT:
                self.confirmed_letters[i] = letter
                # Remove from present letters if it was there
                self.present_letters.discard(letter)

            elif status == LetterStatus.PRESENT:
                self.present_letters.add(letter)
                # Add position to excluded positions
                if letter not in self.excluded_positions:
                    self.excluded_positions[letter] = set()
                self.excluded_positions[letter].add(i)

            elif status == LetterStatus.ABSENT:
                # Only add to absent if not confirmed or present elsewhere
                if (
                    letter not in self.confirmed_letters.values()
                    and letter not in self.present_letters
                ):
                    self.absent_letters.add(letter)

        # Filter possible words
        self._filter_words_by_feedback(guess, feedback)

        logger.info(
            f"KB: {len(self.possible_words)} words remaining. "
            f"Confirmed: {len(self.confirmed_letters)}, "
            f"Present: {len(self.present_letters)}"
        )

    def reset(self) -> None:
        """Reset solver state."""
        super().reset()
        self.confirmed_letters = {}
        self.present_letters = set()
        self.absent_letters = set()
        self.excluded_positions = {}
