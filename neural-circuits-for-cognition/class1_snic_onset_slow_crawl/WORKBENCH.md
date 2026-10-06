# Workbench — class1_snic_onset_slow_crawl

Context: `context_files/contract.md` (the video contract), `science.md`, `model.md`, `style.md`.

## Class 1: rest vanishes, the ball crawls

Status: Built (final render `videos/class1_snic_onset_slow_crawl.mp4`, 1344×1200, 30 fps, 19.67 s)
Scenes: Class1SnicOnset

### Intent
Show that class 1 rest disappears by a collision of the rest point and the saddle, after which
the trajectory crawls through the ghost of the collision, so firing can be arbitrarily slow.

### Decisions in force
- Paper's model, CONTROL (g_shunt = 2, no adaptation), exact 2-D (V, w); one deterministic run of
  the schedule in model.md drives everything (current 38.0 → 38.5 → 38.7 → 38.75 → 39.0 µA/cm²).
- Everything is updater-driven from two trackers: model time T and window zoom Z (plus opacity
  trackers for the ghost and the full-window labels). `FadeIn` is not used on anything whose
  points an updater rebuilds, because the Transform would freeze its points.
- Layout: phase plane left, V(t) right with a current staircase below; tag "Class 1 · SNIC".
  V(t) maps −80…+30 mV into y [−0.45, 2.45] so the L-shaped scale bars (lower right, corner
  at x 4.15) sit wholly below the −73 mV troughs. The brackets sit above the +25 mV peaks.
- "current" label sits just above the strip's left end, not beside it, because the V(t) box
  starts at x 0.45 and leaves no room to the left.
- Hidden warp screen-x = asinh((V+36)/8), screen-y = w^0.4. Knee window, then zoom to the full
  window after the collision. The window zooms with centre linear and size geometric over
  1.5 s (smooth), so it finishes at model 249 ms, before the first spike at 272.
- Time: 1 video s = 50 ms model during the dynamics. The model is paused 0.81 s at the
  collision: half-filled dot for 2 frames, then a 0.3 s RED_C ring, then a still.
- Open question "rest is gone" label → **omitted**: the contract marks it optional, and the flash
  plus the vanishing dots carry the moment (on-screen-text rule: nothing a speaker would say).
- Open question readout unit → **"spikes/s"**: this is the contract's exact text. Values are
  computed from the run's ISIs (8, 34).
- Open question rest dot at 38.0/38.5 → **kept the contract's schedule**. The dot is labelled
  "rest", never "focus" (contract §9.1); the overdamped focus shows no visible ringing.
- Rest dot: white fill r 0.09 **plus a white stroke 8** rim; state point r 0.08 with a thin black
  outline. Without the rim, the yellow state point hid the rest dot in the first frame.
- Optional dashed 0 mV line: omitted (minimal chrome).
- Readout swap: "8 spikes/s" fades out over 3 ms of model time and "34 spikes/s" then fades
  in. A crossfade overlapped the digits.
- Colors: nullclines `GREY_A` / `PURPLE_A`, trail `BLUE_C` (older than 60 ms at 35%), state
  point `YELLOW`, flash `RED_C`, secondary text and axes `GREY_B`.

### Checklist
- [x] Beat 1: first frame (knee window, rest + saddle dots, labels, tag) reads when paused
  - Outcome: revised. The yellow state point hid the rest dot, so I added a white rim. The
    first frame now shows the filled rest dot with yellow inside it, the open saddle, the
    labels, the tag, the V(t) start dot and the scale bars.
- [x] Beat 2: nullcline lift and the two dots sliding together over 3.5 s
  - Outcome: revised. The labels collided at the merge; rest is now at DR and saddle at UL.
    At t = 2.5 s the gap is visibly smaller, and at 4.45 s the dots coincide.
- [x] Beat 3: collision flash at (−38.34 mV, 0.00282) and dots removed
  - Outcome: revised. The `Sector` half-disk rendered unfilled, so I replaced it with a
    Polygon. The ring flash is centred on the merge point (frames 4.55–4.75 s), and the
    labels fade out with it.
- [x] Beat 4: zoom to full window before the first spike; visible crawl in the ghost; 3 slow spikes
  - Outcome: kept. The zoom is done by 6.8 s and the first spike comes at 7.25 s. The
    "ghost" label brushed the x-axis mid-zoom, so it now fades in after the zoom along with
    the nullcline labels.
- [x] Beat 5: step to 39.0; 4 faster spikes; readout changes to "34 spikes/s"
  - Outcome: revised. Only the readout crossfade changed (now fade out, then fade in). The
    frame at 14.1 s shows a clean "34 spikes/s".
- [x] Beat 6–7: caption, ISI brackets, end frame held 3 s; total ≈ 19.6 s
  - Outcome: kept. Total is 19.67 s. The last frame matches §6: loop, ghost and labels,
    brackets "125 ms" and "30 ms", "34 spikes/s", and the caption.
- [x] Asserts in `main.py` for I_SN and spike times (model.md)
  - Outcome: kept. I_SN = 38.7409, V_SN = −38.34, T_SN = 174.40 ms. Spikes 272.0 … 666.6 ms
    all fall within ±0.5 ms.

### Open questions
- (none open; the three above were decided per the contract, see Decisions in force)

### Parking lot
- Optional faint arrows of the flow field in the knee window to show "slow here".
- Ghost blob is soft/faint (fill 0.18 per contract); could be enlarged if it does not read on the projector.
