# Video contract — "The hump unbends"

## 1. Header

| | |
|---|---|
| Deck id | `s07_vid1` |
| Title | The hump unbends (~12 s) |
| Scene class | `IVHumpFlattens` (`main.py`) |
| Place in deck | slide 7, build 7c, **left box** (5.95 × 5.3 in); nothing else is placed on 7c (deck manifest) |
| Duration target | **12 s** (hard cap 25 s) |
| Delivery | silent, play on click, first frame meaningful when paused, last frame a usable still (hold ≥ 2 s) |

Sources: deck outline slide 7 (video 1, static visuals, "Say") and Assembly notes; deck build
contract §6; deck static figure s07_v1 and its status notes; paper Fig. 1B/1C legends, Results
p. 3033, Methods; background notes §10, §11, §23–26. All read 2026-09-28.

## 2. Purpose

- **Takeaway:** as outward current is added to the paper's model (first a shunt, then M-type
  adaptation), the steady-state *I–V* curve loses its hump (its negative-slope region) and the
  model's spike-initiating mechanism switches from SNIC (class 1) to Hopf (class 2). The hump is
  the read-out anyone can check without dynamical systems.
- **Where it sits:** slide 7 is the first results slide. 7a teaches how to read an *I–V* curve
  (static s07_v1: blue control curve with a hump vs orange monotonic curve); 7b shows the paper's
  Fig. 1B a/d and 1C a/d. This video (7c) makes the conversion continuous. Slide 8's video
  (`s08_vid1_mechanism_sync`) reuses this exact curve computation as its right panel.
- **Thesis** (repeated verbatim on slides 4, 7, 8, 10, 11): *Whether a neuron is an integrator
  or a resonator is decided by the sign of the net current near threshold — and that sign is set
  by the synaptic background, not by the cell.*
- Speaker's framing: this is a **model** result, not yet data; the experiments come on slide 8.

## 3. Must show / Must not show

Must show
- The model's own steady-state *I–V* curve (I_Na + shunt/leak + I_K,dr [+ I_M]), recomputed
  every frame from the equations in `model.md` — never a hand-drawn or keyframed shape.
- A continuous ramp of the added shunt conductance, then adaptation (g_M) added on top.
- A live readout of the added conductance(s) in a corner.
- The negative-slope region shaded while it exists; it narrows and closes.
- A flash of the curve and a corner-label flip **"SNIC · class 1" → "Hopf · class 2"** at the
  moment the mechanism switches (see beat B2 for the exact trigger).
- The sign convention (above 0 = net outward, below 0 = net inward), carried over from 7a.

Must not show
- No equations on screen (the talk states the membrane equation in words only).
- No title inside the video (the slide has one). No tick numbers on the current axis (only "0").
- No "0 → 10 nS" readout: the model's high-conductance state is +2 mS/cm², not 10 nS
  (accuracy flag A2). No made-up numbers: every number on screen comes from `model.md`.
- No phase planes or bifurcation diagrams (that is slide 5 / 9 vocabulary, and 7b's paper panels).

## 4. Layout (frame 8.96 × 8 units; keep inside x ∈ [−4.2, 4.2], y ∈ [−3.75, 3.75])

- **Axes box:** x from −3.30 to 4.00 (7.3 units) ↔ V = −62 … −21 mV; y from −3.20 to 1.90
  (5.1 units) ↔ plotted value `y = asinh(net / 0.45)` over [−6.32, +6.68] (fixed for the
  whole video; zero line at y ≈ −0.72). Axis stroke 2, `GREY_B`.
- **x ticks** at −60, −50, −40, −30 (labels font 28, `GREY_B`); x label `txt("V (mV)")` font
  28 centred under the axis (y ≈ −3.6). **y axis:** only a "0" label left of the zero line;
  rotated label `txt("net steady-state current")` font 26, `GREY_B`, at x ≈ −3.75.
- **Zero line:** full-width, `WHITE`, stroke 2.
- **Sign convention (inside the axes, persistent), two lines each, font 24:** top-left,
  left-aligned at x ≈ −3.15, y ≈ 1.55 / 1.2, `TEAL_C`: "above 0 = net outward" / "(pushes V
  down)"; bottom-right, right-aligned at x ≈ 3.95, y ≈ −2.55 / −2.9, `PINK`: "below 0 = net
  inward" / "(pushes V up)". Both regions (V < −36 mV above y = 0.9; V > −34 mV below
  y = −2.3) stay empty of curve in every state.
- **Curve:** stroke 5; `BLUE_C` while class 1, `ORANGE` from the flip on. A ghost copy of the
  control curve (`BLUE_C`, stroke 3, opacity 0.3) stays from B1 onward.
