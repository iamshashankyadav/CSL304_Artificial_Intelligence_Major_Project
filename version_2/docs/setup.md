# 1. Create project directory
mkdir wordle-ai-solver
cd wordle-ai-solver

# 2. Initialize git
git init

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 4. Create all directories (run the first command from Step 1.1)

# 5. Create all __init__.py files (run the second command from Step 1.1)

# 6. Create all configuration files
# - Copy .gitignore content
# - Copy requirements.txt content
# - Copy setup.py content
# - Copy config.yaml content
# - Copy pytest.ini content

# 7. Install dependencies
pip install -r requirements.txt

# 8. Create all source code files
# - Copy all files froleam sections 2-11

# 9. Setup data
mkdir -p data/words data/models data/benchmarks logs
python scripts/setup_data.py

# 10. Install package
pip install -e .

# 11. Run tests
pytest

# 12. Start the app
streamlit run src/ui/app.py