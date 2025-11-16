"""
Bayesian/Probabilistic solver using information theory.
"""

from typing import List, Dict, Set
from solvers.base_solver import BaseSolver
from core.feedback import Feedback, LetterStatus
from core.word_list import WordList
import math
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class BayesianSolver(BaseSolver):
    """Wordle solver using Bayesian probability and information gain."""

    def __init__(self, word_list: WordList, config: dict = None):
        super().__init__(word_list, config)
        self.word_probabilities = self._initialize_probabilities()
        self.entropy_threshold = config.get("entropy_threshold", 0.5) if config else 0.5

    def _initialize_probabilities(self) -> Dict[str, float]:
        """Initialize uniform probabilities for all words."""
        words = list(self.possible_words)
        prob = 1.0 / len(words)
        return {word: prob for word in words}

    def get_next_guess(self) -> str:
        """Get next guess by maximizing expected information gain."""
        if not self.guess_history:
            return self._get_first_guess()

        if len(self.possible_words) == 1:
            return list(self.possible_words)[0]

        if len(self.possible_words) <= 2:
            # Just guess from remaining words
            return max(self.word_probabilities.items(), key=lambda x: x[1])[0]

        # Calculate expected information gain for each possible guess
        best_guess = self._maximize_information_gain()
        return best_guess

    def _get_first_guess(self) -> str:
        """Get optimal first guess."""
        # Pre-computed optimal starting words based on information theory
        optimal_starters = ["soare", "roate", "raise", "slate", "crane"]

        for word in optimal_starters:
            if word in self.possible_words:
                return word

        return list(self.possible_words)[0]

    def _maximize_information_gain(self) -> str:
        """Find word that maximizes expected information gain."""
        # For performance, sample if too many words
        candidate_guesses = list(self.possible_words)
        if len(candidate_guesses) > 20:
            # Sample most probable words plus some exploration
            sorted_words = sorted(
                self.word_probabilities.items(), key=lambda x: x[1], reverse=True
            )
            candidate_guesses = [w for w, _ in sorted_words[:20]]

        best_guess = None
        best_score = -float("inf")
        scores = {}

        for guess in candidate_guesses:
            expected_info = self._calculate_expected_information(guess)
            scores[guess] = expected_info

            if expected_info > best_score:
                best_score = expected_info
                best_guess = guess

        # Update candidates for UI
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        self.candidates = [
            {"word": word, "score": f"{score:.4f}"}
            for word, score in sorted_scores[:5]
        ]
        
        entropy = self._calculate_entropy()
        self.selection_info = {
            "method": "Bayesian Information Theory",
            "entropy": f"{entropy:.2f}",
            "candidates_evaluated": len(scores),
            "total_remaining": len(self.possible_words),
        }

        return best_guess

    def _calculate_expected_information(self, guess: str) -> float:
        """Calculate expected information gain for a guess."""
        # from ...core.feedback import Feedback as FeedbackClass

        # Group possible answers by their feedback pattern
        pattern_groups: Dict[tuple, List[str]] = {}

        for answer in self.possible_words:
            feedback = Feedback(guess, answer)
            pattern = tuple(feedback.to_numeric())

            if pattern not in pattern_groups:
                pattern_groups[pattern] = []
            pattern_groups[pattern].append(answer)

        # Calculate entropy
        total_prob = sum(self.word_probabilities.get(w, 0) for w in self.possible_words)
        expected_info = 0.0

        for pattern, words in pattern_groups.items():
            # Probability of this pattern
            pattern_prob = (
                sum(self.word_probabilities.get(w, 0) for w in words) / total_prob
            )

            if pattern_prob > 0:
                # Information gained from this pattern
                info = -math.log2(pattern_prob)
                expected_info += pattern_prob * info

        return expected_info

    def _calculate_entropy(self) -> float:
        """Calculate current entropy of word distribution."""
        entropy = 0.0
        total_prob = sum(self.word_probabilities.values())

        for prob in self.word_probabilities.values():
            if prob > 0:
                normalized_prob = prob / total_prob
                entropy -= normalized_prob * math.log2(normalized_prob)

        return entropy

    def update_state(self, guess: str, feedback: Feedback) -> None:
        """Update probabilities based on Bayesian inference."""
        self.guess_history.append(guess)
        self.feedback_history.append(feedback)

        # Filter words and update probabilities
        self._bayesian_update(guess, feedback)

        # Normalize probabilities
        self._normalize_probabilities()

        entropy = self._calculate_entropy()
        logger.info(
            f"Bayesian: {len(self.possible_words)} words remaining. "
            f"Entropy: {entropy:.2f}"
        )

    def _bayesian_update(self, guess: str, feedback: Feedback) -> None:
        """Update probabilities using Bayes' rule."""
        # from ...core.feedback import Feedback as FeedbackClass

        # Keep only words consistent with feedback
        new_probabilities = {}

        for word in self.possible_words:
            # Check if word is consistent with feedback
            test_feedback = Feedback(guess, word)

            if test_feedback.feedback == feedback.feedback:
                new_probabilities[word] = self.word_probabilities.get(word, 1.0)

        self.word_probabilities = new_probabilities
        self.possible_words = set(new_probabilities.keys())

    def _normalize_probabilities(self) -> None:
        """Normalize probabilities to sum to 1."""
        total = sum(self.word_probabilities.values())
        if total > 0:
            self.word_probabilities = {
                word: prob / total for word, prob in self.word_probabilities.items()
            }

    def reset(self) -> None:
        """Reset solver state."""
        super().reset()
        self.word_probabilities = self._initialize_probabilities()
