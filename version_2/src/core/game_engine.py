"""
Wordle game engine implementation.
"""

from typing import List, Optional, Tuple
from .feedback import Feedback, LetterStatus
from .validator import Validator
from .word_list import WordList
import random
import logging

logger = logging.getLogger(__name__)


class GameState:
    """Represents the current state of a Wordle game."""

    def __init__(self, target_word: str, max_attempts: int = 6):
        """
        Initialize game state.

        Args:
            target_word: The word to guess
            max_attempts: Maximum number of attempts allowed
        """
        self.target_word = target_word.lower()
        self.max_attempts = max_attempts
        self.attempts = 0
        self.guesses: List[str] = []
        self.feedbacks: List[Feedback] = []
        self.is_won = False
        self.is_over = False

    def make_guess(self, guess: str) -> Feedback:
        """
        Make a guess and get feedback.

        Args:
            guess: The guessed word

        Returns:
            Feedback object
        """
        guess = guess.lower()
        self.guesses.append(guess)
        self.attempts += 1

        feedback = Feedback(guess, self.target_word)
        self.feedbacks.append(feedback)

        if feedback.is_correct():
            self.is_won = True
            self.is_over = True
        elif self.attempts >= self.max_attempts:
            self.is_over = True

        return feedback

    def get_history(self) -> List[Tuple[str, Feedback]]:
        """Get history of guesses and feedbacks."""
        return list(zip(self.guesses, self.feedbacks))


class WordleGame:
    """Main Wordle game controller."""

    def __init__(self, word_list: WordList, max_attempts: int = 6):
        """
        Initialize Wordle game.

        Args:
            word_list: WordList instance
            max_attempts: Maximum number of attempts
        """
        self.word_list = word_list
        self.max_attempts = max_attempts
        self.validator = Validator(word_list)
        self.current_game: Optional[GameState] = None

    def start_new_game(self, target_word: Optional[str] = None) -> GameState:
        """
        Start a new game.

        Args:
            target_word: Specific word to use (None for random)

        Returns:
            New GameState instance
        """
        if target_word is None:
            target_word = random.choice(self.word_list.get_common_words())

        self.current_game = GameState(target_word, self.max_attempts)
        logger.info(f"New game started with word: {target_word}")
        return self.current_game

    def make_guess(self, guess: str) -> Tuple[bool, Feedback, str]:
        """
        Make a guess in the current game.

        Args:
            guess: The guessed word

        Returns:
            Tuple of (success, feedback, error_message)
        """
        if self.current_game is None:
            return False, None, "No active game"

        if self.current_game.is_over:
            return False, None, "Game is already over"

        # Validate guess
        is_valid, error_msg = self.validator.validate(guess)
        if not is_valid:
            return False, None, error_msg

        # Make guess
        guess = self.validator.sanitize(guess)
        feedback = self.current_game.make_guess(guess)

        return True, feedback, ""

    def get_game_state(self) -> Optional[GameState]:
        """Get current game state."""
        return self.current_game

    def get_statistics(self) -> dict:
        """Get game statistics."""
        if self.current_game is None:
            return {}

        return {
            "attempts": self.current_game.attempts,
            "max_attempts": self.current_game.max_attempts,
            "is_won": self.current_game.is_won,
            "is_over": self.current_game.is_over,
            "target_word": (
                self.current_game.target_word if self.current_game.is_over else None
            ),
        }
