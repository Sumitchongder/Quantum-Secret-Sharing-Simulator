# Theory Reference

## Quantum Secret Sharing via GHZ States

This document is the complete theoretical reference for the QSS Simulator.

---

## 1. What is Quantum Secret Sharing?

Quantum Secret Sharing (QSS) is a quantum cryptographic protocol that allows a secret
to be split among multiple parties such that:

- **No single party** can reconstruct the secret alone
- **All parties cooperating** can reconstruct it
- **Any eavesdropper** is detectable via quantum measurement disturbance

Classical secret sharing (Shamir, 1979) requires computational assumptions.
QSS is **information-theoretically secure** — its security follows from the laws of physics.

---

## 2. The GHZ State

The Greenberger–Horne–Zeilinger (GHZ) state for N qubits:

$$|GHZ_N\rangle = \frac{1}{\sqrt{2}}\bigl(|00\cdots0\rangle + |11\cdots1\rangle\bigr)$$

### Properties

- **Normalised**: $\langle GHZ|GHZ\rangle = 1$
- **Maximally entangled**: each single-qubit reduced state has von Neumann entropy = 1 bit
- **Pure state**: purity $\text{Tr}(\rho^2) = 1$
- **Non-local**: violates the Mermin inequality for all N ≥ 3

### QuTiP construction

```python
from qutip import basis, tensor

def build_ghz(n):
    zero = basis(2, 0)
    one  = basis(2, 1)
    return (tensor([zero]*n) + tensor([one]*n)).unit()
```

---

## 3. Protocol — 3-Node Case

### Setup

Nodes A, B, C each hold one qubit of a 3-qubit GHZ state.

### Step 1 — Random phase selection

Each node independently picks a random phase:

$$\phi_A = \alpha \in \{0, \pi/2\}, \quad \phi_B = \beta \in \{0, \pi/2\}, \quad \phi_C = \gamma \in \{0, \pi/2\}$$

### Step 2 — Phase gate application

Each node applies the phase gate $P(\phi)$ to their qubit:

$$P(\phi) = \begin{pmatrix} 1 & 0 \\ 0 & e^{i\phi} \end{pmatrix}$$

$$P(\phi)|0\rangle = |0\rangle, \qquad P(\phi)|1\rangle = e^{i\phi}|1\rangle$$

The new shared state is:

$$|\psi\rangle = \frac{1}{\sqrt{2}}\bigl(|000\rangle + e^{i(\alpha+\beta+\gamma)}|111\rangle\bigr)$$

### Step 3 — Pauli-X measurement

All three nodes measure their qubits in the Pauli-X eigenbasis:

$$|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}, \qquad |-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}$$

Outcomes: $a, b, c \in \{+1, -1\}$ (eigenvalues of $\hat{X}$).

### Step 4 — Parity check (public announcement)

All nodes publicly announce their phases. The protocol **proceeds** only if:

$$\alpha + \beta + \gamma \in \{0, \pi\}$$

Otherwise the round is **discarded**.

**Why?** This ensures $\cos(\alpha+\beta+\gamma) \in \{+1, -1\}$, making the
measurement product deterministic.

### Step 5 — Measurement product constraint

When the parity condition is satisfied:

$$a \cdot b \cdot c = \cos(\alpha + \beta + \gamma) = \pm 1$$

This is the fundamental quantum correlation that makes QSS work.

### Step 6 — Secret reconstruction

Let $d = \cos(\alpha+\beta+\gamma) \in \{+1, -1\}$.

From $a \cdot b \cdot c \cdot d = 1$, nodes A and B can infer C's secret bit:

$$c = a \cdot b \cdot d$$

A and B exchange their outcomes $a$ and $b$ on a **private classical channel**.
They then compute $c$ without needing node C to cooperate.

### Symmetry

The protocol is **symmetric** — any node's bit can be designated the "secret".
This implies **3-party quantum key distribution**.

---

## 4. N-Node Generalisation

For N nodes, the GHZ state generalises trivially. The parity condition becomes:

$$\sum_{i=1}^{N} \phi_i \in \{0, \pi\}$$

The measurement product satisfies:

$$\prod_{i=1}^{N} a_i = \cos\!\left(\sum_{i=1}^{N} \phi_i\right) = \pm 1$$

Any $N-1$ nodes can reconstruct the secret bit of the remaining node.

---

## 5. Security Analysis

### Why eavesdroppers are detectable

The GHZ state is **maximally non-local**. Measurement on one qubit
instantly collapses the joint state of all qubits.

**Eve's best strategy — intercept-resend:**

1. Eve intercepts qubit $i$ with probability $p$
2. Measures in a random basis (50% correct, 50% wrong)
3. Resends a replacement qubit

**Effect:** When Eve guesses wrong basis, she introduces an error.

