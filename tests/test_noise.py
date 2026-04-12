"""
tests/test_noise.py
===================
Tests for noise channel models: depolarise and dephase sweeps.
"""

from __future__ import annotations

import numpy as np
import pytest


class TestDepolariseSweep:

    def test_shape(self):
        from qss.noise import depolarise_sweep
        curve = depolarise_sweep(3, 0.5)
        assert curve.shape == (100, 2)

    def test_zero_noise_fidelity_is_one(self):
        from qss.noise import depolarise_sweep
        curve = depolarise_sweep(3, 0.5)
        assert curve[0, 1] == pytest.approx(1.0, abs=1e-10)

    def test_fidelity_in_range(self):
        from qss.noise import depolarise_sweep
        for n in [3, 4, 5]:
            curve = depolarise_sweep(n, 0.5)
            assert np.all(curve[:, 1] >= 0.0)
            assert np.all(curve[:, 1] <= 1.0)

    def test_fidelity_decreases_with_noise(self):
        from qss.noise import depolarise_sweep
        curve = depolarise_sweep(3, 0.5)
        # Generally decreasing (allow small numerical bumps)
        assert curve[-1, 1] < curve[0, 1]

    def test_more_nodes_lower_fidelity(self):
        from qss.noise import depolarise_sweep
        c3 = depolarise_sweep(3, 0.3)
        c5 = depolarise_sweep(5, 0.3)
        # At same noise, N=5 should have lower fidelity than N=3
        assert c5[-1, 1] <= c3[-1, 1]

    @pytest.mark.parametrize("n", [3, 4, 5, 6])
    def test_analytical_formula(self, n):
        """Test that F(p) = (1-p)^N + p^N/2^N is correctly implemented."""
        from qss.noise import depolarise_sweep
        curve = depolarise_sweep(n, 1.0, n_points=11)
        for p, f in curve:
            expected = (1 - p) ** n + p ** n / 2 ** n
            assert abs(f - expected) < 1e-10, f"N={n}, p={p}: f={f}, expected={expected}"


class TestDephaseSweep:

    def test_shape(self):
        from qss.noise import dephase_sweep
        curve = dephase_sweep(3, 0.5)
        assert curve.shape == (100, 2)

    def test_zero_noise_fidelity_is_one(self):
        from qss.noise import dephase_sweep
        curve = dephase_sweep(3, 0.5)
        assert curve[0, 1] == pytest.approx(1.0, abs=1e-10)

    def test_fidelity_in_range(self):
        from qss.noise import dephase_sweep
        curve = dephase_sweep(3, 0.9)
        assert np.all(curve[:, 1] >= 0.0)
        assert np.all(curve[:, 1] <= 1.0)

    @pytest.mark.parametrize("n", [3, 4, 5])
    def test_analytical_formula(self, n):
        """Test that F(p) = (1-p)^N."""
        from qss.noise import dephase_sweep
        curve = dephase_sweep(n, 1.0, n_points=11)
        for p, f in curve:
            expected = (1 - p) ** n
            assert abs(f - expected) < 1e-10


class TestThresholdNoise:

    def test_threshold_exists(self):
        from qss.noise import threshold_noise
        t = threshold_noise(3, "depolarise", 0.9)
        assert 0.0 <= t <= 1.0

    def test_threshold_higher_for_fewer_nodes(self):
        from qss.noise import threshold_noise
        t3 = threshold_noise(3, "depolarise", 0.9)
        t5 = threshold_noise(5, "depolarise", 0.9)
        assert t3 >= t5   # fewer nodes → more noise tolerance

    def test_threshold_for_dephase(self):
        from qss.noise import threshold_noise
        t = threshold_noise(3, "dephase", 0.9)
        assert 0.0 <= t <= 1.0


class TestHelpers:

    @pytest.mark.parametrize("n,expected_dim", [
        (3, 8), (4, 16), (5, 32), (6, 64),
    ])
    def test_hilbert_space_dim(self, n, expected_dim):
        from qss.noise import hilbert_space_dim
        assert hilbert_space_dim(n) == expected_dim

    def test_memory_mb_positive(self):
        from qss.noise import memory_mb_estimate
        for n in [3, 4, 5]:
            mem = memory_mb_estimate(n)
            assert mem > 0

    def test_memory_grows_with_n(self):
        from qss.noise import memory_mb_estimate
        mems = [memory_mb_estimate(n) for n in [3, 4, 5]]
        assert mems[0] < mems[1] < mems[2]
