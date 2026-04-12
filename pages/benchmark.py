"""
pages/benchmark.py
==================
Tab 6 — Approach 1 vs Approach 2 side-by-side benchmark.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st


@st.fragment
def render(params: dict) -> None:
    """Render the Benchmark tab."""
    n = params["n_nodes"]

    st.markdown("## Approach Benchmark")
    st.markdown(
        "Head-to-head comparison of the two GHZ state distribution approaches "
        "across qubit count, classical overhead, fidelity, and practical range."
    )

    from qss.ghz import compare_approaches
    data = compare_approaches(n)
    a1 = data["approach1"]
    a2 = data["approach2"]

    # ── Summary table ────────────────────────────────────────────────────────
    st.markdown("### Side-by-side comparison")

    col1, col2, col3 = st.columns([1, 2, 2])
    with col1:
        st.markdown("**Metric**")
        for metric in [
            "Qubit count",
            "Classical msgs",
            "Fidelity estimate",
            "Teleportation",
            "Lab demonstrated",
            "Practical range",
            "Key advantage",
        ]:
            st.markdown(metric)

    with col2:
        st.markdown("**Approach 1 — Teleportation**")
        st.markdown(f"{a1['qubit_count']}")
        st.markdown(f"{a1['msg_count']}")
        st.markdown(f"{a1['fidelity_estimate']:.4f}")
        st.markdown("✓ Required")
        st.markdown("✗ Not yet")
        st.markdown("~20–30 km")
        st.markdown("Works over existing Bell-pair links")

    with col3:
        st.markdown("**Approach 2 — Bell pairs + local ops**")
        st.markdown(f"{a2['qubit_count']} ← fewer")
        st.markdown(f"{a2['msg_count']} ← fewer")
        st.markdown(f"{a2['fidelity_estimate']:.4f} ← higher")
        st.markdown("✗ Not needed")
        st.markdown("✓ 2021 lab demo")
        st.markdown("30–40 km")
        st.markdown("Simpler, higher fidelity, lab-proven")

    # ── Qubit count bar chart ─────────────────────────────────────────────────
    st.divider()
    st.markdown("### Qubit count across N nodes")

    ns = list(range(3, 9))
    q1_counts = [compare_approaches(ni)["approach1"]["qubit_count"] for ni in ns]
    q2_counts = [compare_approaches(ni)["approach2"]["qubit_count"] for ni in ns]

    fig_q = go.Figure()
    fig_q.add_trace(go.Bar(
        name="Approach 1 (teleportation)", x=ns, y=q1_counts,
        marker_color="#E76F51",
        hovertemplate="N=%{x}<br>Qubits=%{y}<extra></extra>",
    ))
    fig_q.add_trace(go.Bar(
        name="Approach 2 (Bell pairs)", x=ns, y=q2_counts,
        marker_color="#2A9D8F",
        hovertemplate="N=%{x}<br>Qubits=%{y}<extra></extra>",
    ))
    fig_q.update_layout(
        title="Qubit count vs number of nodes",
        xaxis_title="Number of nodes N",
        yaxis_title="Total qubits required",
        barmode="group",
        height=300,
        margin=dict(l=40, r=20, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_q, use_container_width=True)

    # ── Fidelity comparison across N ─────────────────────────────────────────
    st.divider()
    st.markdown("### Fidelity estimate across N nodes")

    f1_vals = [compare_approaches(ni)["approach1"]["fidelity_estimate"] for ni in ns]
    f2_vals = [compare_approaches(ni)["approach2"]["fidelity_estimate"] for ni in ns]

    fig_f = go.Figure()
    fig_f.add_trace(go.Scatter(
        x=ns, y=f1_vals, mode="lines+markers",
        name="Approach 1", line=dict(color="#E76F51", width=2),
        marker=dict(size=8),
    ))
    fig_f.add_trace(go.Scatter(
        x=ns, y=f2_vals, mode="lines+markers",
        name="Approach 2", line=dict(color="#2A9D8F", width=2),
        marker=dict(size=8),
    ))
    fig_f.add_hline(y=0.9, line_dash="dash", line_color="#888",
                    annotation_text="F=0.9 threshold")
    fig_f.update_layout(
        title="Fidelity estimate vs N (simple gate-error model)",
        xaxis_title="Number of nodes N",
        yaxis_title="Fidelity",
        yaxis=dict(range=[0.8, 1.01]),
        height=300,
        margin=dict(l=40, r=20, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_f, use_container_width=True)

    # ── Radar chart ──────────────────────────────────────────────────────────
    st.divider()
    st.markdown(f"### Radar chart — Approach 1 vs 2  (N={n})")

    categories = ["Low qubit count", "Low msg overhead",
                  "High fidelity", "No teleportation", "Lab demonstrated"]

    # Normalise scores to 0–1 for radar
    max_q = max(a1["qubit_count"], a2["qubit_count"])
    max_m = max(a1["msg_count"], a2["msg_count"])

    scores_a1 = [
        1 - a1["qubit_count"] / max_q,
        1 - a1["msg_count"] / max_m,
        a1["fidelity_estimate"],
        0.0 if a1["teleportation_needed"] else 1.0,
        1.0 if a1["lab_demonstrated"] else 0.0,
    ]
    scores_a2 = [
        1 - a2["qubit_count"] / max_q,
        1 - a2["msg_count"] / max_m,
        a2["fidelity_estimate"],
        0.0 if a2["teleportation_needed"] else 1.0,
        1.0 if a2["lab_demonstrated"] else 0.0,
    ]

    fig_r = go.Figure()
    for name, scores, color in [
        ("Approach 1", scores_a1, "#E76F51"),
        ("Approach 2", scores_a2, "#2A9D8F"),
    ]:
        fig_r.add_trace(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name=name,
            line=dict(color=color, width=2),
            opacity=0.6,
        ))
    fig_r.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title=f"Approach comparison radar (N={n})",
        height=380,
        margin=dict(l=60, r=60, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_r, use_container_width=True)

    st.success(
        "**Conclusion:** Approach 2 wins on every metric for N ≥ 3 — "
        "fewer qubits, fewer messages, higher fidelity, no teleportation, and lab-demonstrated in 2021."
    )
