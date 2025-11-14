"""
Solver selection component.
"""

import streamlit as st
from ...solvers.solver_factory import SolverFactory


def render_solver_selector() -> str:
    """
    Render solver selection UI.

    Returns:
        Selected solver type
    """
    st.sidebar.header("🤖 AI Solver Selection")

    solver_info = SolverFactory.get_solver_info()

    # Create options with descriptions
    solver_options = {
        "CSP": "csp",
        "Knowledge-Based": "knowledge_based",
        "Bayesian": "bayesian",
        "Reinforcement Learning": "reinforcement_learning",
        "Genetic Algorithm": "genetic",
    }

    selected_display = st.sidebar.selectbox(
        "Choose AI Algorithm",
        options=list(solver_options.keys()),
        help="Select which AI algorithm to use for solving",
    )

    selected_solver = solver_options[selected_display]

    # Show description
    with st.sidebar.expander("ℹ️ Algorithm Description"):
        st.write(solver_info[selected_solver])

    return selected_solver


def render_solver_settings(solver_type: str) -> dict:
    """
    Render solver-specific settings.

    Args:
        solver_type: Type of solver

    Returns:
        Configuration dictionary
    """
    st.sidebar.header("⚙️ Solver Settings")

    config = {}

    if solver_type == "bayesian":
        entropy_threshold = st.sidebar.slider(
            "Entropy Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Threshold for information entropy",
        )
        config["entropy_threshold"] = entropy_threshold

    elif solver_type == "reinforcement_learning":
        epsilon = st.sidebar.slider(
            "Exploration Rate (ε)",
            min_value=0.0,
            max_value=0.5,
            value=0.1,
            step=0.05,
            help="Probability of random exploration",
        )
        config["epsilon"] = epsilon

    elif solver_type == "genetic":
        population_size = st.sidebar.slider(
            "Population Size",
            min_value=20,
            max_value=200,
            value=100,
            step=20,
            help="Size of the genetic population",
        )
        mutation_rate = st.sidebar.slider(
            "Mutation Rate",
            min_value=0.0,
            max_value=0.1,
            value=0.01,
            step=0.01,
            help="Probability of mutation",
        )
        config["population_size"] = population_size
        config["mutation_rate"] = mutation_rate

    return config
