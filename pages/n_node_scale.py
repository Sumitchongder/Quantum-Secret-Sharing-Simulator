"""
pages/n_node_scale.py
=====================
Tab 4 — N-node generalisation: fidelity, Hilbert space, classical overhead.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st


@st.fragment
def render(params: dict) -> None:
    """Render the N-Node Scale tab."""
    n = params["n_nodes"]
    max_noise = params["max_noise"]
    noise_model = params["noise"]

    st.markdown("## N-Node Generalisation")
    st.markdown(
        "Scale the QSS protocol from 3 to 8 nodes. "
        "Observe how the Hilbert space grows exponentially and how noise accumulates."
    )

    # ── Memory and dimension warning ─────────────────────────────────────────
    from qss.noise import hilbert_space_dim, memory_mb_estimate
    dim = hilbert_space_dim(n)
    mem_mb = memory_mb_estimate(n)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nodes N", f"{n}")
    col2.metric("Hilbert dim 2ᴺ", f"{dim}")
    col3.metric("Density matrix RAM", f"{mem_mb:.2f} MB")
    col4.metric("Classical msgs (Approach 2)", f"{n - 1}")

    if n > 6:
        st.warning(
            f"⚠ N={n}: Hilbert space dimension = {dim}. "
            "Dense density matrix requires ~{:.0f} MB. Using sparse matrices is recommended.".format(mem_mb)
        )

    # ── GHZ state norm verification ──────────────────────────────────────────
    st.divider()
    st.markdown("### GHZ state properties across N")

    from qss.cache import get_ghz_state

    norms = []
    entropies = []
    ns = list(range(3, min(n + 1, 9)))
    for ni in ns:
        ghz_i = get_ghz_state(ni)
        norms.append(float(ghz_i.norm()))
        try:
            from qss.metrics import von_neumann_entropy, subsystem_entropy
            entropies.append(subsystem_entropy(ghz_i, 0))
        except Exception:
            entropies.append(1.0)

    fig_norm = go.Figure()
    fig_norm.add_trace(go.Scatter(
        x=ns, y=norms, mode="lines+markers",
        name="‖|GHZ⟩‖", line=dict(color="#2A9D8F", width=2),
        marker=dict(size=8),
    ))
    fig_norm.update_layout(
        title="GHZ state norm vs N (should always = 1.0)",
        xaxis_title="Number of nodes N",
        yaxis_title="Norm",
        yaxis=dict(range=[0.99, 1.01]),
        height=280,
        margin=dict(l=40, r=20, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_norm, use_container_width=True)

    # ── Fidelity vs noise ────────────────────────────────────────────────────
    st.divider()
    st.markdown("### Fidelity vs noise level")

    from qss.cache import compute_fidelity_curve

    fig_fid = go.Figure()
    colors = ["#378ADD", "#2A9D8F", "#F4A261", "#E63946", "#A8DADC", "#457B9D"]
    for i, ni in enumerate(range(3, min(n + 1, 9))):
        curve = compute_fidelity_curve(ni, max_noise, noise_model if noise_model != "none" else "depolarise")
        fig_fid.add_trace(go.Scatter(
            x=curve[:, 0],
            y=curve[:, 1],
            mode="lines",
            name=f"N={ni}",
            line=dict(color=colors[i % len(colors)], width=2),
        ))

    fig_fid.add_hline(
        y=0.9, line_dash="dash", line_color="#888",
        annotation_text="F=0.9 threshold", annotation_position="right",
    )
    fig_fid.update_layout(
        title=f"GHZ fidelity under {noise_model if noise_model != 'none' else 'depolarising'} noise",
        xaxis_title="Noise probability p",
        yaxis_title="Fidelity",
        yaxis=dict(range=[0, 1.05]),
        height=340,
        margin=dict(l=40, r=20, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(x=0.75, y=0.98),
    )
    st.plotly_chart(fig_fid, use_container_width=True)

    # ── Classical overhead ───────────────────────────────────────────────────
    st.divider()
    st.markdown("### Classical message overhead vs N")

    all_ns = list(range(3, 9))
    msgs_a1 = [2 * (ni - 1) for ni in all_ns]
    msgs_a2 = [ni - 1 for ni in all_ns]

    fig_msg = go.Figure()
    fig_msg.add_trace(go.Bar(
        name="Approach 1 (teleportation)", x=all_ns, y=msgs_a1,
        marker_color="#E76F51",
    ))
    fig_msg.add_trace(go.Bar(
        name="Approach 2 (Bell pairs)", x=all_ns, y=msgs_a2,
        marker_color="#2A9D8F",
    ))
    fig_msg.update_layout(
        title="Classical messages required vs number of nodes",
        xaxis_title="Number of nodes N",
        yaxis_title="Classical messages",
        barmode="group",
        height=300,
        margin=dict(l=40, r=20, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_msg, use_container_width=True)

    with st.expander("N-node protocol details", expanded=False):
        st.markdown(r"""
For **N nodes**, the GHZ state generalises to:
$$|GHZ_N\rangle = \frac{1}{\sqrt{2}}\bigl(|00\cdots0\rangle + |11\cdots1\rangle\bigr)$$

The parity condition generalises to:
$$\sum_{i=1}^{N} \phi_i \in \{0, \pi\}$$

The measurement product satisfies:
$$\prod_{i=1}^{N} a_i = \cos\!\left(\sum_i \phi_i\right) = \pm 1$$

**Fidelity under depolarising noise:**
$$F(p) = (1-p)^N + \frac{p^N}{2^N}$$

This decays exponentially with N — showing why noise is the main practical challenge.
        """)
