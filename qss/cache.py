"""
qss/cache.py
============
Central caching module for the QSS Simulator.

Caching strategy
----------------
@st.cache_resource  → heavy objects built ONCE per server process (GHZ states,
                       AerSimulator backend). Survive across all user sessions.

@st.cache_data      → per-parameter results keyed by primitive args (Wigner grids,
                       fidelity curves, Qiskit counts). TTL = 1 hour.
                       CRITICAL: prefix Qobj args with '_' so Streamlit skips hashing.

functools.lru_cache → pure Python math in qss/protocol.py (parity_check,
                       reconstruct_secret). Zero Streamlit overhead.

Expected latency after warm-up
-------------------------------
Phase slider move           < 5 ms    (lru_cache hit)
GHZ state (cold)            ~120 ms   (QuTiP tensor)
GHZ state (warm)            0 ms      (cache_resource)
Wigner plot (new params)    ~300 ms   (QuTiP grid)
Wigner plot (same params)   < 1 ms    (cache_data hit)
Qiskit circuit N=3 (cold)   ~200 ms   (AerSimulator)
Qiskit circuit (warm)       < 2 ms    (cache_data hit)
"""

from __future__ import annotations

import numpy as np
import streamlit as st


# ---------------------------------------------------------------------------
# cache_resource — built once per server process
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Building GHZ state…")
def get_ghz_state(n_nodes: int):
    """
    Build and cache an N-qubit GHZ state.

    Uses @st.cache_resource so the Qobj is built once and shared across
    all user sessions on the same server process.

    Parameters
    ----------
    n_nodes : int
        Number of qubits / network nodes.

    Returns
    -------
    qutip.Qobj
        Normalised GHZ ket.
    """
    from qss.ghz import build_ghz_qutip
    return build_ghz_qutip(n_nodes)


@st.cache_resource(show_spinner=False)
def get_aer_simulator():
    """
    Build and cache the Qiskit AerSimulator backend.

    Building the backend involves loading shared libraries (~100 ms).
    Cached once per server process.

    Returns
    -------
    qiskit_aer.AerSimulator
    """
    from qiskit_aer import AerSimulator
    return AerSimulator()


# ---------------------------------------------------------------------------
# cache_data — per-parameter, TTL = 1 hour
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600, show_spinner=False)
def compute_wigner(_state, xvec_tuple: tuple, pvec_tuple: tuple) -> np.ndarray:
    """
    Compute the Wigner function on a phase-space grid.

    The leading underscore on _state tells Streamlit to skip hashing the
    Qobj (which is unhashable). Cache key is effectively (id(_state), xvec, pvec).

    Parameters
    ----------
    _state : qutip.Qobj
        Quantum state (ket or density matrix).
    xvec_tuple : tuple
        X-axis values as a tuple (hashable).
    pvec_tuple : tuple
        P-axis values as a tuple (hashable).

    Returns
    -------
    np.ndarray
        2D Wigner function values.
    """
    from qutip import wigner

    xvec = np.array(xvec_tuple)
    pvec = np.array(pvec_tuple)
    return wigner(_state, xvec, pvec)


@st.cache_data(ttl=3600, show_spinner=False)
def run_qiskit_circuit(
    n: int,
    alpha_i: int,
    beta_i: int,
    gamma_i: int,
    noise_name: str,
    shots: int = 2048,
) -> dict:
    """
    Build, transpile, and run the QSS Qiskit circuit.

    Cached by (n, alpha_i, beta_i, gamma_i, noise_name, shots).
    All args are primitive types — safe for Streamlit hashing.

    Returns
    -------
    dict
        Measurement counts from AerSimulator.
    """
    from qss.circuit import build_and_run
    return build_and_run(n, alpha_i, beta_i, gamma_i, noise_name, shots)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_fidelity_curve(n_nodes: int, max_noise: float, model: str = "depolarise") -> np.ndarray:
    """
    Compute fidelity vs noise level curve.

    Parameters
    ----------
    n_nodes : int
    max_noise : float
        Maximum noise probability (0–1).
    model : str
        'depolarise' or 'dephase'.

    Returns
    -------
    np.ndarray
        Shape (100, 2): columns are [noise_level, fidelity].
    """
    from qss.noise import depolarise_sweep, dephase_sweep
    if model == "dephase":
        return dephase_sweep(n_nodes, max_noise)
    return depolarise_sweep(n_nodes, max_noise)


@st.cache_data(ttl=3600, show_spinner=False)
def compute_optical_probabilities(
    alpha: float, beta: float, gamma: float
) -> dict:
    """
    Compute all 8 Tittel-2000 detection probabilities for given phases.

    Returns
    -------
    dict
        Keys are outcome labels '(+1,+1,+1)' etc., values are probabilities.
    """
    from qss.tittel2000 import all_outcome_probabilities
    return all_outcome_probabilities(alpha, beta, gamma)
