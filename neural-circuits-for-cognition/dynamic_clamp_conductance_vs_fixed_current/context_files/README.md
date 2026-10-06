# context_files — dynamic_clamp_conductance_vs_fixed_current

Self-contained by design: everything needed to build the video is in these files; the deck
sources never need to be opened. Sources are cited by generic label only (no paths).

| File | What it holds |
|---|---|
| `contract.md` | The video contract: purpose, must/must-not, two-column layout, 15-s beat sheet, end frame, accuracy flags (10 nS ↔ mS/cm², matched offset), acceptance checklist |
| `science.md` | Plain-language concepts (current clamp vs conductance vs dynamic clamp), slide 6 content and narration, paper numbers, audience Q&A |
| `model.md` | Morris–Lecar equations + parameters, unit conversion, noise/drive, self-contained simulation snippet with asserts, verified spike counts and ranges, alternatives, drawing recipe |
| `style.md` | Shared look, color roles, motifs (identical in every topic; do not edit here) |

Provenance labels cited (all read 2026-09-29): deck outline (slides 4 and 6, assembly notes);
deck manifest (placement); deck static figures s06_v1, s06_v2 + status notes; deck build
contract §6; deck model module; background notes §3, §13, §14, §41, §45; paper Methods and
Fig. 1A + legend; debrief.
