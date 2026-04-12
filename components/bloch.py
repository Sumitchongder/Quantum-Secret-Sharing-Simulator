"""
components/bloch.py
===================
3D Bloch sphere visualisation using Plotly.
Renders client-side — no server re-render on interaction.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go


def bloch_sphere_figure(
    vectors: list[tuple[float, float, float]] | None = None,
    labels: list[str] | None = None,
    title: str = "Bloch sphere",
) -> go.Figure:
    """
    Build a 3D Bloch sphere Plotly figure.

    Parameters
    ----------
    vectors : list of (x, y, z) tuples
        State vectors to plot on the sphere, each normalised to unit sphere.
    labels : list of str
        Labels for each vector.
    title : str

    Returns
    -------
    plotly.graph_objects.Figure
    """
    fig = go.Figure()

    # Sphere surface
    u = np.linspace(0, 2 * np.pi, 60)
    v = np.linspace(0, np.pi, 40)
    xs = np.outer(np.cos(u), np.sin(v))
    ys = np.outer(np.sin(u), np.sin(v))
    zs = np.outer(np.ones(60), np.cos(v))
    fig.add_trace(go.Surface(
        x=xs, y=ys, z=zs,
        opacity=0.08,
        colorscale=[[0, "#4A90D9"], [1, "#4A90D9"]],
        showscale=False,
        hoverinfo="skip",
    ))

    # Axes
    for axis, label, color in [
        ([0, 0], [0, 0], [-1.3, 1.3], "z", "#555"),
        ([-1.3, 1.3], [0, 0], [0, 0], "x", "#555"),
        ([0, 0], [-1.3, 1.3], [0, 0], "y", "#555"),
    ]:
        pass  # replaced below with proper traces

    for axis_vec, axis_name, col in [
        (([0, 0], [0, 0], [-1.3, 1.3]), "|0⟩/|1⟩", "#777"),
        (([-1.3, 1.3], [0, 0], [0, 0]), "|+⟩/|-⟩", "#777"),
        (([0, 0], [-1.3, 1.3], [0, 0]), "|i⟩/|-i⟩", "#777"),
    ]:
        fig.add_trace(go.Scatter3d(
            x=axis_vec[0], y=axis_vec[1], z=axis_vec[2],
            mode="lines",
            line=dict(color=col, width=2),
            showlegend=False,
            hoverinfo="skip",
        ))

    # Axis labels
    for x, y, z, text in [
        (0, 0, 1.45, "|0⟩"), (0, 0, -1.45, "|1⟩"),
        (1.45, 0, 0, "|+⟩"), (-1.45, 0, 0, "|-⟩"),
        (0, 1.45, 0, "|i⟩"), (0, -1.45, 0, "|-i⟩"),
    ]:
        fig.add_trace(go.Scatter3d(
            x=[x], y=[y], z=[z],
            mode="text",
            text=[text],
            textfont=dict(size=12, color="#333"),
            showlegend=False,
            hoverinfo="skip",
        ))

    # State vectors
    if vectors:
        colors = ["#E63946", "#2A9D8F", "#F4A261", "#457B9D", "#A8DADC"]
        for idx, (vx, vy, vz) in enumerate(vectors):
            label = labels[idx] if labels else f"State {idx + 1}"
            color = colors[idx % len(colors)]
            # Arrow: line from origin to vector tip
            fig.add_trace(go.Scatter3d(
                x=[0, vx], y=[0, vy], z=[0, vz],
                mode="lines+markers",
                line=dict(color=color, width=5),
                marker=dict(size=[0, 8], color=color),
                name=label,
                hovertemplate=f"{label}<br>x={vx:.3f}<br>y={vy:.3f}<br>z={vz:.3f}",
            ))

    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        scene=dict(
            xaxis=dict(showticklabels=False, title="", showgrid=False, zeroline=False),
            yaxis=dict(showticklabels=False, title="", showgrid=False, zeroline=False),
            zaxis=dict(showticklabels=False, title="", showgrid=False, zeroline=False),
            aspectmode="cube",
            camera=dict(eye=dict(x=1.4, y=1.4, z=0.8)),
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_bloch_sphere(state=None, title: str = "Qubit state on Bloch sphere") -> None:
    """
    Render a Bloch sphere in Streamlit for a single-qubit state.

    Parameters
    ----------
    state : qutip.Qobj or None
        Single-qubit ket/density matrix. If None, renders empty sphere.
    title : str
    """
    import streamlit as st
    from qss.metrics import bloch_vector

    vectors = []
    labels = []
    if state is not None:
        try:
            x, y, z = bloch_vector(state)
            vectors = [(x, y, z)]
            labels = ["State |ψ⟩"]
        except Exception:
            st.warning("Could not compute Bloch vector for this state.")

    fig = bloch_sphere_figure(vectors, labels, title)
    st.plotly_chart(fig, use_container_width=True)
