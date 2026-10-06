# Workbench — eigenvalues_integrator_vs_resonator

Context: `context_files/contract.md` (the build contract), `model.md`, `science.md` and
`style.md`. Sources: see `SOURCES.local.md` (deck spec, slide 3).

## Decay vs ring: from eigenvalues to the phase plane

Status: Building (Part 1 v2 rendered 2026-10-01; awaiting review)
Scenes: EigenvalueDecayVsRing, PhasePlaneCurrentSteps, PulsePairIntegratorVsResonator (concatenated → videos/eigenvalues_integrator_vs_resonator.mp4)

### Intent

In ~98 s (1920×1080, 60 fps): real λ means decay and complex λ means ring (a cartoon complex
plane); in the paper's V–w phase plane, current moves the fixed point, and class 1 slides then
crawls past the ghost while class 2 rings then spirals out and fires fast; a pulse-pair test
separates integrator from resonator.

### Decisions in force

- Workspace look; colours from `prescott2008.py`. Three scene classes, concatenated with ffmpeg
  (`-c copy`).
- Part 1 has Re on the vertical axis, aligned with the trace, plus a projector line. It is the
  only rotating complex point in the deck.
- Part 1 v2 (user review, 2026-10-01). The v1 stash (`scratch/v1_2026-09-30/`) was deleted on
  2026-10-01 at the user's request.
  - Class 1 rungs λ = −5 / −1 / −0.2; the −20 rung is cut.
  - Every rung-to-rung transition is a 0.3-s hold on the finished trace, then a 0.5-s reset.
    Old ticks fade out in the first half and new ticks fade in during the second half, so the
    labels never overlap.
  - Each section's caption is up 1.5 s before its dynamics start: cap1 from frame 0, then the
    Im λ caption and the "Re λ sets how fast the voltage decays." caption.
  - The rotation sweep is 4.5 s of model time (9 s of video), down from 6 s. It is still
    2 → 8 → 2 Hz at ×½.
  - Class 2 ladder σ = −2 / −5 (windows 2 / 1 s); the −20 rung is cut.
  - No outro caption: Part 1 fades to black over 1 s and holds black for 0.2 s. The user
    dropped the axes-swap warning.
- Class 1 staircase 0.25/0.5/0.75/0.9×, then 1.0005× (×1/10). Class 2 0.75/0.9/0.97/0.99×, then
  **1.002×** (×1/25), because 1.02× fires in 3.4 ms with no visible spiral.
- Part 3 at **×1/25**, because ×1/20 would give 11.6 frames per ring cycle. A₁ = 48.0 / 12.5;
  the grid is ✓✓ ✗✗ ✗✓ ✗✓.
- All model runs are precomputed into `eigenvalues_integrator_vs_resonator/cache/` (`P.npz_cache`, recipe in meta).
- 60 fps comes from `default_camera_config = dict(fps=60)` on each scene (the `FrameExact`
  mixin), not from `--fps` (which crashes 1.7.2); the mixin also rounds every play/wait to a
  whole number of frames.
- Shared screen builders at module level: `header`, `speed_badge`, `chip`, `caption` (bottom
  band, y = −3.42), `label`/`tlabel`. Header top-left, badge top-right, chip under the header.
- Part 1: panels share one scale (2.0 units per unit of z); the rotation beat holds the last
  1.5 s of model time (scrolling ticks); kick = red arrow + label for 0.7 s of video.
- Part 2: model time frozen during each 1-s zoom-out (zoom starts when the state first leaves
  the subthreshold view). Layout, lifts and labels: see "Part 2 restyle" below (supersedes the
  v1 legend, current panel and captions).
- Part 2: the class 2 onset continues from the end state of the 0.99× step (not the exact
  fixed point), so the trajectory is continuous: first spike at 53.9 ms, 5 pre-spike peaks
  (model.md, from the exact fixed point, lists 64.2 ms and 6).
- Part 3: V(t) y-ranges are per class (class 1 −50…−30, class 2 −37…−25.5 mV) so the 2–3 mV
  ring is visible; spikes clip. The Δt readout sits in the header row between the two column
  headers. The ring bracket is drawn on a dashed single-pulse trace during the Δt = 10 hold.
- Time snapshots: `scratchpad/eigenvalues_integrator_vs_resonator/tsnap.py file Scene t1 t2 … --hd` (frames at scene
  times, same skipped-pass trick as snapshot.py). Not part of the repo.

### Checklist

- [x] Asserts from `model.md` pass and print their values (including the frames-per-cycle check)
  - Outcome: kept — all PASS; fpc min 14.0 (class 2 firing at ×1/25).
