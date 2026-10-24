# rich-content: user manual

How to get diagrams, charts, PDFs and HTML pages out of the skill: what to
say in Claude Code, what to run in a terminal, and how to extend the kit.
Setting it up is one section of the checkout's `SETUP.md`.

The skill makes them all in one look, chosen from twelve themes: six styles --
`technical` (the System Design manual's look, from `ai-workbench-learning`,
whose kit this is, and the default), `corporate`, `editorial`, `minimal`,
`accessible` and `academic` -- each in a `light` and a `dark` mode. It does not
hand anything over unlooked-at: every figure is checked for collisions as it is
saved, and every result is rendered and read before the skill says it is done.

## What to ask

**A diagram.** What it should show; the parts and how they connect.

> draw the architecture of targets/novalife: browser, API, Postgres, the email queue
> a sequence diagram of a checkout that retries a payment

Back comes an SVG beside the script that draws it, and a PNG of it that was
looked at.

**A chart.** The numbers, or where they are, and what the reader should see.

> chart p50 and p99 latency over the day from this CSV, with the 200 ms budget

**A PDF.** What the document is for and who reads it.

> a two-page design note on how the cache works, with a diagram and the latency numbers
> turn this markdown into a PDF handout with its tables

Back comes a folder: `build.py`, the `.typ` source, each figure, and the PDF.

**An HTML page.** A report to open in a browser or send.

> a weekly ops report as one HTML page: KPI tiles, the architecture, two charts, the endpoint table

Back comes one self-contained `.html` file (figures inline, fonts embedded),
looked at in a browser at desktop and phone width.

**Fix one.** "The labels overlap in latency.svg", "make this chart match the
others" -- the skill rebuilds from the script, never by editing the output.

**From data.** Point at a CSV or Excel file and say what to see.

> from requests.csv, show how p99 spreads per endpoint and when the slow hours are, with a table of the week

**From Markdown.** A Markdown file becomes a PDF handout or a page, its tables,
code and images set in the house style.

> make handout.md into a PDF, and a page I can send

Code in either is highlighted in the theme's colours; a QR code can link the
paper to the page.

**In a theme.** Name the style and the mode -- "as a corporate PDF", "the
dark version", "make it accessible" -- or set it once for a project: a
`rich-content.json` holding `{"theme": "corporate", "mode": "dark"}` in the
project's folder makes everything made in or below it corporate-dark.

| Style | For |
|---|---|
| technical | design notes, architecture, engineering documents |
| corporate | client deliverables, board and status reports |
| editorial | essays, analyses, white papers |
| minimal | one-pagers, summaries, screens |
| accessible | the public, low vision, dyslexia: AAA contrast, a font made to be legible |
| academic | research, papers, chart-heavy analyses |

Every theme passes WCAG contrast and keeps its chart colours apart for
colour-blind readers. Dark prints badly: use it for screens. A look of your
own -- your company's colours -- is a style file that starts from one of the
six and changes what differs, in either mode:

```json
{"name": "acme", "extends": "corporate",
 "modes": {"light": {"colour": {"accent": "#C8102E", "heading": "#1A1A40"}},
           "dark":  {"colour": {"accent": "#FF5A6E"}}}}
```

saved beside the project and named in its `rich-content.json`
(`{"theme": "acme.json", "mode": "light"}`). To choose by looking, build
`examples/themes/build.py` and open `themes.html`: every style, light beside
dark.

## Specs: the short way

Most requests are one of the kinds the kit already knows how to make -- a
flow of boxes and arrows, a sequence diagram, a state machine, a tree, a
timeline, a 2x2, a database diagram, a chart, a document, a decision with
its options, a decision record, a status report, a cheat sheet, slides, a
quiz, flashcards, a page that steps through a process, and pages read from
the repository itself. For those, the skill writes a **spec** -- a few lines
of YAML -- and the kit lays it out, draws it and checks it:

```yaml
make: flow
nodes:
  user: Browser
  api: {label: API, sub: FastAPI}
  db: Database
edges:
  - "user -> api: GET /orders"
  - "api --> db: on a miss"
```

`python -m tools.make flow.yaml` writes `flow.svg` beside it. Boxes, icons
and colours are chosen from the words ("Database" is a cylinder, "Browser" a
client); the layout and the routes of the arrows are worked out. Changing
the picture is changing a line of the spec, which is why it is quicker and
cheaper than a build script: fewer words to write, nothing to place by hand.

You can write or change a spec yourself. `--list` shows every kind,
`--schema KIND` its fields and an example, and a misspelt key is refused
with the one it should have been. A document's spec can name other specs as
its figures, so one spec makes a report with its diagrams and charts.
`examples/make/` holds one example of each kind, and `catalog.html` there
shows each spec beside what it makes.

When no kind fits -- a figure drawn for one lesson, a layout of its own --
the skill writes a build script as before.

## What to run yourself

From the checkout root, with the venv's python:

