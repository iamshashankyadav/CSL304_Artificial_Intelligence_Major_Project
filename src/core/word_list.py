"""
Word list management for Wordle solver.
"""

import os
from typing import List, Set
import logging

logger = logging.getLogger(__name__)


class WordList:
    """Manages word lists for Wordle game."""

    def __init__(self, valid_words_path: str, common_words_path: str = None):
        """
        Initialize word lists.

        Args:
            valid_words_path: Path to file containing all valid words
            common_words_path: Path to file containing common answer words
        """
        self.valid_words = self._load_words(valid_words_path)
        self.common_words = (
            self._load_words(common_words_path)
            if common_words_path
            else self.valid_words
        )
        logger.info(
            f"Loaded {len(self.valid_words)} valid words and {len(self.common_words)} common words"
        )

    def _load_words(self, filepath: str) -> Set[str]:
        """Load words from file."""
        if not os.path.exists(filepath):
            logger.warning(f"Word file not found: {filepath}")
            return self._get_default_words()

        with open(filepath, "r") as f:
            words = {line.strip().lower() for line in f if len(line.strip()) == 5}
        return words

    def _get_default_words(self) -> Set[str]:
        """Return a default set of words if file not found."""
        # Small default set for testing
        return {
            "slate",
            "crane",
            "crate",
            "stare",
            "trace",
            "arise",
            "raise",
            "about",
            "alert",
            "argue",
            "beach",
            "above",
            "acute",
            "admit",
            "adopt",
            "adult",
            "after",
            "again",
            "agent",
            "agree",
            "ahead",
            "alarm",
            "album",
            "allow",
            "alone",
            "along",
            "alter",
            "angel",
        }

    def is_valid(self, word: str) -> bool:
        """Check if word is valid."""
        return word.lower() in self.valid_words

    def get_valid_words(self) -> List[str]:
        """Get all valid words as a list."""
        return sorted(list(self.valid_words))

    def get_common_words(self) -> List[str]:
        """Get common answer words as a list."""
        return sorted(list(self.common_words))

    def filter_words(self, words: Set[str]) -> Set[str]:
        """Filter to only valid words."""
        return words & self.valid_words
