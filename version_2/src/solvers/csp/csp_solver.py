"""
Constraint Satisfaction Problem solver for Wordle.
"""

from typing import List, Set
from ..base_solver import BaseSolver
from .constraints import ConstraintSet
from ...core.feedback import Feedback
from ...core.word_list import WordList
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class CSPSolver(BaseSolver):
    """Wordle solver using Constraint Satisfaction Problem approach."""

    def __init__(self, word_list: WordList, config: dict = None):
        super().__init__(word_list, config)
        self.constraints = ConstraintSet()
        self.letter_frequencies = self._compute_letter_frequencies()

    def _compute_letter_frequencies(self) -> dict:
        """Compute letter frequency across all words."""
        freq = Counter()
        for word in self.word_list.get_common_words():
            for letter in set(word):
                freq[letter] += 1
        return dict(freq)

    def get_next_guess(self) -> str:
        """Get next guess using CSP approach with heuristics."""
        if not self.guess_history:
            # First guess - use word with high frequency letters
            return self._get_optimal_first_guess()

        # Filter words that satisfy all constraints
        valid_words = [
            w for w in self.possible_words if self.constraints.is_satisfied(w)
        ]

        if not valid_words:
            logger.warning("No valid words found, using fallback")
            return self._get_fallback_guess()

        if len(valid_words) == 1:
            return valid_words[0]

        # Use heuristic to select best word
        return self._select_best_word(valid_words)

    def _get_optimal_first_guess(self) -> str:
        """Get optimal first guess."""
        # Common starting words with diverse letters
        starting_words = ["slate", "crane", "crate", "stare", "trace"]

        for word in starting_words:
            if word in self.possible_words:
                return word

        return list(self.possible_words)[0]

    def _select_best_word(self, valid_words: List[str]) -> str:
        """Select best word using heuristics."""
        # Score words based on letter frequency and uniqueness
        scores = {}

        for word in valid_words:
            score = 0
            unique_letters = set(word)

            # Reward unique letters
            score += len(unique_letters) * 10

            # Reward common letters
            for letter in unique_letters:
                score += self.letter_frequencies.get(letter, 0)

            scores[word] = score

        # Return word with highest score
        best_word = max(scores.items(), key=lambda x: x[1])[0]
        return best_word

    def _get_fallback_guess(self) -> str:
        """Get fallback guess when no valid words found."""
        if self.possible_words:
            return list(self.possible_words)[0]
        return "slate"

    def update_state(self, guess: str, feedback: Feedback) -> None:
        """Update CSP constraints based on feedback."""
        self.guess_history.append(guess)
        self.feedback_history.append(feedback)

        # Add constraints from feedback
        self.constraints.add_from_feedback(guess, feedback)

        # Filter possible words
        self._filter_words_by_feedback(guess, feedback)

        logger.info(f"CSP: {len(self.possible_words)} words remaining after '{guess}'")

    def reset(self) -> None:
        """Reset solver state."""
        super().reset()
        self.constraints = ConstraintSet()