- **Negative-slope band:** `BLUE_C` rectangle, fill_opacity 0.15, no stroke, full axes height,
  spanning V_max(g)…V_min(g) (the hump's local max and min). Hump-top marker: small
  `Dot(fill_color=BLUE_C)` radius 0.07 at the local max.
- **Corner label** (top-left, x ≈ −3.2 left-aligned, y ≈ 3.3): `txt("SNIC · class 1")` font 40
  `BLUE_C` → `txt("Hopf · class 2")` font 40 `ORANGE`.
- **Readouts** (top-right, right-aligned at x = 4.15):
  - y ≈ 3.35: "added shunt  0.00 mS/cm²" — `PURPLE_C`, font 28, live `DecimalNumber` (2 dp).
  - y ≈ 2.85: "input resistance −0%" — `GREY_B`, font 24, live integer %; from B3's end the
    suffix "(cells, 10 nS: −56%)" appears after it, same line, `GREY_B`.
  - y ≈ 2.35 (appears in B5): "added g_M  0.00 mS/cm²" — `GREEN_C`, font 28, live 2 dp.

## 5. Beat sheet (12.0 s)

`Δg` = added shunt (g_shunt − 2), `g_M` = adaptation conductance, both mS/cm². The curve,
band, dot and readouts are all functions of (Δg, g_M) — drive them from two ValueTrackers.

| # | t (s) | On screen / motion | Readout / label | Data |
|---|---|---|---|---|
| B0 | 0.0–1.0 | Complete control frame (first frame = this): axes, blue curve with hump, band −38.3…−31.6 mV, hump-top dot, sign texts | "SNIC · class 1"; shunt 0.00; R_in −0% | CONTROL |
| B1 | 1.0–4.0 | Ghost of control appears; Δg 0 → 0.166 **linear**. Hump shrinks (depth 1.06 → 0.18 µA/cm²), band narrows to −36.4…−32.8 mV | shunt counts 0.00 → 0.17; R_in → −8% | table §model "shunt ramp" |
| B2 | 4.0–4.5 | **Flip + flash.** At 4.0 (Δg = 0.166, the true switch): label flips, curve snaps to `ORANGE`, flash begins (curve stroke 5 → 9 → 5 with a `RED_C` glow copy fading out, 0.5 s). Δg 0.166 → 0.240 linear; band closes to zero width at 4.5 (Δg = 0.2395) and the dot fades | "Hopf · class 2"; shunt 0.17 → 0.24; R_in → −11% | g_BT = 2.1656, g_IV = 2.2395 |
| B3 | 4.5–6.5 | Δg 0.240 → 2.00, smooth ease-in-out. Curve rotates into a steep monotonic S through (−34.4 mV, 0) | shunt → 2.00; R_in → −52%; at 6.5 suffix "(cells, 10 nS: −56%)" fades in (0.3 s) | SHUNT |
| B4 | 6.5–7.0 | Hold | | |
| B5 | 7.0–9.5 | Line "added g_M 0.00 mS/cm²" fades in; g_M 0 → 2.00 smooth. Curve steepens further (outer ends spread: −80 → −118 and +76 → +174 µA/cm²) | g_M → 2.00 | SHUNT_ADAPT |
| B6 | 9.5–12.0 | Hold end frame | | |

Outline mapping: "redrawn continuously as shunt ramps" → B1–B3; "readout in the corner" →
readouts; "then as adaptation is added on top" → B5; "hump flattens" → B1; "flash + label flip
when the negative-slope region disappears" → B2; "computed from I_Na + I_leak + I_K,dr [+ I_M]
+ shunt" → `model.md`.

## 6. End frame (t ≥ 9.5 s)

Dark-theme counterpart of the orange-vs-blue pair in static s07_v1, but in this video's
"pinned" net-current convention: a thick `ORANGE` monotonic curve rising from the lower-left
(net ≈ −118 µA/cm² at −62 mV), passing steeply through 0 at −34.4 mV, levelling into the
upper-right (≈ +174 at −21 mV); behind it the faint blue ghost of the control curve with its
small hump (local max at −38.3 mV just above 0, dip at −31.6 mV just below 0, zero crossings
−41.7, −34.4, −29.7 mV). No band, no dot. Top-left "Hopf · class 2" (`ORANGE`). Top-right:
"added shunt 2.00 mS/cm²", "input resistance −52% (cells, 10 nS: −56%)", "added g_M 2.00
mS/cm²". Sign-convention texts in place.
Differences from s07_v1: black background and workspace colours; the curves are pinned at
−34.4 mV instead of using one fixed I_stim = 38.2 µA/cm² (so the orange curve crosses 0 at
−34.4 mV, not −59.7 mV — see flag A1); no long annotation sentences.

## 7. Data (all from `model.md`)

- Curve: `yplot(net(V, 2 + Δg, g_M))` on V = linspace(−62, −21, 600) each frame.
- Band / dot: `hump(g)` → (V_max, V_min) for g_M = 0 and Δg < 0.2395; otherwise none.
- Label: `SNIC · class 1` while Δg < 0.1656 (g_M = 0), else `Hopf · class 2`.
- R_in readout: `100·Δg/(1.8753 + Δg)` rounded (matches the exact rest-slope method ±0.1%).

## 8. Continuity

- Same curve function, V_REF pinning, asinh knee 0.45, y range and colours as the right panel of
  `s08_vid1_mechanism_sync` (keep them identical; ideally move `i_ss`, `net`, `yplot` into a
  shared area helper once both exist).
- Static s07_v1 (slide 7a) introduces the same two curves and sign convention; Paper Figs. 2C,
  8E, 9E show the same unbending under other manipulations (motif 4 of the Assembly notes).
- Colour roles: class 1 `BLUE_C`, class 2 `ORANGE`, shunt `PURPLE_C`, g_M `GREEN_C`, outward
  `TEAL_C`, inward `PINK`, flash `RED_C`.

## 9. Accuracy flags

- **A1 — the hump is tiny.** Raw steady-state current spans ~15 to ~110 µA/cm² over the window,
  the hump is 1.06 µA/cm² deep. Plot net current = I_ss(V) − I_ss(−34.435 mV) (each curve pinned
  through 0 at the control hump's centre, i.e. the injected current that holds the cell at
  −34.4 mV) on a sign-preserving asinh scale (knee 0.45 µA/cm²). The static's alternative
  (one fixed I_stim = 38.2) was checked and rejected for animation: the shunt lifts the hump into
  the compressed part of the scale and it *looks* gone by Δg ≈ 0.1, well before it is. Pinning
  keeps the hump at 0 where the scale is linear, and the pin voltage is exactly where the minimum
  slope sits for every shunt value. The transform is monotone: zero crossings, signs and the
  negative-slope region are exact.
- **A2 — "0 to 10 nS" is not the model.** The paper models the in-vivo-like state as g_shunt
  2 → 4 mS/cm² (Methods) and never converts it to nS. With the paper's 300 µm² area, +2 mS/cm² =
  6 nS. What matches honestly is the effect: the model's +2 mS/cm² cuts input resistance by 52%;
  the cells' 10-nS dynamic-clamp shunt cut it by 56% (paper Methods). Hence the readout in
  mS/cm² plus the R_in line.
- **A3 — switch vs hump are 0.074 mS/cm² apart.** In the model (no adaptation, exact 2-D
  system) the rest state starts losing stability through a Hopf at Δg = 0.1656 (a
  Bogdanov–Takens point), while the negative-slope region closes at Δg = 0.2395. Monotonic
  *I–V* ⇒ Hopf holds; the converse fails in that thin sliver. B2 therefore flips the label at
  0.1656 and closes the band at 0.2395 inside one 0.5-s flash. Also: the switch needs only
  ~12% of the high-conductance shunt (≈ 0.7 nS, R_in −11%).
- **A4 — adaptation adds no second flip.** At g_shunt = 4 the curve is already monotonic; g_M
  only steepens it (Hopf voltage −31.7 → −29.6 mV). The label stays "Hopf · class 2".
- **A5 — z in the I–V.** The curve uses I_M at its steady state z_inf(V), which reproduces the
  paper's Fig. 1C c/d; the paper's bifurcation diagrams instead froze z (Fig. 1B legend), so its
  Fig. 1B d threshold (≈ −18 mV at ≈ 160 µA/cm²) differs from ours (−29.6 mV at 193). Not shown.

## 10. Acceptance checklist

- [ ] Frame 0 is the full control picture (curve, band, dot, label, readouts, sign texts).
- [ ] Control curve: local max at −38.3 mV above 0, dip at −31.6 mV below 0, crosses 0 at
      −41.7, −34.4, −29.7 mV.
- [ ] Band narrows continuously and closes at readout 0.24; it never jumps.
- [ ] Label flips at readout 0.17 with the flash; curve colour changes with it.
- [ ] After B3 the curve is monotonic, passes through (−34.4 mV, 0); ghost control visible.
- [ ] Readouts end at "2.00", "−52%", "2.00"; suffix "(cells, 10 nS: −56%)" present.
- [ ] No equations, no title, no y tick numbers, no "nS" ramp; all text ≥ font 24.
- [ ] Nothing outside ±4.2 × ±3.75 (check a `-r 672x600` render); duration 12.0 s.
