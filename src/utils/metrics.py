"""
Performance metrics tracking.
"""

from typing import List, Dict
import statistics


class PerformanceMetrics:
    """Track and calculate performance metrics."""

    def __init__(self):
        """Initialize metrics tracker."""
        self.games_played = 0
        self.games_won = 0
        self.guess_counts = []
        self.solve_times = []

    def add_game(self, won: bool, guesses: int, time_taken: float = 0):
        """
        Add a game result.

        Args:
            won: Whether game was won
            guesses: Number of guesses used
            time_taken: Time taken to solve (seconds)
        """
        self.games_played += 1
        if won:
            self.games_won += 1
        self.guess_counts.append(guesses)
        if time_taken > 0:
            self.solve_times.append(time_taken)

    def get_win_rate(self) -> float:
        """Get win rate percentage."""
        if self.games_played == 0:
            return 0.0
        return (self.games_won / self.games_played) * 100

    def get_average_guesses(self) -> float:
        """Get average number of guesses."""
        if not self.guess_counts:
            return 0.0
        return statistics.mean(self.guess_counts)

    def get_average_time(self) -> float:
        """Get average solve time."""
        if not self.solve_times:
            return 0.0
        return statistics.mean(self.solve_times)

    def get_guess_distribution(self) -> Dict[int, int]:
        """Get distribution of guess counts."""
        distribution = {}
        for count in self.guess_counts:
            distribution[count] = distribution.get(count, 0) + 1
        return distribution

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        return {
            "games_played": self.games_played,
            "games_won": self.games_won,
            "win_rate": self.get_win_rate(),
            "average_guesses": self.get_average_guesses(),
            "average_time": self.get_average_time(),
            "guess_distribution": self.get_guess_distribution(),
        }

    def reset(self):
        """Reset all metrics."""
        self.games_played = 0
        self.games_won = 0
        self.guess_counts = []
        self.solve_times = []
