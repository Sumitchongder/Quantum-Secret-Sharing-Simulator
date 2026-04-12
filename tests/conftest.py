"""
tests/conftest.py
=================
Shared pytest fixtures for the QSS test suite.

Fixtures are session-scoped where possible to avoid rebuilding
heavy quantum objects on every test.
"""

from __future__ import annotations

import numpy as np
import pytest


@pytest.fixture(scope="session")
def ghz3():
    """3-qubit GHZ state (session scope — built once)."""
    from qss.ghz import build_ghz_qutip
    return build_ghz_qutip(3)


@pytest.fixture(scope="session")
def ghz4():
    """4-qubit GHZ state."""
    from qss.ghz import build_ghz_qutip
    return build_ghz_qutip(4)


@pytest.fixture(scope="session")
def ghz5():
    """5-qubit GHZ state."""
    from qss.ghz import build_ghz_qutip
    return build_ghz_qutip(5)


@pytest.fixture
def rng():
    """Seeded NumPy RNG for reproducible randomness."""
    return np.random.default_rng(42)


@pytest.fixture(scope="session")
def protocol_result_valid():
    """A valid (non-discarded) protocol round result."""
    from qss.protocol import run_protocol_round
    # alpha=0, beta=pi/2, gamma=pi/2 → sum=pi → valid
    return run_protocol_round(3, (0, 1, 1), seed=42)


@pytest.fixture(scope="session")
def protocol_result_discard():
    """A discarded protocol round result."""
    from qss.protocol import run_protocol_round
    # alpha=pi/2, beta=0, gamma=0 → sum=pi/2 → discard
    return run_protocol_round(3, (1, 0, 0), seed=42)
