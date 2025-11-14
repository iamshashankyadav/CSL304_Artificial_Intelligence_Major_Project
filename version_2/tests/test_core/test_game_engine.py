"""
Tests for game engine.
"""

import pytest
from src.core.game_engine import WordleGame, GameState
from src.core.word_list import WordList


@pytest.fixture
def word_list():
    """Create a test word list."""
    return WordList("data/words/valid_words.txt", "data/words/common_words.txt")


@pytest.fixture
def game(word_list):
    """Create a test game."""
    return WordleGame(word_list)


def test_game_initialization(game):
    """Test game initialization."""
    assert game.max_attempts == 6
    assert game.current_game is None


def test_start_new_game(game):
    """Test starting a new game."""
    game_state = game.start_new_game("slate")

    assert game_state is not None
    assert game_state.target_word == "slate"
    assert game_state.attempts == 0
    assert not game_state.is_won
    assert not game_state.is_over


def test_valid_guess(game):
    """Test making a valid guess."""
    game.start_new_game("slate")
    success, feedback, error = game.make_guess("crane")

    assert success
    assert feedback is not None
    assert error == ""


def test_invalid_guess_length(game):
    """Test guess with wrong length."""
    game.start_new_game("slate")
    success, feedback, error = game.make_guess("cat")

    assert not success
    assert feedback is None
    assert error != ""


def test_winning_game(game):
    """Test winning a game."""
    game.start_new_game("slate")
    success, feedback, error = game.make_guess("slate")

    assert success
    assert feedback.is_correct()
    assert game.current_game.is_won
    assert game.current_game.is_over


def test_losing_game(game):
    """Test losing a game."""
    game.start_new_game("slate")

    # Make 6 wrong guesses
    for _ in range(6):
        game.make_guess("crane")

    assert not game.current_game.is_won
    assert game.current_game.is_over
