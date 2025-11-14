"""
Reinforcement Learning solver for Wordle.
"""

from typing import List, Dict
from ..base_solver import BaseSolver
from ...core.feedback import Feedback
from ...core.word_list import WordList
import numpy as np
import logging

logger = logging.getLogger(__name__)


class RLSolver(BaseSolver):
    """Wordle solver using Reinforcement Learning (simplified Q-learning)."""

    def __init__(self, word_list: WordList, config: dict = None):
        super().__init__(word_list, config)
        self.config = config or {}
        self.epsilon = self.config.get("epsilon", 0.1)

        # Simplified Q-table: state -> action -> Q-value
        # For simplicity, we'll use a heuristic-based approach
        # In a full implementation, this would be a neural network
        self.q_values = {}

        # Letter position preferences learned over time
        self.position_preferences = self._initialize_preferences()

    def _initialize_preferences(self) -> Dict:
        """Initialize position preferences from word frequency."""
        preferences = [{} for _ in range(5)]

        for word in self.word_list.get_common_words():
            for i, letter in enumerate(word):
                preferences[i][letter] = preferences[i].get(letter, 0) + 1

        # Normalize
        for i in range(5):
            total = sum(preferences[i].values())
            preferences[i] = {k: v / total for k, v in preferences[i].items()}

        return preferences

    def get_next_guess(self) -> str:
        """Get next guess using epsilon-greedy policy."""
        if not self.guess_history:
            return self._get_first_guess()

        if len(self.possible_words) == 1:
            return list(self.possible_words)[0]

        # Epsilon-greedy action selection
        if np.random.random() < self.epsilon:
            # Explore: random valid word
            return np.random.choice(list(self.possible_words))
        else:
            # Exploit: use learned policy
            return self._select_best_action()

    def _get_first_guess(self) -> str:
        """Get first guess based on learned preferences."""
        starting_words = ["slate", "crane", "stare", "raise", "arise"]

        for word in starting_words:
            if word in self.possible_words:
                return word

        return list(self.possible_words)[0]

    def _select_best_action(self) -> str:
        """Select best action based on current policy."""
        # Score each possible word
        scores = {}

        for word in self.possible_words:
            score = self._evaluate_word(word)
            scores[word] = score

        # Return highest scoring word
        return max(scores.items(), key=lambda x: x[1])[0]

    def _evaluate_word(self, word: str) -> float:
        """Evaluate a word using learned preferences."""
        score = 0.0

        # Position-based scoring
        for i, letter in enumerate(word):
            score += self.position_preferences[i].get(letter, 0) * 10

        # Diversity bonus
        unique_letters = len(set(word))
        score += unique_letters * 2

        # Exploration bonus if few guesses made
        if len(self.guess_history) < 2:
            score += unique_letters * 3

        return score

    def update_state(self, guess: str, feedback: Feedback) -> None:
        """Update learned policy based on feedback."""
        self.guess_history.append(guess)
        self.feedback_history.append(feedback)

        # Update preferences based on feedback
        self._update_preferences(guess, feedback)

        # Filter possible words
        self._filter_words_by_feedback(guess, feedback)

        logger.info(f"RL: {len(self.possible_words)} words remaining")

    def _update_preferences(self, guess: str, feedback: Feedback) -> None:
        """Update position preferences based on feedback (simple learning)."""
        from ...core.feedback import LetterStatus

        learning_rate = 0.1

        for i, (letter, status) in enumerate(zip(guess, feedback.feedback)):
            if status == LetterStatus.CORRECT:
                # Increase preference for this letter at this position
                current = self.position_preferences[i].get(letter, 0)
                self.position_preferences[i][letter] = current + learning_rate
            elif status == LetterStatus.ABSENT:
                # Decrease preference for this letter
                current = self.position_preferences[i].get(letter, 0)
                self.position_preferences[i][letter] = max(
                    0, current - learning_rate * 0.5
                )

        # Re-normalize
        for i in range(5):
            total = sum(self.position_preferences[i].values())
            if total > 0:
                self.position_preferences[i] = {
                    k: v / total for k, v in self.position_preferences[i].items()
                }

    def reset(self) -> None:
        """Reset solver state."""
        super().reset()
        # Keep learned preferences across games
