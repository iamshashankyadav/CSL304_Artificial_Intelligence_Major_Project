"""
Wordle environment for reinforcement learning.
"""

import numpy as np
from typing import Tuple, List
from core.feedback import Feedback, LetterStatus


class WordleEnvironment:
    """Wordle game environment for RL agents."""

    def __init__(self, word_list: List[str], max_attempts: int = 6):
        """
        Initialize environment.

        Args:
            word_list: List of valid words
            max_attempts: Maximum number of attempts
        """
        self.word_list = word_list
        self.max_attempts = max_attempts
        self.word_to_idx = {word: idx for idx, word in enumerate(word_list)}
        self.idx_to_word = {idx: word for word, idx in self.word_to_idx.items()}

        self.target_word = None
        self.current_attempt = 0
        self.done = False
        self.history = []

    def reset(self, target_word: str = None) -> np.ndarray:
        """
        Reset environment for new episode.

        Args:
            target_word: Specific target word (None for random)

        Returns:
            Initial state
        """
        if target_word is None:
            target_word = np.random.choice(self.word_list)

        self.target_word = target_word
        self.current_attempt = 0
        self.done = False
        self.history = []

        return self._get_state()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, dict]:
        """
        Take a step in the environment.

        Args:
            action: Index of word to guess

        Returns:
            Tuple of (next_state, reward, done, info)
        """
        if self.done:
            raise ValueError("Episode is done. Call reset() to start new episode.")

        guess = self.idx_to_word[action]
        feedback = Feedback(guess, self.target_word)

        self.history.append((guess, feedback))
        self.current_attempt += 1

        # Calculate reward
        reward = self._calculate_reward(feedback)

        # Check if done
        if feedback.is_correct():
            self.done = True
            reward += 10.0  # Bonus for winning
        elif self.current_attempt >= self.max_attempts:
            self.done = True
            reward -= 5.0  # Penalty for losing

        next_state = self._get_state()
        info = {"guess": guess, "feedback": feedback}

        return next_state, reward, self.done, info

    def _get_state(self) -> np.ndarray:
        """Get current state representation."""
        # State: flattened representation of all previous guesses and feedbacks
        # Plus remaining attempts
        state_size = (self.max_attempts * 5 * 3) + 1  # 5 letters * 3 states + attempts
        state = np.zeros(state_size)

        # Encode history
        for i, (guess, feedback) in enumerate(self.history):
            for j, (letter, status) in enumerate(zip(guess, feedback.feedback)):
                base_idx = i * 15 + j * 3
                # One-hot encode letter status
                state[base_idx + status.value] = 1

        # Add remaining attempts
        state[-1] = (self.max_attempts - self.current_attempt) / self.max_attempts

        return state

    def _calculate_reward(self, feedback: Feedback) -> float:
        """Calculate reward for a guess."""
        reward = 0.0

        # Reward correct positions
        correct_positions = sum(
            1 for s in feedback.feedback if s == LetterStatus.CORRECT
        )
        reward += correct_positions * 2.0

        # Small reward for present letters
        present_letters = sum(1 for s in feedback.feedback if s == LetterStatus.PRESENT)
        reward += present_letters * 0.5

        # Small penalty for each attempt
        reward -= 0.1

        return reward

    def get_valid_actions(self) -> List[int]:
        """Get list of valid action indices."""
        return list(range(len(self.word_list)))