$$\text{QBER} = \frac{p}{2}$$

**Security threshold:** QBER $> 5\%$ → abort and restart.

**Detection probability after $n$ rounds:**

$$P(\text{detect}) = 1 - \left(1 - \frac{p}{2}\right)^n$$

At $p = 0.3$, $n = 100$: $P(\text{detect}) \approx 1 - 0.85^{100} \approx 0.9999$.

### Local randomness

In the X-eigenbasis expansion, the 3-qubit state is:

$$|\psi\rangle = \frac{1 + e^{i(\alpha+\beta+\gamma)}}{4}\bigl(|{+}{+}{+}\rangle + |{+}{-}{-}\rangle + |{-}{+}{-}\rangle + |{-}{-}{+}\rangle\bigr) + \frac{1 - e^{i(\alpha+\beta+\gamma)}}{4}\bigl(|{+}{+}{-}\rangle + \ldots\bigr)$$

When $\alpha+\beta+\gamma = 0$: only **even-parity** outcomes occur.  
When $\alpha+\beta+\gamma = \pi$: only **odd-parity** outcomes occur.

**In either case, each node's local outcome is uniformly $\pm 1$.**  
An eavesdropper observing a single qubit sees complete noise.

---

## 6. Tittel et al. (2000) Optical Experiment

**Reference:** W. Tittel, H. Zbinden, N. Gisin, *Phys. Rev. A* **63**, 042301 (2001).
University of Geneva.

### Key features

- Energy-time entanglement (not polarisation)
- **Pseudo-GHZ state** — only two entangled photons exist at any time
- Three phase shifters, one at each node
- Detection probability formula identical to true GHZ

### Detection probability

$$P_{ijk} = \frac{1}{8}\bigl[1 + ijk\cos(\alpha+\beta+\gamma)\bigr], \qquad i,j,k \in \{+1,-1\}$$

All 8 probabilities sum to 1. At $\alpha+\beta+\gamma = 0$:
only even-parity outcomes $(ijk = +1)$ are nonzero, each with $P = 1/4$.

### Measured parameters

| Parameter | Value |
|-----------|-------|
| Generation rate | ~15 Hz |
| Fibre loss | 0.35 dB/km |
| Phase shifter loss | 3 dB |
| Estimated range | 30–40 km |

### Generation rate model

$$\text{Rate}(d) = 15 \times 10^{-(0.35d + 3)/10} \text{ Hz}$$

where $d$ is the fibre distance in km.

---

## 7. GHZ Distribution Approaches

### Approach 1 — Teleportation-based

1. Node B creates a local GHZ state
2. B performs two Bell-state measurements (BSMs) — one per link
3. B broadcasts 2 classical bits to A and 2 to C
4. A and C apply Pauli corrections

**Properties:**
- Qubit count: $N + 2(N-1)$
- Classical messages: $2(N-1)$
- Teleportation introduces fidelity loss
- Requires two E2E connections before starting

### Approach 2 — Bell pairs + local operations

1. Bell pairs shared between A-B and B-C
2. B entangles its two qubits with a local CNOT
3. B measures one qubit and sends result to C
4. C applies conditional Pauli correction

**Properties:**
- Qubit count: $N$ (one per node)
- Classical messages: $N-1$
- No teleportation required
- Higher fidelity
- Demonstrated experimentally in a laboratory in 2021

**Fidelity comparison:**

$$F_1(N) = 0.98^{N-1}, \qquad F_2(N) = 0.99^{N-1}$$

(Simple gate-error model; $F_2 > F_1$ for all $N \geq 2$.)

---

## 8. Noise Models

### Depolarising channel

Each qubit independently undergoes:

$$\mathcal{E}(\rho) = (1-p)\rho + \frac{p}{3}(X\rho X + Y\rho Y + Z\rho Z)$$

Fidelity of N-qubit GHZ state:

$$F(p) = (1-p)^N + \frac{p^N}{2^N}$$

### Dephasing channel

$$\mathcal{E}(\rho) = (1-p)\rho + p Z\rho Z$$

Fidelity of N-qubit GHZ state:

$$F(p) = (1-p)^N$$

Dephasing decays faster for large N, making it the more restrictive noise model.

---

## 9. References

1. M. Hillery, V. Bužek, A. Berthiaume, "Quantum secret sharing", *Phys. Rev. A* **59**, 1829 (1999)
2. W. Tittel, H. Zbinden, N. Gisin, "Experimental demonstration of quantum secret sharing", *Phys. Rev. A* **63**, 042301 (2001)
3. D. Gottesman, "Theory of quantum secret sharing", *Phys. Rev. A* **61**, 042311 (2000)
4. A. Karlsson, M. Koashi, N. Imoto, "Quantum entanglement for secret sharing and secret splitting", *Phys. Rev. A* **59**, 162 (1999)
