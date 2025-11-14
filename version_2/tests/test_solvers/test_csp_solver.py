"""
Tests for CSP solver.
"""

import pytest
from src.solvers.csp.csp_solver import CSPSolver
from src.core.word_list import WordList
from src.core.feedback import Feedback


@pytest.fixture
def word_list():
    """Create a test word list."""
    return WordList("data/words/valid_words.txt", "data/words/common_words.txt")


@pytest.fixture
def solver(word_list):
    """Create a CSP solver."""
    return CSPSolver(word_list)


def test_solver_initialization(solver):
    """Test solver initialization."""
    assert solver is not None
    assert len(solver.possible_words) > 0


def test_first_guess(solver):
    """Test that first guess is valid."""
    guess = solver.get_next_guess()
    assert len(guess) == 5
    assert guess in solver.word_list.get_valid_words()


def test_update_state(solver):
    """Test updating solver state."""
    initial_words = len(solver.possible_words)

    guess = "slate"
    feedback = Feedback(guess, "crane")
    solver.update_state(guess, feedback)

    # Number of possible words should decrease
    assert len(solver.possible_words) < initial_words


def test_reset(solver):
    """Test resetting solver."""
    # Make a guess
    guess = solver.get_next_guess()
    feedback = Feedback(guess, "slate")
    solver.update_state(guess, feedback)

    # Reset
    solver.reset()

    assert len(solver.guess_history) == 0
    assert len(solver.feedback_history) == 0