- [x] Part 1 layout: square complex plane + aligned trace panel + projector + sliders + header + footnote
  - Outcome: revised — horizontal tick labels moved above the Im axis (collided with the rest
    label), notes right-aligned at the trace panel top (collided with δV), readout parens
    centred on the number.
- [x] Part 1 class 1 ladder (1×), rotation beat (×½, 2→8→2 Hz), class 2 ladder (×½), fade
  - Outcome: revised — play-level `rate_func=linear` overrode the squished caption fades (old
    caption lingered at 50%); the linear rate now goes on the tracker animation only.
- [x] Part 2 Step 1: nullclines + a sliding fixed point, no trajectory
  - Outcome: kept — live λ chip (DecimalNumber, no thousands commas) + I_stim readout.
- [x] Part 2 Step 2: class 1 staircase, freeze + nullcline lift + saddle merge, crawl past the ghost, zoom out
  - Outcome: revised — legend moved out of the plot; ghost label anchored per window (left of
    the V-nullcline in the subthreshold view, inside the limit cycle after the zoom) with a leader.
- [x] Part 2 Step 3: class 2 staircase with visible rings at 0.97/0.99×, spiral opens at 1.002×, zoom out, fast firing
  - Outcome: kept — ring visible in the phase plane; V(t) at −75…+25 shows it only as a wiggle.
    The growing spiral pokes above w = 0.015 for its last ~2 cycles (clipped) before the zoom.
- [x] Part 3: two columns, four simultaneous trials with ✓/✗ stamps, ring bracket, ✓/✗ grid end frame
  - Outcome: revised — dimming by setting opacity filled the stroke-only curves; replaced by a
    black overlay at 80%.
- [x] Timing per part; totals ≈ 34 / 44 / 22 s
  - Outcome: kept — scene clocks 34.40 / 43.80 / 22.43 s.
- [x] Final `--hd` 60 fps renders, concat, end PNG; ffprobe check
  - Outcome: kept — 1920×1080, 60/1 fps: Part 1 2064 frames (34.40 s), Part 2 2628 (43.80 s),
    Part 3 1346 (22.43 s); concat 6038 frames, 100.63 s. End PNG = last frame of Part 3.
    First frames of Parts 2/3 showed updater-driven ticks/dots at full opacity over black (the
    updaters overrode FadeIn); now multiplied by an intro-opacity tracker. Part 1 opens on the
    full layout so the paused first frame reads.

- [x] Part 1 v2: class 1 ladder without the λ = −20 rung, with longer transitions
  - Outcome: revised — at the first 0.5-s reset, the old and new tick labels overlapped
    ("0.4" over "1"). Sequential tick fades fixed it (frames at 3.05 / 3.3 s).
- [x] Part 1 v2: 1.5-s caption leads (cap1, the Im λ sweep, the class 2 decays)
  - Outcome: kept — frames at 1.4, 12.7 and 23.4 s show each caption alone over an empty
    trace panel.
- [x] Part 1 v2: faster Im λ sweep
  - Outcome: kept — at 17 s it reads 7.9 Hz with a clean scrolling trace. 15 frames/cycle at
    8 Hz.
- [x] Part 1 v2: class 2 σ −2 / −5, new caption
  - Outcome: kept — σ = −2 reads ×0.67 per cycle, and the envelope is near zero by 2 s.
- [x] Part 1 v2: fade to black
  - Outcome: kept — at 31.0 s everything dims with no caption; the concat is black at 31.55 s,
    and Part 2 fades in from black.
- [x] Part 1 v2: final render
  - Outcome: kept — `EigenvalueDecayVsRing.mp4` is 1896 frames (31.60 s), 1920×1080, 60/1 fps.
    The concat `eigenvalues_integrator_vs_resonator.mp4` is 5870 frames (97.83 s); the end PNG (Part 3) is
    unchanged.

### Deviations from contract.md (Part 1)

- Beat sheet:
  - class 1 has three rungs, not four
  - captions lead their dynamics by 1.5 s
  - the rotation is 4.5 s, not 6 s
  - class 2 is σ −2 / −5, not −1 / −5 / −20 (per-cycle factors 0.67 / 0.37)
  - no "Now the real model" caption
  - Part 1 is 31.6 s, not 34 s
- The caption "Re λ sets how fast the ring dies." is now "Re λ sets how fast the voltage
  decays."

### Open questions

- Part 2 zoom: model time is frozen during the 1-s zoom (the contract does not say whether the
  clock keeps running); freezing keeps the first spike legible.

### Parking lot

- Mark the ISI on the class 1 V(t) (88 ms) and the class 2 ISI (9.3 ms) with brackets.

## Part 2 restyle: SNIC/Hopf look

Status: Building (all items built, verified and rendered 2026-10-01; awaiting review)
Scenes: PhasePlaneCurrentSteps

