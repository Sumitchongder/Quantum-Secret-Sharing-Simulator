"""
components/phase_panel.py
=========================
Phase selector panel with live parity display.
Wraps the alpha/beta/gamma controls and shows the parity result
immediately — no backend call needed (lru_cache on parity_check).
"""

from __future__ import annotations

import streamlit as st


def render_phase_panel(alpha_i: int, beta_i: int, gamma_i: int) -> None:
    """
    Display the phase configuration and live parity check result.

    Parameters
    ----------
    alpha_i, beta_i, gamma_i : int
        Phase indices (0 → 0 rad, 1 → π/2 rad).
    """
    from qss.protocol import parity_check, PHASES
    import numpy as np

    phase_names = {0: "0", 1: "π/2"}
    phase_vals = [PHASES[alpha_i], PHASES[beta_i], PHASES[gamma_i]]
    total = sum(phase_vals)
    parity = parity_check(alpha_i, beta_i, gamma_i)

    st.markdown("#### Phase configuration")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("α (Node A)", phase_names[alpha_i] + " rad")
    col2.metric("β (Node B)", phase_names[beta_i] + " rad")
    col3.metric("γ (Node C)", phase_names[gamma_i] + " rad")
    col4.metric("α+β+γ", f"{total/np.pi:.2g}π rad")

    if parity == 0:
        st.error(
            "🚫 **Discard this round** — α+β+γ = π/2 does not satisfy the "
            "proceed condition {0, π}. Choose different phases."
        )
    elif parity == +1:
        st.success(
            "✅ **Proceed** — α+β+γ = 0 rad → cos(α+β+γ) = **+1** → "
            "even-parity outcomes only."
        )
    else:
        st.success(
            "✅ **Proceed** — α+β+γ = π rad → cos(α+β+γ) = **−1** → "
            "odd-parity outcomes only."
        )


def render_n_phase_panel(phase_indices: tuple, n: int) -> None:
    """
    Display phase configuration for N nodes.

    Parameters
    ----------
    phase_indices : tuple of int
    n : int
    """
    from qss.protocol import parity_check_n, PHASES
    import numpy as np

    parity = parity_check_n(phase_indices)
    total = sum(PHASES[i] for i in phase_indices)
    phase_names = {0: "0", 1: "π/2"}

    phase_str = " + ".join(phase_names[i] for i in phase_indices)
    st.caption(f"Phase sum: {phase_str} = {total/np.pi:.2g}π rad")

    if parity == 0:
        st.error("Discard — phases do not sum to 0 or π.")
    else:
        st.success(f"Proceed — d = cos(Σφ) = {parity:+d}")
