# API Reference

Complete reference for all public functions in the `qss` package.

---

## `qss.ghz`

### `build_ghz_qutip(n)`

Build an N-qubit GHZ state using QuTiP tensor products.

**Parameters**
- `n` (`int`): Number of qubits. Must be ≥ 2.

**Returns**
- `qutip.Qobj`: Normalised GHZ ket, shape `(2^n, 1)`.

**Raises**
- `ValueError`: If `n < 2`.

**Example**
```python
from qss.ghz import build_ghz_qutip
state = build_ghz_qutip(3)
print(state.norm())  # 1.0
```

---

### `build_ghz_approach1(n)`

GHZ distribution via teleportation (Approach 1).

**Returns** `tuple`: `(ghz_state, qubit_count, classical_msg_count, fidelity_estimate)`

---

### `build_ghz_approach2(n)`

GHZ distribution via Bell pairs + local ops (Approach 2).

**Returns** `tuple`: `(ghz_state, qubit_count, classical_msg_count, fidelity_estimate)`

---

### `compare_approaches(n)`

Side-by-side comparison dict for both approaches.

**Returns** `dict`: Keys `approach1`, `approach2`, each with sub-keys:
`qubit_count`, `msg_count`, `fidelity_estimate`, `teleportation_needed`, `lab_demonstrated`.

---

## `qss.protocol`

### `PHASES`

```python
PHASES: list[float] = [0.0, numpy.pi / 2]
```

Phase lookup table. Index 0 → 0 rad, index 1 → π/2 rad.

---

### `parity_check(alpha_i, beta_i, gamma_i)`

Check 3-node parity condition. Cached via `functools.lru_cache`.

**Parameters**: `alpha_i, beta_i, gamma_i` (`int`) — indices into `PHASES`.

**Returns** `int`: `+1`, `-1`, or `0` (discard).

```python
from qss.protocol import parity_check
parity_check(0, 0, 0)   # → +1  (0+0+0=0)
parity_check(1, 1, 0)   # → -1  (π/2+π/2+0=π)
parity_check(1, 0, 0)   # →  0  (discard)
```

---

### `parity_check_n(phase_indices)`

N-node parity check. Cached via `functools.lru_cache`.

**Parameters**: `phase_indices` (`tuple[int, ...]`)

**Returns** `int`: `+1`, `-1`, or `0`.

---

### `reconstruct_secret(a, b, d)`

Infer node C's secret bit. Cached via `functools.lru_cache`.

From $a \cdot b \cdot c \cdot d = 1 \Rightarrow c = a \cdot b \cdot d$.

**Parameters**: `a, b, d` (`int`) — all `±1`.

**Returns** `int`: `+1` or `-1`.

---

### `simulate_measurement(n, phase_indices, seed)`

Simulate Pauli-X basis measurements. Enforces the parity product constraint.

**Parameters**
- `n` (`int`): Number of nodes.
- `phase_indices` (`tuple[int, ...]`): Phase index per node.
- `seed` (`int`): RNG seed.

**Returns** `list[int]`: Outcomes, each `±1`.

---

### `run_protocol_round(n, phase_indices, seed)`

Execute one complete QSS protocol round.

**Returns** `dict`:

| Key | Type | Description |
|-----|------|-------------|
| `phase_indices` | tuple | Input phases |
| `phases_rad` | list | Phases in radians |
| `parity` | int | +1, -1, or 0 |
| `outcomes` | list | Measurement outcomes |
| `discard` | bool | True if round discarded |
| `success` | bool | True if reconstruction correct |
| `secret_node_idx` | int | Index of secret-holding node |
| `secret_value` | int or None | The secret bit |
| `inferred_value` | int or None | What A and B infer |

---

## `qss.eavesdropper`

### `inject_eve_attack(intercept_prob, n_rounds, seed)`

Simulate intercept-resend attack.

**Parameters**
- `intercept_prob` (`float`): Eve's interception probability, `[0, 1]`.
- `n_rounds` (`int`): Protocol rounds to simulate.
- `seed` (`int`): RNG seed.

**Returns** `dict`:

| Key | Type | Description |
|-----|------|-------------|
| `qber` | float | Quantum bit error rate |
| `n_errors` | int | Number of errors |
| `n_rounds` | int | Total rounds |
| `n_intercepts` | int | Rounds Eve intercepted |
| `intercept_prob` | float | Input probability |
| `detected` | bool | True if QBER > 5% |
| `security_msg` | str | Human-readable status |

---

### `qber_vs_intercept_curve(n_points)`

Theoretical QBER = p/2 curve. Fully vectorised.

