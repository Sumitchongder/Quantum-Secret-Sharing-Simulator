"""
qss/eavesdropper.py
===================
Eve (eavesdropper) attack simulation for the QSS protocol.

Eve strategy modelled
---------------------
Intercept-resend attack: Eve intercepts a qubit with probability p,
measures it in a random basis, and resends a replacement qubit.
When she guesses the wrong basis (50% chance), she introduces an error.

Result: QBER = p_intercept / 2 (theoretical).

Security threshold
------------------
QBER > 0.05 (5%) → Eve is detected.
"""

from __future__ import annotations

import numpy as np


def inject_eve_attack(
    intercept_prob: float,
    n_rounds: int = 1000,
    seed: int = 42,
) -> dict:
    """
    Simulate Eve intercepting qubits with probability intercept_prob.

    Parameters
    ----------
    intercept_prob : float
        Probability Eve intercepts any given qubit (0–1).
    n_rounds : int
        Number of protocol rounds to simulate.
    seed : int
        RNG seed for reproducibility.

    Returns
    -------
    dict with keys:
        qber          - quantum bit error rate
        n_errors      - number of error rounds
        n_rounds      - total rounds
        n_intercepts  - rounds where Eve intercepted
        intercept_prob
        detected      - True if qber > 0.05
        security_msg  - human-readable status string
    """
    rng = np.random.default_rng(seed)

    # Eve intercepts with probability intercept_prob
    intercepted = rng.random(n_rounds) < intercept_prob

    # When Eve intercepts, she has a 50% chance of guessing wrong basis → error
    basis_error = rng.random(n_rounds) < 0.5
    errors = intercepted & basis_error

    qber = float(errors.mean())
    detected = qber > 0.05

    security_msg = (
        "Eve detected — QBER exceeds 5% threshold." if detected
        else "Channel appears secure — QBER within normal range."
    )

    return {
        "qber": round(qber, 6),
        "n_errors": int(errors.sum()),
        "n_rounds": n_rounds,
        "n_intercepts": int(intercepted.sum()),
        "intercept_prob": intercept_prob,
        "detected": detected,
        "security_msg": security_msg,
    }


def qber_vs_intercept_curve(n_points: int = 200) -> np.ndarray:
    """
    Theoretical QBER = p_intercept / 2 over full intercept probability range.

    Fully vectorised — no Python loop.

    Parameters
    ----------
    n_points : int
        Number of sample points.

    Returns
    -------
    np.ndarray
        Shape (n_points, 2): columns [intercept_prob, theoretical_qber].
    """
    probs = np.linspace(0.0, 1.0, n_points)
    qbers = probs * 0.5
    return np.column_stack([probs, qbers])


def simulated_qber_curve(n_points: int = 50, n_rounds: int = 2000) -> np.ndarray:
    """
    Simulated (Monte Carlo) QBER vs intercept probability.

    Parameters
    ----------
    n_points : int
        Number of intercept probability values to test.
    n_rounds : int
        Protocol rounds per simulation.

    Returns
    -------
    np.ndarray
        Shape (n_points, 2): columns [intercept_prob, simulated_qber].
    """
    probs = np.linspace(0.0, 1.0, n_points)
    rng = np.random.default_rng(0)
    qbers = []
    for p in probs:
        intercepted = rng.random(n_rounds) < p
        errors = intercepted & (rng.random(n_rounds) < 0.5)
        qbers.append(float(errors.mean()))
    return np.column_stack([probs, qbers])


def detection_probability(intercept_prob: float, n_rounds: int = 100) -> float:
    """
    Probability that Eve is detected after n_rounds of QSS protocol.

    P(detected) = 1 - (1 - QBER)^n_rounds ≈ 1 - (1 - p/2)^n_rounds.

    Parameters
    ----------
    intercept_prob : float
    n_rounds : int

    Returns
    -------
    float
        Detection probability (0–1).
    """
    qber = intercept_prob / 2.0
    return 1.0 - (1.0 - qber) ** n_rounds
