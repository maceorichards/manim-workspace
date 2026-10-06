# Workbench — iv_curve_hump_flattens_snic_to_hopf

Context: `context_files/contract.md` (the video contract), `science.md`, `model.md`, `style.md`.

## The hump unbends

Status: Building (rendered: videos/iv_curve_hump_flattens_snic_to_hopf.mp4, 1344×1200, 30 fps, 12.0 s)
Scenes: IVHumpFlattens

### Intent
Adding outward current (shunt, then adaptation) to the paper's model unbends the steady-state
I–V curve — the hump and its negative-slope region vanish — and the model switches from SNIC
(class 1) to Hopf (class 2).

### Decisions in force
- Workspace look (black, CMU Serif), 1344×1200, 12.0 s, silent; colour roles from `style.md`
  (class 1 `BLUE_C`, class 2 `ORANGE`, shunt `PURPLE_C`, g_M `GREEN_C`, flash `RED_C`).
- Curve = model steady-state current, pinned: `net = I_ss(V) − I_ss(−34.435 mV)`, plotted as
  `asinh(net/0.45)`, V −62…−21 mV, fixed y range [−6.32, 6.68]; no y tick numbers.
- Ramp: added shunt 0 → 2.00 mS/cm² (the paper's high-conductance state), then g_M 0 → 2.00.
  Readout in mS/cm² plus live input-resistance drop (−52% at the end; cells' 10 nS: −56%).
- Label flips at Δg = 0.1656 (true SNIC→Hopf switch); band closes at Δg = 0.2395 (hump gone);
  both inside one 0.5-s flash (B2).
- Share `i_ss`, `net`, `yplot`, V_REF, knee and y range with `s08_vid1_mechanism_sync`
  (defined locally in `main.py` for now; no shared area helper exists yet).
- Decided (open question 1): pinned net current, per contract §9 A1.
- Decided (open question 2): "added shunt x.xx mS/cm²" + live "input resistance −n%" line,
  suffix "(cells, 10 nS: −56%)" from 6.5 s. No nS ramp.
- Decided (open question 3): keep the split — label/colour flip at Δg 0.1656 (4.0 s), band
  closes at 0.2395 (4.5 s), both inside the 0.5-s flash.
- Decided (open question 4): shunt ramp ends at the model's +2.00 mS/cm².
- Curve colour follows a class flag flipped together with the label (not the Δg threshold),
  so the last B1 frame (Δg exactly 0.1656) is still blue under "SNIC · class 1".
- x label "V (mV)" sits on the tick-label row, right-aligned at the axis end (x = 4.0):
  centred under the axis at y −3.6 it collides with the "−40" tick label.
- R_in line: prefix is left-anchored for the two-digit width so it does not jump at 10%;
  it slides left 2.3 units when the cells suffix fades in, so the full line is right-aligned.

### Checklist
- [x] B0: first frame shows the full control picture (curve, band, hump dot, label, readouts, sign texts)
  - Outcome: kept — 1344×1200 frame 0 shows blue hump, band −38.3…−31.6, dot at the max, all labels.
- [x] B1: hump shrinks continuously while Δg 0 → 0.17 (band narrows, ghost control stays)
  - Outcome: kept — t 2.5 s shows 0.08 / −4%, narrower band, ghost separating from the curve.
- [x] B2: flip + flash — label/colour change at 0.17, band closes at 0.24, all within 0.5 s
  - Outcome: revised — frame 119 blue "SNIC", frame 120 orange "Hopf" + red glow at 0.17; band gone
    by frame 134 at 0.24 / −11%. Colour was first tied to Δg and flipped one frame early.
- [x] B3: curve rotates to a monotonic S through (−34.4, 0); readouts reach 2.00 / −52% + cells suffix
  - Outcome: kept — t 6.8 s: steep orange S through the zero line at −34.4, suffix on one line.
- [x] B5: g_M line appears and ramps to 2.00; curve steepens, no second flip
  - Outcome: revised — the g_M symbol first overlapped the value; after the fix the line reads "added g_M 2.00 mS/cm²".
- [x] B6: end frame holds 2.5 s and reads as a still (compare contract §6)
  - Outcome: kept — last frame matches §6: orange S, faint blue ghost with hump, no band/dot, 3 readouts.
- [x] Asserts from `model.md` §5 pass in `__main__`; fits ±4.2 × ±3.75 at `-r 672x600`
  - Outcome: kept — all asserts pass (plus sign-region emptiness and y-range); leftmost ink
    is the y label at x ≈ −3.87, lowest is the tick-label row.

### Open questions
- None open; all four resolved under Decisions in force.

### Parking lot
- Optional inset of raw I_ss (linear µA/cm², like the paper's Fig. 1C) to show what the
  compressed axis hides.
- E_shunt = −57 mV variant (paper says results were qualitatively unchanged).