**Returns** `np.ndarray`: Shape `(n_points, 2)` — columns `[intercept_prob, qber]`.

---

### `detection_probability(intercept_prob, n_rounds)`

$P(\text{detect}) = 1 - (1 - p/2)^n$

**Returns** `float`.

---

## `qss.noise`

### `depolarise_sweep(n_nodes, max_noise, n_points)`

Analytical fidelity under depolarising noise: $F(p) = (1-p)^N + p^N/2^N$.

**Returns** `np.ndarray`: Shape `(n_points, 2)` — columns `[noise_prob, fidelity]`.

---

### `dephase_sweep(n_nodes, max_noise, n_points)`

Analytical fidelity under dephasing: $F(p) = (1-p)^N$.

**Returns** `np.ndarray`: Shape `(n_points, 2)`.

---

### `threshold_noise(n_nodes, model, target_fidelity)`

Find noise level at which fidelity drops below target.

**Returns** `float`: Noise probability threshold.

---

### `hilbert_space_dim(n_nodes)`

Returns $2^N$.

---

### `memory_mb_estimate(n_nodes)`

Density matrix RAM in MB (complex128): $(2^N)^2 \times 16 / 1024^2$.

---

## `qss.tittel2000`

### `detection_probability(i, j, k, alpha, beta, gamma)`

$P_{ijk} = \frac{1}{8}[1 + ijk\cos(\alpha+\beta+\gamma)]$

**Parameters**: `i, j, k` (`int`) ∈ `{+1, -1}`, phases in radians.

**Returns** `float`: Probability in `[0, 0.25]`.

---

### `all_outcome_probabilities(alpha, beta, gamma)`

All 8 outcome probabilities for given phases.

**Returns** `dict`: Keys like `'(+1,+1,+1)'`, values are probabilities summing to 1.

---

### `parity_groups(alpha, beta, gamma)`

**Returns** `dict`: Keys `'even'` and `'odd'`, each a `{label: probability}` dict.

---

### `generation_rate_estimate(distance_km, fiber_loss_db_km, phase_shifter_loss_db, base_rate_hz)`

Estimate secret bit generation rate using Tittel-2000 parameters.

**Returns** `float`: Rate in Hz.

---

### `max_range_km(min_rate_hz, ...)`

Maximum usable range given minimum acceptable rate.

**Returns** `float`: Range in km.

---

### `rate_vs_distance(max_km, n_points)`

Vectorised generation rate curve.

**Returns** `np.ndarray`: Shape `(n_points, 2)` — columns `[distance_km, rate_hz]`.

---

## `qss.metrics`

### `state_fidelity(state1, state2)`

$F(\rho_1, \rho_2)$ via QuTiP. **Returns** `float` in `[0, 1]`.

---

### `state_purity(state)`

$\text{Tr}(\rho^2)$. **Returns** `float`.

---

### `von_neumann_entropy(state)`

$S(\rho) = -\text{Tr}(\rho\log_2\rho)$ in bits. **Returns** `float`.

---

### `subsystem_entropy(state, qubit_idx)`

Von Neumann entropy of single-qubit reduced state. **Returns** `float`.

---

### `qber_from_counts(counts)`

Estimate QBER from Qiskit bitstring counts. **Returns** `float`.

---

### `bloch_vector(state)`

Bloch sphere components $(x, y, z)$ for a single-qubit state. **Returns** `tuple[float, float, float]`.

---

### `ghz_concurrence(n)`

Bipartite concurrence for N-qubit GHZ. **Returns** `float`.

---

## `qss.cache`

All functions here are wrapped with Streamlit cache decorators.
Import from `qss.cache` only inside Streamlit context (i.e., from `pages/` or `components/`).

### `get_ghz_state(n_nodes)` — `@st.cache_resource`

Returns cached N-qubit GHZ state. Built once per server process.

### `get_aer_simulator()` — `@st.cache_resource`

Returns cached `AerSimulator` backend.

### `run_qiskit_circuit(n, alpha_i, beta_i, gamma_i, noise_name, shots)` — `@st.cache_data`

Runs and caches Qiskit QSS circuit. All args are primitives.

### `compute_wigner(_state, xvec_tuple, pvec_tuple)` — `@st.cache_data`

Computes and caches Wigner function grid.

### `compute_fidelity_curve(n_nodes, max_noise, model)` — `@st.cache_data`

Returns fidelity vs noise sweep array.

### `compute_optical_probabilities(alpha, beta, gamma)` — `@st.cache_data`

Returns Tittel-2000 outcome probabilities dict.
