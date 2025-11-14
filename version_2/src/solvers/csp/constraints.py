"""
Constraint definitions for CSP solver.
"""

from typing import Set, List, Dict
from ...core.feedback import Feedback, LetterStatus


class Constraint:
    """Base class for constraints."""

    def is_satisfied(self, word: str) -> bool:
        """Check if word satisfies constraint."""
        raise NotImplementedError


class PositionConstraint(Constraint):
    """Constraint for letter at specific position."""

    def __init__(self, position: int, letter: str):
        self.position = position
        self.letter = letter

    def is_satisfied(self, word: str) -> bool:
        return word[self.position] == self.letter


class ExcludePositionConstraint(Constraint):
    """Constraint to exclude letter from specific position."""

    def __init__(self, position: int, letter: str):
        self.position = position
        self.letter = letter

    def is_satisfied(self, word: str) -> bool:
        return word[self.position] != self.letter


class ContainsLetterConstraint(Constraint):
    """Constraint that word must contain letter."""

    def __init__(self, letter: str):
        self.letter = letter

    def is_satisfied(self, word: str) -> bool:
        return self.letter in word


class ExcludeLetterConstraint(Constraint):
    """Constraint that word must not contain letter."""

    def __init__(self, letter: str):
        self.letter = letter

    def is_satisfied(self, word: str) -> bool:
        return self.letter not in word


class ConstraintSet:
    """Collection of constraints."""

    def __init__(self):
        self.constraints: List[Constraint] = []

    def add_constraint(self, constraint: Constraint):
        """Add a constraint."""
        self.constraints.append(constraint)

    def is_satisfied(self, word: str) -> bool:
        """Check if word satisfies all constraints."""
        return all(c.is_satisfied(word) for c in self.constraints)

    def add_from_feedback(self, guess: str, feedback: Feedback):
        """Add constraints based on feedback."""
        for i, (letter, status) in enumerate(zip(guess, feedback.feedback)):
            if status == LetterStatus.CORRECT:
                self.add_constraint(PositionConstraint(i, letter))
            elif status == LetterStatus.PRESENT:
                self.add_constraint(ContainsLetterConstraint(letter))
                self.add_constraint(ExcludePositionConstraint(i, letter))
            elif status == LetterStatus.ABSENT:
                # Only exclude if letter doesn't appear as CORRECT or PRESENT elsewhere
                if letter not in [
                    guess[j]
                    for j, s in enumerate(feedback.feedback)
                    if s in [LetterStatus.CORRECT, LetterStatus.PRESENT]
                ]:
                    self.add_constraint(ExcludeLetterConstraint(letter))
