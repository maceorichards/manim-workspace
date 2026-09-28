# Provenance

This skill merges two upstreams. They are kept in separate directories because
they carry different licenses.

## `core/` — MIT

From https://github.com/do-gongil/manimgl-skill (plugin `manimgl` v0.2.1,
`skills/manimgl-video/`), vendored 2026-09-19. License in `core/LICENSE`.

`core/SKILL-upstream.md` is the original entry point, kept unmodified for
re-syncing. Our `SKILL.md` is adapted from it: same footgun table and workflow,
extended with the `extra/` reference rows, the additional CE-name substitutions,
the `reorient` argument order, and this project's Manim Notebook workflow in
place of the `-se` CLI loop.

## `extra/` — CC BY-NC-SA 4.0

From https://github.com/adithya-s-k/manim_skill
(`skills/manimgl-best-practices/`), vendored 2026-09-19. License in
`extra/LICENSE.txt`. The repository root is MIT, but that directory carries its
own CC BY-NC-SA 4.0 because its examples derive from
https://github.com/3b1b/videos. Attribution: Grant Sanderson (3Blue1Brown),
adapted by Adithya S Kolavi.

**NonCommercial** and **ShareAlike** apply to this material. Teaching and
research use is fine; model fresh code on the examples rather than pasting them
into anything published.

Only the eight rule files that `core/` does not cover were taken. Dropped as
redundant, because `core/` covers them and is source-verified: `scenes`,
`mobjects`, `animations`, `creation-animations`, `tex`, `text`, `colors`, `cli`,
`config`.

Not vendored: the upstream `SKILL.md`, whose line 138 reverses `reorient`'s
argument order.

## Defects fixed in `extra/`

All verified against manimlib 1.7.2. Each was a Manim CE name absent from
ManimGL, or an API claim contradicted by the source.

| File | Was | Now |
|---|---|---|
| `rules/animation-groups.md` | `Star()` ×2 | `RegularPolygon(5)` |
| `rules/animation-groups.md` | `Succession(Wait(delay), …)` | lag via `LaggedStart`, with a note |
| `rules/transform-animations.md` | `Star()` ×2 | `RegularPolygon(5)` |
| `examples/token_to_embedding.py` | `Wait()` | removed |
| `examples/double_slit_interference.py` | `DoubleArrow(...)` | `Arrow(...)` + `add_tip(at_start=True)` |
| `examples/mlp_neurons_flow.py` | `Dot3D(...)` | `TrueDot(...)` |

Two further fixes were made in rule files that were later dropped as redundant
(`creation-animations.md`'s `SpinInFromNothing`, `tex.md`'s substring indexing);
both are covered correctly by `core/` and by this skill's footgun section.

## Re-syncing

Neither upstream auto-updates. To pull changes deliberately:

```bash
# core
claude plugin marketplace add do-gongil/manimgl-skill
# then diff ~/.claude/plugins/cache/manimgl-skill/manimgl/*/skills/manimgl-video/
# against core/, and uninstall the plugin again

# extra
git clone --depth 1 https://github.com/adithya-s-k/manim_skill /tmp/ms
# diff /tmp/ms/skills/manimgl-best-practices/rules/ against extra/rules/
```

After any re-sync, re-run the CE-name audit from the project root:

```bash
python - <<'PY'
import re, pathlib, manimlib
root = pathlib.Path(".claude/skills/manimgl")
CE = ['Create','MathTex','Unwrite','Angle','RightAngle','Star','Axes3D','Dot3D',
      'DoubleArrow','SpinInFromNothing','Wait','AddTextLetterByLetter']
hits = 0
for f in list(root.rglob("*.md")) + list(root.rglob("*.py")):
    txt = f.read_text(encoding="utf-8")
    code = "\n".join(re.findall(r'```python\n(.*?)```', txt, re.DOTALL)) if f.suffix == ".md" else txt
    for n in CE:
        for m in re.finditer(rf'(?<![A-Za-z_]){n}\s*\(', code):
            line = code.splitlines()[code[:m.start()].count("\n")]
            if line.lstrip().startswith("#"):
                continue
            hits += 1
            print(f"{f.relative_to(root)}: {line.strip()[:80]}")
print("clean" if not hits else f"{hits} hits")
PY
```

Expected output on the vendored state: `clean` (the footgun table in `SKILL.md`
names these classes in prose and a markdown table, not as calls).
