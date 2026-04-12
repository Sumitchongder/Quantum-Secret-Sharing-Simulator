"""
pages/protocol_lab.py
=====================
Tab 1 — Step-by-step 3-node QSS protocol walkthrough.

Performance: all heavy work is cache_resource/lru_cache.
After first load, slider changes are < 5 ms.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st


@st.fragment
def render(params: dict) -> None:
    """Render the Protocol Lab tab."""
    n = params["n_nodes"]
    alpha_i = params["alpha_i"]
    beta_i = params["beta_i"]
    gamma_i = params["gamma_i"]

    st.markdown("## Protocol Lab")
    st.markdown(
        "Interactive step-by-step simulation of the Quantum Secret Sharing protocol "
        "using a GHZ state. Adjust phases in the sidebar to explore different protocol rounds."
    )

    # ── Phase panel ─────────────────────────────────────────────────────────
    from components.phase_panel import render_phase_panel
    render_phase_panel(alpha_i, beta_i, gamma_i)

    from qss.protocol import parity_check, run_protocol_round
    parity = parity_check(alpha_i, beta_i, gamma_i)
    if parity == 0:
        return   # discard — phase panel already showed the error

    # ── Protocol round ───────────────────────────────────────────────────────
    phase_indices = (alpha_i, beta_i, gamma_i) + (0,) * (n - 3)
    result = run_protocol_round(n, phase_indices, seed=42)

    st.divider()
    st.markdown("### Protocol round result")
    from components.metrics_bar import render_protocol_result
    render_protocol_result(result)

    # ── GHZ state info ───────────────────────────────────────────────────────
    st.divider()
    st.markdown("### GHZ state properties")

    from qss.cache import get_ghz_state
    ghz = get_ghz_state(n)

    col1, col2, col3 = st.columns(3)
    col1.metric("Norm ‖|GHZ⟩‖", f"{ghz.norm():.6f}")
    col2.metric("Hilbert dim", f"{2**n}")
    col3.metric("Qubits (nodes)", f"{n}")

    # ── Measurement outcome bar chart ────────────────────────────────────────
    st.divider()
    st.markdown("### Measurement outcomes (simulated rounds)")

    outcomes_data = _simulate_many_rounds(n, phase_indices, n_rounds=500)
    fig = _outcomes_bar_chart(outcomes_data, parity)
    st.plotly_chart(fig, use_container_width=True)

    # ── Theory expander ──────────────────────────────────────────────────────
    with st.expander("Theory — how does this work?", expanded=False):
        st.markdown(r"""
**GHZ state:** $|GHZ\rangle = \frac{1}{\sqrt{2}}(|00\cdots0\rangle + |11\cdots1\rangle)$

**Phase gate:** $P(\phi)|0\rangle = |0\rangle,\quad P(\phi)|1\rangle = e^{i\phi}|1\rangle$

**After phase gates:** $|\psi\rangle = \frac{1}{\sqrt{2}}\bigl(|000\rangle + e^{i(\alpha+\beta+\gamma)}|111\rangle\bigr)$

**Measurement product:** $a \cdot b \cdot c = \cos(\alpha+\beta+\gamma) = \pm 1$

**Secret reconstruction:** $c = a \cdot b \cdot d$ where $d = \cos(\alpha+\beta+\gamma)$

The protocol is **symmetric** — any node's bit can be the secret.
Local outcomes are completely random, so an eavesdropper sees only noise.
        """)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _simulate_many_rounds(n: int, phase_indices: tuple, n_rounds: int) -> dict:
    """Simulate n_rounds and count outcome frequencies."""
    from qss.protocol import simulate_measurement, parity_check_n

    parity = parity_check_n(phase_indices)
    freq: dict = {}
    for seed in range(n_rounds):
        outcomes = simulate_measurement(n, phase_indices, seed=seed)
        key = tuple(outcomes)
        freq[key] = freq.get(key, 0) + 1
    return freq


def _outcomes_bar_chart(freq: dict, parity: int) -> go.Figure:
    """Build a Plotly bar chart of measurement outcome frequencies."""
    labels = [str(list(k)) for k in freq.keys()]
    counts = list(freq.values())
    colors = [
        "#2A9D8F" if np.prod(list(k)) == parity else "#E76F51"
        for k in freq.keys()
    ]

    fig = go.Figure(go.Bar(
        x=labels,
        y=counts,
        marker_color=colors,
        hovertemplate="Outcome: %{x}<br>Count: %{y}<extra></extra>",
    ))
    fig.update_layout(
        title="Measurement outcome frequencies (500 rounds)",
        xaxis_title="Outcome (a, b, c, …)",
        yaxis_title="Count",
        height=320,
        margin=dict(l=40, r=20, t=40, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    fig.add_annotation(
        text=f"Green = parity {parity:+d} (correct) · Red = wrong parity",
        xref="paper", yref="paper", x=0.5, y=-0.22,
        showarrow=False, font=dict(size=11, color="#666"),
    )
    return fig
