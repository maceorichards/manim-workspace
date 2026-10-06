# Video contract — "Class 2: the whirlpool lets go"

## 1. Header

| | |
|---|---|
| Deck id | `s05_vid2` |
| Title | Class 2: the whirlpool lets go |
| Scene class | `Class2HopfOnset` |
| Placement | outline slide 5, build slide **5c, right box** (5.95 × 5.3 in). Left box = `s05_vid1` (class 1), played first |
| Duration | ~20 s (target 19.2 s; hard cap 25 s) |
| Audio | silent |
| Playback | click-to-play; first frame must read on its own when paused |

Sources: deck outline, slide 5 (video 2, content table, "Say", "If asked"), slide 6 (model), and
Assembly notes; deck build manifest; deck build contract §6; deck static figures s05_v1 and
s05_v2 with status notes; deck static figure s09_v3 status notes; paper Methods, Fig. 4A and
Fig. 5A/5B legends. All read 2026-09-29.

## 2. Purpose

Takeaway: **in a class 2 cell the rest point is a spiral (a focus). Below threshold a kick makes
it ring on the way back; as current rises the ringing dies more slowly; at threshold the spiral
stops pulling in and pushes out, and the cell jumps straight to fast repetitive firing. It is
already turning at ~100 Hz when it lets go, so it cannot start slowly.** The subthreshold
ringing and the minimum firing rate are the same fact seen twice.

Place in the talk: plays right after `class1_snic_onset_slow_crawl` on slide 5c, as the second half of the slide 5
table (class 2 row: outward net current at threshold, Hopf, whirlpool analogy, f_min, ringing,
frequency preference). Sets up slide 9 (MPOs are this ringing, driven by noise) and slides 7–11
(this is the shunted model: g_shunt 2 → 4). Thesis: *integrator vs resonator is decided by the
sign of the net current near threshold, set by the synaptic background, not by the cell.*

## 3. Must show / must not show

Must show
- Same layout as `class1_snic_onset_slow_crawl`: V–w phase plane left, V(t) right, in sync, current strip below V(t).
- Below threshold: a small kick sends the state point spiralling back into the focus while V(t)
  shows damped ringing. Three kicks of equal size at three rising currents, with visibly slower
  decay each time.
- At the Hopf point the focus turns unstable (filled → open dot, flash), the state spirals
  outward and jumps onto the large limit cycle; V(t) goes straight to repetitive spiking at a
  high rate with no slow first interval.
- Caption, exact text: **"already turning when it lets go"**.
- The paper's modified Morris–Lecar, SHUNT parameters (control + 2 mS/cm² shunt), so the picture
  matches the model of slides 7–11.

Must not show
- No equations, eigenvalues or µA/cm² values; no phase-plane tick numbers.
- Do not label the firing rate after the Hopf as "f_min" (see §9.1). Do not imply θ frequencies.
- No noise in this video (kicks only); noise-driven ringing is slide 9.
- No title inside the video; only the panel tag.

## 4. Layout (identical grid to `class1_snic_onset_slow_crawl`)

| Region | Box | Content |
|---|---|---|
| Tag | anchor (−4.15, 3.45), left | "Class 2 · Hopf", `ORANGE`, font 32 |
| Readout | anchor (4.15, 3.45), right | line 1 "rings at ≈ 100 Hz" (`ORANGE`, font 30) from kick 2 on; line 2 "fires at ≈ 110 spikes/s" (`WHITE`, font 30) below it, from the 3rd spike |
| Phase plane | x [−4.15, 0.05] × y [−2.45, 2.95] | as in `class1_snic_onset_slow_crawl`: `GREY_B` axes, no ticks, "V", "w" + "K⁺ activation" |
| V(t) | x [0.45, 4.15] × y [−1.05, 2.95] | model time 0–260 ms. y range **animated**: −36 … −24 mV until the escape, then −80 … +30 mV. Scale bars "10 ms" and "2 mV" (switch to "20 mV" after the zoom-out), `GREY_B`, font 24 |
| Current strip | x [0.45, 4.15] × y [−2.35, −1.55] | I(t) in `GREY_B`, stroke 3, label "current"; kicks drawn as `RED_C` upward triangles (size 0.12) at the kick times, label "kick" next to the first |
| Caption | centred (0, −3.3) | "already turning when it lets go", font 40 |

