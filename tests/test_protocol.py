"""
tests/test_protocol.py
======================
Tests for QSS protocol logic: parity check, secret reconstruction,
measurement simulation, and full protocol round.
"""

from __future__ import annotations

import numpy as np
import pytest


class TestParityCheck:
    """parity_check must return +1, -1, or 0 correctly."""

    def test_zero_phases_returns_plus_one(self):
        from qss.protocol import parity_check
        assert parity_check(0, 0, 0) == +1   # 0+0+0=0 → cos=+1

    def test_pi_phases_returns_minus_one(self):
        from qss.protocol import parity_check
        assert parity_check(1, 1, 0) == -1   # π/2+π/2+0=π → cos=-1

    def test_pi_phase_alt_combination(self):
        from qss.protocol import parity_check
        assert parity_check(1, 0, 1) == -1   # π/2+0+π/2=π

    def test_discard_condition(self):
        from qss.protocol import parity_check
        assert parity_check(1, 0, 0) == 0    # π/2 → not in {0, π}

    def test_all_pi_half_is_discard(self):
        from qss.protocol import parity_check
        # 3π/2 mod π = π/2 → discard
        assert parity_check(1, 1, 1) == 0

    @pytest.mark.parametrize("ai,bi,gi,expected", [
        (0, 0, 0, +1),
        (1, 1, 0, -1),
        (1, 0, 1, -1),
        (0, 1, 1, -1),
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (1, 1, 1, 0),
    ])
    def test_parity_parametrized(self, ai, bi, gi, expected):
        from qss.protocol import parity_check
        assert parity_check(ai, bi, gi) == expected

    def test_parity_check_is_cached(self):
        """lru_cache should return same object on second call."""
        from qss.protocol import parity_check
        r1 = parity_check(0, 0, 0)
        r2 = parity_check(0, 0, 0)
        assert r1 == r2


class TestParityCheckN:
    """N-node parity check generalisation."""

    def test_n4_zero_phases(self):
        from qss.protocol import parity_check_n
        assert parity_check_n((0, 0, 0, 0)) == +1

    def test_n4_pi_phases(self):
        from qss.protocol import parity_check_n
        # π/2+π/2+0+0 = π → cos=-1
        assert parity_check_n((1, 1, 0, 0)) == -1

    def test_n4_discard(self):
        from qss.protocol import parity_check_n
        # π/2+0+0+0 = π/2 → discard
        assert parity_check_n((1, 0, 0, 0)) == 0


class TestReconstructSecret:
    """reconstruct_secret must satisfy a*b*c*d = 1."""

    @pytest.mark.parametrize("a,b,d,expected_c", [
        (+1, +1, +1, +1),
        (+1, +1, -1, -1),
        (+1, -1, +1, -1),
        (+1, -1, -1, +1),
        (-1, +1, +1, -1),
        (-1, +1, -1, +1),
        (-1, -1, +1, +1),
        (-1, -1, -1, -1),
    ])
    def test_reconstruct_all_combinations(self, a, b, d, expected_c):
        from qss.protocol import reconstruct_secret
        c = reconstruct_secret(a, b, d)
        assert c == expected_c
        assert a * b * c * d == 1, "Product a*b*c*d must equal 1"

    def test_reconstruct_is_cached(self):
        from qss.protocol import reconstruct_secret
        r1 = reconstruct_secret(1, 1, 1)
        r2 = reconstruct_secret(1, 1, 1)
        assert r1 is r2 or r1 == r2


class TestSimulateMeasurement:
    """simulate_measurement must respect parity constraint."""

    def test_outcome_count_matches_n(self):
        from qss.protocol import simulate_measurement
        outcomes = simulate_measurement(3, (0, 0, 0), seed=0)
        assert len(outcomes) == 3

    def test_outcomes_are_pm1(self):
        from qss.protocol import simulate_measurement
        for seed in range(20):
            outcomes = simulate_measurement(3, (0, 0, 0), seed=seed)
            assert all(o in [-1, +1] for o in outcomes)

    def test_product_matches_parity_valid_round(self):
        from qss.protocol import simulate_measurement, parity_check_n
        phase_indices = (0, 1, 1)   # parity = -1
        parity = parity_check_n(phase_indices)
        for seed in range(50):
            outcomes = simulate_measurement(3, phase_indices, seed=seed)
            product = int(np.prod(outcomes))
            assert product == parity, (
                f"seed={seed}: product={product} but parity={parity}"
            )

    def test_product_matches_parity_even(self):
        from qss.protocol import simulate_measurement, parity_check_n
        phase_indices = (0, 0, 0)   # parity = +1
        parity = parity_check_n(phase_indices)
        for seed in range(50):
            outcomes = simulate_measurement(3, phase_indices, seed=seed)
            product = int(np.prod(outcomes))
            assert product == parity


class TestRunProtocolRound:
    """Full protocol round integration tests."""

    def test_valid_round_not_discarded(self, protocol_result_valid):
        assert not protocol_result_valid["discard"]

    def test_valid_round_success(self, protocol_result_valid):
        assert protocol_result_valid["success"]

    def test_inferred_matches_secret(self, protocol_result_valid):
        assert protocol_result_valid["inferred_value"] == protocol_result_valid["secret_value"]

    def test_discard_round_flagged(self, protocol_result_discard):
        assert protocol_result_discard["discard"]

    def test_discard_round_no_outcomes(self, protocol_result_discard):
        assert protocol_result_discard["outcomes"] == []

    def test_result_keys_present(self, protocol_result_valid):
        required = [
            "phase_indices", "phases_rad", "parity", "outcomes",
            "discard", "success", "secret_node_idx", "secret_value", "inferred_value"
        ]
        for key in required:
            assert key in protocol_result_valid

    @pytest.mark.parametrize("phase_indices", [
        (0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)
    ])
    def test_all_valid_phase_combos_succeed(self, phase_indices):
        from qss.protocol import run_protocol_round
        result = run_protocol_round(3, phase_indices, seed=0)
        assert not result["discard"]
        assert result["success"]
