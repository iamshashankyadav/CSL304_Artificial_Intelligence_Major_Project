"""
Genetic Algorithm solver for Wordle (hardened against empty-population failures).
"""

from typing import List, Set, Tuple, Dict, Optional
from solvers.base_solver import BaseSolver
from core.feedback import Feedback, LetterStatus
from core.word_list import WordList
import random
import logging
from collections import Counter

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class GeneticSolver(BaseSolver):
    """Wordle solver using Genetic Algorithm with defensive checks."""

    def __init__(self, word_list: WordList, config: dict = None):
        super().__init__(word_list, config)
        self.config = config or {}

        self.population_size = int(self.config.get("population_size", 100))
        self.mutation_rate = float(self.config.get("mutation_rate", 0.01))
        self.crossover_rate = float(self.config.get("crossover_rate", 0.7))
        self.elite_size = int(self.config.get("elite_size", 10))

        # State
        valid_words = list(self.word_list.get_valid_words() or [])
        self.possible_words: Set[str] = set(valid_words)
        self.population: List[str] = []
        self.generation = 0
        self.letter_frequencies = self._compute_frequencies()

        # Ensure histories exist (BaseSolver may initialize them)
        self.guess_history = getattr(self, "guess_history", [])
        self.feedback_history = getattr(self, "feedback_history", [])

    def _compute_frequencies(self) -> Dict[str, float]:
        """Compute letter frequencies from common words (fallback if none)."""
        freq = Counter()
        try:
            sources = list(self.word_list.get_common_words() or [])
        except Exception:
            sources = []

        if not sources:
            # fallback to a small starter list
            sources = ["slate", "crane", "stare", "raise", "arise"]

        for word in sources:
            for letter in word:
                freq[letter] += 1

        total = sum(freq.values()) or 1
        return {k: v / total for k, v in freq.items()}

    def get_next_guess(self) -> str:
        """Get next guess using genetic algorithm with fallbacks."""
        # Ensure we have some possible words
        if not self.possible_words:
            logger.warning("possible_words empty in GeneticSolver.get_next_guess(); attempting recovery.")
            self._recover_possible_words()
            if not self.possible_words:
                fallback = self._fallback_guess()
                logger.error("Recovery failed; returning fallback guess: %s", fallback)
                return fallback

        # First guess behavior
        if not self.guess_history:
            return self._get_first_guess()

        # If only one candidate left, return it
        if len(self.possible_words) == 1:
            return next(iter(self.possible_words))

        # Initialize population if needed
        if not self.population or self.generation == 0:
            self.population = self._initialize_population()
            # If population still empty, try to seed it
            if not self.population:
                self._seed_population_from_possible_words()

        # Evolve population
        try:
            self.population = self._evolve_population()
            self.generation += 1
        except Exception:
            logger.exception("Evolution step failed, attempting fallback population re-seed.")
            self._seed_population_from_possible_words()

        # Choose best individual (with safety)
        best = self._get_best_individual()
        if not best or not isinstance(best, str):
            logger.warning("Best individual invalid (%r), using fallback.", best)
            return self._fallback_guess()
        return best

    def _get_first_guess(self) -> str:
        """Choose a robust first guess (prefer common starters)."""
        starting_words = ["slate", "crane", "stare", "trace", "raise"]
        for word in starting_words:
            if word in self.possible_words:
                return word
        # fallback to common words or any valid word
        return self._fallback_guess()

    def _fallback_guess(self) -> str:
        """Safe fallback guess (prefer common words, else any valid)."""
        try:
            commons = list(self.word_list.get_common_words() or [])
        except Exception:
            commons = []
        try:
            valids = list(self.word_list.get_valid_words() or [])
        except Exception:
            valids = []

        if commons:
            return commons[0]
        if valids:
            return valids[0]
        # final last-resort word
        return "raise"

    def _initialize_population(self) -> List[str]:
        """Initialize population with random possible words."""
        candidates = list(self.possible_words)
        if not candidates:
            return []
        if len(candidates) <= self.population_size:
            # shuffle to avoid deterministic behavior
            random.shuffle(candidates)
            return candidates.copy()
        return random.sample(candidates, self.population_size)

    def _seed_population_from_possible_words(self) -> None:
        """Seed a minimal population when evolution mechanisms fail."""
        candidates = list(self.possible_words)[: max(1, self.population_size // 4)]
        if not candidates:
            # fallback to valid/common words
            try:
                candidates = list(self.word_list.get_common_words() or [])[:10]
            except Exception:
                candidates = []
        if not candidates:
            try:
                candidates = list(self.word_list.get_valid_words() or [])[:10]
            except Exception:
                candidates = []
        self.population = candidates.copy()

    def _fitness(self, word: str) -> float:
        """Calculate fitness of a word (higher is better)."""
        score = 0.0

        # Letter frequency score (unique letter set)
        for letter in set(word):
            score += self.letter_frequencies.get(letter, 0) * 100

        # Unique letters bonus
        unique = len(set(word))
        score += unique * 20

        # Position diversity heuristic
        for i, letter in enumerate(word):
            score += self._position_score(i, letter)

        # Constraint satisfaction score if we have history
        if self.guess_history:
            score += self._constraint_score(word) * 50

        return score

    def _position_score(self, position: int, letter: str) -> float:
        """Score based on letter position frequency (heuristic)."""
        common_positions = {
            0: {"s": 1.0, "c": 0.8, "t": 0.7, "b": 0.6},
            1: {"a": 1.0, "o": 0.9, "e": 0.8, "i": 0.7},
            2: {"a": 0.9, "i": 0.8, "o": 0.7, "r": 0.6},
            3: {"e": 1.0, "n": 0.8, "a": 0.7, "s": 0.6},
            4: {"e": 1.0, "s": 0.9, "t": 0.8, "d": 0.7},
        }
        return common_positions.get(position, {}).get(letter, 0.1)

    def _constraint_score(self, word: str) -> float:
        """Return 1.0 if word is consistent with previous feedbacks, else 0.0."""
        if not self.feedback_history:
            return 1.0

        for guess, feedback in zip(self.guess_history, self.feedback_history):
            try:
                test_feedback = Feedback(guess, word)
                # If formats differ, be conservative and reward less strongly rather than reject
                if getattr(test_feedback, "feedback", None) is None or getattr(feedback, "feedback", None) is None:
                    # unknown formats -> mild penalty
                    return 0.5
                if test_feedback.feedback != feedback.feedback:
                    return 0.0
            except Exception:
                # If Feedback construction fails, don't harshly penalize candidate
                logger.debug("Feedback comparison failed for guess=%s candidate=%s", guess, word)
                return 0.5
        return 1.0

    def _evolve_population(self) -> List[str]:
        """Evolve population for one generation with checks."""
        if not self.population:
            self._seed_population_from_possible_words()
            if not self.population:
                logger.error("No population to evolve; returning empty population.")
                return []

        # Calculate fitness for all individuals
        fitness_scores = []
        for word in self.population:
            try:
                fitness_scores.append((word, self._fitness(word)))
            except Exception:
                logger.exception("Fitness computation failed for %s; skipping.", word)

        if not fitness_scores:
            logger.warning("No fitness scores computed; attempting to reseed population.")
            self._seed_population_from_possible_words()
            # compute again as best-effort
            fitness_scores = [(w, self._fitness(w)) for w in self.population] if self.population else []

        fitness_scores.sort(key=lambda x: x[1], reverse=True)

        # Elitism: keep best individuals
        new_population = [word for word, _ in fitness_scores[: self.elite_size]]

        # If fitness_scores is small, allow duplicates from top performers
        if not fitness_scores:
            logger.error("Fitness scores empty after reseed; returning previous population safely.")
            return list(self.population)[: self.population_size]

        # Fill rest with offspring
        attempts = 0
        max_attempts = self.population_size * 10  # avoid infinite loop
        while len(new_population) < self.population_size and attempts < max_attempts:
            attempts += 1
            parent1 = self._tournament_selection(fitness_scores)
            parent2 = self._tournament_selection(fitness_scores)

            # Crossover
            child = parent1
            if random.random() < self.crossover_rate and parent1 and parent2:
                child = self._crossover(parent1, parent2)

            # Mutation
            child = self._mutate(child)

            # If child not valid, try to repair using valid/common words heuristic
            if child not in self.possible_words:
                # try to replace some letters with high-frequency letters
                child = self._repair_candidate(child)

            if child in self.possible_words and child not in new_population:
                new_population.append(child)

        # If we couldn't fill population, pad with top candidates
        if len(new_population) < self.population_size:
            logger.warning("Could not fill population by evolution; padding with top candidates.")
            for word, _ in fitness_scores:
                if word not in new_population:
                    new_population.append(word)
                if len(new_population) >= self.population_size:
                    break

        return new_population[: self.population_size]

    def _tournament_selection(self, fitness_scores: List[Tuple[str, float]]) -> str:
        """Select individual using tournament selection (handles small pools)."""
        if not fitness_scores:
            return self._fallback_guess()

        tournament_size = min(5, max(1, len(fitness_scores)))
        tournament = random.sample(fitness_scores, tournament_size)
        return max(tournament, key=lambda x: x[1])[0]

    def _crossover(self, parent1: str, parent2: str) -> str:
        """Single-point crossover with safety."""
        if not parent1 or not parent2:
            return parent1 or parent2 or self._fallback_guess()
        point = random.randint(1, 4)
        child = parent1[:point] + parent2[point:]
        return child

    def _mutate(self, word: str) -> str:
        """Mutate a word but try to keep it valid where possible."""
        if random.random() > self.mutation_rate:
            return word

        # Random mutation: change one letter to a high-frequency letter
        word_list = list(word)
        pos = random.randint(0, 4)
        # pick replacement letter from frequency distribution or alphabet
        if self.letter_frequencies:
            letters, weights = zip(*self.letter_frequencies.items())
            replacement = random.choices(letters, weights=weights, k=1)[0]
        else:
            replacement = random.choice("abcdefghijklmnopqrstuvwxyz")
        word_list[pos] = replacement
        candidate = "".join(word_list)

        # If candidate is not in valid words, try to repair
        if candidate not in self.possible_words:
            candidate = self._repair_candidate(candidate)
        return candidate

    def _repair_candidate(self, candidate: str) -> str:
        """Attempt to repair a candidate to a valid possible word."""
        # 1) If any valid word with same pattern exists, pick it
        #    (simple heuristic: swap letters with high-frequency ones)
        try:
            valids = set(self.word_list.get_valid_words() or [])
            commons = list(self.word_list.get_common_words() or [])
        except Exception:
            valids = set()
            commons = []

        # try commons first
        for w in commons:
            if sum(a == b for a, b in zip(w, candidate)) >= 3:
                return w

        # try valids
        for w in valids:
            if sum(a == b for a, b in zip(w, candidate)) >= 3:
                return w

        # fallback to any possible word
        if self.possible_words:
            return next(iter(self.possible_words))

        # ultimate fallback
        return self._fallback_guess()

    def _get_best_individual(self) -> str:
        """Get best individual from current population in a safe way."""
        if not self.population:
            return self._fallback_guess()
        fitness_scores = []
        for word in self.population:
            try:
                fitness_scores.append((word, self._fitness(word)))
            except Exception:
                logger.exception("Fitness error for %s", word)
        if not fitness_scores:
            return self._fallback_guess()
        return max(fitness_scores, key=lambda x: x[1])[0]

    def update_state(self, guess: str, feedback: Feedback) -> None:
        """Update solver state based on feedback and reset population appropriately."""
        if guess:
            self.guess_history.append(guess)
        self.feedback_history.append(feedback)

        # Filter possible words using BaseSolver method if available (protected)
        before = len(self.possible_words)
        try:
            if hasattr(super(), "_filter_words_by_feedback"):
                try:
                    super()._filter_words_by_feedback(guess, feedback)
                except Exception:
                    logger.exception("BaseSolver._filter_words_by_feedback failed; performing conservative local filter.")
                    self._local_filter(guess, feedback)
            else:
                self._local_filter(guess, feedback)
        except Exception:
            logger.exception("Error during filtering step.")

        after = len(self.possible_words)
        logger.info("Genetic update_state: possible_words before=%d after=%d", before, after)

        # Reset population to force re-initialization in next generation
        self.population = []
        self.generation = 0

        if not self.possible_words:
            logger.warning("possible_words empty after update_state; attempting recovery.")
            self._recover_possible_words()

    def _local_filter(self, guess: str, feedback: Feedback) -> None:
        """Conservative local filtering fallback (similar to RL local filter)."""
        statuses = getattr(feedback, "feedback", None)
        if statuses is None:
            logger.debug("Feedback object missing .feedback; skipping local filter.")
            return

        keep = set(self.possible_words)
        for i, status in enumerate(statuses):
            letter = guess[i]
            if status == LetterStatus.CORRECT:
                keep = {w for w in keep if len(w) > i and w[i] == letter}
            elif status == LetterStatus.ABSENT:
                # conservative: remove words that have letter at all
                keep = {w for w in keep if letter not in w}
            elif status == LetterStatus.PRESENT:
                keep = {w for w in keep if (letter in w and (len(w) <= i or w[i] != letter))}
        if keep:
            self.possible_words = keep
        else:
            logger.debug("Local filter would remove all words; preserving previous possible_words to avoid empty set.")

    def _recover_possible_words(self) -> None:
        """Attempt to recover possible_words when the set becomes empty."""
        logger.info("Attempting to recover possible_words for GeneticSolver.")
        try:
            valids = set(self.word_list.get_valid_words() or [])
            commons = set(self.word_list.get_common_words() or [])
        except Exception:
            valids = set()
            commons = set()

        candidates = (commons & valids) or valids or commons
        if candidates:
            candidates = {w for w in candidates if w not in set(self.guess_history)}
            if candidates:
                self.possible_words = set(candidates)
                logger.info("Recovered possible_words with %d candidates.", len(self.possible_words))
                return

        all_candidates = set(self.guess_history) | valids | commons
        if all_candidates:
            self.possible_words = all_candidates
            logger.info("Recovered possible_words from history/valids/commons; size=%d", len(self.possible_words))
            return

        logger.error("Unable to recover any possible words; possible_words remains empty.")

    def reset(self) -> None:
        """Reset solver state for a new game (preserve some learned data if desired)."""
        super().reset()
        try:
            valid_words = list(self.word_list.get_valid_words() or [])
        except Exception:
            valid_words = []
        self.possible_words = set(valid_words)
        self.population = []
        self.generation = 0
        self.guess_history = []
        self.feedback_history = []
