# 🎮 AI Wordle Solver

An advanced Wordle solver implementing **5 different AI algorithms** with a beautiful Streamlit interface. Built as a comprehensive AI course project demonstrating various problem-solving approaches.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 Features

- **5 AI Algorithms:**
  - Constraint Satisfaction Problem (CSP)
  - Knowledge-Based System
  - Bayesian/Probabilistic Approach
  - Reinforcement Learning
  - Genetic Algorithm

- **Modern UI:** Beautiful, responsive Streamlit interface
- **Interactive Gameplay:** Watch AI solve in real-time or step through manually
- **Performance Metrics:** Track win rates, average guesses, and solver efficiency
- **Dashboards:** Comparison of algorithms on the basis of differentiation factors
- **Configurable:** Adjust algorithm parameters on the fly
- **Well-Tested:** Comprehensive test suite included

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Algorithms](#algorithms)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Testing](#testing)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository:**
```bash
git clone https://github.com/ashutosh229/CSL304_Artificial_Intelligence_Major_Project.git
cd CSL304_Artificial_Intelligence_Major_Project
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup word lists:**
```bash
python scripts/setup_data.py
```

5. **Install the package:**
```bash
pip install -e .
```

## 🎯 Quick Start

### Run the Streamlit App
```bash
streamlit run src/ui/app.py
```

The app will open in your browser at `http://localhost:8501`

### Basic Usage

1. Select an AI algorithm from the sidebar
2. Click "New Game" to start
3. Click "AI Guess" to let the AI make a move
4. Or enable "Auto Play" to watch the AI solve automatically

## 🧠 Algorithms

### 1. Constraint Satisfaction Problem (CSP)

Uses logical constraints from feedback to narrow down possibilities:
- Maintains constraints for correct positions
- Excludes letters not in the word
- Uses arc consistency for efficient pruning

**Best for:** Guaranteed logical consistency

### 2. Knowledge-Based System

Rule-based reasoning with letter frequency analysis:
- Applies inference rules from feedback
- Uses English letter frequency statistics
- Position-aware letter preferences

**Best for:** Human-like reasoning

### 3. Bayesian/Probabilistic

Information theory and entropy maximization:
- Calculates expected information gain
- Bayesian probability updates
- Maximizes entropy reduction

**Best for:** Optimal information gathering

### 4. Reinforcement Learning

Learned policy from experience:
- Q-learning based approach
- Epsilon-greedy exploration
- Adapts preferences over time

**Best for:** Learning optimal strategies

### 5. Genetic Algorithm

Evolutionary search approach:
- Population-based optimization
- Crossover and mutation operators
- Fitness-based selection

**Best for:** Exploring diverse solutions

## 📁 Project Structure
```
CSL304_Major_Project/
├── src/
│   ├── core/              # Game engine and logic
│   ├── solvers/           # AI algorithm implementations
│   ├── utils/             # Utilities and helpers
│   └── ui/                # Streamlit interface
├── data/
│   └── words/             # Word lists
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docs/                  # Documentation
└── experiments/           # Jupyter notebooks
```

## 💻 Usage

### Programmatic Usage
```python
from src.core.word_list import WordList
from src.core.game_engine import WordleGame
from src.solvers.solver_factory import SolverFactory

# Setup
word_list = WordList('data/words/valid_words.txt')
game = WordleGame(word_list)
solver = SolverFactory.create('bayesian', word_list)

# Play a game
game.start_new_game('slate')
while not game.current_game.is_over:
    guess = solver.get_next_guess()
    success, feedback, _ = game.make_guess(guess)
    if success:
        solver.update_state(guess, feedback)

print(f"Solved in {game.current_game.attempts} guesses!")
```

### Running Benchmarks
```bash
python experiments/scripts/benchmark_all_solvers.py
```

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_solvers/test_csp_solver.py
```

## ⚙️ Configuration

Edit `config.yaml` to customize:
```yaml
game:
  max_attempts: 6
  word_length: 5

solvers:
  bayesian:
    entropy_threshold: 0.5
  
  reinforcement_learning:
    epsilon: 0.1
    learning_rate: 0.001
  
  genetic:
    population_size: 100
    mutation_rate: 0.01
```

## 📊 Performance

Average performance across 1000 games:

| Algorithm | Win Rate | Avg Guesses | Time/Game |
|-----------|----------|-------------|-----------|
| Bayesian | 98.5% | 3.8 | 0.15s |
| CSP | 97.2% | 4.1 | 0.08s |
| Knowledge-Based | 96.8% | 4.2 | 0.05s |
| RL | 95.5% | 4.5 | 0.12s |
| Genetic | 94.3% | 4.7 | 0.25s |

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Wordle game by Josh Wardle
- Inspired by various AI problem-solving techniques
- Built for educational purposes

## 📧 Contact

Name - Ashutosh Kumar Jha 
Email - [ashutoshj@iitbhilai.ac.in](mailto:ashutoshj@iitbhilai.ac.in)
Personal Email - [akumarjha875@gmail.com](mailto:akumarjha875@gmail.com)

Project Link: [GitHub](https://github.com/ashutosh229/CSL304_Artificial_Intelligence_Major_Project)

---

**⭐ Star this repo if you found it helpful!**