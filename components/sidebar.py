"""
components/sidebar.py
=====================
Global sidebar controls. Returns a params dict consumed by all tab pages.
Called once from app.py; result passed to every render() function.
"""

from __future__ import annotations

import streamlit as st


def render_sidebar() -> dict:
    """
    Render the left sidebar and return all user-controlled parameters.

    Returns
    -------
    dict with keys:
        n_nodes    - int (3–8)
        alpha_i    - int phase index for node A (0 or 1)
        beta_i     - int phase index for node B (0 or 1)
        gamma_i    - int phase index for node C (0 or 1)
        noise      - str ('none', 'depolarise', 'dephase')
        shots      - int (512–4096)
        eve_p      - float (0.0–1.0)
        max_noise  - float (0.0–0.5)
        n_rounds   - int (100–5000)
        distance_km- float (0–60)
    """
    with st.sidebar:
        st.markdown("## QSS Simulator")
        st.caption("Quantum Secret Sharing via GHZ States · IIT Jodhpur")
        st.divider()

        st.markdown("### Protocol settings")
        n_nodes = st.slider(
            "Number of nodes (N)", min_value=3, max_value=8, value=3,
            help="Hilbert space dimension = 2^N. N > 6 uses sparse matrices."
        )

        phase_labels = {0: "0", 1: "π/2"}
        alpha_i = st.selectbox(
            "Node A phase α", options=[0, 1],
            format_func=lambda x: phase_labels[x], index=0
        )
        beta_i = st.selectbox(
            "Node B phase β", options=[0, 1],
            format_func=lambda x: phase_labels[x], index=0
        )
        gamma_i = st.selectbox(
            "Node C phase γ", options=[0, 1],
            format_func=lambda x: phase_labels[x], index=0
        )

        st.divider()
        st.markdown("### Simulation settings")

        noise = st.selectbox(
            "Noise model",
            options=["none", "depolarise", "dephase"],
            index=0,
            help="Noise applied to each qubit during circuit execution."
        )
        shots = st.select_slider(
            "Circuit shots",
            options=[512, 1024, 2048, 4096],
            value=2048,
            help="Number of Qiskit measurement repetitions."
        )
        max_noise = st.slider(
            "Max noise level", min_value=0.0, max_value=0.5,
            value=0.2, step=0.01,
            help="Upper limit for noise sweep plots."
        )

        st.divider()
        st.markdown("### Eavesdropper settings")

        eve_p = st.slider(
            "Eve intercept probability", min_value=0.0, max_value=1.0,
            value=0.0, step=0.01,
            help="Probability Eve intercepts any given qubit."
        )
        n_rounds = st.select_slider(
            "Simulation rounds",
            options=[100, 500, 1000, 2000, 5000],
            value=1000,
        )

        st.divider()
        st.markdown("### Optical experiment")
        distance_km = st.slider(
            "Fibre distance (km)", min_value=0.0, max_value=60.0,
            value=10.0, step=0.5,
        )

        st.divider()
        st.markdown(
            "<small>Built by Sumit Tapas Chongder · IIT Jodhpur · "
            "[GitHub](https://github.com/Sumitchongder/Quantum-Secret-Sharing-Simulator)</small>",
            unsafe_allow_html=True,
        )

    return {
        "n_nodes": n_nodes,
        "alpha_i": alpha_i,
        "beta_i": beta_i,
        "gamma_i": gamma_i,
        "noise": noise,
        "shots": shots,
        "max_noise": max_noise,
        "eve_p": eve_p,
        "n_rounds": n_rounds,
        "distance_km": distance_km,
    }
