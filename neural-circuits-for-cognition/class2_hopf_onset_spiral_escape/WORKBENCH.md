# Workbench — class2_hopf_onset_spiral_escape

Context: `context_files/contract.md` (the video contract), `science.md`, `model.md`, `style.md`.

## Class 2: the whirlpool lets go

Status: Built — final render `videos/class2_hopf_onset_spiral_escape.mp4`, 1344×1200, 30 fps, 19.27 s
Scenes: Class2HopfOnset

### Intent
Show that class 2 rest is a spiral: kicks ring on the way back, the ringing lasts longer as
current rises, and at the Hopf point the spiral throws the state onto fast spiking — already
turning when it lets go.

### Decisions in force
- Paper's model, SHUNT (g_shunt = 4, no adaptation), exact 2-D; one deterministic run of the
  schedule in model.md (110 → 112.5 → 114 → 115 µA/cm², kicks +1.2 mV at 5, 50, 105 ms).
- One ValueTracker (model time T) drives everything; nullclines, focus, trail, V(t), current
  strip, kick marks and both zoom windows are pure functions of T redrawn each frame.
- Grid, warp, full window and dot conventions as in the `class1_snic_onset_slow_crawl` contract; tag
  "Class 2 · Hopf" in `ORANGE`. Phase-plane plot area x [−3.70, 0.0] × y [−2.05, 2.80].
- Focus window V −40…−24, w 0.004…0.026; V(t) y range −36…−24 mV, both zoom out (eased,
  bounds interpolated in warped space) over model t = 195–210 ms at half speed.
- Time: 1 video s = 20 ms model (V(t) x-axis is model time, so pacing never distorts data).
- V(t) data rows map to y [−0.55, 2.95]; the strip below holds the scale bars ("10 ms",
  "2 mV" → "20 mV", the vertical bar fading out 195–200 ms and in 205–210 ms).
- Dots: focus radius 0.10 (filled while stable, open once I > I_Hopf), state radius 0.06 so the
  white focus rim stays visible under the state at rest. Yellow pen dot at the V(t) head and
  a grey pen dot at the current-strip head (first frame shows where the traces start).
- Kick triangles hang under the current line, pointing up; "kick" label under the first.
- Hopf flash: `RED_C` ring radius 0.42 grows in the 0.4 s hold, fades (scale 1.6) over the
  first 1.34 s of beat 6. A 0.2 radius ring was lost inside the kick-3 spiral.
- Trail: split at kicks (the dashed arrow shows the jump), thinned by screen arc length,
  last 15 ms opaque, older at 35%.
- Open question 1 (inset): **no inset**; the faint kick spirals in the phase plane carry the
  ringing in the end frame, which §6 describes without an inset.
- Open question 2 (units): "Hz" for ringing, "spikes/s" for firing (contract §4 exact text).
- Open question 3 (f_min): accepted per contract §9.1; the rate after the Hopf is labelled
  "≈ 110 spikes/s", never f_min.
- No nullcline name labels (the vid2 contract §4/§6 lists none; the end frame is dense).
- Labels colored with `.set_color()` after `txt()`: `txt(..., color=X)` renders white in 1.7.2.

### Checklist
- [x] Beat 1: first frame reads when paused (focus window, filled focus, tag)
  - Outcome: kept — nullclines cross at an angle, white focus rim around the yellow state, "focus", orange tag.
- [x] Beat 2: kick 1 at I = 110, barely one overshoot
  - Outcome: kept — short dashed red arrow, trail makes one arc back; V(t) one step and one small dip.
- [x] Beat 3: ramp to 112.5, kick 2, ~3 visible turns; "rings at ≈ 100 Hz"
  - Outcome: kept — 4.2 s frame shows the loop spiralling in, V(t) three decaying peaks; readout orange from 4.0 s.
- [x] Beat 4: ramp to 114, kick 3, ringing barely decays
  - Outcome: kept — 8.0 s and 9.25 s frames: stacked opaque loops, V(t) still ringing at full height.
- [x] Beat 5: Hopf crossing — focus turns open with red flash
  - Outcome: revised — ring enlarged 0.2 → 0.42 after the crop at 9.7 s showed it hidden in the spiral.
- [x] Beat 6: ring grows, zoom-out, jump to the big loop, first spike at 203.9 ms
  - Outcome: kept — 10.6/11.3 s frames show the growing ellipse, trail clipped at the window edge during the zoom; 12.1 s first spike.
- [x] Beat 7: steady spiking, readout "fires at ≈ 110 spikes/s"
  - Outcome: kept — dense spike run, readout below line 1, clear of spike tops.
- [x] Beats 8–9: caption and 3 s hold; total ≈ 19.2 s
  - Outcome: kept — ffprobe 19.27 s; last frame matches §6 ("focus" label moved further down-right in the full window to clear the loop).
- [x] Asserts in `main.py` (I_Hopf sign change, spike times, kicks subthreshold)
  - Outcome: kept — also asserts ring peaks per kick, t_Hopf = 168.23, focus-window bounds and 111.7 spikes/s.

### Open questions
- (none open; see Decisions in force for the three resolved ones)

### Parking lot
- Optional faint dashed unstable limit cycle around the focus in beats 3–4.
- Small V(t) inset keeping the zoomed ringing visible in the end frame.
