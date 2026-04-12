"""
tests/test_tittel2000.py
========================
Tests for Tittel-2000 optical experiment replication.
"""

from __future__ import annotations

import numpy as np
import pytest


class TestDetectionProbability:

    def test_all_plus_zero_phases(self):
        """P_{+1,+1,+1}(0,0,0) = (1/8)(1+1) = 1/4."""
        from qss.tittel2000 import detection_probability
        p = detection_probability(1, 1, 1, 0.0, 0.0, 0.0)
        assert abs(p - 0.25) < 1e-12

    def test_mixed_sign_zero_phases(self):
        """P_{+1,-1,+1}(0,0,0) = (1/8)(1-1) = 0."""
        from qss.tittel2000 import detection_probability
        p = detection_probability(1, -1, 1, 0.0, 0.0, 0.0)
        assert abs(p) < 1e-12

    def test_probability_always_nonneg(self):
        from qss.tittel2000 import detection_probability
        for i in [+1, -1]:
            for j in [+1, -1]:
                for k in [+1, -1]:
                    for phase_sum in [0, np.pi/2, np.pi, 3*np.pi/2]:
                        p = detection_probability(i, j, k, phase_sum, 0, 0)
                        assert p >= -1e-12, f"Negative probability: {p}"

    def test_pi_phase_sum_flips_parity(self):
        """At α+β+γ=π, only odd-parity outcomes have nonzero probability."""
        from qss.tittel2000 import detection_probability
        alpha, beta, gamma = np.pi/2, np.pi/2, 0.0
        # Even parity (+1,+1,+1): product=+1, cos(π)=-1 → P=(1/8)(1-1)=0
        p_even = detection_probability(1, 1, 1, alpha, beta, gamma)
        assert abs(p_even) < 1e-12
        # Odd parity (+1,+1,-1): product=-1, cos(π)=-1 → P=(1/8)(1+1)=1/4
        p_odd = detection_probability(1, 1, -1, alpha, beta, gamma)
        assert abs(p_odd - 0.25) < 1e-12


class TestAllOutcomeProbabilities:

    def test_probabilities_sum_to_one(self):
        from qss.tittel2000 import all_outcome_probabilities
        for alpha, beta, gamma in [(0, 0, 0), (np.pi/2, np.pi/2, 0), (1.0, 0.5, 0.3)]:
            probs = all_outcome_probabilities(alpha, beta, gamma)
            total = sum(probs.values())
            assert abs(total - 1.0) < 1e-12, f"Sum={total} for ({alpha},{beta},{gamma})"

    def test_eight_outcomes(self):
        from qss.tittel2000 import all_outcome_probabilities
        probs = all_outcome_probabilities(0, 0, 0)
        assert len(probs) == 8

    def test_label_format(self):
        from qss.tittel2000 import all_outcome_probabilities
        probs = all_outcome_probabilities(0, 0, 0)
        for label in probs:
            assert label.startswith("(")
            assert label.endswith(")")


class TestParityGroups:

    def test_zero_phase_all_even(self):
        """At α+β+γ=0, only even-parity outcomes allowed."""
        from qss.tittel2000 import parity_groups
        groups = parity_groups(0.0, 0.0, 0.0)
        # Even parity should have nonzero probs, odd should be zero
        for label, p in groups["even"].items():
            assert p > 0, f"Even outcome {label} should be nonzero at phase=0"
        for label, p in groups["odd"].items():
            assert abs(p) < 1e-12, f"Odd outcome {label} should be zero at phase=0"

    def test_pi_phase_all_odd(self):
        """At α+β+γ=π, only odd-parity outcomes allowed."""
        from qss.tittel2000 import parity_groups
        groups = parity_groups(np.pi/2, np.pi/2, 0.0)
        for label, p in groups["even"].items():
            assert abs(p) < 1e-12, f"Even outcome {label} should be zero at phase=π"
        for label, p in groups["odd"].items():
            assert p > 0, f"Odd outcome {label} should be nonzero at phase=π"


class TestGenerationRate:

    def test_zero_distance_gives_baseline(self):
        """At distance=0, only phase shifter loss matters."""
        from qss.tittel2000 import generation_rate_estimate
        # At distance=0: loss = 3 dB → factor = 10^(-0.3) ≈ 0.501
        rate = generation_rate_estimate(0.0)
        expected = 15.0 * 10 ** (-3.0 / 10)
        assert abs(rate - expected) < 0.001

    def test_rate_decreases_with_distance(self):
        from qss.tittel2000 import generation_rate_estimate
        rates = [generation_rate_estimate(d) for d in [0, 10, 20, 40]]
        assert rates[0] > rates[1] > rates[2] > rates[3]

    def test_rate_nonnegative(self):
        from qss.tittel2000 import generation_rate_estimate
        for d in [0, 10, 30, 60]:
            assert generation_rate_estimate(d) >= 0


class TestRateVsDistance:

    def test_shape(self):
        from qss.tittel2000 import rate_vs_distance
        curve = rate_vs_distance(60.0, 200)
        assert curve.shape == (200, 2)

    def test_decreasing(self):
        from qss.tittel2000 import rate_vs_distance
        curve = rate_vs_distance(60.0, 100)
        assert curve[-1, 1] < curve[0, 1]

    def test_nonnegative(self):
        from qss.tittel2000 import rate_vs_distance
        curve = rate_vs_distance(60.0, 100)
        assert np.all(curve[:, 1] >= 0)
