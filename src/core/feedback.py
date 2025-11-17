"""
Feedback processing for Wordle game.
"""

from enum import Enum
from typing import List, Tuple
from collections import Counter


class LetterStatus(Enum):
    """Status of a letter in a guess."""

    CORRECT = 2  # Green - correct letter in correct position
    PRESENT = 1  # Yellow - correct letter in wrong position
    ABSENT = 0  # Gray - letter not in word


class Feedback:
    """Represents feedback for a Wordle guess."""

    def __init__(self, guess: str, target: str):
        """
        Generate feedback for a guess.

        Args:
            guess: The guessed word
            target: The target word
        """
        self.guess = guess.lower()
        self.target = target.lower()
        self.feedback = self._generate_feedback()

    def _generate_feedback(self) -> List[LetterStatus]:
        """
        Generate feedback using Wordle's rules.

        Returns:
            List of LetterStatus for each position
        """
        feedback = [LetterStatus.ABSENT] * len(self.guess)
        target_chars = list(self.target)

        # First pass: Mark correct positions (green)
        for i, (g_char, t_char) in enumerate(zip(self.guess, self.target)):
            if g_char == t_char:
                feedback[i] = LetterStatus.CORRECT
                target_chars[i] = None  # Mark as used

        # Second pass: Mark present letters (yellow)
        for i, g_char in enumerate(self.guess):
            if feedback[i] == LetterStatus.ABSENT and g_char in target_chars:
                feedback[i] = LetterStatus.PRESENT
                target_chars[target_chars.index(g_char)] = None  # Mark as used

        return feedback

    def to_string(self) -> str:
        """Convert feedback to string representation."""
        mapping = {
            LetterStatus.CORRECT: "🟩",
            LetterStatus.PRESENT: "🟨",
            LetterStatus.ABSENT: "⬜",
        }
        return "".join(mapping[status] for status in self.feedback)

    def to_color_codes(self) -> List[str]:
        """Convert feedback to color codes for UI."""
        mapping = {
            LetterStatus.CORRECT: "green",
            LetterStatus.PRESENT: "yellow",
            LetterStatus.ABSENT: "gray",
        }
        return [mapping[status] for status in self.feedback]

    def to_numeric(self) -> List[int]:
        """Convert feedback to numeric values."""
        return [status.value for status in self.feedback]

    def is_correct(self) -> bool:
        """Check if the guess is completely correct."""
        return all(status == LetterStatus.CORRECT for status in self.feedback)

    def get_correct_positions(self) -> List[int]:
        """Get indices of correctly placed letters."""
        return [
            i
            for i, status in enumerate(self.feedback)
            if status == LetterStatus.CORRECT
        ]

    def get_present_letters(self) -> set:
        """Get letters that are present but misplaced."""
        return {
            self.guess[i]
            for i, status in enumerate(self.feedback)
            if status == LetterStatus.PRESENT
        }

    def get_absent_letters(self) -> set:
        """Get letters that are not in the word."""
        return {
            self.guess[i]
            for i, status in enumerate(self.feedback)
            if status == LetterStatus.ABSENT
        }
