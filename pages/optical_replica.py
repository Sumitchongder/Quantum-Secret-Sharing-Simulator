"""
pages/optical_replica.py
========================
Tab 5 — Replication of the Tittel et al. (2000) optical QSS experiment.

Reference: W. Tittel, H. Zbinden, N. Gisin,
"Experimental demonstration of quantum secret sharing",
Physical Review A 63, 042301 (2001).
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st


@st.fragment
def render(params: dict) -> None:
    """Render the Optical Replica tab."""
    alpha_i = params["alpha_i"]
    beta_i = params["beta_i"]
    gamma_i = params["gamma_i"]
    distance_km = params["distance_km"]

    # Convert phase indices to radians for continuous sliders
    from qss.protocol import PHASES
    alpha_rad = PHASES[alpha_i]
    beta_rad = PHASES[beta_i]
    gamma_rad = PHASES[gamma_i]

    st.markdown("## Optical Experiment Replica")
    st.markdown(
        "Replication of the **Tittel et al. (2000)** photonic QSS experiment "
        "at the University of Geneva. Uses energy-time entanglement "
        "(pseudo-GHZ state — only two entangled photons at one time)."
    )

    # ── Continuous phase sliders for this tab ────────────────────────────────
    st.markdown("### Phase settings (continuous)")
    col1, col2, col3 = st.columns(3)
    with col1:
        alpha_cont = st.slider("α (rad)", 0.0, float(np.pi), float(alpha_rad), step=0.01, key="opt_alpha")
    with col2:
        beta_cont = st.slider("β (rad)", 0.0, float(np.pi), float(beta_rad), step=0.01, key="opt_beta")
    with col3:
        gamma_cont = st.slider("γ (rad)", 0.0, float(np.pi), float(gamma_rad), step=0.01, key="opt_gamma")

    total_phase = alpha_cont + beta_cont + gamma_cont
    cos_val = float(np.cos(total_phase))

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("α+β+γ (rad)", f"{total_phase:.3f}")
    col_m2.metric("cos(α+β+γ)", f"{cos_val:.4f}")
    col_m3.metric("Phase condition", "✓ Even" if abs(cos_val - 1) < 0.01
                  else ("✓ Odd" if abs(cos_val + 1) < 0.01 else "— Intermediate"))

    # ── Detection probabilities ──────────────────────────────────────────────
    st.divider()
    st.markdown("### Detection outcome probabilities")
    st.markdown(r"Formula: $P_{ijk} = \frac{1}{8}\left[1 + ijk\cos(\alpha+\beta+\gamma)\right]$")

    from qss.cache import compute_optical_probabilities
    probs = compute_optical_probabilities(alpha_cont, beta_cont, gamma_cont)

    from qss.tittel2000 import parity_groups
    groups = parity_groups(alpha_cont, beta_cont, gamma_cont)

    labels = list(probs.keys())
    values = list(probs.values())
    colors = [
        "#2A9D8F" if label in groups["even"] else "#E76F51"
        for label in labels
    ]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        hovertemplate="Outcome %{x}<br>P = %{y:.4f}<extra></extra>",
    ))
    fig.update_layout(
        title="P_ijk for all 8 detector outcomes  [green = even parity, orange = odd parity]",
        xaxis_title="Outcome (i, j, k)",
        yaxis_title="Probability",
        yaxis=dict(range=[0, 0.27]),
        height=320,
        margin=dict(l=40, r=20, t=40, b=70),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.add_hline(y=0.125, line_dash="dot", line_color="#aaa",
                  annotation_text="Uniform (no correlation)", annotation_position="right")
    st.plotly_chart(fig, use_container_width=True)

    prob_sum = sum(values)
    st.caption(f"Sum of all probabilities = {prob_sum:.6f} (should be exactly 1.0)")

    # ── Generation rate estimator ────────────────────────────────────────────
    st.divider()
    st.markdown("### Secret bit generation rate estimator")

    from qss.tittel2000 import generation_rate_estimate, rate_vs_distance, max_range_km

    rate = generation_rate_estimate(distance_km)
    max_range = max_range_km()

    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("Distance", f"{distance_km:.1f} km")
    col_r2.metric("Generation rate", f"{rate:.3f} Hz")
    col_r3.metric("Max usable range", f"{max_range:.1f} km")

    # Rate vs distance curve
    curve = rate_vs_distance(max_km=60.0, n_points=300)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=curve[:, 0], y=curve[:, 1],
        mode="lines",
        line=dict(color="#534AB7", width=2),
        name="Rate vs distance",
        hovertemplate="Distance: %{x:.1f} km<br>Rate: %{y:.3f} Hz<extra></extra>",
    ))
    fig2.add_trace(go.Scatter(
        x=[distance_km], y=[rate],
        mode="markers",
        marker=dict(size=12, color="#E63946", symbol="circle",
                    line=dict(width=2, color="white")),
        name=f"Current ({distance_km:.1f} km, {rate:.3f} Hz)",
    ))
    fig2.add_hline(y=0.1, line_dash="dash", line_color="#888",
                   annotation_text="Min usable rate (0.1 Hz)",
                   annotation_position="right")
    fig2.update_layout(
        title="Secret bit generation rate vs fibre distance",
        xaxis_title="Distance (km)",
        yaxis_title="Generation rate (Hz)",
        height=320,
        margin=dict(l=40, r=20, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # ── Experiment summary ───────────────────────────────────────────────────
    with st.expander("Experiment details — Tittel et al. 2000", expanded=False):
        st.markdown("""
| Parameter | Value |
|-----------|-------|
| Entanglement type | Energy-time (pseudo-GHZ) |
| Photons at one time | 2 (not 3) |
| Phase shifters | 3 (one per node) |
| Generation rate | ~15 Hz (lab) |
| Fibre loss | 0.35 dB/km |
| Phase shifter loss | 3 dB |
| Estimated range | 30–40 km |
| Reference | Phys. Rev. A 63, 042301 (2001) |

**Pseudo-GHZ state:** Although only two photons are entangled at any time,
the detection probability statistics are identical to a true 3-photon GHZ state.
This was verified experimentally and is the key result of the paper.
        """)
