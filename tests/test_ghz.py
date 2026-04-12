"""
tests/test_ghz.py
=================
Tests for GHZ state construction and properties.
"""

from __future__ import annotations

import numpy as np
import pytest


class TestGHZNorm:
    """GHZ state must always be normalised."""

    def test_ghz3_norm(self, ghz3):
        assert abs(ghz3.norm() - 1.0) < 1e-10

    def test_ghz4_norm(self, ghz4):
        assert abs(ghz4.norm() - 1.0) < 1e-10

    def test_ghz5_norm(self, ghz5):
        assert abs(ghz5.norm() - 1.0) < 1e-10

    @pytest.mark.parametrize("n", [3, 4, 5, 6, 7, 8])
    def test_ghz_n_norm(self, n):
        from qss.ghz import build_ghz_qutip
        state = build_ghz_qutip(n)
        assert abs(state.norm() - 1.0) < 1e-10, f"GHZ({n}) norm = {state.norm()}"


class TestGHZEntanglement:
    """GHZ qubit subsystems must be maximally mixed."""

    def test_ghz3_subsystem_entropy(self, ghz3):
        """Reduced density matrix of any qubit should have entropy = 1 bit."""
        from qutip import ket2dm, ptrace, entropy_vn
        dm = ket2dm(ghz3)
        rho_A = ptrace(dm, 0)
        entropy = float(entropy_vn(rho_A, base=2))
        assert abs(entropy - 1.0) < 1e-6, f"Subsystem entropy = {entropy}, expected 1.0"

    def test_ghz3_purity_is_one(self, ghz3):
        """Full GHZ state must be pure."""
        from qutip import ket2dm
        dm = ket2dm(ghz3)
        purity = float((dm * dm).tr().real)
        assert abs(purity - 1.0) < 1e-8

    def test_ghz3_subsystem_purity(self, ghz3):
        """Single-qubit reduced state must be maximally mixed (purity = 0.5)."""
        from qutip import ket2dm, ptrace
        dm = ket2dm(ghz3)
        rho_A = ptrace(dm, 0)
        purity = float((rho_A * rho_A).tr().real)
        assert abs(purity - 0.5) < 1e-8


class TestGHZDimensions:
    """GHZ state dimensions must match N qubits."""

    @pytest.mark.parametrize("n", [3, 4, 5])
    def test_ghz_dims(self, n):
        from qss.ghz import build_ghz_qutip
        state = build_ghz_qutip(n)
        assert state.shape == (2**n, 1)

    def test_ghz_invalid_n(self):
        from qss.ghz import build_ghz_qutip
        with pytest.raises(ValueError, match="n must be >= 2"):
            build_ghz_qutip(1)


class TestGHZApproaches:
    """Both GHZ distribution approaches must return correct structure."""

    @pytest.mark.parametrize("n", [3, 4, 5])
    def test_approach1_structure(self, n):
        from qss.ghz import build_ghz_approach1
        state, qubits, msgs, fidelity = build_ghz_approach1(n)
        assert abs(state.norm() - 1.0) < 1e-10
        assert qubits == n + 2 * (n - 1)
        assert msgs == 2 * (n - 1)
        assert 0.0 < fidelity <= 1.0

    @pytest.mark.parametrize("n", [3, 4, 5])
    def test_approach2_structure(self, n):
        from qss.ghz import build_ghz_approach2
        state, qubits, msgs, fidelity = build_ghz_approach2(n)
        assert abs(state.norm() - 1.0) < 1e-10
        assert qubits == n
        assert msgs == n - 1
        assert 0.0 < fidelity <= 1.0

    def test_approach2_fewer_qubits_than_approach1(self):
        from qss.ghz import build_ghz_approach1, build_ghz_approach2
        for n in [3, 4, 5]:
            _, q1, _, _ = build_ghz_approach1(n)
            _, q2, _, _ = build_ghz_approach2(n)
            assert q2 < q1, f"Approach 2 should use fewer qubits for N={n}"

    def test_compare_approaches_keys(self):
        from qss.ghz import compare_approaches
        result = compare_approaches(3)
        assert "approach1" in result
        assert "approach2" in result
        for key in ["qubit_count", "msg_count", "fidelity_estimate",
                    "teleportation_needed", "lab_demonstrated"]:
            assert key in result["approach1"]
            assert key in result["approach2"]