```bash
.venv/Scripts/python.exe .claude/skills/rich-content/scripts/setup.py --check   # is everything there?
.venv/Scripts/python.exe -m tools.make path/to/spec.yaml --preview            # make what a spec says
.venv/Scripts/python.exe -m tools.make --list                                  # the kinds a spec can name
.venv/Scripts/python.exe -m tools.make --check path/to/folder                  # outputs behind their specs?
.venv/Scripts/python.exe path/to/figure.py                                     # (re)build a figure
.venv/Scripts/python.exe -m tools.render pdf path/to/doc.typ                    # set a PDF
.venv/Scripts/python.exe -m tools.render png path/to/doc.pdf                    # look at it: PNGs in _preview/
.venv/Scripts/python.exe -m tools.render check path/to/doc.pdf                  # overlapping text?
.venv/Scripts/python.exe .claude/skills/rich-content/selftest/selftest.py       # prove the kit
```

A line starting `check:` while building names a collision: two labels
overlapping, a label across the edge of a box or bar, a legend over a title or
the data, text off the canvas. Set `RICH_CONTENT_STRICT=1` to make those stop
a build, and `RICH_CONTENT_THEME=editorial` to build in a theme for one run.

The PNGs are previews, made to look at: they go into a `_preview/` folder
beside the file they show, which carries a `.gitignore` of its own, so git
ignores it wherever it is. What you keep
and commit is the build script and what it writes -- the SVG, the PDF, the
HTML page.

## The examples

`examples/` holds one worked folder per kind, each the reference for its
kind and part of the selftest:

| Folder | Makes | Shows |
|---|---|---|
| `diagram/` | `diagram.svg` | nodes, a region, labelled and dashed arrows |
| `chart/` | `chart.svg` | a line chart, a threshold, lines labelled at their ends |
| `pdf/` | its figures, `report.pdf` | a design note: architecture and sequence diagrams, a bar and a line chart, a table, callouts |
| `html/` | `report.html` | stat tiles, a diagram with a failed component, charts side by side, a sequence diagram, a table |
| `data/` | `spread.svg`, `heatmap.svg`, `report.html` | a CSV read with pandas, a box plot and a heatmap by seaborn, a DataFrame as a table |
| `markdown/` | `handout.pdf`, `handout.html` | `handout.md` set as a PDF (cmarker) and a page, with a table, highlighted code, a figure and a QR code |
| `explainer/` | `explainer.html` | a page that teaches: a contents bar, and a read-through cache as three steps the reader turns through, the same diagram each step |
| `themes/` | a folder per theme, `themes.html` | the same diagram, chart, one-page PDF and HTML page in every theme, light beside dark |
| `make/` | one spec per kind and what it makes, `catalog.html` | every kind `tools.make` knows, from a spec of a few lines |

What they write sits beside them and is committed, so it can be opened
without running anything. A rebuild writes it byte for byte the same unless
what it shows has changed -- charts get the same ids every run, PDFs and
embedded fonts carry no time -- so the outputs change in git only when the
examples do. Only previews (`_preview/`) are ignored.

## Extending the kit

- **A new shape or component** goes into `scripts/tools/svgkit.py` as a
  `Canvas` method, drawing through `self.text` and `self.rect` (so the check
  sees it) and taking its colours and shapes from the canvas's theme
  (`self.col("ink")`, `self.th.kinds`, `self.th.shape`). Use it in an
  example, run the selftest, look at the result.
- **A style** is a file in `themes/`: the four fonts (text, headings, labels,
  code), corners, lines and the chart's grid and frame, then under `modes`
  each mode's colours -- page and text, the kinds', the signals', six chart
  colours. Every theme must pass WCAG AA contrast (or the style's own bar) and
  keep its first four chart colours apart for colour-blind readers; the
  selftest measures both.
- **A font** goes into `themes/fonts.json`: its files, its download, its
  licence -- SIL OFL 1.1 only, reserving no name and claiming no trademark,
  so it is free to use, cut down, embed and share under its own name -- its
  generic family, and a `scale` when its x-height is small. `setup.py`
  downloads it.
- **An icon** is drawn for the skill, never copied from an icon set: a
  `<name>.svg` in `icons/` on the 24 px grid the others use.
- **A PDF element** (a new block, a cover page) goes into `lib.typ` beside
  it, as a function documented with `///`.
- **A change that alters drawings** makes the selftest's golden comparison
  fail. Render the changed diagrams, look at them, and when they are right
  run the selftest with `--update-golden`.
- **The version** is `version.json` in the skill's folder, bumped once
  per push that changes the skill; the workbench's README says by how much.

## Where it came from

The diagram kit and chart style are `Manuals/System Design/figures/kit` from
`ai-workbench-learning`; the render commands are from that manual's
`tools/build.py`. Changed here: paths no longer assume the manual's folders
(the palette became the `technical` theme, the fonts live in the venv), the
manual's course map and its page-only palette keys are left out, type
annotations were added where pyright needed them, `_point_along` returns the
point for a one-point path instead of `None`, and every text and box is
recorded for the check. Run through this kit as it first was, the manual's
figures came out as the manual's own, byte for byte once matplotlib's random
ids were set aside; since then the kit sets other fonts and draws its own
icons, so they no longer do. The check was tuned on them: what it still reports there is each a real
overlap or a label touching an edge, looked at one by one. `html.py`,
`check.py`, `theme.py`, `setup.py`, the Typst package and the four themes
beside `technical` are new. For contrast, `technical` was darkened in two
places (the cache teal, the error red), and region titles are set in `muted`
rather than `faint`.

Everything it uses is free, commercially too: typst, matplotlib, pypdfium2
(which replaced PyMuPDF, an AGPL library), fontTools, Pillow and OFL fonts
that reserve no name and claim no trademark. The icons are its own drawings.
