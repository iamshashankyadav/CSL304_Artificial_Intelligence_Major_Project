"""
Statistics panel component.
"""

import streamlit as st
from typing import Dict
import plotly.graph_objects as go


def render_statistics(metrics: Dict):
    """
    Render statistics panel.

    Args:
        metrics: Dictionary of metrics
    """
    st.sidebar.header("📊 Statistics")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        st.metric("Games Played", metrics.get("games_played", 0))
        st.metric("Win Rate", f"{metrics.get('win_rate', 0):.1f}%")

    with col2:
        st.metric("Games Won", metrics.get("games_won", 0))
        st.metric("Avg Guesses", f"{metrics.get('average_guesses', 0):.1f}")

    # Guess distribution
    distribution = metrics.get("guess_distribution", {})
    if distribution:
        st.sidebar.subheader("Guess Distribution")

        fig = go.Figure(
            data=[
                go.Bar(
                    x=list(distribution.keys()),
                    y=list(distribution.values()),
                    marker_color="#6aaa64",
                )
            ]
        )

        fig.update_layout(
            xaxis_title="Number of Guesses",
            yaxis_title="Count",
            height=200,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
        )

        st.sidebar.plotly_chart(fig, use_container_width=True)


def render_solver_info(solver_stats: Dict):
    """
    Render solver-specific information.

    Args:
        solver_stats: Solver statistics
    """
    if not solver_stats:
        return

    with st.expander("🔍 Solver Details"):
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Algorithm:** {solver_stats.get('algorithm', 'N/A')}")
            st.write(f"**Guesses Made:** {solver_stats.get('guesses_made', 0)}")

        with col2:
            st.write(f"**Remaining Words:** {solver_stats.get('remaining_words', 0)}")
