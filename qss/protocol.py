"""
qss/protocol.py
===============
Core QSS protocol logic — no Streamlit imports, pure Python + NumPy + QuTiP.

Protocol summary (3-node case)
-------------------------------
1. Nodes A, B, C share a GHZ state.
2. Each picks a random phase index from {0, 1} → {0, π/2}.
3. Each applies phase gate P(φ) to their qubit.
4. All measure in Pauli-X basis → outcomes a, b, c ∈ {+1, -1}.
5. Phases declared publicly; protocol proceeds only if α+β+γ ∈ {0, π}.
6. Product a·b·c = cos(α+β+γ) = ±1.
7. A and B exchange outcomes on a private channel → infer c = a·b·d.
"""

from __future__ import annotations

import functools
import numpy as np

# Phase lookup — index 0 → 0 rad, index 1 → π/2 rad
PHASES: list[float] = [0.0, np.pi / 2]


# ---------------------------------------------------------------------------
# Phase gate application
# ---------------------------------------------------------------------------

def apply_phase_gates(ghz_state, phase_indices: tuple[int, ...]):
    """
    Apply P(φᵢ) to each qubit i of the GHZ state.

    P(φ)|0⟩ = |0⟩,  P(φ)|1⟩ = e^{iφ}|1⟩

    Parameters
    ----------
    ghz_state : qutip.Qobj
        N-qubit GHZ ket.
    phase_indices : tuple[int, ...]
        Index into PHASES for each node, length N.

    Returns
    -------
    qutip.Qobj
        Phase-gated state.
    """
    from qutip import phasegate, tensor, qeye

    n = len(phase_indices)
    result = ghz_state
    for i, idx in enumerate(phase_indices):
        phi = PHASES[idx]
        if phi == 0.0:
            continue
        gate_list = [qeye(2)] * n
        gate_list[i] = phasegate(phi)
        op = tensor(gate_list)
        result = op * result
    return result


# ---------------------------------------------------------------------------
# Parity check — cached, takes only ints (hashable)
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=256)
def parity_check(alpha_i: int, beta_i: int, gamma_i: int) -> int:
    """
    Check whether the phase combination satisfies the QSS proceed condition.

    Protocol proceeds only if α + β + γ ∈ {0, π}.
    Returns +1 (α+β+γ = 0), -1 (α+β+γ = π), or 0 (discard this round).

    Parameters
    ----------
    alpha_i, beta_i, gamma_i : int
        Indices into the PHASES list (0 or 1).

    Returns
    -------
    int
        +1, -1, or 0.

    Examples
    --------
    >>> parity_check(0, 0, 0)   # 0+0+0=0 → cos=+1
    1
    >>> parity_check(1, 1, 0)   # π/2+π/2+0=π → cos=-1
    -1
    >>> parity_check(1, 0, 0)   # π/2 → discard
    0
    """
    total = PHASES[alpha_i] + PHASES[beta_i] + PHASES[gamma_i]
    remainder = total % np.pi
    if np.isclose(remainder, 0.0, atol=1e-9):
        return int(round(np.cos(total)))   # +1 or -1
    return 0  # discard


@functools.lru_cache(maxsize=256)
def parity_check_n(phase_indices: tuple[int, ...]) -> int:
    """
    N-node generalisation of parity_check.

    Protocol proceeds only if sum of phases ∈ {0, π}.

    Parameters
    ----------
    phase_indices : tuple[int, ...]
        Phase index for each node.

    Returns
    -------
    int
        +1, -1, or 0 (discard).
    """
    total = sum(PHASES[i] for i in phase_indices)
    remainder = total % np.pi
    if np.isclose(remainder, 0.0, atol=1e-9):
        return int(round(np.cos(total)))
    return 0


# ---------------------------------------------------------------------------
# Secret reconstruction — cached
# ---------------------------------------------------------------------------

@functools.lru_cache(maxsize=512)
def reconstruct_secret(a: int, b: int, d: int) -> int:
    """
    Nodes A and B infer node C's secret bit.

    From the relation a · b · c · d = 1  →  c = a · b · d.
    All values are ±1.

    Parameters
    ----------
    a, b : int
        Measurement outcomes of nodes A and B (±1).
    d : int
        Value of cos(α+β+γ) = ±1 (from parity_check).

    Returns
    -------
    int
        Inferred value of c (±1).

    Examples
    --------
    >>> reconstruct_secret(1, 1, 1)
    1
    >>> reconstruct_secret(1, -1, 1)
    -1
    """
    return a * b * d


# ---------------------------------------------------------------------------
# Measurement simulation
# ---------------------------------------------------------------------------

def simulate_measurement(n: int, phase_indices: tuple[int, ...], seed: int = 42) -> list[int]:
    """
    Simulate Pauli-X basis measurements on the phase-gated GHZ state.

    Individual outcomes are uniformly random (±1) but their product
    equals cos(α+β+γ) when the parity condition is satisfied.

    Parameters
    ----------
    n : int
        Number of nodes.
    phase_indices : tuple[int, ...]
        Phase index for each node.
    seed : int
        RNG seed for reproducibility.

    Returns
    -------
    list[int]
        Measurement outcomes, one per node, each ±1.
    """
    rng = np.random.default_rng(seed)
    d = parity_check_n(phase_indices)
    if d == 0:
        # Discard round — return random anyway (caller should check parity first)
        return [int(rng.choice([-1, 1])) for _ in range(n)]

    # First n-1 outcomes are uniformly random
    outcomes = [int(rng.choice([-1, 1])) for _ in range(n - 1)]
    # Last outcome is determined by the parity constraint: product = d
    product_so_far = int(np.prod(outcomes))
    last = d * product_so_far  # ensures a·b·…·z = d
    outcomes.append(last)
    return outcomes


# ---------------------------------------------------------------------------
# Full protocol round
# ---------------------------------------------------------------------------

def run_protocol_round(
    n: int,
    phase_indices: tuple[int, ...],
    seed: int = 42,
) -> dict:
    """
    Execute one complete QSS protocol round.

    Parameters
    ----------
    n : int
        Number of nodes.
    phase_indices : tuple[int, ...]
        Phase index for each node (length n).
    seed : int
        RNG seed.

    Returns
    -------
    dict with keys:
        phase_indices, phases_rad, parity, outcomes, secret_node_idx,
        secret_value, inferred_value, success, discard
    """
    phases_rad = [PHASES[i] for i in phase_indices]
    parity = parity_check_n(phase_indices)

    if parity == 0:
        return {
            "phase_indices": phase_indices,
            "phases_rad": phases_rad,
            "parity": 0,
            "outcomes": [],
            "discard": True,
            "success": False,
            "secret_node_idx": n - 1,
            "secret_value": None,
            "inferred_value": None,
        }

    outcomes = simulate_measurement(n, phase_indices, seed)
    secret_node_idx = n - 1          # last node holds the secret
    secret_value = outcomes[secret_node_idx]

    # All other nodes collaborate to infer the secret
    a, b = outcomes[0], outcomes[1]
    inferred = reconstruct_secret(a, b, parity)

    return {
        "phase_indices": phase_indices,
        "phases_rad": phases_rad,
        "parity": parity,
        "outcomes": outcomes,
        "discard": False,
        "success": inferred == secret_value,
        "secret_node_idx": secret_node_idx,
        "secret_value": secret_value,
        "inferred_value": inferred,
    }
