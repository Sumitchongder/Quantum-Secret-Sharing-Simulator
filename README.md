# 🔐 Quantum Secret Sharing Simulator

[![CI](https://github.com/Sumitchongder/Quantum-Secret-Sharing-Simulator/actions/workflows/ci.yml/badge.svg)](https://github.com/Sumitchongder/Quantum-Secret-Sharing-Simulator/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sumitchongder-quantum-secret-sharing-simulator.streamlit.app)

> **Interactive simulation of the Quantum Secret Sharing (QSS) protocol using GHZ states** — built with Streamlit, QuTiP, Qiskit, and Plotly. Deployed live. Cite-able via Zenodo DOI.

---

## 🚀 Live Demo

**[sumitchongder-quantum-secret-sharing-simulator.streamlit.app](https://sumitchongder-quantum-secret-sharing-simulator.streamlit.app)**

---

## 📖 What This Is

This simulator replicates the full QSS protocol from the seminal paper by Hillery, Bužek, and Berthiaume (1999), extended with the Tittel et al. (2000) optical experiment. It is **protocol-specific** — not a general gate simulator — making it publishable-level work rather than a demo.

### Why it stands out vs CDAC QSim

| Feature | CDAC QSim | This Simulator |
|---------|-----------|---------------|
| Protocol specificity | General gates | Full QSS end-to-end |
| Eavesdropper simulation | ✗ | ✓ QBER detection |
| Optical experiment replica | ✗ | ✓ Tittel 2000 |
| N-node generalisation | ✗ | ✓ Up to 8 nodes |
| Approach comparison | ✗ | ✓ Approach 1 vs 2 |
| Noise models | Basic | Depolarise + Dephase |
| Live deployment | ✗ | ✓ Streamlit Cloud |
| Zenodo DOI | ✗ | ✓ Citable |

---

## 🗂️ Repository Structure

```
Quantum-Secret-Sharing-Simulator/
├── app.py                        # Streamlit entrypoint
├── requirements.txt              # Pinned dependencies
├── pyproject.toml                # Build + ruff config
├── README.md
├── CITATION.cff                  # Zenodo DOI
├── LICENSE                       # MIT
│
├── qss/                          # Core simulation package (no Streamlit)
│   ├── __init__.py
│   ├── protocol.py               # QSS round orchestrator
│   ├── ghz.py                    # GHZ state, both approaches
│   ├── cache.py                  # @st.cache_resource / cache_data
│   ├── circuit.py                # Qiskit circuit builder + runner
│   ├── noise.py                  # Depolarise / dephase channels
│   ├── eavesdropper.py           # Eve attack, QBER calculation
│   ├── metrics.py                # Fidelity, purity, entropy
│   └── tittel2000.py             # Optical experiment replica
│
├── pages/                        # One file per Streamlit tab
│   ├── protocol_lab.py           # Tab 1: 3-node walkthrough
│   ├── circuit_view.py           # Tab 2: Qiskit circuit + noise
│   ├── eve_attack.py             # Tab 3: Eve + QBER live plot
│   ├── n_node_scale.py           # Tab 4: N-node generalisation
│   ├── optical_replica.py        # Tab 5: Tittel-2000 photons
│   └── benchmark.py              # Tab 6: Approach 1 vs 2
│
├── components/                   # Reusable UI widgets
│   ├── sidebar.py
│   ├── bloch.py
│   ├── wigner.py
│   ├── metrics_bar.py
│   ├── phase_panel.py
│   └── circuit_drawer.py
│
├── tests/                        # pytest suite
│   ├── conftest.py
│   ├── test_ghz.py
│   ├── test_protocol.py
│   ├── test_eavesdropper.py
│   ├── test_noise.py
│   ├── test_tittel2000.py
│   └── test_metrics.py
│
├── .github/workflows/
│   ├── ci.yml                    # pytest + ruff on every push
│   └── release.yml               # tag → Zenodo DOI
│
├── notebooks/
│   └── walkthrough.ipynb         # Academic narrative notebook
│
└── docs/
    ├── theory.md                 # Full theory reference
    └── api_reference.md          # Public API docs
```

---

## ⚡ Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/Sumitchongder/Quantum-Secret-Sharing-Simulator.git
cd Quantum-Secret-Sharing-Simulator

# 2. Install
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## 🧮 Theory

### GHZ State

$$|GHZ_N\rangle = \frac{1}{\sqrt{2}}\bigl(|00\cdots0\rangle + |11\cdots1\rangle\bigr)$$

### Protocol (3-node case)

1. Nodes A, B, C share a GHZ state
2. Each picks phase $\phi_i \in \{0, \pi/2\}$
3. Each applies $P(\phi)|1\rangle = e^{i\phi}|1\rangle$
4. New state: $|\psi\rangle = \frac{1}{\sqrt{2}}\bigl(|000\rangle + e^{i(\alpha+\beta+\gamma)}|111\rangle\bigr)$
5. All measure in Pauli-X basis → outcomes $a, b, c \in \{+1, -1\}$
6. Proceed only if $\alpha + \beta + \gamma \in \{0, \pi\}$
7. Product: $a \cdot b \cdot c = \cos(\alpha+\beta+\gamma) = \pm 1$
8. A and B exchange outcomes → infer $c = a \cdot b \cdot d$ where $d = \cos(\alpha+\beta+\gamma)$

### Security

Local outcomes are uniformly random → Eve sees only noise.  
Intercept-resend attack: QBER $= p_{\text{intercept}}/2$.  
Detection threshold: QBER $> 5\%$.

### Tittel et al. (2000) Detection Formula

$$P_{ijk} = \frac{1}{8}\bigl[1 + ijk\cos(\alpha+\beta+\gamma)\bigr], \quad i,j,k \in \{+1,-1\}$$

---

## 📊 Dashboard Tabs

| Tab | What it shows | Key interaction |
|-----|--------------|-----------------|
| 📡 Protocol Lab | Step-by-step 3-node QSS | Phase sliders → live parity + secret |
| ⚛️ Circuit View | Qiskit circuit diagram + counts | Noise toggle → QBER from counts |
| 🕵️ Eve Attack | QBER vs intercept probability | Eve probability slider |
| 🔢 N-Node Scale | Fidelity vs noise for N=3–8 | N slider → Hilbert space growth |
| 🔬 Optical Replica | Tittel-2000 P_ijk probabilities | Continuous phase sliders |
| 📊 Benchmark | Approach 1 vs 2 radar + bars | N slider → all metrics update |

---

## 🏎️ Performance

All interactions after warm-up are < 5 ms:

| Operation | Cold | Warm |
|-----------|------|------|
| GHZ state build | ~120 ms | **0 ms** (cache_resource) |
| Phase slider | — | **< 5 ms** (lru_cache) |
| Wigner function | ~300 ms | **< 1 ms** (cache_data) |
| Qiskit circuit | ~200 ms | **< 2 ms** (cache_data) |
| QBER curve | — | **< 2 ms** (vectorised NumPy) |

---

## 🧪 Tests

```bash
pytest tests/ -v --tb=short
```

Test coverage includes: GHZ norm/entanglement, parity rule, secret reconstruction,
measurement product constraint, QBER bounds, noise analytical formulas, Tittel-2000 probability sums.

---

## 📚 References

1. M. Hillery, V. Bužek, A. Berthiaume, "Quantum secret sharing", *Phys. Rev. A* **59**, 1829 (1999)
2. W. Tittel, H. Zbinden, N. Gisin, "Experimental demonstration of quantum secret sharing", *Phys. Rev. A* **63**, 042301 (2001)
3. A. K. Ekert, "Quantum cryptography based on Bell's theorem", *Phys. Rev. Lett.* **67**, 661 (1991)

---

## 📄 How to Cite

```bibtex
@software{chongder2025qss,
  author    = {Chongder, Sumit Tapas},
  title     = {Quantum Secret Sharing Simulator},
  year      = {2025},
  version   = {1.0.0},
  url       = {https://github.com/Sumitchongder/Quantum-Secret-Sharing-Simulator},
  license   = {MIT}
}
```

---

## 👤 Author

**Sumit Tapas Chongder**  
M.Tech in Quantum Technologies · IIT Jodhpur  
Supervisor: Dr. Atul Kumar  
Course: Seminal Features of Quantum Information

---

## 📜 License

MIT — see [LICENSE](LICENSE)
