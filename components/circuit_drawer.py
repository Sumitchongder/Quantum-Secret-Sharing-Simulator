"""
components/circuit_drawer.py
=============================
Qiskit circuit diagram renderer for Streamlit.
Uses matplotlib backend from Qiskit and renders as an image.
"""

from __future__ import annotations

import streamlit as st


def render_circuit_diagram(
    n: int,
    alpha_i: int,
    beta_i: int,
    gamma_i: int,
) -> None:
    """
    Draw and display the QSS Qiskit circuit in Streamlit.

    Parameters
    ----------
    n : int
        Number of qubits.
    alpha_i, beta_i, gamma_i : int
        Phase indices.
    """
    from qss.circuit import get_circuit_figure

    try:
        fig = get_circuit_figure(n, alpha_i, beta_i, gamma_i)
        st.pyplot(fig, use_container_width=True)
    except Exception as exc:
        st.error(f"Circuit rendering failed: {exc}")
        st.info(
            "This usually means `pylatexenc` is not installed. "
            "Run: `pip install pylatexenc`"
        )


def render_circuit_text(n: int, alpha_i: int, beta_i: int, gamma_i: int) -> None:
    """
    Render the QSS circuit as text (fallback if matplotlib unavailable).

    Parameters
    ----------
    n, alpha_i, beta_i, gamma_i : int
    """
    from qss.circuit import build_ghz_circuit, apply_phase_gates_circuit
    from qss.protocol import PHASES

    extra = (0,) * (n - 3)
    phase_indices = (alpha_i, beta_i, gamma_i) + extra
    qc = build_ghz_circuit(n)
    qc = apply_phase_gates_circuit(qc, phase_indices)

    try:
        text = str(qc.draw("text"))
        st.code(text, language="text")
    except Exception as exc:
        st.error(f"Text circuit rendering failed: {exc}")
