"""
qss/noise.py
============
Depolarising and dephasing channel models.

All sweep functions are fully vectorised with NumPy — no Python loops.
Results are returned as (n_points, 2) arrays: [noise_level, fidelity].
"""

from __future__ import annotations

import numpy as np


def depolarise_sweep(
    n_nodes: int,
    max_noise: float,
    n_points: int = 100,
) -> np.ndarray:
    """
    Analytical fidelity of the N-qubit GHZ state under independent
    single-qubit depolarising noise.

    Model: each qubit undergoes depolarising channel with parameter p.
    Fidelity: F(p) = (1-p)^N + p^N / 2^N

    This is vectorised — no Python loop over noise levels.

    Parameters
    ----------
    n_nodes : int
        Number of qubits.
    max_noise : float
        Maximum depolarising probability (0 to 1).
    n_points : int
        Number of sample points.

    Returns
    -------
    np.ndarray
        Shape (n_points, 2): columns [noise_prob, fidelity].
    """
    N = n_nodes
    p = np.linspace(0.0, max_noise, n_points)
    fidelities = (1.0 - p) ** N + (p ** N) / (2.0 ** N)
    fidelities = np.clip(fidelities, 0.0, 1.0)
    return np.column_stack([p, fidelities])


def dephase_sweep(
    n_nodes: int,
    max_noise: float,
    n_points: int = 100,
) -> np.ndarray:
    """
    Analytical fidelity under independent single-qubit dephasing.

    Model: phase-flip channel with parameter p.
    Fidelity: F(p) = ((1-p)^N + (1-p)^N) / 2 ≈ (1-p)^N for GHZ off-diagonal.

    Parameters
    ----------
    n_nodes : int
    max_noise : float
    n_points : int

    Returns
    -------
    np.ndarray
        Shape (n_points, 2): columns [noise_prob, fidelity].
    """
    p = np.linspace(0.0, max_noise, n_points)
    fidelities = (1.0 - p) ** n_nodes
    fidelities = np.clip(fidelities, 0.0, 1.0)
    return np.column_stack([p, fidelities])


def threshold_noise(
    n_nodes: int,
    model: str = "depolarise",
    target_fidelity: float = 0.9,
) -> float:
    """
    Find the noise threshold at which fidelity drops below target_fidelity.

    Parameters
    ----------
    n_nodes : int
    model : str
        'depolarise' or 'dephase'.
    target_fidelity : float

    Returns
    -------
    float
        Noise probability threshold (0–1). Returns 1.0 if always above target.
    """
    curve = depolarise_sweep(n_nodes, 1.0, 1000) if model == "depolarise" \
        else dephase_sweep(n_nodes, 1.0, 1000)
    below = curve[:, 1] < target_fidelity
    if not below.any():
        return 1.0
    return float(curve[below.argmax(), 0])


def hilbert_space_dim(n_nodes: int) -> int:
    """Return the Hilbert space dimension 2^N."""
    return 2 ** n_nodes


def memory_mb_estimate(n_nodes: int) -> float:
    """Estimate density matrix memory in MB for N qubits (complex128)."""
    dim = hilbert_space_dim(n_nodes)
    return dim ** 2 * 16 / (1024 ** 2)   # 16 bytes per complex128 element
