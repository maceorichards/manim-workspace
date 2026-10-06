# Model — "Two clocks, and sliding the threshold"

Sources: the paper's Methods (Eqs. 1–6; the noise model) and its Fig 8 and Fig 9 legends; deck
spec, slide 6 and Code prerequisites; deck model module. Read 2026-09-30. Everything was
recomputed on 2026-09-30 with `prescott2008.py`.

## 1. Model (3-D; V mV, t ms, g mS/cm², I µA/cm²; outward +)

    C dV/dt = I_stim + I_noise − ḡ_Na m∞(V)(V − 50) − ḡ_K,dr w (V + 100) − g_shunt (V + 70) − ḡ_M z (V + 100)
    dw/dt = φ_w (w∞(V) − w)/τ_w(V)        dz/dt = (z∞(V) − z)/τ_z
    z∞(V) = 1/(1 + exp((β_z − V)/γ_z))

- Noise (paper Methods): Ornstein–Uhlenbeck, dI/dt = −I/τ_noise + σ N(0,1), with stationary
  variance **σ²τ/2**. The paper pairs σ 0.1 with τ 5 ms and σ 0.01 with τ 500 ms, which give
  equal variance. `P.simulate_noisy(p, I, t_ms, dt=0.02, sigma, tau_noise, y0, seed)` implements
  exactly this.
- The area module provides the prerequisites the deck spec listed:
  - `P.fixed_points_3d` / `P.stable_fp_3d`: 3-D Jacobian by central differences
  - `P.find_I_bif`: bisection on "a stable fixed point exists"
  - `P.bifurcation_type`: an exact rest-branch walk, returning (type, V*, I_bif)
  - `P.z_Vnull`: the V–z nullcline with w = w∞(V)
  - `P.FIG9`, `P.FIG9_INACT`, `P.FIG9_SHUNT`, `P.FIG9_INACT_NO_IM`
- `P.THETA_MODEL` = γ_w 8, ḡ_K,dr 30, ḡ_M 2, τ_z 400 (Fig 8A/B legends).

## 2. Beat A runs

| | A1 fast ring | A2 θ ring |
|---|---|---|
| p | `replace(P.THETA_MODEL, g_shunt=4.0)` | `P.THETA_MODEL` |
| I_bif (V*) | 183.06 (−29.48) | 53.39 (−39.22) |
| hold | 0.99× = 181.23 | 0.99× = 52.86 |
| fixed point (V, w, z) | −29.68, 0.00567, 0.5162 | −39.41, 0.00050, 0.1323 |
| 3-D λ (s⁻¹) | −21.99 ± 721.21i, −10.71 | −6.93 ± 63.22i, −740.4 |
| ring | 114.8 Hz | 10.06 Hz |
| noise | **τ 5 ms, σ 0.1**, seed 0 | **τ 500 ms, σ 0.004**, seed 0 |
| run | start at the 3-D FP, dt 0.02, 13 s; discard the first 3 s | same |
| result | no spikes; V p-p (99%) 1.51 mV; SD 0.30; peak 114.8 Hz | no spikes; V p-p 1.58 mV; SD 0.26; peak 9.5 Hz |
| modulation over the displayed window | V 3.3%, g_K,dr 14%, g_M 0.11% | V 4.3%, g_K,dr 43%, g_M 1.8% |
| phase lag behind V (at the ring freq.) | g_K,dr 56°, g_M 90° (tiny amplitude) | g_K,dr **5°**, g_M **88°** |
| displayed window | 75 ms at ×1/40 | 2 s at ×1/4 |

Rejected (spec) settings, recorded:
- A1 at τ 500 / σ 0.01 gives 0.22 mV p-p, with the spectrum dominated by the 1-Hz drift.
- A2 at σ 0.01 gives 30 spikes; at σ 0.006, 9 spikes. A2 at 0.97–0.98× with σ 0.01 still spikes.

**Windows** (§ contract 4): ±3 SD of each segment's kept run around its mean.
- A1: V −29.67 ± 0.89, w 0.00567 ± 0.00075, z 0.5162 ± 0.0006.
- A2: V −39.40 ± 0.77, w 0.00050 ± 0.00010, z 0.1326 ± 0.0015.
- Shared spans = the larger of the two per axis, × 1.2: **V ≈ 2.2 mV, w ≈ 0.0018,
  z ≈ 0.0036**. Each segment's windows are centred on its own mean.

Choose the displayed window as a stretch of the kept run with no large slow excursion, for
example the first 75 ms / 2 s after burn-in. Recompute the modulation tags from that same
stretch.

## 3. Beat B runs (precomputed spectra)

- Each variant is held at **0.995 × its own I_bif**, with **σ 0.001, τ_noise 500 ms**, seed 0,
  dt 0.02, 23 s. Discard the first 3 s and keep 20 s.
