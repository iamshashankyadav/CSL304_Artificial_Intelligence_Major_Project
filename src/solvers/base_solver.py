"""
Abstract base class for all Wordle solvers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from core.feedback import Feedback
from core.word_list import WordList
import logging

logger = logging.getLogger(__name__)


class BaseSolver(ABC):
    """Abstract base class for Wordle solving algorithms."""

    def __init__(self, word_list: WordList, config: Dict[str, Any] = None):
        """
        Initialize solver.

        Args:
            word_list: WordList instance
            config: Configuration dictionary
        """
        self.word_list = word_list
        self.config = config or {}
        self.possible_words = set(word_list.get_common_words())
        self.guess_history: List[str] = []
        self.feedback_history: List[Feedback] = []
        self.candidates: List[Dict[str, Any]] = []  # Top candidates with scores
        self.selection_info: Dict[str, Any] = {}  # Additional selection info

    @abstractmethod
    def get_next_guess(self) -> str:
        """
        Get the next guess based on current state.

        Returns:
            The next word to guess
        """
        pass

    @abstractmethod
    def update_state(self, guess: str, feedback: Feedback) -> None:
        """
        Update solver state based on feedback.

        Args:
            guess: The guessed word
            feedback: Feedback received
        """
        pass

    def reset(self) -> None:
        """Reset solver to initial state."""
        self.possible_words = set(self.word_list.get_common_words())
        self.guess_history = []
        self.feedback_history = []
        self.candidates = []
        self.selection_info = {}
        logger.info(f"{self.__class__.__name__} reset")

    def get_statistics(self) -> Dict[str, Any]:
        """Get solver statistics."""
        return {
            "guesses_made": len(self.guess_history),
            "remaining_words": len(self.possible_words),
            "algorithm": self.__class__.__name__,
            "candidates": self.candidates,
            "selection_info": self.selection_info,
        }

    def _filter_words_by_feedback(self, guess: str, feedback: Feedback) -> None:
        """
        Filter possible words based on feedback.

        Args:
            guess: The guessed word
            feedback: Feedback received
        """
        new_possible_words = set()

        for word in self.possible_words:
            if self._word_matches_feedback(word, guess, feedback):
                new_possible_words.add(word)

        self.possible_words = new_possible_words
        logger.debug(f"Filtered to {len(self.possible_words)} possible words")

    def _word_matches_feedback(self, word: str, guess: str, feedback: Feedback) -> bool:
        """
        Check if a word is consistent with the feedback.

        Args:
            word: Word to check
            guess: The guessed word
            feedback: Feedback received

        Returns:
            True if word is consistent with feedback
        """
        from core.feedback import LetterStatus, Feedback as FeedbackClass

        # Generate what the feedback would be for this word
        test_feedback = FeedbackClass(guess, word)

        # Check if feedbacks match
        return test_feedback.feedback == feedback.feedback
