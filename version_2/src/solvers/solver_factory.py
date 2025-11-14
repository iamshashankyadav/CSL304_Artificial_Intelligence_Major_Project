"""
Factory for creating solver instances.
"""

from typing import Dict, Type
from .base_solver import BaseSolver
from .csp.csp_solver import CSPSolver
from .knowledge_based.kb_solver import KnowledgeBasedSolver
from .bayesian.bayesian_solver import BayesianSolver
from .reinforcement_learning.rl_solver import RLSolver
from .genetic.genetic_solver import GeneticSolver
from ..core.word_list import WordList


class SolverFactory:
    """Factory for creating solver instances."""

    _solvers: Dict[str, Type[BaseSolver]] = {
        "csp": CSPSolver,
        "knowledge_based": KnowledgeBasedSolver,
        "bayesian": BayesianSolver,
        "reinforcement_learning": RLSolver,
        "genetic": GeneticSolver,
    }

    @classmethod
    def create(
        cls, solver_type: str, word_list: WordList, config: dict = None
    ) -> BaseSolver:
        """
        Create a solver instance.

        Args:
            solver_type: Type of solver to create
            word_list: WordList instance
            config: Configuration dictionary

        Returns:
            Solver instance

        Raises:
            ValueError: If solver type is invalid
        """
        if solver_type not in cls._solvers:
            raise ValueError(
                f"Unknown solver type: {solver_type}. "
                f"Available: {list(cls._solvers.keys())}"
            )

        solver_class = cls._solvers[solver_type]
        return solver_class(word_list, config)

    @classmethod
    def get_available_solvers(cls) -> list:
        """Get list of available solver types."""
        return list(cls._solvers.keys())

    @classmethod
    def get_solver_info(cls) -> Dict[str, str]:
        """Get information about each solver."""
        return {
            "csp": "Constraint Satisfaction Problem - Uses logical constraints and backtracking",
            "knowledge_based": "Knowledge-Based System - Rule-based reasoning with letter frequency",
            "bayesian": "Bayesian/Probabilistic - Information gain and entropy maximization",
            "reinforcement_learning": "Reinforcement Learning - Learned policy from experience",
            "genetic": "Genetic Algorithm - Evolutionary search with population-based optimization",
        }
