"""
pages/eve_attack.py
===================
Tab 3 — Eavesdropper (Eve) attack simulation and QBER visualisation.

The most visually dramatic tab — QBER spike clearly shows Eve's presence.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st


@st.fragment
def render(params: dict) -> None:
    """Render the Eve Attack tab."""
    eve_p = params["eve_p"]
    n_rounds = params["n_rounds"]

    st.markdown("## Eavesdropper (Eve) Attack")
    st.markdown(
        "Simulate Eve intercepting qubits with a configurable probability. "
        "The Quantum Bit Error Rate (QBER) reveals her presence — "
        "even a small interception probability is detectable."
    )

    # ── Attack result ────────────────────────────────────────────────────────
    from qss.eavesdropper import inject_eve_attack
    result = inject_eve_attack(eve_p, n_rounds=n_rounds, seed=42)

    st.markdown("### Attack result")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Eve intercept prob", f"{eve_p:.2f}")
    col2.metric("QBER", f"{result['qber']:.4f}")
    col3.metric("Errors / rounds", f"{result['n_errors']} / {result['n_rounds']}")
    col4.metric(
        "Status",
        "⚠ Eve detected!" if result["detected"] else "✓ Secure",
        delta=f"Threshold: 5%",
        delta_color="inverse" if result["detected"] else "normal",
    )

    if result["detected"]:
        st.error(
            f"**Eve detected!** QBER = {result['qber']:.2%} exceeds the 5% security threshold. "
            "Abort this key and restart the protocol."
        )
    elif eve_p == 0.0:
        st.success("**No eavesdropper.** Channel is secure. QBER ≈ 0%.")
    else:
        st.warning(
            f"Eve intercepts {eve_p:.0%} of qubits but QBER = {result['qber']:.2%} is "
            "below detection threshold. Increase protocol rounds for better detection."
        )

    # ── QBER vs intercept curve ──────────────────────────────────────────────
    st.divider()
    st.markdown("### QBER vs Eve intercept probability")

    from qss.eavesdropper import qber_vs_intercept_curve
    curve = qber_vs_intercept_curve(n_points=200)

    fig = _qber_curve_figure(curve, eve_p, result["qber"])
    st.plotly_chart(fig, use_container_width=True)

    # ── Detection probability ────────────────────────────────────────────────
    st.divider()
    st.markdown("### Detection probability vs number of rounds")

    from qss.eavesdropper import detection_probability as det_prob
    rounds_range = np.array([10, 50, 100, 200, 500, 1000, 2000, 5000])
    det_probs = np.array([det_prob(eve_p, int(r)) for r in rounds_range])

    fig2 = go.Figure(go.Scatter(
        x=rounds_range,
        y=det_probs,
        mode="lines+markers",
        line=dict(color="#E63946", width=2),
        marker=dict(size=7),
        hovertemplate="Rounds: %{x}<br>P(detect): %{y:.4f}<extra></extra>",
    ))
    fig2.update_layout(
        title=f"P(Eve detected) vs rounds  [intercept prob = {eve_p:.2f}]",
        xaxis_title="Number of protocol rounds",
        yaxis_title="P(Eve detected)",
        yaxis=dict(range=[0, 1.05]),
        height=300,
        margin=dict(l=40, r=20, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Theory ───────────────────────────────────────────────────────────────
    with st.expander("Theory — why is Eve detectable?", expanded=False):
        st.markdown(r"""
**Why Eve cannot hide:**

The GHZ state is highly non-local — any measurement on one qubit
instantaneously affects the correlations across all nodes.

**Eve's strategy (intercept-resend):**
1. Intercepts qubit with probability $p$
2. Measures in a random basis
3. Resends a replacement qubit

**Effect:** When Eve guesses the wrong basis (probability ½),
she introduces an error in the measurement outcomes.

$$\text{QBER} = \frac{p}{2}$$

**Security threshold:** QBER > 5% → abort and restart.

**Detection probability after $n$ rounds:**
$$P(\text{detect}) = 1 - \left(1 - \frac{p}{2}\right)^n$$

At $p = 0.5$ and $n = 100$ rounds: $P(\text{detect}) \approx 1 - 0.75^{100} \approx 1.0$
        """)


def _qber_curve_figure(curve: np.ndarray, current_p: float, current_qber: float) -> go.Figure:
    """Build the QBER vs intercept probability figure."""
    fig = go.Figure()

    # Theoretical curve
    fig.add_trace(go.Scatter(
        x=curve[:, 0],
        y=curve[:, 1],
        mode="lines",
        name="QBER = p/2 (theoretical)",
        line=dict(color="#378ADD", width=2),
    ))

    # Detection threshold line
    fig.add_hline(
        y=0.05,
        line_dash="dash",
        line_color="#E63946",
        annotation_text="5% detection threshold",
        annotation_position="top right",
        annotation_font_size=11,
    )

    # Current Eve position
    fig.add_trace(go.Scatter(
        x=[current_p],
        y=[current_qber],
        mode="markers",
        name=f"Current (p={current_p:.2f}, QBER={current_qber:.3f})",
        marker=dict(
            size=14,
            color="#E63946" if current_qber > 0.05 else "#2A9D8F",
            symbol="circle",
            line=dict(width=2, color="white"),
        ),
    ))

    fig.update_layout(
        title="QBER vs Eve intercept probability",
        xaxis_title="Eve intercept probability p",
        yaxis_title="QBER",
        yaxis=dict(range=[-0.01, 0.55]),
        height=340,
        margin=dict(l=40, r=20, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(x=0.02, y=0.98),
    )
    return fig
