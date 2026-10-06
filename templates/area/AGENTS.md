# Area — <area>

Agent notes for every movie in `<area>/`. Agents read this file whenever they work in this folder,
on top of the root `AGENTS.md`. Keep it short and specific to this area. Root rules stay in the
root file, so this one never conflicts when the template is merged in.

- **Subject:** <one line: course, audience, what these movies explain>
- **Shared code:** `<area>/<module>.py` holds models and palettes several topics use (pure
  functions, checked by its own `__main__` asserts). Topics import it by name (`import <module>`);
  `common.py` puts this folder on `sys.path`. Don't name a module `common`.
- **Conventions:** <naming, recurring visual vocabulary, color meanings shared by these movies>
