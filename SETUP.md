# Setting up the Python environment

This repository has two toolchains that share nothing:

- **The website** is Node. `cd webapp && npm ci && npm run build`. It needs no
  Python at all, and nothing on this page applies to it.
- **The Claude Code skills** under `.claude/skills/` are Python. They draw
  diagrams and charts and set PDFs. This page is how that environment is built.

Follow the four steps in order. They are written to be run literally, from the
repository root, on a machine where none of this exists yet.

## Before you start

- **Python 3.14** on `PATH`. The pinned versions in `requirements.txt` were
  resolved on 3.14.6; another minor version may have no wheel for some of them.
  Check with `python -V`.
- **Network access.** Step 3 downloads fonts and a Typst package. Steps 1, 2
  and 4 are the only ones that work offline, and only after step 3 has run once.
- Everything lands in `.venv/` at the repository root, about 310 MB. It is not
  committed; it is rebuilt from this page.

## Step 1 — create the virtual environment

```bash
python -m venv .venv
```

On POSIX the interpreter is then `.venv/bin/python`; on Windows it is
`.venv\Scripts\python.exe`. Every command below uses the Windows form, because
that is where this repository is worked on. Substitute as needed.

## Step 2 — install the packages

```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

That is 23 packages, every version pinned. It should end with a long
`Successfully installed ...` line.

## Step 3 — finish the skill setup

```bash
.venv\Scripts\python.exe .claude\skills\rich-content\scripts\setup.py
```

**Do not skip this.** `pip` installs the Python packages and nothing else, but
the skill needs three things pip knows nothing about:

- the Typst package `@preview/cmarker`, copied into
  `.venv/share/typst/packages/`, so nothing is fetched while a PDF compiles;
- seven font families (all OFL-1.1), downloaded from their pinned releases into
  `.venv/share/fonts/`. **Without them every PDF compiles in a fallback font**,
  which changes line breaks and pagination — it does not fail, it just comes out
  wrong;
- `rich-content.pth` in `site-packages`, naming the skill's `scripts/` folder,
  which is what makes `import tools` work from any directory.

The script installs only what is missing, so running it again is cheap and safe.

## Step 4 — verify

```bash
.venv\Scripts\python.exe .claude\skills\rich-content\scripts\setup.py --check
```

The last line must be `ready`. Anything else names what is missing; run step 3
again. `--check` changes nothing, so it is also the right way to ask a strange
machine whether it is set up.

For a fuller check — it rebuilds every example, compares the diagrams against
references, and takes about a minute:

```bash
.venv\Scripts\python.exe .claude\skills\rich-content\selftest\selftest.py
```

Expect `114 passed, 2 failed`. Both failures are example specs that read files
belonging to the skill's home repository — `examples/make/licences.yaml` wants a
`third_party.py` that is not here. Everything else should pass; a third failure
is a real one.

If you redirect its output to a file, set the encoding first, or it dies with
`UnicodeEncodeError` part way through: Windows defaults a redirected stream to
cp1252, and the output contains characters that codepage has no room for.

```bash
set PYTHONIOENCODING=utf-8
.venv\Scripts\python.exe .claude\skills\rich-content\selftest\selftest.py > selftest.log 2>&1
```

## Using it

Always call the interpreter inside `.venv` by path. A bare `python` is the
system one, which has none of this installed and no `.pth` file, so `import
tools` will fail there.

```bash
.venv\Scripts\python.exe -m tools.make --list          # every kind of output
.venv\Scripts\python.exe -m tools.make path\to\spec.yaml
.venv\Scripts\python.exe -m tools.render png out.pdf   # look at the result
```

## When it goes wrong

**`ModuleNotFoundError: No module named 'tools'`** — either you used the system
`python` instead of `.venv\Scripts\python.exe`, or the `.pth` file is missing or
points at an old path. Re-run step 3; it rewrites the file. This is also what
happens if the repository has been moved or renamed since setup, because the
`.pth` records an absolute path.

**PDFs compile but the typography is wrong** — the fonts never downloaded.
Re-run step 3 with network access and check that `--check` lists seven families.

**A pinned version will not install** — check `python -V` is 3.14. If you must
use a different Python, install without the pins
(`pip install typst matplotlib pypdfium2 seaborn pandas openpyxl pygments
markdown-it-py segno pyyaml`), confirm the selftest still passes, and then
regenerate this file's pins as below.

**`UnicodeEncodeError` from any of these commands** — you redirected output to a
file on Windows, which switches the stream to cp1252. Set `PYTHONIOENCODING` to
`utf-8` first, as above.

**`path "../x.svg" would escape the project root`** — Typst is sandboxed to the
git checkout the file sits in, and falls back to the file's own folder when
there is no checkout. Run from inside the repository, not from a copy of it made
somewhere else.

**Starting over** — delete `.venv` and repeat from step 1. Nothing else on the
machine is touched.

## Changing what is installed

`requirements.txt` pins transitive dependencies as well as chosen ones, so it
cannot be edited by hand without drifting from reality. Install the change,
confirm the selftest still passes, then write the versions back:

```bash
.venv\Scripts\python.exe -m pip install <package>
.venv\Scripts\python.exe -m pip freeze --exclude-editable
```

Copy the output into `requirements.txt`, keeping the two sections and the
comment on each chosen package.