Phase-plane display: same hidden warp as `class1_snic_onset_slow_crawl` (screen-x = asinh((V + 36)/8),
screen-y = w^0.4). Windows:
- **Focus window** (beats 1–5): V −40 … −24 mV, w 0.004 … 0.026.
- **Full window** (beat 6 on): V −78 … +30 mV, w 0 … 0.36 (same as `class1_snic_onset_slow_crawl`).

Elements: V-nullcline `GREY_A` stroke 4; w-nullcline `PURPLE_A` stroke 4; focus = filled dot
(`WHITE` fill) while stable, open dot (`WHITE` stroke) once unstable; label "focus" (font 26,
`GREY_B`); state point `YELLOW` (`Dot(fill_color=YELLOW)`); trail `ORANGE` stroke 3 (last ~15 ms
of model time opaque, older at 35%); kick = dashed `RED_C` arrow from the focus to the kicked
point (+1.2 mV along V), shown 0.4 s; Hopf flash = `RED_C` ring on the focus.

## 5. Beat sheet (1 video s = 20 ms model; slowed to 1 s = 10 ms during the escape)

| # | Video t (s) | Model t (ms) | On screen / motion | Text | Data |
|---|---|---|---|---|---|
| 1 | 0.0–1.0 | 0 (still) | Focus window, nullclines at I = 110, filled focus, state on it; V(t) zoomed, flat at −34.0 mV | tag, "focus" | FP at 110 |
| 2 | 1.0–2.25 | 0–25 | Kick 1 at 5 ms (video 1.25): +1.2 mV; state swings back with barely one loop; V(t) one overshoot (2nd peak 0.11 mV) | "kick" | I = 110, λ = −0.241 ± 0.599i |
| 3 | 2.25–5.0 | 25–80 | Current ramps 110 → 112.5 (25–45 ms); nullcline shifts, focus moves up-right. Kick 2 at 50 ms (video 3.5): spirals in over ~3 turns; V(t) peaks 1.39, 0.53, 0.20 mV | "rings at ≈ 100 Hz" appears at 4.0 s | I = 112.5, λ = −0.099 ± 0.634i |
| 4 | 5.0–9.25 | 80–165 | Ramp 112.5 → 114.0 (80–100 ms). Kick 3 at 105 ms (video 6.25): spiral barely shrinks (peaks 1.64, 1.46, 1.31 mV …), still ringing at the end | — | I = 114.0, λ = −0.013 ± 0.650i |
| 5 | 9.25–9.81 | 165–168.2, then hold 0.4 s | Ramp 114 → 115 starts; at 168.23 ms the current passes the Hopf point: focus dot turns open, `RED_C` flash | — | I_Hopf = 114.236 |
| 6 | 9.81–12.65 | 168.2–210 | The ring grows instead of decaying (peaks −29.9, −29.0, −25.8 mV at 174, 184, 195 ms); from 195 ms time slows 2× and both windows zoom out (phase plane → full; V(t) → −80…+30) while the state jumps onto the big loop; first spike at 203.9 ms (video 12.04) | — | I = 115 |
| 7 | 12.65–15.15 | 210–260 | Repetitive spiking on the loop, spikes at 212.8, 221.8, 230.7, 239.7, 248.6, 257.6 ms | "fires at ≈ 110 spikes/s" at 13.3 s | ISI 8.95 ms (111.7 Hz) |
| 8 | 15.15–16.15 | hold | Caption writes in | "already turning when it lets go" | — |
| 9 | 16.15–19.15 | — | Hold end frame | — | — |

Outline mapping: kick → spiral back + damped ringing (2); ringing decays more slowly as current
rises (2 → 3 → 4); focus turns unstable at the Hopf (5); spirals outward, jumps to the large
limit cycle, straight to repetitive spiking (6–7); caption (8).

## 6. End frame (still-image fallback)

Full window: V-nullcline (at I = 115) `GREY_A`, w-nullcline `PURPLE_A`, open (unstable) focus at
the crossing just right of the lower knee, labelled "focus"; the three kick spirals remain as
faint `ORANGE` loops around it (35%), and the outward spiral leads onto the large closed `ORANGE`
loop. V(t) at full scale: a nearly flat start with small ripples, then a dense run of spikes;
current strip with its steps and the three kick triangles; readout lines "rings at ≈ 100 Hz" and
"fires at ≈ 110 spikes/s"; caption.

