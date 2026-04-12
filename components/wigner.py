"""
components/wigner.py
====================
Wigner function heatmap using QuTiP + Plotly.
Rendered client-side — no server re-render on zoom/pan.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st


def wigner_figure(
    wigner_grid: np.ndarray,
    xvec: np.ndarray,
    pvec: np.ndarray,
    title: str = "Wigner function W(x, p)",
) -> go.Figure:
    """
    Build a Plotly heatmap of the Wigner function.

    Parameters
    ----------
    wigner_grid : np.ndarray
        2D Wigner values, shape (len(pvec), len(xvec)).
    xvec, pvec : np.ndarray
        Phase space axes.
    title : str

    Returns
    -------
    plotly.graph_objects.Figure
    """
    fig = go.Figure(data=go.Heatmap(
        x=xvec,
        y=pvec,
        z=wigner_grid,
        colorscale="RdBu",
        zmid=0,
        colorbar=dict(title="W(x,p)", thickness=12),
        hovertemplate="x=%{x:.2f}<br>p=%{y:.2f}<br>W=%{z:.4f}<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        xaxis=dict(title="x (quadrature)"),
        yaxis=dict(title="p (momentum)"),
        height=380,
        margin=dict(l=50, r=20, t=40, b=50),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render_wigner(state=None, grid_size: int = 80, xmax: float = 4.0) -> None:
    """
    Compute and render the Wigner function for a quantum state.

    Parameters
    ----------
    state : qutip.Qobj or None
    grid_size : int
        Resolution of the phase-space grid (grid_size × grid_size).
    xmax : float
        Phase space extent [-xmax, xmax].
    """
    if state is None:
        st.info("No state available for Wigner function.")
        return

    from qss.cache import compute_wigner

    xvec = np.linspace(-xmax, xmax, grid_size)
    pvec = np.linspace(-xmax, xmax, grid_size)
    xvec_t = tuple(xvec.tolist())
    pvec_t = tuple(pvec.tolist())

    with st.spinner("Computing Wigner function…"):
        W = compute_wigner(state, xvec_t, pvec_t)

    fig = wigner_figure(W, xvec, pvec)
    st.plotly_chart(fig, use_container_width=True)
