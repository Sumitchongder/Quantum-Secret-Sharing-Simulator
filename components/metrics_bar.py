"""
components/metrics_bar.py
=========================
Fidelity, QBER, purity, and entropy metric cards.
Uses st.metric for a clean, scannable dashboard row.
"""

from __future__ import annotations

import streamlit as st


def render_metrics_bar(
    fidelity: float | None = None,
    purity: float | None = None,
    entropy: float | None = None,
    qber: float | None = None,
    n_nodes: int = 3,
) -> None:
    """
    Render a horizontal row of metric cards.

    Parameters
    ----------
    fidelity : float or None
        State fidelity vs ideal GHZ (0–1).
    purity : float or None
        State purity Tr(ρ²) (0–1).
    entropy : float or None
        Von Neumann entropy in bits.
    qber : float or None
        Quantum bit error rate (0–1).
    n_nodes : int
        Used to display Hilbert space dimension.
    """
    cols = st.columns(5)

    with cols[0]:
        if fidelity is not None:
            delta_color = "normal" if fidelity >= 0.9 else "inverse"
            st.metric(
                label="Fidelity F",
                value=f"{fidelity:.4f}",
                delta=f"{'✓ High' if fidelity >= 0.9 else '✗ Degraded'}",
                delta_color=delta_color,
                help="Overlap with ideal GHZ state. F=1 is perfect.",
            )
        else:
            st.metric("Fidelity F", "—")

    with cols[1]:
        if purity is not None:
            st.metric(
                label="Purity Tr(ρ²)",
                value=f"{purity:.4f}",
                help="1.0 = pure state, 1/2^N = maximally mixed.",
            )
        else:
            st.metric("Purity Tr(ρ²)", "—")

    with cols[2]:
        if entropy is not None:
            st.metric(
                label="Entropy S(ρ) (bits)",
                value=f"{entropy:.4f}",
                help="Von Neumann entropy. 0 = pure, 1 = maximally entangled qubit.",
            )
        else:
            st.metric("Entropy S(ρ) (bits)", "—")

    with cols[3]:
        if qber is not None:
            delta_color = "inverse" if qber > 0.05 else "normal"
            st.metric(
                label="QBER",
                value=f"{qber:.4f}",
                delta=f"{'⚠ Eve detected' if qber > 0.05 else '✓ Secure'}",
                delta_color=delta_color,
                help="Quantum bit error rate. > 5% signals eavesdropping.",
            )
        else:
            st.metric("QBER", "—")

    with cols[4]:
        dim = 2 ** n_nodes
        st.metric(
            label="Hilbert dim 2ᴺ",
            value=f"{dim}",
            help=f"State space dimension for N={n_nodes} qubits.",
        )


def render_protocol_result(result: dict) -> None:
    """
    Render the QSS protocol round result in a clean card layout.

    Parameters
    ----------
    result : dict
        Output of qss.protocol.run_protocol_round().
    """
    if result["discard"]:
        st.warning(
            "**Round discarded** — phases do not satisfy α+β+γ ∈ {0, π}. "
            "Discard and restart."
        )
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Parity d = cos(Σφ)", f"{result['parity']:+d}")
    col2.metric("Secret bit c (node C)", f"{result['secret_value']:+d}")
    col3.metric("A & B infer c as", f"{result['inferred_value']:+d}")
    col4.metric(
        "Reconstruction",
        "✓ Success" if result["success"] else "✗ Failed",
    )

    phases_str = " + ".join(
        f"{'π/2' if i == 1 else '0'}" for i in result["phase_indices"]
    )
    st.caption(f"Phase sum: {phases_str} = {'π' if result['parity'] == -1 else '0'} rad  |  "
               f"Outcomes: {result['outcomes']}")
