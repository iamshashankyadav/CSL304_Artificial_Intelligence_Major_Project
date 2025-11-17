"""
Dashboard component to compare two solvers across a set of words.

Shows per-attempt candidate words with probabilities and tracks score progression.
"""
from typing import List, Dict, Any
import streamlit as st
from solvers.solver_factory import SolverFactory
from core.game_engine import WordleGame
import plotly.graph_objects as go


def _simulate_solver_on_word_detailed(solver_type: str, word: str, word_list, max_attempts: int = 6) -> Dict[str, Any]:
    """Simulate a solver with detailed per-attempt tracking.

    Returns a dict with:
    - attempts (int)
    - won (bool)
    - guesses (list of guess strings)
    - attempts_detail (list of dicts with per-attempt candidates and scores)
    """
    solver = SolverFactory.create(solver_type, word_list, config={})
    solver.reset()

    game = WordleGame(word_list, max_attempts=max_attempts)
    game_state = game.start_new_game(word)

    attempts_detail = []
    won = False

    # Loop until game over
    while not game_state.is_over:
        try:
            guess = solver.get_next_guess()
        except Exception:
            guess = None

        if not guess or not isinstance(guess, str):
            commons = list(word_list.get_common_words() or [])
            guess = commons[0] if commons else list(word_list.get_valid_words() or ["raise"])[0]

        guess = guess.lower()[:5]

        success, feedback, error = game.make_guess(guess)
        if error:
            break

        try:
            solver.update_state(guess, feedback)
        except Exception:
            pass

        # Capture current candidates and scores AFTER update
        stats = solver.get_statistics()
        candidates = stats.get("candidates", [])
        
        # Extract top 3 candidates with scores
        top_candidates = []
        for cand in candidates[:3]:
            if isinstance(cand, dict):
                word_val = cand.get("word", "")
                score_val = cand.get("score", 0)
                top_candidates.append({"word": word_val, "score": score_val})

        attempts_detail.append({
            "attempt": game_state.attempts,
            "candidates": top_candidates,
            "remaining_words": len(solver.possible_words),
        })

        if game_state.is_won:
            won = True
            break

        if game_state.attempts >= max_attempts:
            break

    return {
        "attempts": game_state.attempts,
        "won": won,
        "guesses": list(game_state.guesses),
        "attempts_detail": attempts_detail,
    }


def _run_comparison_detailed(solver_a: str, solver_b: str, words: List[str], word_list) -> Dict[str, Any]:
    """Run both solvers with detailed per-attempt tracking."""
    results = {solver_a: [], solver_b: []}

    for w in words:
        a_res = _simulate_solver_on_word_detailed(solver_a, w, word_list)
        b_res = _simulate_solver_on_word_detailed(solver_b, w, word_list)
        results[solver_a].append({"word": w, **a_res})
        results[solver_b].append({"word": w, **b_res})

    return results