The approved restyle (step functions, ghost label) is stashed in `scratch/part2_v2_2026-10-01/`
(gitignored): `main.py`, `WORKBENCH.md`, `PhasePlaneCurrentSteps.mp4` and the 100.9-s
`eigenvalues_integrator_vs_resonator.mp4`. The pre-restyle stash was deleted at the user's request. Style references (read only, not edited): `class1_snic_onset_slow_crawl`,
`class2_hopf_onset_spiral_escape`.

### Intent

Part 2 should read as the SNIC video followed by the Hopf video. It keeps three things those
lack: nullcline labels in every view, the λ box, and a loud moment where the fixed point loses
stability (Re λ crosses 0). It should look less cramped than v1.

### Decisions in force

- Phase plane in the s05 warp: x = asinh((V + 36)/8), y = sign(w)|w|^0.4 (signed, so the
  V-nullcline's negative-w part clips below the view instead of lying along w = 0). No numeric
  ticks; italic V and w at the arrow tips, small rotated "K⁺ activation".
- Windows: subthreshold `P2_SUB_WIN` V −80…−17, w 0…0.024 (about 20% wider than v1 in warped
  units); full view = the limit-cycle window ×1.2 in warped units (`P2_ZOOM_OUT`), never left of
  −90 mV (`P2_V_MIN`, the V-nullcline has a pole at E_K = −100). A small floor below w = 0 keeps
  rest off the axis. Plot top lowered to y = 1.9 so the 2-line chip clears the `w` letter.
- The zoom-out starts when the state first leaves the subthreshold view (either edge).
- Part 3 keeps its own linear `SUB_WIN`; the Part 2 windows are separate constants.
- Nullcline labels ("V-nullcline", "w-nullcline", no equations) ride on their curves: each
  sits beside the point where its curve crosses a set height of the plot (`NULL_LABEL_SPEC`,
  per class and view). A label that changes side between views fades through mid-zoom.
- No ghost text (user): the class 1 halo stays, unlabelled; the class 1 end caption is
  "arbitrarily slow firing".
- Staircase steps are raised-cosine ramps over `RAMP_MS` = 5 ms (0.2 s of video at ×1/40) in
  the model and on screen, not jumps. 5 ms keeps the class 2 rings (first overshoot 2.19 /
  1.41 mV at 0.97 / 0.99×; 8 ms drops the 0.99× ring to 0.92 mV, below the ≥ 1 mV check). The
  onset steps stay as the frozen on-screen lifts.
- Keep the λ chip (top-left) and the speed badge (top-right).
- Re λ crossing, both classes: freeze model time, lift the current to I_bif with a live chip,
  then a thick red ring flash (0.7 s) and a 0.3 s hold. Class 1: half-filled dot for 2 frames
  at the merge; the chip shows only "slowest λ" (real value; the imaginary part of the
  0.93–0.999× damped focus is never written, per the user) and turns red at 0. Class 2: chip
  "λ = Re ± Im i" with three second lines (Re < 0 dies out / Re = 0 on the edge / Re > 0
  unstable — the spiral opens); then 1.0 → 1.002× and the focus opens.
- Live chips (digits change mid-play) fade through their own `vis` opacity (`chip_fade`):
  ManimGL animations do not suspend updaters, so a Transform fade breaks on the point count.
- Every swap (chips, captions, header, badge, scale bars at the class change) is out-then-in.
- Fixed points white (stable: rim stroke 6, so the state dot reads on top), open = black fill;
  grey labels: class 1 always "rest" (never "focus"), "saddle" UL; class 2 "rest"/"focus",
  DR in the subthreshold view, UL in the full view (clear of the loop).
- Trail: class colour, last 30 ms opaque, older at 35%, yellow state dot drawn on top.
- Right column: V(t) and current build up over the whole class run (500 / 320 ms), no ticks;
  scale bars 20 mV / 100 ms (class 1) and 5 → 20 mV / 50 ms (class 2, V(t) zoomed to
  −48…−26 mV until the zoom-out); "current" strip 0–1.1 I_bif with the dashed I_bif line.
- Text: tags "Class 1 · SNIC" / "Class 2 · Hopf"; readouts under the badge (≈ 11 spikes/s;
  rings at ≈ 102 Hz → fires at ≈ 107 spikes/s); captions: one short sweep line, then one per
  class written in at its end hold. Part 3 keeps its own headers.
- Part 2 is 46.83 s (was 43.80): the class 2 lift + flash adds ~3 s.

### Checklist

- [x] (batch 1) Warped plane, both windows about 20% wider, no numeric ticks, s05 axis labels
  - Outcome: kept — the class 1 and class 2 loops now fill the plot with the knee still
    readable underneath (v1's full view pressed rest flat onto w = 0). The first widening
    reached −109 mV, past the V-nullcline pole at −100, which drew a spurious branch, so the
    window is capped at −90. The wider view also shows the upper unstable fixed point (open
    circle, top right) during the class 1 lift and crawl; it is real.
- [x] (batch 1) Inline nullcline labels in every view (sub and full, both classes), replacing
  the legend
  - Outcome: revised — each spot was moved off what crosses it in the frames: the saddle's
    path in the lift, the V-nullcline's right branch at 0.9×, the class 2 spiral and fixed
    points, the ghost label. Final: V label right of the left branch high up; w label
    up-left of the curve near the top (class 1 sub), below the curve at 0.3 (class 2 sub),
    upper right (class 1 full), inside the loop (class 2 full). Frames 0.9–43 s clean.
- [x] Re λ crossing, class 2: freeze, lift 0.99 → 1.002× with a live λ chip, red flash, focus opens
  - Outcome: revised — the first 0.4-s, 6-px flash was barely visible at its midpoint; now
    10 px, grows 0.85, 0.7 s. Added the "Re λ = 0: on the edge" line, because the chip sat at
    "+0" with "dies out" during the flash.
- [x] Re λ crossing, class 1: half-filled dot + red ring at the merge
  - Outcome: kept — chip reaches a red 0 at the merge; half dot then flash read in order
    (frames 16.0 / 16.22 / 16.4).
- [x] Class-coloured trail that builds up + yellow state dot
  - Outcome: revised — the state dot rendered under the white fixed point; it is now re-added
    on top after setup.
- [x] White fixed points + grey labels
  - Outcome: revised — class 1 near threshold was labelled "focus" (it is a damped focus
    0.93–0.999×), which hints at a ring we promise not to show; class 1 is always "rest". The
    class 2 "focus" label sat on the ring trail (DR) and on the loop (full view); moved.
- [x] Right column, s05 style
  - Outcome: revised — the I_bif label collided with the "100 ms" bar label; the strip moved
    down 0.2. The 5/20 mV bars cross-faded text on text mid-zoom; now one at a time.
- [x] Lighter text
  - Outcome: kept — readouts fit under the badge; captions in the bottom band, one at a time.
- [x] Chip swaps out-then-in
  - Outcome: kept — also fixed the class change (header, badge, bars faded in sequence) and
    the final fade (live chip faded via `chip_fade`; plain `FadeOut` left it bright).
- [x] Continuous current steps (5-ms raised-cosine ramps)
  - Outcome: kept — mid-ramp frames (11.4, 31.4 s) show the fixed point gliding with the state
    trailing it and sloped edges on the current strip; the class 2 rings still read (33.5 s).
    Class 2's first spike moves 53.9 → 54.6 ms; all acceptance checks pass.
- [x] Remove the ghost label, its leader and the ghost caption
  - Outcome: kept — halo only in the crawl and full view (18.0, 24.0 s).
- [x] Final `--hd` render of Part 2 + re-concat (old versions deleted from `videos/`; copies in
  the stash)
  - Outcome: kept — `PhasePlaneCurrentSteps.mp4` 2810 frames (46.83 s), 1920×1080, 60/1 fps;
    concat `eigenvalues_integrator_vs_resonator.mp4` 1896 + 2810 + 1346 = 6052 frames (100.87 s). Frames from the
    concat at 32.3 / 48.0 / 68.5 / 78.9 s read correctly; end PNG (Part 3) unchanged.

### Deviations from contract.md (Part 2)

- Warped phase plane without numeric ticks; windows ~20% wider than the contract's.
- Nullcline labels inline, without "dV/dt = 0" / "dw/dt = 0".
- No ghost label (the contract asks for "ghost of the fixed point: slow passage → long ISI").
- Staircase steps ramp over 5 ms instead of jumping (each ramp still acts as the kick).
- Fixed points white (not class-coloured); trail in class colour, builds up (not a 30-ms
  yellow tail).
- V(t) builds up over the whole class run (no scrolling, no tick axes); current strip without
  µA/cm² or pA numbers; class 2 V(t) zoomed until its zoom-out.
- Headers "Class 1 · SNIC" / "Class 2 · Hopf"; captions shortened; readouts added.
- Live chips during both lifts (class 1 shows only the slowest eigenvalue's real value);
  class 2 adds a frozen lift through I_bif. Part 2 is 46.8 s, not ~44 s.

### Open questions

- Part 3's small planes are still linear with ticks and v1 headers; at the 2→3 join the style
  visibly changes. Restyle Part 3 to match?

### Parking lot

- s05 lens ghost with an italic "ghost" label instead of the halo + leader.