Correspondence to deck static s05_v1 panel (b) ("Class 2 · Hopf"): same tag and orange class
color, nullclines crossing at an angle just right of the knee, an orange spiral around a focus.
Differences, intended: dark theme; the static shows the stable focus just below the Hopf
(I = 113) with an inset, linear V / sqrt(w) scale and no limit cycle; the video ends above the
Hopf (open focus, limit cycle drawn, asinh/power warp). Optional (Open question): a small inset
in the V(t) panel that keeps the zoomed ringing visible in the end frame.

## 7. Data

| Element | Source in model.md |
|---|---|
| Nullclines | `V_null(V, I(t), SHUNT)`, `winf(V, SHUNT)` |
| Focus dot, stable/unstable | `fixed_points(I(t), SHUNT)[0]`; open once Re λ > 0 (I > 114.236) |
| State point, trail, V(t), kicks | the one deterministic schedule run in model.md |
| Readouts | ringing ≈ 95–104 Hz from Im λ (model.md table), spiking 111.7 Hz from ISIs |

## 8. Continuity

- `class1_snic_onset_slow_crawl`: partner video, identical grid, warp, full window, dot conventions.
- Deck static s05_v1 (panel b) and s05_v2 (whirlpool icon, "already turning when it lets go").
- `s09_vid1_spiral_vs_ghost`: the same SHUNT focus with noise instead of kicks (I = 112.5).
- `s09_vid2_frequency_geometry`: the SHUNT stage (g_shunt = 4) of the frequency ladder.
- Deck static s09_v3 used the same SHUNT operating point (112.5) and labels ringing "≈100 Hz".

## 9. Accuracy flags

1. **"Straight to repetitive spiking at f_min" is not what happens at the Hopf.** Just above the
   Hopf the model fires at ≈ 105–112 spikes/s (104.9 at I_Hopf, 111.7 at 115). The minimum rate
   f_min ≈ 78–80 spikes/s exists only inside the bistable window 113.14–114.24, where rest is
   still stable and spiking must be started by a large enough push (paper Fig. 5B). The honest
   message, and the caption, is "already turning when it lets go": ringing at 103.5 Hz just below
   vs firing at 104.9 Hz at the Hopf. Readouts avoid the word f_min.
2. **Deck build contract §6 says f_min ≈ 90–100 Hz.** Measured here: the spiking branch ends at
   I ≈ 113.137 with rate 78–80 spikes/s (80.1 at 113.14), matching the paper (Fig. 4A: shunted
   f_min 80 spikes/s; Fig. 5B: f_min ≈ 77, max MPO ≈ 103 Hz, Δf ≈ 25 Hz).
3. **~100 Hz, not θ.** This model's fast K⁺ spiral rings near 100 Hz; the paper says so and fixes
   it on slide 11 with slow I_M. Show Hz honestly; never put a θ label here.
4. **Kicks are instantaneous +1.2 mV steps** (brief current pulses), not noise. Spike threshold for
   a kick is 4.9 / 3.4 / 2.1 mV at I = 110 / 112.5 / 114; a 1.2 mV kick is safe (a 2.2 mV third
   kick would fire). I = 114 lies in the bistable window, which is why the kick must stay small.
5. Current steps also nudge the state off the focus (small step responses, ≤ 0.3 mV); they are
   real model behaviour and may stay visible.
6. The unstable limit cycle that separates the basins (subcritical Hopf) is not drawn.

## 10. Acceptance checklist

- [ ] First frame: focus window, nullclines crossing at an angle, filled "focus", tag.
- [ ] Three equal kicks (red triangles, dashed red arrow), each followed by a spiral back.
- [ ] Ringing clearly lasts longer after each kick (V(t) zoomed scale shows it).
- [ ] The focus dot turns open with a red flash at the Hopf crossing.
- [ ] The ring visibly grows, then the state jumps to the big loop during the zoom-out.
- [ ] V(t): no slow first interval; spikes about 9 ms apart; readout "fires at ≈ 110 spikes/s".
- [ ] Caption text exact; no "f_min" label; no equations, ticks or θ.
- [ ] Colors: trail `ORANGE`, state `YELLOW`, kicks and flash `RED_C`, nullclines `GREY_A`/`PURPLE_A`.
- [ ] End frame held ≥ 1 s, matches §6; total ≤ 20 s; grid identical to `class1_snic_onset_slow_crawl`.
- [ ] `main.py` asserts I_Hopf and spike times from model.md.