- Spectrum: decimate V by 5 (fs 10 kHz), subtract the mean, then
  `welch(x, fs=10000, nperseg=40000)` (4 s → 0.25-Hz bins). Plot 1–100 Hz, log–log.
- Peak ratio used in the checks: the maximum over 2–15 Hz divided by a log–log line fitted
  through the bins in 1–1.5 Hz and 25–40 Hz, evaluated at the peak frequency.

| variant | spikes | V p-p | θ peak | ratio (seed 0 / seed 1) | P range (1–100 Hz) |
|---|---|---|---|---|---|
| control | 0 | 0.34 | none (2.0 Hz max) | 1.5 / 2.2 | 1.3e−9 … 1.3e−3 |
| inact | 0 | 0.87 | **5.75 Hz** | 140 / 336 | 1.7e−9 … 3.2e−3 |
| shunt | 0 | 0.43 | **9.5 Hz** (8.25 with seed 1) | 89 / 85 | 2.0e−9 … 5.8e−4 |
| no I_M | 0 | 0.32 | none | 1.4 / 2.0 | 1.5e−9 … 1.0e−3 |

- → y range ≈ 10⁻⁹ … 10⁻², fixed.
- Thresholds, V*, z∞(V*) and I_M at V* come from `P.bifurcation_type(p)` → (type, V*, I_bif).
  - control: Hopf-labelled at I_bif (a degenerate 1.2-Hz crossing right at the fold), with all
    eigenvalues real at 0.995×. Label its V–z fixed point "saddle-node", following the paper's
    Fig 9D wording.
  - inact: Hopf, V* −37.14, z∞ 1.68%, I_M 2.11.
  - shunt: Hopf, V* −35.80, z∞ 3.23%, I_M 4.15.
  - no I_M: SN, V* −37.44, I_M 0.
- Eigenvalues at 0.995× (`P.stable_fp_3d`, ×1000):
  - control −1112.9, −103.6, −2.8
  - inact −7.8 ± 39.3i, −558.7
  - shunt −18.4 ± 60.3i, −408.3
  - no I_M −709.6, −137.2, −2.5
  - For reference, at 0.99×: inact −16.2 ± 34.3i (5.5 Hz), shunt −38.3 ± 46.3i (7.4 Hz). These
    are the deck spec's values; they are correct at 0.99×.
- Rejected settings, recorded:
  - 0.99×, σ 0.01: inact 39 spikes, shunt 32.
  - 0.99×, σ 0.004: inact 3, shunt 1.
  - 0.99×, σ 0.002: no spikes, but shunt ×5.0 at 4.25 Hz (marginal).
  - 0.98×, σ 0.002–0.004: shunt and inact peaks weak (×2–4).

## 4. Phase-lag measurement (for the Beat A check)

Band-pass V and the conductance with a 2nd-order Butterworth over 0.6–1.5 × f_ring, applied
with `filtfilt`, then take Hilbert analytic signals h_V and h_g.
Lag of g behind V = `degrees(angle(mean(h_V · conj(h_g))))`. Positive means g lags. Verified
values are in §2.

## 5. Nullclines and planes

- V–w (Beat A): `P.V_nullcline_w(V, p, I, z=z_fp)` and `P.w_nullcline(V, p)`, over the
  segment's V window.
- V–z: `P.z_Vnull(V, p, I)` and `P.z_nullcline(V, p)`. For the no-I_M variant, ḡ_M = 0 and
  z_Vnull is undefined, so grey the plane out instead of computing it.
- The Beat B z∞ panel uses `P.z_inf(V, P.FIG9)`, with β_z −29 and γ_z 2 (a steep curve: 0.09%
  at −43.1 mV, 3.2% at −35.8 mV, 10% at ≈ −33.4 mV).

## 6. Performance and caching

`P.simulate_noisy` runs 1.15·10⁶ steps (23 s) in about 1–2 s. Cache every run with
`P.npz_cache("m_current_theta_ringing/cache/<name>.npz", fn, sigma=..., tau=..., frac=..., seed=0, dt=0.02)`.
Cache the spectra too.

## 7. Asserts for `main.py __main__` (print each value)

- I_bif: A1 183.06, A2 53.39, FIG9 33.19, INACT 44.12, SHUNT 83.08, NO_IM 42.02 (±0.05).
- λ tables within 3%.
- Beat A:
  - no spikes; 1.0 ≤ p-p ≤ 2.0 mV
  - A2 peak in 8–11 Hz
  - A2 lag g_M ≥ 60° and g_K,dr < 15°
- Beat B:
  - no spikes
  - ratio ≥ 5 for inact and shunt, < 3 for control and no-I_M
  - peaks in 3–10.5 Hz
- I_M at V*: 0.10 / 2.11 / 4.15 / 0 (±0.05).
