---
name: rich-content
description: Make diagrams, charts, PDFs and HTML pages as files, in one consistent look, from a short YAML spec or a kit rather than from scratch -- and look at every result before calling it done. Use when asked to draw or diagram something (an architecture, a request flow, a sequence diagram, a timeline, a before/after), to chart data as an image or SVG, to produce a PDF document (a report, a design note, a one-pager, a handout with figures and tables), or to build a standalone HTML page or report (stat tiles, figures, tables, callouts) as a file in this checkout; also to restyle or fix such a figure or document ("the labels overlap", "make it match the others"), to chart a CSV or Excel file, to turn Markdown into a PDF or page, to show highlighted code or a QR code; or to make any of them in a theme (technical, corporate, editorial, minimal, accessible, academic -- each light or dark -- or a company's own colours). Not for reading, merging or filling existing PDFs (the pdf skill), Word, PowerPoint or Excel files (their skills), shared claude.ai documents or Artifacts (the docs and Artifact tools), or UI code in an application.
---

# Rich content, made from a kit and looked at

This skill makes, in one visual language, **diagrams** (SVG, drawn as code),
**charts** (matplotlib, styled), **PDFs** (Typst, in a house style) and
**HTML pages** (one self-contained file). The kit came from the System Design
manual in `ai-workbench-learning`. A **theme** -- colours, fonts, corners,
lines, chart style -- is shared by all of them, so a figure looks the same in
a PDF, in an HTML page and on its own.

Four rules hold throughout.

- **A spec before a script.** Most of what is asked for is one of the kinds
  `tools.make` knows -- a flow, a sequence, a chart, a document, a decision,
  a status report, a quiz and more. Then the source is a spec: a few lines of
  YAML naming the kind and saying what to show, made with
  `python -m tools.make spec.yaml`. It costs a tenth of a build script to
  write and to change, and the kind lays it out, checks it and writes it.
  Write a build script only for what no kind can say.
- **Build with the kit.** A diagram is drawn with `tools.svgkit`, a chart
  styled by `tools.chartstyle`, a PDF set with the `@local/rich-content`
  Typst package, an HTML page built by `tools.html`. Not hand-written SVG,
  not matplotlib's default look, not a fresh stylesheet. Where the kit lacks
  something, add it to the kit, in its style, rather than working around it.
- **Every output has a build script beside it.** The script is the source;
  the SVG, PDF or HTML it writes sits next to it and can be made again by
  running it. Never edit an output by hand.
- **Nothing is done until it has been looked at.** The automatic check is a
  net, not a substitute: render the result, read the image, and for HTML open
  it at desktop and phone width. What you have not looked at, you say you have
  not looked at.

The API -- every method, parameter and colour name -- is in
[references/api.md](references/api.md). Read it before writing a build script;
do not guess parameter names.

## First: is the kit ready?

```bash
.venv/Scripts/python.exe .claude/skills/rich-content/scripts/setup.py --check
```

`ready` means go. Anything missing: run it without `--check`, which installs
the packages it needs into the venv, downloads the fonts from their pinned
releases into it, and writes the `.pth` file that makes `import tools`
work from any folder. Always run the venv's python; `setup.py` warns when it
is not a venv's. Everything it installs is free to use, commercially too;
a new package or font must be as well (references/api.md, "Licences").

## Choosing the theme

A theme is a **style** in a **mode**: `corporate-dark`. A bare style name is
its light mode.

| Style | For |
|---|---|
| `technical` (the default) | design notes, architecture, engineering documents |
| `corporate` | client deliverables, board and status reports |
| `editorial` | essays, analyses, white papers |
| `minimal` | one-pagers, summaries, anything shown on a screen |
| `accessible` | anything for the public, readers with low vision or dyslexia: AAA contrast |
| `academic` | research reports, papers, chart-heavy analyses |

| Mode | For |
|---|---|
| `light` (the default) | documents, print, most pages |
| `dark` | pages and figures read on a screen; it prints badly, so not for a PDF meant for paper |

The first of these that is set wins: `use_theme("corporate-dark")` at the top
of a build script (from `tools.theme`, before drawing); `RICH_CONTENT_THEME` for
one run; a `rich-content.json` holding `{"theme": "corporate", "mode": "dark"}`
in the work's folder or one above it -- a project's look, set once; else
`technical-light`. When the user names a look, use the nearest style and the
mode they ask for; when they give their own colours or brand, write a style
file beside the work that `extends` the nearest one and changes only what
differs, in either mode, name it in `rich-content.json`, and run its colours
through `contrast_issues` and `colour_vision_issues` (references/api.md,
"Themes"). Never type a colour or a font into a build script: take it from the
theme, so a change of theme changes everything.

## A spec first

```bash
.venv/Scripts/python.exe -m tools.make --list              # every kind, by what it is for
.venv/Scripts/python.exe -m tools.make --schema flow       # one kind's fields, and its example
.venv/Scripts/python.exe -m tools.make path/to/name.yaml --preview
```

Pick the kind from `--list`, read its `--schema` (not api.md: the schema is
the whole of what the spec can say), and write `name.yaml` where the output
belongs. It starts with `make: <kind>`; `theme:` and `out:` work in every
kind. `name.svg`, `name.html` or `name.pdf` appears beside it, and with
`--preview` a PNG of each SVG and PDF page in `_preview/`, to read. A key the
kind does not know stops the make and names the nearest one it does; a
`check:` line is a finding, as from a script, and `--strict` makes it fail.

Specs nest: a `doc` (or any document kind) takes a figure as another spec,
by its file or written inline, so one spec can make a page with its
diagrams and charts. `--all DIR` makes every spec under a folder; `--check
DIR` writes nothing and says which outputs are no longer what their specs
make. The examples, one per kind, are in `examples/make/`, and
`examples/make/catalog.html` shows each beside what it makes.

When a kind lays something out badly -- a crowded label, a box in the
wrong group -- first change the spec (pin a box with `at:`, shorten a label,
give a gap more room); when the kind itself is wrong, fix the kind, in its
style, and make its example again. A build script is for a figure no kind
can draw: then the next sections hold.

## Choosing the form

| Asked for | Make | With |
|---|---|---|
| how parts connect, what calls what, a flow, a timeline | a diagram | `tools.svgkit`: `Canvas`, `node`, `arrow`, `region`; `Sequence` for messages over time |
| numbers: a trend, a comparison, a distribution | a chart | matplotlib after `import tools.chartstyle`; `save_chart` |
| a document to print, attach or read top to bottom | a PDF | a `.typ` file importing `@local/rich-content:0.1.0`, figures drawn beside it, `render pdf` |
| a page to open in a browser, share or scroll | an HTML page | `tools.html.Page`, figures passed in as objects |
| numbers in a CSV or Excel file | charts and tables from data | pandas to read it, seaborn for statistical charts (box plots, heatmaps, distributions), `Page.frame` for a table |
| text someone wrote in Markdown | a PDF or a page | `render.markdown_pdf` (cmarker) and `Page.markdown` |
| code to show | highlighted code | `Page.code`; code in a PDF is highlighted in the theme's colours by itself |
| a link to put on paper | a QR code | `Canvas.qr` |

Which chart to draw for which data is a design question: where the dataviz
skill is available, follow it for the choice of chart and its marks, and use
this kit for the file, its colours and its fonts. Where the two differ, this
skill wins for what it makes -- static files: no hover layer, the line widths
and palette of `chartstyle`. Prefer labelling lines and
bars directly over a legend; a legend that a reader must match by colour is
the last resort, and never placed over the title or the data.

## Making it

Put the work where it belongs -- beside what it documents, or where the user
says -- in a folder of its own: the spec or the build script, then what it
writes. What follows is for a build script, when no kind fits.

**A diagram.** A `<name>.py` that builds a `Canvas`, places nodes on a grid
you have planned (left to right is the direction of flow), connects them, and
calls `save(c, __file__)`. Give the canvas the size the content needs, no
more. Labels go on arrows only where they add something.

**A chart.** A `<name>.py` that imports `C, plt, save_chart` from
`tools.chartstyle`, plots with the colours in `C`, and calls
`save_chart(fig, __file__)`. Titles say what to see, not what the axes are.

**A PDF.** A folder with `build.py` (draws each figure with `save(c, HERE /
"name.svg")` or `save_chart`, then calls `tools.render.pdf(HERE /
"doc.typ")`) and `doc.typ`, which starts:

```typst
#import "@local/rich-content:0.1.0": *
#show: report.with(title: "…", eyebrow: "…", footer: "…")
```

and uses `#figure(image("name.svg"), caption: […])`, `#callout(…)`,
`#data-table(…)` and `#beside(…)` from the package. Give every figure a
caption that says what to notice. A page limit ("a one-pager") is planned
from the start -- `dense: true`, figures sized to their content, a chart
beside its text -- as references/api.md, "Fitting a page", describes.

**An HTML page.** A `build.py` that makes a `Page`, adds `kpis`, `h2`, `p`,
`figure` (a `Canvas` or a matplotlib figure, passed as the object),
`row` (figures side by side), `callout`, `table`, `frame` (a DataFrame),
`code` and `markdown`, then `page.save(…)`. The page embeds everything; the
one file is the deliverable. A page that explains how something works takes
`Page(…, contents=True)` for a contents bar, and `steps` for a process the
reader turns through one step at a time. A manual shows what someone says and
what comes back with `chat`, and a screenshot with `image`, as WebP cut to the
width it is shown at -- or `annotated`, with numbered markers and their
legend; `diff` shows a file before and after a change. Several pages that
belong together, a manual's chapters, are a `Site`: one navigation they
share. A page links its fonts from Google Fonts, with similar system fonts
behind them sized to take the same room; only a PDF embeds its fonts.

**From data.** Read the file with pandas (`read_csv`, `read_excel`), keep the
data file beside the build script as its source, and chart with seaborn after
`import tools.chartstyle` -- never `sns.set_theme()` -- with
`palette=C_SERIES` or `cmap=sequential()` / `diverging()`.

**From Markdown.** `render.markdown_pdf(path)` or `python -m tools.render md
file.md` for the PDF; `Page.markdown(text, base=folder)` for the page. Images
the Markdown names are drawn by the build script beside it.

[examples/](examples/) has one worked folder per kind -- `diagram/`,
`chart/`, `pdf/` (a design note), `html/` (a weekly report), `data/` (a CSV
charted and tabled),
`markdown/` (a handout, as PDF and page, with code and a QR code) and
`explainer/` (a page that teaches how something works: a contents bar, and a
process the reader steps through, the same diagram each step). Start
from the nearest one.

## Looking at it

Run the build script. Every diagram and chart is checked as it is saved, and
every figure as it goes into a page: a line starting `check:` is a label
colliding with a label, crossing the edge of a box or a region, with a line
(a lifeline) through it, running into a step marker, sitting on a line or the
edge of a bar, a legend over a title or over the data, or text off the
canvas. Fix every one; none is accepted as it is without telling the user.
For a PDF also run:

```bash
.venv/Scripts/python.exe -m tools.render check path/to/doc.pdf
```

Then look -- the check finds overlaps, not crowding, wrong emphasis or a
figure that says the wrong thing:

1. **Render and read.** `python -m tools.render png <file.pdf|file.svg …>`
   writes PNGs into a `_preview/` folder beside each file (one per PDF page);
   read every one. An SVG opened directly shows a fallback font; the rendered
   PNG shows it as it will be. For a long PDF, `render sheet` gives contact
   sheets for layout and page breaks. Previews are for looking: each `_preview/` folder carries a `.gitignore`
   of `*`, so nothing in one is ever committed, and nothing in one is a
   deliverable.
2. **HTML in a browser, at two widths.** Serve its folder on localhost
   (`python -m http.server --bind 127.0.0.1 --directory <folder>`, in the
   background; browsers under automation refuse `file:` URLs), open it at
   about 1100 px and 390 px wide, take a full-page screenshot at each, and
   read them. Confirm the page does not scroll sideways
   (`document.documentElement.scrollWidth` equals `clientWidth`). Stop the
   server afterwards.
3. **Read like the reader.** Text that touches a line, a box or another
   label, even without overlapping; a note nearer the wrong message; a label
   cut at an edge; a legend to decode where a direct label would do; colour
   carrying a meaning nothing else carries. Fix, rebuild, look again.

## Reporting

Say what was made and where (the full paths of the outputs and of the spec
or build script that makes them again), in which theme, what the check reported and
what was done about it, and what was looked at -- which renders, which widths.
Say plainly what was not looked at. What to keep is the build script and what
it writes; previews and temporary files are never committed.

## Where things are

| Path | What |
|---|---|
| `scripts/tools/make/` | `python -m tools.make`: specs to files; one module per kind in `kinds/`, its docstring its fields; `layout.py` places boxes and routes edges; `document.py` writes blocks as a page or a PDF |
| `examples/make/` | one example spec per kind, what it makes, and `catalog.html` of them all |
| `scripts/tools/svgkit.py` | diagrams: `Canvas`, `Sequence`, `save`, `Canvas.qr` |
| `scripts/tools/code.py` | code highlighted in the theme's colours, for pages and PDFs |
| `scripts/tools/chartstyle.py` | charts: `plt` styled, `C` and `C_SERIES` colours, `sequential`, `diverging`, `save_chart` |
| `scripts/tools/html.py` | HTML: `Page` |
| `scripts/tools/webfonts.py` | how a page links its fonts, and the system fonts behind them (`python -m tools.webfonts` measures them into `themes/fallbacks.json`) |
| `scripts/tools/render.py` | `python -m tools.render pdf / md / png / sheet / check` |
| `scripts/tools/check.py` | the overlap check behind all of them |
| `scripts/tools/theme.py` | which theme: `use_theme`, `current`, `load`; contrast and colour-vision checks |
| `themes/` | the styles, one JSON file each with its light and dark modes, and `fonts.json`: every font family, its files, download and licence |
| `scripts/setup.py` | installs and checks what the skill needs |
| `typst/local/rich-content/0.1.0/` | the Typst package: `lib.typ`, the house style, set in the theme `render pdf` passes it |
| `references/api.md` | the full API |
| `examples/` | one worked folder per kind of output; `themes/` shows every theme side by side |
| `selftest/selftest.py` | proves the kit: builds the examples, checks them, compares the diagrams with references |
| `USER-MANUAL.md` | for people: what the skill is, how to set it up and extend it |
