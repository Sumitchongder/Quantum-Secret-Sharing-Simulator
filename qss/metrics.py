"""
qss/metrics.py
==============
Quantum information metrics: fidelity, purity, entropy, QBER.
All functions are pure — no Streamlit imports.
"""

from __future__ import annotations

import numpy as np


def state_fidelity(state1, state2) -> float:
    """
    Compute fidelity F(ρ₁, ρ₂) between two quantum states.

    Parameters
    ----------
    state1, state2 : qutip.Qobj
        Ket or density matrix.

    Returns
    -------
    float
        Fidelity in [0, 1].
    """
    from qutip import fidelity
    return float(fidelity(state1, state2))


def state_purity(state) -> float:
    """
    Compute purity Tr(ρ²) of a quantum state.

    Pure state: purity = 1.0
    Maximally mixed N-qubit state: purity = 1/2^N.

    Parameters
    ----------
    state : qutip.Qobj

    Returns
    -------
    float
    """
    from qutip import ket2dm
    dm = ket2dm(state) if state.type == "ket" else state
    return float((dm * dm).tr().real)


def von_neumann_entropy(state) -> float:
    """
    Compute von Neumann entropy S(ρ) = -Tr(ρ log₂ ρ).

    Parameters
    ----------
    state : qutip.Qobj

    Returns
    -------
    float
        Entropy in bits.
    """
    from qutip import ket2dm, entropy_vn
    dm = ket2dm(state) if state.type == "ket" else state
    return float(entropy_vn(dm, base=2))


def subsystem_entropy(state, qubit_idx: int) -> float:
    """
    Compute von Neumann entropy of a single-qubit subsystem.

    Useful for verifying entanglement: a maximally entangled subsystem has
    entropy = 1.0 bit.

    Parameters
    ----------
    state : qutip.Qobj
        N-qubit state (ket or density matrix).
    qubit_idx : int
        Which qubit subsystem to trace out (keep this qubit).

    Returns
    -------
    float
    """
    from qutip import ket2dm, ptrace, entropy_vn
    dm = ket2dm(state) if state.type == "ket" else state
    rho_sub = ptrace(dm, qubit_idx)
    return float(entropy_vn(rho_sub, base=2))


def qber_from_counts(counts: dict) -> float:
    """
    Estimate QBER from Qiskit measurement counts.

    Error = bitstring with odd number of 1s (parity violation).

    Parameters
    ----------
    counts : dict
        Measurement bitstring counts from AerSimulator.

    Returns
    -------
    float
        Estimated QBER (0–1).
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0
    errors = sum(v for k, v in counts.items() if k.count("1") % 2 != 0)
    return errors / total


def bloch_vector(state) -> tuple[float, float, float]:
    """
    Compute the Bloch sphere vector (x, y, z) for a single-qubit state.

    Parameters
    ----------
    state : qutip.Qobj
        Single-qubit ket or density matrix.

    Returns
    -------
    tuple[float, float, float]
        (x, y, z) Bloch vector components, each in [-1, 1].
    """
    from qutip import ket2dm, sigmax, sigmay, sigmaz, expect
    dm = ket2dm(state) if state.type == "ket" else state
    x = float(expect(sigmax(), dm).real)
    y = float(expect(sigmay(), dm).real)
    z = float(expect(sigmaz(), dm).real)
    return x, y, z


def ghz_concurrence(n: int) -> float:
    """
    Approximate concurrence for the N-qubit GHZ state.

    For 2 qubits: C = 1. For N > 2, returns the bipartite concurrence
    between qubit 0 and the rest.

    Parameters
    ----------
    n : int

    Returns
    -------
    float
    """
    if n == 2:
        return 1.0
    # GHZ state has maximal multipartite entanglement
    # Bipartite concurrence between any qubit and the rest = 1/sqrt(2^(N-2))
    return 1.0 / np.sqrt(2.0 ** (n - 2)) if n > 2 else 1.0
