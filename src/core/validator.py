"""
Guess validation for Wordle game.
"""

from typing import List, Tuple
import re


class Validator:
    """Validates Wordle guesses."""

    def __init__(self, word_list):
        """
        Initialize validator.

        Args:
            word_list: WordList instance
        """
        self.word_list = word_list

    def validate(self, guess: str) -> Tuple[bool, str]:
        """
        Validate a guess.

        Args:
            guess: The word to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not guess:
            return False, "Guess cannot be empty"

        guess = guess.strip().lower()

        # Check length
        if len(guess) != 5:
            return False, f"Word must be 5 letters long (got {len(guess)})"

        # Check if alphabetic
        if not guess.isalpha():
            return False, "Word must contain only letters"

        # Check if valid word
        if not self.word_list.is_valid(guess):
            return False, f"'{guess}' is not a valid word"

        return True, ""

    def sanitize(self, guess: str) -> str:
        """Sanitize and normalize a guess."""
        return guess.strip().lower()
