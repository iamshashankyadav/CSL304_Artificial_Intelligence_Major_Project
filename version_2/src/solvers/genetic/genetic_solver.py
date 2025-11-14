"""
Genetic Algorithm solver for Wordle.
"""

from typing import List, Set, Tuple, Dict
from solvers.base_solver import BaseSolver
from core.feedback import Feedback, LetterStatus
from core.word_list import WordList
import random
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class GeneticSolver(BaseSolver):
    """Wordle solver using Genetic Algorithm."""

    def __init__(self, word_list: WordList, config: dict = None):
        super().__init__(word_list, config)
        self.config = config or {}

        self.population_size = self.config.get("population_size", 100)
        self.mutation_rate = self.config.get("mutation_rate", 0.01)
        self.crossover_rate = self.config.get("crossover_rate", 0.7)
        self.elite_size = self.config.get("elite_size", 10)

        self.population = []
        self.generation = 0
        self.letter_frequencies = self._compute_frequencies()

    def _compute_frequencies(self) -> Dict[str, float]:
        """Compute letter frequencies."""
        freq = Counter()
        for word in self.word_list.get_common_words():
            for letter in word:
                freq[letter] += 1

        total = sum(freq.values())
        return {k: v / total for k, v in freq.items()}

    def get_next_guess(self) -> str:
        """Get next guess using genetic algorithm."""
        if not self.guess_history:
            return self._get_first_guess()

        if len(self.possible_words) == 1:
            return list(self.possible_words)[0]

        # Initialize population if needed
        if not self.population or self.generation == 0:
            self.population = self._initialize_population()

        # Evolve population
        self.population = self._evolve_population()
        self.generation += 1

        # Return best individual
        return self._get_best_individual()

    def _get_first_guess(self) -> str:
        """Get optimal first guess."""
        starting_words = ["slate", "crane", "stare", "trace", "raise"]

        for word in starting_words:
            if word in self.possible_words:
                return word

        return list(self.possible_words)[0]

    def _initialize_population(self) -> List[str]:
        """Initialize population with random valid words."""
        candidates = list(self.possible_words)

        if len(candidates) <= self.population_size:
            return candidates

        # Random sample
        return random.sample(candidates, self.population_size)

    def _fitness(self, word: str) -> float:
        """Calculate fitness of a word."""
        score = 0.0

        # Letter frequency score
        for letter in set(word):
            score += self.letter_frequencies.get(letter, 0) * 100

        # Unique letters bonus
        unique = len(set(word))
        score += unique * 20

        # Position diversity (avoid repeated patterns)
        for i, letter in enumerate(word):
            # Positional scoring based on common positions
            score += self._position_score(i, letter)

        # Constraint satisfaction score
        if self.guess_history:
            score += self._constraint_score(word) * 50

        return score

    def _position_score(self, position: int, letter: str) -> float:
        """Score based on letter position frequency."""
        # Simple heuristic based on English word patterns
        common_positions = {
            0: {"s": 1.0, "c": 0.8, "t": 0.7, "b": 0.6},
            1: {"a": 1.0, "o": 0.9, "e": 0.8, "i": 0.7},
            2: {"a": 0.9, "i": 0.8, "o": 0.7, "r": 0.6},
            3: {"e": 1.0, "n": 0.8, "a": 0.7, "s": 0.6},
            4: {"e": 1.0, "s": 0.9, "t": 0.8, "d": 0.7},
        }

        return common_positions.get(position, {}).get(letter, 0.1)

    def _constraint_score(self, word: str) -> float:
        """Score based on constraint satisfaction."""
        if not self.feedback_history:
            return 1.0

        # Check if word is consistent with all feedback
        from ...core.feedback import Feedback as FeedbackClass

        for guess, feedback in zip(self.guess_history, self.feedback_history):
            test_feedback = FeedbackClass(guess, word)
            if test_feedback.feedback != feedback.feedback:
                return 0.0  # Invalid candidate

        return 1.0

    def _evolve_population(self) -> List[str]:
        """Evolve population for one generation."""
        # Calculate fitness for all individuals
        fitness_scores = [(word, self._fitness(word)) for word in self.population]
        fitness_scores.sort(key=lambda x: x[1], reverse=True)

        # Elitism: keep best individuals
        new_population = [word for word, _ in fitness_scores[: self.elite_size]]

        # Fill rest with offspring
        while len(new_population) < self.population_size:
            # Selection
            parent1 = self._tournament_selection(fitness_scores)
            parent2 = self._tournament_selection(fitness_scores)

            # Crossover
            if random.random() < self.crossover_rate:
                child = self._crossover(parent1, parent2)
            else:
                child = parent1

            # Mutation
            child = self._mutate(child)

            # Add if valid
            if child in self.possible_words:
                new_population.append(child)

        return new_population[: self.population_size]

    def _tournament_selection(self, fitness_scores: List[Tuple[str, float]]) -> str:
        """Select individual using tournament selection."""
        tournament_size = 5
        tournament = random.sample(
            fitness_scores, min(tournament_size, len(fitness_scores))
        )
        return max(tournament, key=lambda x: x[1])[0]

    def _crossover(self, parent1: str, parent2: str) -> str:
        """Perform crossover between two parents."""
        # Single-point crossover
        point = random.randint(1, 4)
        child = parent1[:point] + parent2[point:]
        return child

    def _mutate(self, word: str) -> str:
        """Mutate a word."""
        if random.random() > self.mutation_rate:
            return word

        # Random mutation: change one letter
        word_list = list(word)
        pos = random.randint(0, 4)
        word_list[pos] = random.choice("abcdefghijklmnopqrstuvwxyz")

        return "".join(word_list)

    def _get_best_individual(self) -> str:
        """Get best individual from current population."""
        fitness_scores = [(word, self._fitness(word)) for word in self.population]
        best_word = max(fitness_scores, key=lambda x: x[1])[0]
        return best_word

    def update_state(self, guess: str, feedback: Feedback) -> None:
        """Update solver state based on feedback."""
        self.guess_history.append(guess)
        self.feedback_history.append(feedback)

        # Filter possible words
        self._filter_words_by_feedback(guess, feedback)

        # Reset population for next evolution
        self.population = []
        self.generation = 0

        logger.info(f"Genetic: {len(self.possible_words)} words remaining")

    def reset(self) -> None:
        """Reset solver state."""
        super().reset()
        self.population = []
        self.generation = 0
