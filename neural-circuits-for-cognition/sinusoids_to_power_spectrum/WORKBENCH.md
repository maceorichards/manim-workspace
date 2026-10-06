# Workbench — sinusoids_to_power_spectrum

Context: `context_files/contract.md` (the build contract), `model.md`, `science.md` and
`style.md`. Sources: see `SOURCES.local.md` (deck spec, slide 1).

## From sinusoids to spectra

Status: Building (v2 rendered 2026-10-01; awaiting review)
Scenes: SinusoidsToPowerSpectrum

### Intent

In two beats (40 s, 1920×1080, 60 fps): a signal is a sum of sinusoids stored as Re/Im stems,
and phase moves weight between Re and Im without touching power. A live power spectrum then
grows one peak per rhythm.

### Decisions in force

- Workspace look (black, CMU Serif); colours from `prescott2008.py`, with the slide-only
  component palette.
- No phasors, dials or circles; Re/Im appear only as stems. Stems are analytic from (a, b).
- Beat A: from 11.3 s the 6-Hz phase spins continuously, ramping to 0.5 turn/s over 1 s
  (about 4.1 turns by the crossfade at 20 s, where it freezes). Chosen by the user over 1¼ or
  2 turns that then stop.
- Beat B: Welch on the trailing 2-s window, recomputed every frame. Each "+ rhythm" caption
  swaps in as the rhythm enters the window (6 Hz at signal T 7 = video 25; 40 Hz at T 13 =
  video 31); its marker draws 1.5 s later, once the peak is ≥ 25× background. The scroll eases
  to a stop at 38.5 s and holds still to 40 s for the end frame.
- Beat C (impedance) is cut, not replaced (user, 2026-10-01). v1, with Beat C, is stashed in
  `scratch/v1_2026-09-30/` (gitignored): code, the 56-s MP4 and its end PNG. The stashed
  `WORKBENCH.md` already includes the 2026-10-01 review items.
- Output: `--file_name sinusoids_to_power_spectrum`; end frame `videos/sinusoids_to_power_spectrum_end.png`.

### Checklist

- [x] Beat A: a faster, more drastic phase drift, with the 6-Hz Re/Im stems and the sum changing live
  - Outcome: revised. The old phase slide went 0→90° and stopped; it is now a continuous spin.
    In frames at 12–15 s the 6-Hz Re and Im stems swing through both signs (±0.6), the sum
    changes shape, and the power stem stays at 0.36 in its "unchanged" box.
- [x] Beat B: no stale caption when a rhythm is added (both 6 Hz and 40 Hz)
  - Outcome: revised. "Noise only" now runs 21.5–25 s over a spectrum with no peak (6-Hz ratio
    3.3 at 25 s). The 6-Hz caption swaps in at 25 s, and the marker draws at 26.5 s (ratio 25).
    The 40-Hz caption swaps in at 31 s (40-Hz ratio 1.3), and the marker draws at 32.5 s
    (ratio 64). Frames at 24.9, 25.7, 30.9 and 31.7 s confirmed it.
- [x] Beat B caption wording
  - Outcome: kept. Changed to "Noise only: no peaks." The 2-s Welch spans 1.7 decades on the
    log axis, so "smooth" did not match the frame.
- [x] Beat C output-trace low-pass, Beat C axis gaps
  - Outcome: discarded. Beat C was deleted.

### Deviations from contract.md

- Beat C is cut; the video is 40 s (2400 frames), not 56 s.
- Beat A: a continuous phase spin replaces the 0→90° slide.
- Beat B: the rhythm onsets move from T 6/12 to T 7/13. Captions swap at onset rather than
  after the peak is up (markers still wait for the peak). The final 1.5 s is a still hold.
- Back-to-back cross-fade (out, then in) inside the specified 1-s window at 20 s.

### Open questions

### Parking lot

- Beat B time ruler shows only 1–2 labelled ticks in the 2-s window; half-second ticks would help.
