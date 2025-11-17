"""
Word selection visualization component.
"""

import streamlit as st
from typing import Dict, List, Any
import pandas as pd


def render_word_selection(solver_stats: Dict):
    """
    Render word selection process and top candidates.

    Args:
        solver_stats: Solver statistics including candidates and selection info
    """
    if not solver_stats:
        return

    candidates = solver_stats.get("candidates", [])
    selection_info = solver_stats.get("selection_info", {})
    
    if not candidates or not selection_info:
        return

    with st.expander("🎯 Word Selection Process", expanded=True):
        # Algorithm info
        col1, col2 = st.columns(2)
        
        with col1:
            method = selection_info.get("method", "Unknown")
            st.write(f"**Algorithm:** {method}")
            st.write(f"**Remaining Words:** {selection_info.get('total_remaining', 'N/A')}")
        
        with col2:
            # Algorithm-specific info
            if "entropy" in selection_info:
                st.write(f"**Entropy:** {selection_info.get('entropy', 'N/A')}")
            
            if "generation" in selection_info:
                st.write(f"**Generation:** {selection_info.get('generation', 'N/A')}")
            
            if "confirmed_letters" in selection_info:
                st.write(f"**Confirmed Letters:** {selection_info.get('confirmed_letters', 0)}")
        
        st.divider()
        
        # Top candidates table
        st.subheader("Top Candidates")
        
        if candidates:
            # Create DataFrame for better visualization
            df_data = []
            for i, candidate in enumerate(candidates, 1):
                df_data.append({
                    "Rank": i,
                    "Word": candidate.get("word", "").upper(),
                    "Score": candidate.get("score", "N/A")
                })
            
            df = pd.DataFrame(df_data)
            
            # Display as table with formatting
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Rank": st.column_config.NumberColumn(
                        "Rank",
                        format="%d",
                        width="small",
                    ),
                    "Word": st.column_config.TextColumn(
                        "Word",
                        width="medium",
                    ),
                    "Score": st.column_config.TextColumn(
                        "Score",
                        width="medium",
                    ),
                }
            )
            
            # Show selected word (first in candidates)
            selected = candidates[0]
            st.success(f"🤖 **Selected:** {selected.get('word', '').upper()}")
        else:
            st.info("No candidates available yet")


def render_selection_progress(
    guess_history: List[str],
    remaining_words: int,
    total_candidates: int,
):
    """
    Render progress bar showing word elimination.

    Args:
        guess_history: List of guesses made
        remaining_words: Number of remaining possible words
        total_candidates: Total number of candidate words
    """
    if total_candidates > 0:
        elimination_rate = (total_candidates - remaining_words) / total_candidates
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.progress(
                min(elimination_rate, 1.0),
                text=f"{elimination_rate*100:.1f}% Words Eliminated"
            )
        
        with col2:
            st.metric("Remaining", remaining_words)
