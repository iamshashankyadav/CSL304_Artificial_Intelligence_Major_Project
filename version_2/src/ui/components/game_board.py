"""
Wordle game board component.
"""

import streamlit as st
from typing import List, Tuple
from core.feedback import Feedback, LetterStatus


def render_game_board(
    guesses: List[str], feedbacks: List[Feedback], max_attempts: int = 6
):
    """
    Render the Wordle game board.

    Args:
        guesses: List of guesses made
        feedbacks: List of feedback for each guess
        max_attempts: Maximum number of attempts
    """
    # CSS for the board
    st.markdown(
        """
    <style>
    .wordle-grid {
        display: grid;
        grid-gap: 5px;
        padding: 10px;
        justify-content: center;
    }
    .wordle-row {
        display: flex;
        gap: 5px;
        margin-bottom: 5px;
    }
    .letter-box {
        width: 62px;
        height: 62px;
        border: 2px solid #d3d6da;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 32px;
        font-weight: bold;
        text-transform: uppercase;
        border-radius: 4px;
    }
    .letter-correct {
        background-color: #6aaa64;
        border-color: #6aaa64;
        color: white;
    }
    .letter-present {
        background-color: #c9b458;
        border-color: #c9b458;
        color: white;
    }
    .letter-absent {
        background-color: #787c7e;
        border-color: #787c7e;
        color: white;
    }
    .letter-empty {
        background-color: white;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Render grid
    html = '<div class="wordle-grid">'

    for i in range(max_attempts):
        html += '<div class="wordle-row">'

        if i < len(guesses):
            # Render filled row
            guess = guesses[i]
            feedback = feedbacks[i]
            colors = feedback.to_color_codes()

            for letter, color in zip(guess, colors):
                css_class = f"letter-{color}"
                html += f'<div class="letter-box {css_class}">{letter.upper()}</div>'
        else:
            # Render empty row
            for _ in range(5):
                html += '<div class="letter-box letter-empty"></div>'

        html += "</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def render_keyboard(guesses: List[str], feedbacks: List[Feedback]):
    """
    Render virtual keyboard showing letter status.

    Args:
        guesses: List of guesses made
        feedbacks: List of feedback for each guess
    """

    # Track letter status
    letter_status = {}

    for guess, feedback in zip(guesses, feedbacks):
        for letter, status in zip(guess, feedback.feedback):
            # Keep best status for each letter
            current = letter_status.get(letter, LetterStatus.ABSENT)
            if status.value > current.value:
                letter_status[letter] = status

    # Keyboard layout
    rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]

    st.markdown(
        """
    <style>
    .keyboard {
        margin: 20px 0;
    }
    .keyboard-row {
        display: flex;
        justify-content: center;
        gap: 6px;
        margin-bottom: 8px;
    }
    .key {
        min-width: 43px;
        height: 58px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: bold;
        cursor: pointer;
        user-select: none;
    }
    .key-default {
        background-color: #d3d6da;
        color: black;
    }
    .key-correct {
        background-color: #6aaa64;
        color: white;
    }
    .key-present {
        background-color: #c9b458;
        color: white;
    }
    .key-absent {
        background-color: #787c7e;
        color: white;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    html = '<div class="keyboard">'

    for row in rows:
        html += '<div class="keyboard-row">'
        for letter in row:
            status = letter_status.get(letter.lower())
            if status == LetterStatus.CORRECT:
                css_class = "key-correct"
            elif status == LetterStatus.PRESENT:
                css_class = "key-present"
            elif status == LetterStatus.ABSENT:
                css_class = "key-absent"
            else:
                css_class = "key-default"

            html += f'<div class="key {css_class}">{letter}</div>'
        html += "</div>"

    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)
