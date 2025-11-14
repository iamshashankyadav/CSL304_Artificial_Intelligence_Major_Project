"""
Knowledge-based solver using rule-based reasoning.
"""

from typing import List, Dict, Set
from ..base_solver import BaseSolver
from ...core.feedback import Feedback, LetterStatus
from ...core.word_list import WordList
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class KnowledgeBasedSolver(BaseSolver):
    """Wordle solver using knowledge-based rules and inference."""

    def __init__(self, word_list: WordList, config: dict = None):
        super().__init__(word_list, config)
        self.confirmed_letters: Dict[int, str] = {}  # position -> letter
        self.present_letters: Set[str] = set()  # letters in word but position unknown
        self.absent_letters: Set[str] = set()  # letters not in word
        self.excluded_positions: Dict[str, Set[int]] = (
            {}
        )  # letter -> positions to avoid

        # Letter frequency analysis
        self.letter_freq = self._analyze_letter_frequency()
        self.position_freq = self._analyze_position_frequency()

    def _analyze_letter_frequency(self) -> Dict[str, float]:
        """Analyze frequency of letters across all words."""
        freq = Counter()
        total = 0

        for word in self.word_list.get_common_words():
            for letter in set(word):
                freq[letter] += 1
                total += 1

        return {letter: count / total for letter, count in freq.items()}

    def _analyze_position_frequency(self) -> List[Dict[str, float]]:
        """Analyze frequency of letters at each position."""
        position_freq = [{} for _ in range(5)]

        for word in self.word_list.get_common_words():
            for i, letter in enumerate(word):
                position_freq[i][letter] = position_freq[i].get(letter, 0) + 1

        # Normalize
        for i in range(5):
            total = sum(position_freq[i].values())
            position_freq[i] = {k: v / total for k, v in position_freq[i].items()}

        return position_freq

    def get_next_guess(self) -> str:
        """Get next guess using knowledge-based rules."""
        if not self.guess_history:
            return self._get_first_guess()

        # Apply rules to filter candidates
        candidates = self._apply_rules()

        if not candidates:
            logger.warning("No candidates found, using fallback")
            return self._get_fallback_guess()

        if len(candidates) == 1:
            return list(candidates)[0]

        # Score and select best candidate
        return self
