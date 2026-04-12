"""
pages/circuit_view.py
=====================
Tab 2 — Qiskit circuit diagram + measurement counts + noise toggle.

Performance: run_qiskit_circuit is cache_data — ~200 ms first run, < 2 ms cached.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st


@st.fragment
def render(params: dict) -> None:
    """Render the Circuit View tab."""
    n = params["n_nodes"]
    alpha_i = params["alpha_i"]
    beta_i = params["beta_i"]
    gamma_i = params["gamma_i"]
    noise = params["noise"]
    shots = params["shots"]

    st.markdown("## Circuit View")
    st.markdown(
        "Qiskit implementation of the QSS protocol circuit. "
        "Toggle noise models to see how decoherence affects measurement statistics."
    )

    # ── Circuit diagram ──────────────────────────────────────────────────────
    st.markdown("### Circuit diagram")
    col_info, col_stats = st.columns([2, 1])

    with col_info:
        from components.circuit_drawer import render_circuit_diagram, render_circuit_text
        try:
            render_circuit_diagram(n, alpha_i, beta_i, gamma_i)
        except Exception:
            render_circuit_text(n, alpha_i, beta_i, gamma_i)

    with col_stats:
        st.markdown("**Circuit structure**")
        st.markdown(f"- Qubits: **{n}**")
        st.markdown(f"- Gates: H + {n-1}× CX + P(φ) × {n}")
        st.markdown(f"- Noise model: **{noise}**")
        st.markdown(f"- Shots: **{shots}**")
        st.markdown(f"- Phase α: **{'π/2' if alpha_i else '0'}**")
        st.markdown(f"- Phase β: **{'π/2' if beta_i else '0'}**")
        st.markdown(f"- Phase γ: **{'π/2' if gamma_i else '0'}**")

    # ── Measurement counts ───────────────────────────────────────────────────
    st.divider()
    st.markdown("### Measurement counts")

    with st.spinner("Running Qiskit simulation…"):
        from qss.cache import run_qiskit_circuit
        try:
            counts = run_qiskit_circuit(n, alpha_i, beta_i, gamma_i, noise, shots)
            fig = _counts_bar_chart(counts, shots)
            st.plotly_chart(fig, use_container_width=True)

            # QBER from counts
            from qss.metrics import qber_from_counts
            qber = qber_from_counts(counts)
            col1, col2, col3 = st.columns(3)
            col1.metric("QBER (from counts)", f"{qber:.4f}")
            col2.metric("Total shots", f"{shots}")
            col3.metric(
                "Security status",
                "⚠ Eve?" if qber > 0.05 else "✓ Secure",
            )
        except Exception as exc:
            st.error(f"Qiskit simulation failed: {exc}")
            st.info(
                "Make sure `qiskit` and `qiskit-aer` are installed. "
                "Check `requirements.txt`."
            )

    # ── Noise explanation ────────────────────────────────────────────────────
    with st.expander("About noise models", expanded=False):
        st.markdown("""
**None** — ideal simulation, no decoherence.

**Depolarise** — each qubit randomly flips to a completely mixed state with
probability `p`. Models general decoherence. Applied to H, P, and CX gates.

**Dephase** — phase-damping channel. Preserves populations |0⟩ and |1⟩
but destroys off-diagonal coherences. Models pure dephasing (T₂ processes).

Higher noise → counts spread more uniformly → QBER increases.
        """)


def _counts_bar_chart(counts: dict, shots: int) -> go.Figure:
    """Build a Plotly bar chart of Qiskit measurement counts."""
    sorted_counts = dict(sorted(counts.items(), key=lambda x: -x[1]))
    top_n = dict(list(sorted_counts.items())[:20])   # top 20 outcomes

    labels = list(top_n.keys())
    values = list(top_n.values())
    probabilities = [v / shots for v in values]

    fig = go.Figure(go.Bar(
        x=labels,
        y=probabilities,
        marker_color="#378ADD",
        hovertemplate="Bitstring: %{x}<br>Probability: %{y:.4f}<extra></extra>",
    ))
    fig.update_layout(
        title=f"Measurement outcome probabilities (top {len(top_n)} of {len(counts)} bitstrings)",
        xaxis_title="Bitstring",
        yaxis_title="Probability",
        height=340,
        margin=dict(l=40, r=20, t=40, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig
