"""
qss/tittel2000.py
=================
Replication of the Tittel et al. (2000) optical QSS experiment.

Reference
---------
W. Tittel, H. Zbinden, N. Gisin,
"Experimental demonstration of quantum secret sharing",
Physical Review A 63, 042301 (2001).
University of Geneva.

Experiment details
------------------
- Used energy-time entanglement (pseudo-GHZ state)
- Only two entangled photons exist at any one time
- Phase shifters apply α, β, γ at each node
- Detection probability: P_ijk = (1/8)[1 + i·j·k·cos(α+β+γ)]
- Measured generation rate: ~15 Hz
- Estimated practical range: 30–40 km
  (fibre loss 0.35 dB/km, phase shifter insertion loss 3 dB)
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Core probability formula
# ---------------------------------------------------------------------------

def detection_probability(
    i: int,
    j: int,
    k: int,
    alpha: float,
    beta: float,
    gamma: float,
) -> float:
    """
    Compute P_ijk = (1/8)[1 + i·j·k·cos(α + β + γ)].

    Parameters
    ----------
    i, j, k : int
        Detector outcome labels, each ∈ {+1, -1}.
    alpha, beta, gamma : float
        Phase shifter settings in radians.

    Returns
    -------
    float
        Detection probability, always in [0, 1/4].

    Examples
    --------
    >>> abs(detection_probability(1, 1, 1, 0, 0, 0) - 0.25) < 1e-10
    True
    >>> abs(detection_probability(-1, 1, 1, 0, 0, 0)) < 1e-10
    True
    """
    return (1.0 / 8.0) * (1.0 + i * j * k * np.cos(alpha + beta + gamma))


def all_outcome_probabilities(
    alpha: float,
    beta: float,
    gamma: float,
) -> dict:
    """
    Compute all 8 detection outcome probabilities for given phases.

    Parameters
    ----------
    alpha, beta, gamma : float
        Phase settings in radians.

    Returns
    -------
    dict
        Keys are '(+1,+1,+1)' etc., values are probabilities.
        Probabilities always sum to 1.0.
    """
    outcomes: dict = {}
    for i in [+1, -1]:
        for j in [+1, -1]:
            for k in [+1, -1]:
                label = f"({i:+d},{j:+d},{k:+d})"
                outcomes[label] = detection_probability(i, j, k, alpha, beta, gamma)
    return outcomes


def parity_groups(alpha: float, beta: float, gamma: float) -> dict:
    """
    Group outcomes into even-parity and odd-parity sets.

    When α+β+γ = 0: only even-parity outcomes (+1,+1,+1), (+1,-1,-1), etc.
    When α+β+γ = π: only odd-parity outcomes.

    Returns
    -------
    dict with keys 'even' and 'odd', each a dict of {label: probability}.
    """
    all_probs = all_outcome_probabilities(alpha, beta, gamma)
    even: dict = {}
    odd: dict = {}
    for label, prob in all_probs.items():
        vals = [int(x) for x in label.strip("()").split(",")]
        product = vals[0] * vals[1] * vals[2]
        if product == 1:
            even[label] = prob
        else:
            odd[label] = prob
    return {"even": even, "odd": odd}


# ---------------------------------------------------------------------------
# Range and rate estimation
# ---------------------------------------------------------------------------

def generation_rate_estimate(
    distance_km: float,
    fiber_loss_db_km: float = 0.35,
    phase_shifter_loss_db: float = 3.0,
    base_rate_hz: float = 15.0,
) -> float:
    """
    Estimate secret bit generation rate based on Tittel-2000 parameters.

    Baseline rate: 15 Hz at lab scale (effectively zero distance).
    Rate scales with total channel loss in dB.

    Parameters
    ----------
    distance_km : float
        One-way fibre distance in km.
    fiber_loss_db_km : float
        Fibre attenuation coefficient (default: 0.35 dB/km).
    phase_shifter_loss_db : float
        Insertion loss of phase shifters (default: 3 dB).
    base_rate_hz : float
        Laboratory generation rate (default: 15 Hz).

    Returns
    -------
    float
        Estimated generation rate in Hz.

    Examples
    --------
    >>> abs(generation_rate_estimate(0.0) - 15.0) < 0.01
    True
    """
    total_loss_db = fiber_loss_db_km * distance_km + phase_shifter_loss_db
    loss_factor = 10.0 ** (-total_loss_db / 10.0)
    return base_rate_hz * loss_factor


def max_range_km(
    min_rate_hz: float = 0.1,
    fiber_loss_db_km: float = 0.35,
    phase_shifter_loss_db: float = 3.0,
    base_rate_hz: float = 15.0,
) -> float:
    """
    Estimate maximum usable range given a minimum acceptable generation rate.

    Parameters
    ----------
    min_rate_hz : float
        Minimum acceptable rate in Hz.
    fiber_loss_db_km, phase_shifter_loss_db, base_rate_hz : float

    Returns
    -------
    float
        Maximum range in km.
    """
    # Solve: base_rate * 10^(-(loss_km*d + ps_loss)/10) = min_rate
    # d = (10*log10(base_rate/min_rate) - ps_loss) / loss_km
    if min_rate_hz <= 0 or base_rate_hz <= 0:
        return 0.0
    numerator = 10.0 * np.log10(base_rate_hz / min_rate_hz) - phase_shifter_loss_db
    if numerator <= 0:
        return 0.0
    return numerator / fiber_loss_db_km


def rate_vs_distance(
    max_km: float = 60.0,
    n_points: int = 200,
) -> np.ndarray:
    """
    Vectorised generation rate vs distance curve.

    Parameters
    ----------
    max_km : float
    n_points : int

    Returns
    -------
    np.ndarray
        Shape (n_points, 2): columns [distance_km, rate_hz].
    """
    distances = np.linspace(0.0, max_km, n_points)
    loss_db = 0.35 * distances + 3.0
    loss_factor = 10.0 ** (-loss_db / 10.0)
    rates = 15.0 * loss_factor
    return np.column_stack([distances, rates])
