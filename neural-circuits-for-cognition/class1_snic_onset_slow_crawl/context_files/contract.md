# Video contract — "Class 1: rest vanishes, the ball crawls"

## 1. Header

| | |
|---|---|
| Deck id | `s05_vid1` |
| Title | Class 1: rest vanishes, the ball crawls |
| Scene class | `Class1SnicOnset` |
| Placement | outline slide 5, build slide **5c, left box** (5.95 × 5.3 in). Right box = `s05_vid2` (class 2), played next |
| Duration | ~20 s (target 19.6 s; hard cap 25 s) |
| Audio | silent |
| Playback | click-to-play; first frame must read on its own when paused |

Sources: deck outline, slide 5 (video 1, content table, "Say", "If asked") and Assembly notes;
deck build manifest; deck static figure s05_v1 and its status notes; deck static figure s05_v2;
deck build contract §6; paper Methods and Fig. 5A legend. All read 2026-09-29.

## 2. Purpose

Takeaway: **in a class 1 cell, rest disappears because two fixed points (a stable rest point and
a saddle) collide and annihilate. Afterwards the trajectory still has to pass the spot where they
were, and it crawls there, so the interval between spikes can be as long as you like.** This is
where "arbitrarily slow firing" comes from.

Place in the talk: slide 5 introduces the phase plane in plain words (voltage against the slow K⁺
variable; nullclines are where one variable stops changing; where they cross nothing changes =
rest; spiking = rest ceasing to exist). The audience has just seen the two static phase planes
(s05_v1) and the analogy icons (s05_v2: "a valley that flattens out and vanishes" / "slow
crawl"). This video animates the class 1 panel; `class2_hopf_onset_spiral_escape` then animates the class 2 panel. It
sets up slide 9 (class 1 has no focus, so no ringing) and slides 7–8 (the control model is this
model). Thesis the talk hangs on: *whether a neuron is an integrator or a resonator is decided by
the sign of the net current near threshold, and that sign is set by the synaptic background, not
by the cell.*

## 3. Must show / must not show

Must show
- Left: the V–w phase plane; right: V(t) drawn in sync with the moving state point.
- Injected current stepping up (as a staircase trace under V(t)); the V-nullcline lifting.
- The rest point and the saddle sliding toward each other, merging, and vanishing, with a
  **flash at the moment of collision**.
- After the collision: the state point loops around the plane and **lingers in the ghost
  bottleneck** where the fixed points were; V(t) shows long, slow interspike intervals.
- **One more current step**: the bottleneck passage shortens and so does the ISI.
- Caption, exact text: **"arbitrarily slow firing is possible"**.
- Generated from the paper's modified Morris–Lecar model, CONTROL parameters (model.md).

Must not show
- No equations, no eigenvalues, no µA/cm² numbers. Phase-plane axes carry no tick numbers
  (stripped-down motif, as on the static).
- No ringing or spiral anywhere (there is none in this model at these currents; see §9).
- Do not call the rest point a "focus" and do not draw the unstable third fixed point.
- No title inside the video (the slide has one); only the small panel tag in §4.

## 4. Layout (frame 8.96 × 8 units; keep content inside x ±4.2, y ±3.75)

| Region | Box (x range × y range) | Content |
|---|---|---|
| Tag | top-left, anchor (−4.15, 3.45) | "Class 1 · SNIC", `BLUE_C`, font 32 |
| Rate readout | top-right, anchor (4.15, 3.45), right-aligned | "8 spikes/s" → "34 spikes/s", `WHITE`, font 32; hidden until the 2nd spike of each rate |
| Phase plane | x [−4.15, 0.05] × y [−2.45, 2.95] | axes `GREY_B` stroke 2, no ticks. Label "V" under the x-axis end; "w" at top of y-axis plus secondary "K⁺ activation" (`GREY_B`, font 24) rotated along it |
| V(t) | x [0.45, 4.15] × y [−1.05, 2.95] | model time 0–700 ms on x, V −80…+30 mV on y. No tick numbers; scale bars: "100 ms" horizontal and "20 mV" vertical (`GREY_B`, font 24) at lower right; thin dashed `GREY_D` line at 0 mV optional |
| Current strip | x [0.45, 4.15] × y [−2.35, −1.55] | I(t) staircase in `GREY_B` (injected current is not the shunt, so not `PURPLE_C`), stroke 3, no numbers; label "current" (`GREY_B`, font 24) at its left end |
| Caption | centred at (0, −3.3) | "arbitrarily slow firing is possible", font 40, `WHITE` |

Phase-plane display (hidden warp, from model.md): screen-x = asinh((V + 36)/8), screen-y = w^0.4.
Two windows, animated between with a ValueTracker (not a camera move, so V(t) is unaffected):
- **Knee window** (beats 1–3): V −47 … −31 mV, w 0.0003 … 0.012.
- **Full window** (beat 4 on): V −78 … +30 mV, w 0 … 0.36.

Elements and roles: V-nullcline `GREY_A` stroke 4; w-nullcline `PURPLE_A` stroke 4; rest point
filled dot (`WHITE` fill, radius 0.09); saddle open dot (`WHITE` stroke, black fill); at the
collision a half-filled dot for one frame, then the `RED_C` flash; state point `YELLOW` dot
(`Dot(fill_color=YELLOW)`, radius 0.08) with a `BLUE_C` trail (stroke 3, last ~60 ms of model
time fully opaque, older path at 35% opacity); ghost region: soft `BLUE_C` blob (fill 0.18, no
stroke) hugging the nullclines around the collision point, label "ghost" (`BLUE_C`, font 28,
italic if available). Labels "rest" and "saddle" (font 26, `GREY_B`) next to the two dots in the
knee window; they fade at the collision. Direct nullcline labels "V-nullcline" / "w-nullcline"
(font 26, their curve colors) in the full window only. V(t) trace `WHITE` stroke 3.

Persistent: axes, nullclines, V(t) axes, current strip, tag. The rest/saddle dots vanish at the
collision; the ghost blob persists to the end.

## 5. Beat sheet (model time → video: 1 video s = 50 ms model, constant except the collision hold)

| # | Video t (s) | Model t (ms) | On screen / motion | Text | Data |
|---|---|---|---|---|---|
| 1 | 0.0–1.0 | 0 (still) | Knee window. Nullclines at I = 38.0; rest dot + saddle dot, labels. State point on the rest dot. V(t) and current strip empty except a start dot at V = −42.0 mV | tag only | FP table I = 38.0 |
| 2 | 1.0–4.49 | 0–174.4 | Current ramps 38.0 → 38.5 → 38.7 → (toward 38.75). V-nullcline lifts; rest and saddle slide together (8.2 → 4.5 → 1.8 mV apart). State point rides the rest dot. V(t) creeps up −42.0 → −39.2 mV; current strip draws the staircase | "rest", "saddle" | schedule, FP positions each frame |
| 3 | 4.49–5.3 | hold at 174.4 | Collision: dots merge (half-filled for 2 frames) → `RED_C` flash ring at (−38.34 mV, w 0.00282), 0.3 s; labels fade | optional small "rest is gone" (`RED_C`, font 28) for 0.5 s | I_SN = 38.741 |
| 4 | 5.3–13.02 | 174.4–560 | Window zooms knee → full (5.3–6.8 s). Ghost blob fades in at the old merge site. State point crawls up the channel, then shoots round the big loop (spike), returns and crawls again. V(t): spikes at 272, 396.6, 521.2 ms (video 7.25, 9.74, 12.24 s) | "8 spikes/s" appears at 9.8 s | I = 38.75, ISI 124.6 ms |
| 5 | 13.02–15.62 | 560–690 | Current steps 38.75 → 39.0 (560–570 ms). V-nullcline lifts a little more; the channel widens; the loop repeats faster. Spikes at 577.5, 607.2, 636.9, 666.6 ms | readout → "34 spikes/s" at 14.0 s | I = 39.0, ISI 29.7 ms |
| 6 | 15.62–16.6 | hold at 690 | Caption writes in. Two ISI brackets on V(t) (`GREY_B`, font 24): over the 396.6→521.2 interval "125 ms", over 607.2→636.9 "30 ms" | "arbitrarily slow firing is possible" | spike times |
| 7 | 16.6–19.6 | — | Hold end frame (≥ 1 s required) | — | — |

Every outline item maps: phase plane + V(t) in sync (all beats), current steps + nullcline lift +
saddle/node slide (2), merge/vanish/flash (3), loops and lingering in the ghost, long ISIs (4),
one more step shortens the ISI (5), caption (6).

## 6. End frame (still-image fallback)

Full window. V-nullcline (at I = 39.0) in `GREY_A` and w-nullcline in `PURPLE_A`, labelled; the
closed spiking loop in `BLUE_C` (the 38.75 and 39.0 loops overlap almost exactly; draw both, the
older at 35% opacity); the `BLUE_C` ghost blob with the label "ghost" at the lower knee where
the curves nearly touch; no fixed-point markers at the knee. Right: V(t) over 0–690 ms, a flat
creeping start, three widely spaced spikes, then four closely spaced spikes, with brackets
"125 ms" and "30 ms"; staircase current strip below; readout "34 spikes/s"; caption at the bottom.

Correspondence to the deck static s05_v1 panel (a) ("Class 1 · SNIC"): same tag text and blue
class color, same nullcline roles, "ghost" shading at the lower knee where the nullclines are
tangent. Differences, intended: dark theme with light curves; the static draws the moment just
before the bifurcation (half-filled "saddle-node" dot, no loop) with a linear V / sqrt(w) scale
plus a magnified inset, while the video ends after the bifurcation (loop drawn, no dot) using
the asinh/power warp and no inset. The static's f–I and V_m thumbnails are not repeated here.

## 7. Data

| Element | Source in model.md |
|---|---|
| Nullclines per frame | `V_null(V, I(t), CONTROL)`, `winf(V, CONTROL)` at the current I(t) of the schedule |
| Rest / saddle dots | `fixed_points(I(t), CONTROL)`: out[0] = rest, out[1] = saddle (hide out[2]) |
| State point, trail, V(t) | one deterministic run of the schedule in model.md §"Schedule" |
| Current strip | the same I(t) |
| Rate readout, ISI brackets | spike times from that run |
| Ghost blob | centred on (V_SN, w_SN) = (−38.34, 0.00282), elongated along the w-nullcline ±4 mV |

## 8. Continuity

- `class2_hopf_onset_spiral_escape` — same layout, window logic, warp, colors and dot conventions; it
  plays right after this in the right-hand box. Keep them visually parallel.
- Deck static s05_v1 (panel a) and s05_v2 (valley icon, "slow crawl"): same story.
- `s09_vid1_spiral_vs_ghost` reuses CONTROL near the saddle-node (the "no ringing" half).
- `s09_vid2_frequency_geometry` starts from this tangential geometry (stage 1).
- `iv_curve_hump_flattens_snic_to_hopf`: I_SN = 38.741 is the local maximum of the CONTROL steady-state I–V
  curve (at V = −38.34 mV); cross-check if that topic quotes it.
- `s01_vid1_fi_curve_live`: the continuous f–I curve is the rate law measured here.

## 9. Accuracy flags

1. **The rest point is not always a "node".** For 37.68 < I < 38.634 µA/cm² the stable point has
   a complex eigenvalue pair (e.g. −0.36 ± 0.08i /ms at 38.0), i.e. formally a focus, but so
   overdamped (damping ratio 0.97) that no oscillation is visible. It is a true node only for
   I > 38.634. Label it "rest", never "focus"; the outline's "saddle and node" is fine as speech.
2. **The saddle only exists above 37.684** (it is born, together with the unstable third point,
   at V ≈ −31.6 mV). Do not start the video below 37.7.
3. **A third fixed point** (unstable node near −29 mV) survives the collision; the spiking loop
   goes around it. The static omits it; so does the video (the knee window excludes it).
4. "Arbitrarily slow" is true of the model: f ≈ 85·√(I − I_SN) Hz near onset (5.5 Hz at +0.004,
   8.0 Hz at +0.009 µA/cm²). Real cells cannot show 0 Hz (channel noise); the paper argues from
   the *rise* of f_min, not from a literal 0 (paper Results, f–I section).
5. The knee sits at w ≈ 0.003, invisible on a linear 0–0.35 axis; the hidden warp is what makes
   the collision and the ghost readable. The warp is monotone, so tangency and topology are kept.
6. Honest time: keep 1 video s = 50 ms during beats 4–5, so the crawl is real speed; ~92% of each
   124.6 ms ISI at I = 38.75 is spent with V between −44 and −34 mV.

## 10. Acceptance checklist

- [ ] First frame: knee window, two nullclines, filled "rest" dot and open "saddle" dot, tag.
- [ ] During beat 2 the V-nullcline visibly rises and the two dots approach each other.
- [ ] One `RED_C` flash exactly where the dots merge; both dots gone afterwards.
- [ ] Zoom to the full window completes before the first spike.
- [ ] The yellow state point visibly slows near the old merge site and races round the loop.
- [ ] V(t): 3 widely spaced spikes, then 4 closer ones; brackets read "125 ms" and "30 ms".
- [ ] Readouts show "8 spikes/s" then "34 spikes/s".
- [ ] Caption text exact; no equations or tick numbers; no spiral.
- [ ] Colors: nullclines `GREY_A`/`PURPLE_A`, trail `BLUE_C`, state point `YELLOW`, flash `RED_C`.
- [ ] End frame held ≥ 1 s and matches §6; total length ≤ 20 s.
- [ ] `main.py` asserts the model numbers in model.md (I_SN, spike times ±0.5 ms).
