from setuptools import setup
from setuptools.command.install import install
import os


class InitStructureCommand(install):
    """Custom command: python setup.py init_structure"""

    description = "Create the full Wordle Solver project folder structure."

    def run(self):
        # List of directories to create
        dirs = [
            "wordle-solver/assets",
            "docs",
            "docs",
            "docs",
            "experiments/configs",
            "experiments/runs",
            "experiments/notebooks",
            "notebooks",
            "src/wordle_solver/core",
            "src/wordle_solver/solvers",
            "src/wordle_solver/trainers",
            "src/wordle_solver/models",
            "src/wordle_solver/utils",
            "src/cli",
            "tests/unit",
            "tests/integration",
            "data/wordlists",
            "data/preprocessed",
            "models",
            "docker",
        ]

        files = {
            "wordle-solver/home.py": "",
            "wordle-solver/solver_playground.py": "",
            "wordle-solver/compare_methods.py": "",
            "wordle-solver/training_dashboard.py": "",
            "docs/architecture.md": "# System Architecture\n",
            "docs/methods.md": "# Solver Methods\n",
            "docs/api.md": "# Public API Docs\n",
            "src/wordle_solver/__init__.py": "",
            "src/wordle_solver/api.py": "# Public API\n",
            "src/wordle_solver/core/board.py": "# Wordle board logic\n",
            "src/wordle_solver/core/wordlist.py": "# Wordlist utilities\n",
            "src/wordle_solver/core/evaluator.py": "# Evaluation tools\n",
            "src/wordle_solver/solvers/base.py": "# Base solver interface\n",
            "src/wordle_solver/solvers/csp_solver.py": "",
            "src/wordle_solver/solvers/uninformed_solver.py": "",
            "src/wordle_solver/solvers/informed_solver.py": "",
            "src/wordle_solver/solvers/logic_solver.py": "",
            "src/wordle_solver/solvers/bayes_solver.py": "",
            "src/wordle_solver/solvers/supervised_solver.py": "",
            "src/wordle_solver/solvers/rl_solver.py": "",
            "src/wordle_solver/solvers/neural_solver.py": "",
            "src/wordle_solver/solvers/ga_solver.py": "",
            "src/wordle_solver/solvers/info_theory_solver.py": "",
            "requirements.txt": "",
            "pyproject.toml": "",
            "Makefile": "",
            "tox.ini": "",
            ".pre-commit-config.yaml": "",
            "README.md": "# Wordle Solver Project\n",
            "CONTRIBUTING.md": "# Contribution Guidelines\n",
            "data/wordlists/allowed_words.txt": "",
            "data/wordlists/solutions.txt": "",
            "docker/Dockerfile": "",
            "docker/docker-compose.yml": "",
        }

        # Create directories
        for d in dirs:
            os.makedirs(d, exist_ok=True)
            print(f"Created directory: {d}")

        # Create files
        for filepath, content in files.items():
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created file: {filepath}")

        print("\n🎉 Project structure created successfully!")


setup(
    name="wordle-solver",
    version="0.1.0",
    description="Wordle solver project scaffolding",
    packages=[],
    cmdclass={"init_structure": InitStructureCommand},
)
