"""
Configuration loader utility.
"""

import yaml
import os
from typing import Dict, Any


class ConfigLoader:
    """Load and manage configuration."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize config loader.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            return self._get_default_config()

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "game": {
                "max_attempts": 6,
                "word_length": 5,
                "word_list": "data/words/valid_words.txt",
                "answer_list": "data/words/common_words.txt",
            },
            "solvers": {
                "csp": {"use_arc_consistency": True},
                "bayesian": {"entropy_threshold": 0.5},
                "rl": {"epsilon": 0.1},
                "genetic": {"population_size": 100},
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_solver_config(self, solver_name: str) -> Dict[str, Any]:
        """Get configuration for specific solver."""
        return self.get(f"solvers.{solver_name}", {})