def render_dashboard(
    solver_a: str,
    solver_b: str,
    word_list,
    sample_size: int = 5,
    allow_controls: bool = True,
):
    """Render a detailed comparison dashboard.

    Shows per-attempt top 3 candidate words with scores for each algorithm.
    Displays line charts tracking score progression and word-by-word details.
    """
    st.header("📊 Detailed Algorithm Comparison")

    available = SolverFactory.get_available_solvers()
    options = ["None"] + available

    chosen_a = solver_a
    chosen_b = solver_b if solver_b else "None"
    custom_words_input = ""

    if allow_controls:
        with st.expander("Dashboard Controls", expanded=False):
            cols = st.columns([1, 1, 2])
            with cols[0]:
                chosen_a = st.selectbox("Algorithm 1", options=available, index=max(0, available.index(solver_a)) if solver_a in available else 0)
            with cols[1]:
                b_index = 0
                if solver_b and solver_b in options:
                    b_index = options.index(solver_b)
                chosen_b = st.selectbox("Algorithm 2 (or None)", options=options, index=b_index)
            with cols[2]:
                custom_words_input = st.text_area(
                    "Custom target words (comma-separated, leave empty for random)",
                    value="",
                    height=80,
                )

    # Prepare sample words
    common_words = list(word_list.get_common_words() or [])
    sample_words = []
    
    if custom_words_input and isinstance(custom_words_input, str):
        parsed = [w.strip().lower() for w in custom_words_input.split(",") if w.strip()]
        sample_words = [w for w in parsed if len(w) == 5]
        if not sample_words:
            st.warning("No valid 5-letter words. Please enter valid 5-letter words.")

    with st.expander("Words Used (preview)", expanded=False):
        if sample_words:
            st.write(", ".join(sample_words))
        else:
            st.write("No words specified yet. Enter comma-separated words above to start.")

    if chosen_b == "None":
        chosen_b = None

    # Only run simulations if there are words to analyze
    if not sample_words:
        st.info("👈 Enter target words in the Dashboard Controls above to begin the comparison.")
    else:
        # Run detailed simulations
        with st.spinner("Running detailed comparison (this may take a minute)..."):
            if chosen_b:
                results = _run_comparison_detailed(chosen_a, chosen_b, sample_words, word_list)
            else:
                results = {chosen_a: []}
                for w in sample_words:
                    a_res = _simulate_solver_on_word_detailed(chosen_a, w, word_list)
                    results[chosen_a].append({"word": w, **a_res})

        # Display results word by word with side chart
        st.subheader("Per-Word Analysis")

        # Prepare data for side chart (highest probability words per attempt)
        highest_words_a = {}
        highest_words_b = {} if chosen_b else None

        for word_idx, word in enumerate(sample_words):
            st.markdown(f"### Word {word_idx + 1}: **{word.upper()}**")

            a_data = results[chosen_a][word_idx]
            attempts_a = a_data.get("attempts_detail", [])
            won_a = a_data.get("won", False)

            col_chart, col_text = st.columns([1, 2])

            # Collect highest words for this word across attempts for side chart
            for attempt_info in attempts_a:
                att_num = attempt_info.get("attempt", 0)
                candidates = attempt_info.get("candidates", [])
                if candidates:
                    top_word = candidates[0].get("word", "")
                    top_score = candidates[0].get("score", 0)
                    # Convert to float if string
                    if isinstance(top_score, str):
                        try:
                            top_score = float(top_score)
                        except (ValueError, TypeError):
                            top_score = 0
                    if att_num not in highest_words_a:
                        highest_words_a[att_num] = []
                    highest_words_a[att_num].append((top_word, top_score))

            if chosen_b:
                b_data = results[chosen_b][word_idx]
                attempts_b = b_data.get("attempts_detail", [])
                won_b = b_data.get("won", False)

                for attempt_info in attempts_b:
                    att_num = attempt_info.get("attempt", 0)
                    candidates = attempt_info.get("candidates", [])
                    if candidates:
                        top_word = candidates[0].get("word", "")
                        top_score = candidates[0].get("score", 0)
                        # Convert to float if string
                        if isinstance(top_score, str):
                            try:
                                top_score = float(top_score)
                            except (ValueError, TypeError):
                                top_score = 0
                        if att_num not in highest_words_b:
                            highest_words_b[att_num] = []
                        highest_words_b[att_num].append((top_word, top_score))

            # Text details: per-attempt breakdown
            with col_text:
                col_a, col_b_text = st.columns(2 if chosen_b else [1, 0.001])

                with col_a:
                    st.write(f"**{chosen_a}** — {'✅ Won' if won_a else '❌ Failed'} in {a_data.get('attempts', 0)} attempts")
                    
                    for attempt_info in attempts_a:
                        att_num = attempt_info.get("attempt", 0)
                        candidates = attempt_info.get("candidates", [])
                        st.write(f"  *Attempt {att_num} — Top 3:*")
                        for i, cand in enumerate(candidates, 1):
                            word_c = cand.get("word", "?")
                            score_c = cand.get("score", 0)
                            score_str = f"{score_c:.3f}" if isinstance(score_c, float) else str(score_c)
                            st.write(f"    {i}. **{word_c.upper()}** ({score_str})")

                if chosen_b:
                    with col_b_text:
                        b_data = results[chosen_b][word_idx]
                        attempts_b = b_data.get("attempts_detail", [])
                        won_b = b_data.get("won", False)

                        st.write(f"**{chosen_b}** — {'✅ Won' if won_b else '❌ Failed'} in {b_data.get('attempts', 0)} attempts")
                        
                        for attempt_info in attempts_b:
                            att_num = attempt_info.get("attempt", 0)
                            candidates = attempt_info.get("candidates", [])
                            st.write(f"  *Attempt {att_num} — Top 3:*")
                            for i, cand in enumerate(candidates, 1):
                                word_c = cand.get("word", "?")
                                score_c = cand.get("score", 0)
                                score_str = f"{score_c:.3f}" if isinstance(score_c, float) else str(score_c)
                                st.write(f"    {i}. **{word_c.upper()}** ({score_str})")

            st.divider()

        # Side chart: Highest probability words connecting across attempts
        st.subheader("Highest Probability Word Progression")

        chart_col_a, chart_col_b = st.columns(2 if chosen_b else [1, 0.001])

        # Chart for Algorithm 1 - highest probability words
        with chart_col_a:
            fig_a = go.Figure()
            attempts_sorted = sorted(highest_words_a.keys())
            avg_scores_a = []
            
            for att in attempts_sorted:
                scores = [score for word, score in highest_words_a[att]]
                avg_score = sum(scores) / len(scores) if scores else 0
                avg_scores_a.append(avg_score)
            
            fig_a.add_trace(go.Scatter(
                x=attempts_sorted,
                y=avg_scores_a,
                mode="lines+markers",
                name=f"{chosen_a} Top Word",
                line=dict(color="#6aaa64", width=3),
                marker=dict(size=10),
                text=[f"Attempt {att}" for att in attempts_sorted],
                hovertemplate="<b>%{text}</b><br>Avg Score: %{y:.3f}<extra></extra>"
            ))
            
            fig_a.update_layout(
                title=f"{chosen_a} — Highest Probability per Attempt",
                xaxis_title="Attempt",
                yaxis_title="Score",
                height=350,
                margin=dict(t=50, l=50, r=20, b=50),
            )
            st.plotly_chart(fig_a, use_container_width=True)

        # Chart for Algorithm 2 (if selected)
        if chosen_b:
            with chart_col_b:
                fig_b = go.Figure()
                attempts_sorted_b = sorted(highest_words_b.keys())
                avg_scores_b = []
                
                for att in attempts_sorted_b:
                    scores = [score for word, score in highest_words_b[att]]
                    avg_score = sum(scores) / len(scores) if scores else 0
                    avg_scores_b.append(avg_score)
                
                fig_b.add_trace(go.Scatter(
                    x=attempts_sorted_b,
                    y=avg_scores_b,
                    mode="lines+markers",
                    name=f"{chosen_b} Top Word",
                    line=dict(color="#f4c542", width=3),
                    marker=dict(size=10),
                    text=[f"Attempt {att}" for att in attempts_sorted_b],
                    hovertemplate="<b>%{text}</b><br>Avg Score: %{y:.3f}<extra></extra>"
                ))
                
                fig_b.update_layout(
                    title=f"{chosen_b} — Highest Probability per Attempt",
                    xaxis_title="Attempt",
                    yaxis_title="Score",
                    height=350,
                    margin=dict(t=50, l=50, r=20, b=50),
                )
                st.plotly_chart(fig_b, use_container_width=True)

