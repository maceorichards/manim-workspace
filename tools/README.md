# tools

Workspace tooling, called through `just` (any agent or person can run it):

| Script | Recipe | What it does |
|---|---|---|
| `snapshot.py` | `just list`, `just snap` | numbers a scene's beats; PNGs at chosen indices, headless |
| `doctor.py` | `just doctor` | checks manimlib, ffmpeg, LaTeX/MiKTeX, dvisvgm, fonts, `custom_config.yml` |

Both started in the MIT-licensed upstream of the `manimgl` skill
(https://github.com/do-gongil/manimgl-skill, `skills/manimgl-video/assets/`) and
carry this project's changes. License and provenance:
`.agents/skills/manimgl/core/LICENSE` and `.agents/skills/manimgl/NOTICE.md`.
