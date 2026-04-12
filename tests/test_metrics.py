"""
tests/test_metrics.py
=====================
Tests for quantum information metrics.
"""

from __future__ import annotations

import numpy as np
import pytest


class TestQBERFromCounts:
    """qber_from_counts does not need QuTiP — pure Python."""

    def test_all_even_parity_zero_qber(self):
        from qss.metrics import qber_from_counts
        counts = {"000": 500, "110": 250, "101": 150, "011": 100}
        assert qber_from_counts(counts) == pytest.approx(0.0)

    def test_all_odd_parity_full_qber(self):
        from qss.metrics import qber_from_counts
        counts = {"001": 500, "010": 300, "100": 200}
        assert qber_from_counts(counts) == pytest.approx(1.0)

    def test_empty_counts_zero(self):
        from qss.metrics import qber_from_counts
        assert qber_from_counts({}) == pytest.approx(0.0)

    def test_mixed_qber(self):
        from qss.metrics import qber_from_counts
        # 500 even parity, 500 odd parity → QBER = 0.5
        counts = {"000": 500, "001": 500}
        assert qber_from_counts(counts) == pytest.approx(0.5)


class TestGHZConcurrence:

    def test_two_qubit_concurrence_is_one(self):
        from qss.metrics import ghz_concurrence
        assert ghz_concurrence(2) == pytest.approx(1.0)

    def test_concurrence_decreases_with_n(self):
        from qss.metrics import ghz_concurrence
        vals = [ghz_concurrence(n) for n in [2, 3, 4, 5]]
        assert vals[0] >= vals[1] >= vals[2] >= vals[3]

    def test_concurrence_positive(self):
        from qss.metrics import ghz_concurrence
        for n in [2, 3, 4, 5, 6]:
            assert ghz_concurrence(n) > 0


class TestStateMetricsWithQutip:
    """Tests requiring QuTiP — skipped if not available."""

    pytest.importorskip("qutip", reason="qutip not installed")

    def test_fidelity_identical_states(self, ghz3):
        from qss.metrics import state_fidelity
        f = state_fidelity(ghz3, ghz3)
        assert abs(f - 1.0) < 1e-8

    def test_purity_pure_state(self, ghz3):
        from qss.metrics import state_purity
        p = state_purity(ghz3)
        assert abs(p - 1.0) < 1e-8

    def test_entropy_pure_state(self, ghz3):
        from qss.metrics import von_neumann_entropy
        s = von_neumann_entropy(ghz3)
        assert abs(s) < 1e-8

    def test_subsystem_entropy_is_one(self, ghz3):
        from qss.metrics import subsystem_entropy
        s = subsystem_entropy(ghz3, 0)
        assert abs(s - 1.0) < 1e-6
