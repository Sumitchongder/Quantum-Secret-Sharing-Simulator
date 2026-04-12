"""
app.py
======
Quantum Secret Sharing Simulator — Streamlit entrypoint.

Must live at repo root. Streamlit Cloud looks for this exact file.

Architecture
------------
- render_sidebar() returns a params dict consumed by all 6 tab pages.
- Each tab page is imported inside its 'with tabs[i]:' block — lazy loading.
- Every render() function is wrapped in @st.fragment — slider changes
  only redraw that one tab's content, not the entire app.
- Heavy quantum objects (GHZ states, AerSimulator) are built once via
  @st.cache_resource and shared across all sessions.

Performance target: < 5 ms for any slider interaction after warm-up.
"""

import streamlit as st

st.set_page_config(
    page_title="QSS Simulator — Quantum Secret Sharing",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/Sumitchongder/Quantum-Secret-Sharing-Simulator",
        "Report a bug": "https://github.com/Sumitchongder/Quantum-Secret-Sharing-Simulator/issues",
        "About": (
            "**Quantum Secret Sharing Simulator** · v1.0.0\n\n"
            "Built by Sumit Tapas Chongder · IIT Jodhpur\n\n"
            "Supervisor: Dr. Atul Kumar\n\n"
            "Stack: Streamlit · QuTiP · Qiskit · PennyLane · Plotly"
        ),
    },
)

# ── Global sidebar (renders on every run) ────────────────────────────────────
from components.sidebar import render_sidebar
params = render_sidebar()

# ── App header ───────────────────────────────────────────────────────────────
st.title("🔐 Quantum Secret Sharing Simulator")
st.markdown(
    "**Interactive simulation of the QSS protocol using GHZ states** · "
    "Adjust phases and noise in the sidebar · All heavy computation is cached for instant response."
)
st.divider()

# ── Six tabs — each module loaded lazily (only when tab is active) ───────────
tabs = st.tabs([
    "📡 Protocol Lab",
    "⚛️ Circuit View",
    "🕵️ Eve Attack",
    "🔢 N-Node Scale",
    "🔬 Optical Replica",
    "📊 Benchmark",
])

with tabs[0]:
    from pages.protocol_lab import render as render_protocol
    render_protocol(params)

with tabs[1]:
    from pages.circuit_view import render as render_circuit
    render_circuit(params)

with tabs[2]:
    from pages.eve_attack import render as render_eve
    render_eve(params)

with tabs[3]:
    from pages.n_node_scale import render as render_nnode
    render_nnode(params)

with tabs[4]:
    from pages.optical_replica import render as render_optical
    render_optical(params)

with tabs[5]:
    from pages.benchmark import render as render_benchmark
    render_benchmark(params)
