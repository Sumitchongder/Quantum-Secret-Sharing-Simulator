"""
tests/test_eavesdropper.py
==========================
Tests for eavesdropper attack simulation and QBER calculations.
"""

from __future__ import annotations

import numpy as np
import pytest


class TestInjectEveAttack:
    """inject_eve_attack must return physically correct results."""

    def test_zero_intercept_zero_qber(self):
        from qss.eavesdropper import inject_eve_attack
        result = inject_eve_attack(0.0, n_rounds=1000, seed=42)
        assert result["qber"] == 0.0
        assert result["n_errors"] == 0
        assert not result["detected"]

    def test_full_intercept_qber_near_half(self):
        from qss.eavesdropper import inject_eve_attack
        result = inject_eve_attack(1.0, n_rounds=10000, seed=42)
        # QBER ≈ 0.5 with large n_rounds
        assert abs(result["qber"] - 0.5) < 0.03

    def test_qber_increases_with_intercept_prob(self):
        from qss.eavesdropper import inject_eve_attack
        qbers = [
            inject_eve_attack(p, n_rounds=5000, seed=0)["qber"]
            for p in [0.0, 0.2, 0.5, 1.0]
        ]
        assert qbers[0] <= qbers[1] <= qbers[2] <= qbers[3]

    def test_detection_threshold_at_five_percent(self):
        from qss.eavesdropper import inject_eve_attack
        # p=0.0 → QBER=0 → not detected
        r1 = inject_eve_attack(0.0, n_rounds=1000, seed=0)
        assert not r1["detected"]
        # p=1.0 → QBER≈0.5 → detected
        r2 = inject_eve_attack(1.0, n_rounds=1000, seed=0)
        assert r2["detected"]

    def test_result_has_required_keys(self):
        from qss.eavesdropper import inject_eve_attack
        result = inject_eve_attack(0.3, n_rounds=100, seed=0)
        required = ["qber", "n_errors", "n_rounds", "n_intercepts",
                    "intercept_prob", "detected", "security_msg"]
        for key in required:
            assert key in result

    def test_n_errors_leq_n_rounds(self):
        from qss.eavesdropper import inject_eve_attack
        result = inject_eve_attack(0.5, n_rounds=500, seed=7)
        assert result["n_errors"] <= result["n_rounds"]

    def test_n_intercepts_leq_n_rounds(self):
        from qss.eavesdropper import inject_eve_attack
        result = inject_eve_attack(0.5, n_rounds=500, seed=7)
        assert result["n_intercepts"] <= result["n_rounds"]

    def test_reproducibility_with_same_seed(self):
        from qss.eavesdropper import inject_eve_attack
        r1 = inject_eve_attack(0.4, n_rounds=1000, seed=99)
        r2 = inject_eve_attack(0.4, n_rounds=1000, seed=99)
        assert r1["qber"] == r2["qber"]


class TestQBERCurve:
    """qber_vs_intercept_curve must be physically correct."""

    def test_shape(self):
        from qss.eavesdropper import qber_vs_intercept_curve
        curve = qber_vs_intercept_curve(100)
        assert curve.shape == (100, 2)

    def test_starts_at_zero(self):
        from qss.eavesdropper import qber_vs_intercept_curve
        curve = qber_vs_intercept_curve(100)
        assert curve[0, 0] == pytest.approx(0.0)
        assert curve[0, 1] == pytest.approx(0.0)

    def test_ends_at_half(self):
        from qss.eavesdropper import qber_vs_intercept_curve
        curve = qber_vs_intercept_curve(100)
        assert curve[-1, 0] == pytest.approx(1.0)
        assert curve[-1, 1] == pytest.approx(0.5)

    def test_monotonically_increasing(self):
        from qss.eavesdropper import qber_vs_intercept_curve
        curve = qber_vs_intercept_curve(50)
        diffs = np.diff(curve[:, 1])
        assert np.all(diffs >= 0)

    def test_qber_equals_half_intercept(self):
        from qss.eavesdropper import qber_vs_intercept_curve
        curve = qber_vs_intercept_curve(200)
        np.testing.assert_allclose(curve[:, 1], curve[:, 0] / 2, rtol=1e-10)


class TestDetectionProbability:
    """detection_probability must grow correctly with rounds."""

    def test_zero_intercept_zero_detection(self):
        from qss.eavesdropper import detection_probability
        assert detection_probability(0.0, 100) == pytest.approx(0.0)

    def test_full_intercept_near_one(self):
        from qss.eavesdropper import detection_probability
        p = detection_probability(1.0, 1000)
        assert p > 0.9999

    def test_increases_with_rounds(self):
        from qss.eavesdropper import detection_probability
        probs = [detection_probability(0.3, r) for r in [10, 50, 100, 500]]
        assert probs[0] <= probs[1] <= probs[2] <= probs[3]

    def test_increases_with_intercept_prob(self):
        from qss.eavesdropper import detection_probability
        probs = [detection_probability(p, 100) for p in [0.0, 0.2, 0.5, 1.0]]
        assert probs[0] <= probs[1] <= probs[2] <= probs[3]
