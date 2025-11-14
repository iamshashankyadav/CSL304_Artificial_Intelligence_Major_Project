# Architecture Documentation

## System Overview

The Wordle AI Solver is designed with a modular, extensible architecture that separates concerns and allows for easy addition of new solving algorithms.

## Core Components

### 1. Game Engine (`src/core/`)

The game engine provides the foundational logic for Wordle gameplay:

- **WordList**: Manages valid and common word dictionaries
- **GameEngine**: Controls game flow and state
- **Feedback**: Generates and processes guess feedback
- **Validator**: Validates guesses against game rules

### 2. Solvers (`src/solvers/`)

All solvers implement the `BaseSolver` abstract class, ensuring a consistent interface:
```python
class BaseSolver(ABC):
    def get_next_guess(self) -> str
    def update_state(self, guess: str, feedback: Feedback) -> None
    def reset(self) -> None
```

Each algorithm is implemented in its own module with algorithm-specific logic encapsulated.

### 3. User Interface (`src/ui/`)

The Streamlit-based UI is componentized:

- **app.py**: Main application entry point
- **components/**: Reusable UI components
  - game_board.py: Wordle grid display
  - solver_selector.py: Algorithm selection
  - stats_panel.py: Performance metrics

### 4. Utilities (`src/utils/`)

Common functionality shared across the application:

- **logger.py**: Centralized logging
- **config_loader.py**: Configuration management
- **metrics.py**: Performance tracking

## Data Flow
```
User Input → Solver Selection → Game Initialization
                ↓
           Get Next Guess (AI)
                ↓
           Make Guess → Generate Feedback
                ↓
           Update Solver State
                ↓
        Repeat until game over
                ↓
           Update Metrics → Display Results
```

## Design Patterns

### 1. Factory Pattern
`SolverFactory` creates solver instances dynamically based on type.

### 2. Strategy Pattern
Different algorithms implement the same interface, allowing runtime selection.

### 3. Observer Pattern
UI components observe game state changes and update accordingly.

## Extensibility

### Adding a New Solver

1. Create a new module in `src/solvers/your_algorithm/`
2. Implement `BaseSolver` interface
3. Register in `SolverFactory`
4. Add configuration in `config.yaml`
5. Add tests in `tests/test_solvers/`

Example:
```python
class NewSolver(BaseSolver):
    def __init__(self, word_list, config):
        super().__init__(word_list, config)
        # Your initialization
    
    def get_next_guess(self) -> str:
        # Your algorithm logic
        pass
    
    def update_state(self, guess, feedback):
        # Update internal state
        pass
```

## Performance Considerations

- **Caching**: Commonly accessed data is cached
- **Lazy Loading**: Word lists loaded on demand
- **Efficient Filtering**: Set operations for word filtering
- **Parallel Processing**: Optional parallel evaluation

## Security

- Input validation on all user inputs
- No external network calls required
- Local data storage only
- No sensitive data handling
```

---

## Step 15: Final Setup Instructions

### 4.21 Create `LICENSE`
```
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.