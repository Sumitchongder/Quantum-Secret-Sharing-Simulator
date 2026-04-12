"""
qss/circuit.py
==============
Qiskit circuit builder and runner for the QSS protocol.

Performance notes
-----------------
- Vectorised CX gate: qc.cx([0,0,...], [1,2,...]) — no Python loop.
- Transpiled once with optimization_level=3.
- AerSimulator backend obtained from cache.get_aer_simulator().
- All args to build_and_run are primitives → safe for st.cache_data.
"""

from __future__ import annotations

import numpy as np
from qss.protocol import PHASES


# ---------------------------------------------------------------------------
# Circuit construction
# ---------------------------------------------------------------------------

def build_ghz_circuit(n: int):
    """
    Build an N-qubit GHZ preparation circuit.

    H on qubit 0, then CNOT from 0 to each of qubits 1…n-1.
    Uses vectorised CX — no Python loop in the hot path.

    Parameters
    ----------
    n : int
        Number of qubits.

    Returns
    -------
    qiskit.QuantumCircuit
    """
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(n, n)
    qc.h(0)
    # Vectorised: pass lists of control and target qubits
    controls = [0] * (n - 1)
    targets = list(range(1, n))
    qc.cx(controls, targets)
    return qc


def apply_phase_gates_circuit(qc, phase_indices: tuple[int, ...]):
    """
    Apply P(φᵢ) gates to each qubit and append measurement.

    Parameters
    ----------
    qc : qiskit.QuantumCircuit
        GHZ circuit (without measurements).
    phase_indices : tuple[int, ...]
        Phase index (0 or 1) for each qubit.

    Returns
    -------
    qiskit.QuantumCircuit
        Circuit with phase gates and measure_all appended.
    """
    qc2 = qc.copy()
    for qubit, idx in enumerate(phase_indices):
        phi = PHASES[idx]
        if phi != 0.0:
            qc2.p(phi, qubit)
    qc2.measure_all()
    return qc2


# ---------------------------------------------------------------------------
# Noise model factory
# ---------------------------------------------------------------------------

def _make_noise_model(name: str, error_rate: float = 0.01):
    """
    Create a Qiskit noise model.

    Parameters
    ----------
    name : str
        'none', 'depolarise', or 'dephase'.
    error_rate : float
        Error probability per gate.

    Returns
    -------
    qiskit_aer.noise.NoiseModel or None
    """
    if name == "none":
        return None

    from qiskit_aer.noise import NoiseModel, depolarizing_error, phase_damping_error

    nm = NoiseModel()
    if name == "depolarise":
        err = depolarizing_error(error_rate, 1)
    else:  # dephase
        err = phase_damping_error(error_rate)
    nm.add_all_qubit_quantum_error(err, ["h", "p", "cx"])
    return nm


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def build_and_run(
    n: int,
    alpha_i: int,
    beta_i: int,
    gamma_i: int,
    noise_name: str,
    shots: int = 2048,
) -> dict:
    """
    Build, transpile, and run the full QSS Qiskit circuit.

    All parameters are primitives (int, str) so this function is safely
    wrapped by @st.cache_data in qss/cache.py.

    Parameters
    ----------
    n : int
        Number of nodes.
    alpha_i, beta_i, gamma_i : int
        Phase indices (0 or 1).
    noise_name : str
        'none', 'depolarise', or 'dephase'.
    shots : int
        Number of measurement shots.

    Returns
    -------
    dict
        Measurement bitstring counts.
    """
    from qiskit import transpile
    from qss.cache import get_aer_simulator

    # Build phase index tuple (pad remaining nodes with 0)
    extra = (0,) * (n - 3)
    phase_indices = (alpha_i, beta_i, gamma_i) + extra

    qc = build_ghz_circuit(n)
    qc = apply_phase_gates_circuit(qc, phase_indices)
    nm = _make_noise_model(noise_name)

    backend = get_aer_simulator()
    tqc = transpile(qc, backend, optimization_level=3)
    job = backend.run(tqc, noise_model=nm, shots=shots)
    return job.result().get_counts()


# ---------------------------------------------------------------------------
# Circuit diagram helper
# ---------------------------------------------------------------------------

def get_circuit_figure(n: int, alpha_i: int, beta_i: int, gamma_i: int):
    """
    Return a Matplotlib figure of the QSS circuit (for display in Streamlit).

    Parameters
    ----------
    n, alpha_i, beta_i, gamma_i : int

    Returns
    -------
    matplotlib.figure.Figure
    """
    extra = (0,) * (n - 3)
    phase_indices = (alpha_i, beta_i, gamma_i) + extra
    qc = build_ghz_circuit(n)
    qc = apply_phase_gates_circuit(qc, phase_indices)
    return qc.draw("mpl", fold=-1, style="iqp")
