---
name: set-style-default
description: Override this machine's default look for every scene (background, font, text color, saturation, fps, named palette colors) without changing the shared template. Use when the user wants a different background or font, a light/slide-friendly look, house colors for their deck, or to reset to the 3b1b default.
argument-hint: 'light-slides | background #0B1020 | font "Latin Modern Roman" | accent #E07A5F | reset'
---

# Set style default

The house look (black background, CMU Serif, saturation 1.5) is `DEFAULT_STYLE` in
`common.py` and applies to everyone who clones the template. A user's own preference goes in
`style.local.yml` at the repo root. That file is gitignored and read by `common.py` at
import, so it reaches every scene, Manim Notebook preview, snapshot, and render on this
machine, and nobody else's.

Never edit `DEFAULT_STYLE` or `custom_config.yml` for a personal preference. Change them only
when the user explicitly wants to change the template for everyone.

## Knobs

| Key | Effect | Default |
|---|---|---|
| `background` | camera background, hex | `#000000` |
| `font` | Pango font for `txt()` and plain `Text` | `CMU Serif` |
| `text_color` | default fill for `txt()` / `tex()` when no `color=` is given | white |
| `saturation` | file-writer saturation boost | `1.5` |
| `fps` | frame rate (use this, not the `--fps` CLI flag, which crashes in 1.7.2) | `30` |
| `tex_template` | manimlib tex template; `None` auto-picks `empty_ctex` under MiKTeX | `None` |
| `palette.<name>` | named color, exposed to scenes as `NAME` (e.g. `palette.accent` → `ACCENT`) | none |

Presets: `3b1b-dark` (the default), `light-slides`, `navy-slides`.

## Steps

1. Show the current state: `just style` (or `uv run python scripts/set_style.py --show`).
2. Ask only what the request leaves open. Recommend a preset when one fits. Ask whether
   palette names should match the deck's names for its colors.
3. If the font changes, confirm Pango has it, since it substitutes silently:
   `just doctor "<font>"`. If the font is missing, say so and stop. Don't write a font that
   will fall back.
4. Write the override, merging into what's there:
   `just style --preset light-slides` and/or `just style --set background=#0B1020 palette.accent=#E07A5F`.
   Remove one key with `--unset key`.
5. Verify by eye: `just snap templates/topic FiringRateCurve`, then read
   `templates/topic/frames/FiringRateCurve_final.png`. Check that the text is readable on the
   background, and that axes and the curve still show. Delete `templates/topic/frames/`
   afterwards so it isn't copied into new topics.
6. Report what changed and how to undo it: `just style --reset`.

## Caveats to tell the user

- A light background doesn't recolor manimlib's own defaults. Axes, `Dot`, `Line`, and
  `Arrow` stay light-colored, so scenes must color them explicitly (e.g. `stroke_color=`). Say
  this whenever the background gets lighter.
- `txt()`/`tex()` honor `text_color`. Plain `Text`/`Tex` built without these helpers do not.
- Restart a running Manim Notebook scene after changing the style. The camera reads its
  config when the scene starts.
- `custom_config.yml` still holds the house defaults for any file that skips `common.py`.
