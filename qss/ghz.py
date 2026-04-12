"""
qss/ghz.py
==========
GHZ state generation using QuTiP tensor products.
Implements both approaches for distributing a GHZ state across a quantum network.

No Streamlit imports — pure QuTiP + NumPy.
All functions are pure (no side effects) and safely cacheable.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Core GHZ state builder
# ---------------------------------------------------------------------------

def build_ghz_qutip(n: int):
    """
    Build an N-qubit GHZ state using QuTiP.

    |GHZ⟩ = (1/√2)(|00…0⟩ + |11…1⟩)

    Parameters
    ----------
    n : int
        Number of qubits (nodes), must be >= 2.

    Returns
    -------
    qutip.Qobj
        Normalised GHZ ket state.

    Examples
    --------
    >>> state = build_ghz_qutip(3)
    >>> abs(state.norm() - 1.0) < 1e-10
    True
    """
    from qutip import basis, tensor

    if n < 2:
        raise ValueError(f"n must be >= 2, got {n}")

    zero = basis(2, 0)
    one = basis(2, 1)
    all_zero = tensor([zero] * n)
    all_one = tensor([one] * n)
    return (all_zero + all_one).unit()


def build_density_matrix(n: int):
    """
    Build the density matrix ρ = |GHZ⟩⟨GHZ| for N qubits.

    Parameters
    ----------
    n : int
        Number of qubits.

    Returns
    -------
    qutip.Qobj
        Density matrix (ket2dm of GHZ state).
    """
    from qutip import ket2dm

    return ket2dm(build_ghz_qutip(n))


# ---------------------------------------------------------------------------
# Approach 1 — teleportation-based GHZ distribution
# ---------------------------------------------------------------------------

def build_ghz_approach1(n: int) -> tuple:
    """
    Approach 1: B creates a local GHZ state, then teleports qubits to A and C
    via Bell-state measurements (BSMs).

    Properties
    ----------
    - Uses more qubits: n (GHZ) + 2*(n-1) (Bell pair ancillas)
    - Requires two E2E connections before teleportation
    - Hop-by-hop teleportation degrades fidelity
    - Classical messages: 2*(n-1) from B to other nodes

    Parameters
    ----------
    n : int
        Number of network nodes.

    Returns
    -------
    tuple
        (ghz_state, qubit_count, classical_msg_count, fidelity_estimate)
    """
    ghz = build_ghz_qutip(n)
    qubit_count = n + 2 * (n - 1)   # local GHZ + Bell pair qubits
    msg_count = 2 * (n - 1)          # 2 bits per BSM result
    # Fidelity degrades with hops — approximate model
    fidelity_estimate = float(0.98 ** (n - 1))
    return ghz, qubit_count, msg_count, fidelity_estimate


# ---------------------------------------------------------------------------
# Approach 2 — Bell pairs + local entangling operations
# ---------------------------------------------------------------------------

def build_ghz_approach2(n: int) -> tuple:
    """
    Approach 2: Bell pairs shared between adjacent nodes. B entangles its two
    qubits locally, measures one out, sends one classical bit to C.

    Properties
    ----------
    - Fewer qubits: exactly n (one per node)
    - No teleportation required
    - Demonstrated experimentally in a laboratory in 2021
    - Classical messages: n-1 (one per link)

    Parameters
    ----------
    n : int
        Number of network nodes.

    Returns
    -------
    tuple
        (ghz_state, qubit_count, classical_msg_count, fidelity_estimate)
    """
    ghz = build_ghz_qutip(n)
    qubit_count = n           # one qubit per node only
    msg_count = n - 1         # one classical message per link
    fidelity_estimate = float(0.99 ** (n - 1))  # fewer operations → higher fidelity
    return ghz, qubit_count, msg_count, fidelity_estimate


# ---------------------------------------------------------------------------
# Comparison helper
# ---------------------------------------------------------------------------

def compare_approaches(n: int) -> dict:
    """
    Return a side-by-side comparison dict for both approaches.

    Parameters
    ----------
    n : int
        Number of network nodes.

    Returns
    -------
    dict
        Keys: 'approach1', 'approach2', each with sub-keys:
        qubit_count, msg_count, fidelity_estimate, teleportation_needed, lab_demonstrated.
    """
    _, q1, m1, f1 = build_ghz_approach1(n)
    _, q2, m2, f2 = build_ghz_approach2(n)
    return {
        "approach1": {
            "qubit_count": q1,
            "msg_count": m1,
            "fidelity_estimate": round(f1, 4),
            "teleportation_needed": True,
            "lab_demonstrated": False,
        },
        "approach2": {
            "qubit_count": q2,
            "msg_count": m2,
            "fidelity_estimate": round(f2, 4),
            "teleportation_needed": False,
            "lab_demonstrated": True,
        },
    }
