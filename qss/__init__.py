"""
Quantum Secret Sharing Simulator
=================================
Core simulation package — no Streamlit imports anywhere in this module.
All public symbols are importable from ``qss`` directly.

Usage
-----
>>> from qss.ghz import build_ghz_qutip
>>> from qss.protocol import parity_check, reconstruct_secret
>>> from qss.eavesdropper import inject_eve_attack
"""

from qss.protocol import parity_check, reconstruct_secret, PHASES
from qss.ghz import build_ghz_qutip, build_ghz_approach1, build_ghz_approach2
from qss.eavesdropper import inject_eve_attack, qber_vs_intercept_curve
from qss.metrics import state_fidelity, state_purity, von_neumann_entropy, qber_from_counts
from qss.noise import depolarise_sweep, dephase_sweep
from qss.tittel2000 import (
    detection_probability,
    all_outcome_probabilities,
    generation_rate_estimate,
)

__version__ = "1.0.0"
__author__ = "Sumit Tapas Chongder"
__all__ = [
    "parity_check",
    "reconstruct_secret",
    "PHASES",
    "build_ghz_qutip",
    "build_ghz_approach1",
    "build_ghz_approach2",
    "inject_eve_attack",
    "qber_vs_intercept_curve",
    "state_fidelity",
    "state_purity",
    "von_neumann_entropy",
    "qber_from_counts",
    "depolarise_sweep",
    "dephase_sweep",
    "detection_probability",
    "all_outcome_probabilities",
    "generation_rate_estimate",
]
