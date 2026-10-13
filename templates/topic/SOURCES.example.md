# Sources — <topic>

Copy this file to `SOURCES.local.md` in the topic folder and fill it in.
`*.local.md` is gitignored: absolute paths stay on this machine, and nothing
from the external files is committed here.

This file only holds paths. Never paste content from those files here. Record
the Manim decisions they lead to in `WORKBENCH.md` (still changing) or this
topic's optional `context_files/` (stable reference notes), naming the source
by its label below.

## Sources

One line per source: a short label (cite it by that label), then an absolute
path to a file or folder. After `just guard-sync`, each folder named here (or
the folder holding a named file) is read-only for the agent.

- <label>: /absolute/path/to/file-or-folder
- spec: /absolute/path/to/spec.md
- notes: /absolute/path/to/notes/
