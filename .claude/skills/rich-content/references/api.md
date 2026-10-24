# The kit's API

Everything a build script calls, with the real signatures. Coordinates are SVG
pixels from the top left; sizes are pixels; colours are `#RRGGBB` strings,
taken from the theme below rather than typed.

All of it imports as `tools.…` once `scripts/setup.py` has run (it writes the
`.pth` file that puts `scripts/` on the venv's path).

## Themes — `tools.theme`, `themes/`

A theme is a **style** in a **mode**, named `style-mode`: `corporate-dark`. Each
style is one JSON file in `themes/`, read by the diagram kit, the chart style,
the HTML page and the Typst package alike: what its modes share at the top --
fonts, shapes, chart style -- and each mode's colours under `modes`. The skill
carries six styles -- `technical` (the default), `corporate`, `editorial`,
`minimal`, `accessible`, `academic` -- each `light` and `dark`: twelve themes.
A bare style name means its light mode.

```python
from tools.theme import use_theme, current
use_theme("corporate-dark")         # before drawing; or a file: use_theme("brand.json", mode="dark")
th = current()                      # the Theme in force: th.name "corporate-dark", th.style, th.mode, th.dark
```

Which theme, the first set winning: `use_theme(…)` in the script;
`RICH_CONTENT_THEME=corporate-dark` in the environment; a `rich-content.json`
holding `{"theme": "corporate", "mode": "dark"}` (or `"theme": "brand.json"`,
relative to it) in the script's folder or one above it, up to the checkout's
root; else `technical-light`. `Canvas(…, theme=…)` and `Page(…, theme=…)` take
one for themselves; `render pdf --theme` for the command.

What a theme holds, and how to read it from Python:

| Key | Holds | In Python |
|---|---|---|
| `colour` | `ink` text, `muted` secondary text and arrows, `faint` region borders and what is dimmed (decoration only), `rule` lines and grid, `paper` and `wash` backgrounds, `heading`, `accent` one emphasis colour, `on` text on a coloured badge or marker | `th.colour["ink"]`; on a canvas `c.col("ink")` |
| `kinds` | `stroke` / `fill` per kind of component: `client`, `edge` (network), `compute`, `cache`, `data`, `async` (queues, streams), `external` | `th.kinds["cache"]["stroke"]` |
| `signal` | `good`, `bad`, `warn`, `info` and each `_fill`: meaning, not decoration | `th.signal["bad"]` |
| `series` | six chart colours, in order; matplotlib's colour cycle. The first four stay apart for colour-blind readers | `th.series` |
| `fonts` | the family for `text` (running text), `heading`, `label` (diagrams, charts, captions, tables), `mono`; `heading_weight` | `th.label`, `th.mono`, … |
| `shape` | `radius` of boxes, `region_radius`, `stroke` width, `shadow` colour or null, `nodes` (`tint`, or `bar`: an outline with the kind on a coloured bar), `pills` (round chips and badges, or square) | `th.shape["radius"]` |
| `chart` | `grid` (`both`, `y` or `none`), `frame` (`left-bottom`, `bottom` or `box`), `ticks` (tick marks, pointing in) | |
| `contrast` | the style's own bar for text, above AA: `{"text": 7}` (AAA) in accessible | |
| `dark` | set by the mode: canvases and charts carry their paper, PDFs a dark page | `th.dark` |

A style of one's own starts from one of these and changes what differs, in
either mode or both:

```json
{"name": "acme", "extends": "corporate",
 "modes": {"light": {"colour": {"accent": "#C8102E", "heading": "#1A1A40"},
                     "kinds": {"compute": {"stroke": "#1A1A40", "fill": "#ECECF5"}}},
           "dark":  {"colour": {"accent": "#FF5A6E"}}}}
```

Two checks hold every theme, and a style of one's own should be run through
both (`from tools.theme import load, contrast_issues, colour_vision_issues`):

- `contrast_issues(th)` -- WCAG AA, 4.5:1, for text on what it sits on: `ink`,
  `muted`, `heading`, the signals on their fills and on the page, `on` on the
  kinds' strokes, and every colour the kit also writes in -- the kinds, the
  series and the accent label lines and set code. A style may ask for more
  (`"contrast": {"text": 7}`).
- `colour_vision_issues(th)` -- the first four series colours must stay at
  least 12 apart in CIELAB for typical vision and for protanopia, deuteranopia
  and tritanopia (Machado et al. 2009), so a chart's lines do not merge for one
  reader in twelve. Past four lines, label them directly.

Fonts are named by family. `themes/fonts.json` lists each family a theme may
use -- its files by weight, its download (a release archive, or files from a
pinned commit), its licence, its CSS generic family (`serif`, `sans-serif`
or `monospace`, the fallback a page names after it) and, for a face with a
small x-height, the `scale` it is set at (Crimson Pro 1.12, EB Garamond 1.15),
which PDFs and pages both apply so its text reads as large as the rest. A new
family goes there,
and only one under the OFL 1.1 that reserves no name and whose files claim no
trademark (name ID 7), so it can be cut down and embedded under its own name;
the selftest reads the files to hold that. `setup.py` downloads it.

## Specs — `python -m tools.make`

A spec is a YAML (or JSON) mapping whose `make:` names a kind; the kind draws
or writes the file with the rest of this kit. For writing a spec, `--schema
KIND` is the reference -- each kind's own fields and its example -- and this
section is for running the command and for adding a kind.

| Command | Does |
|---|---|
| `python -m tools.make SPEC …` | makes each spec's file(s) beside it: `name.yaml` writes `name.svg`, `.html` or `.pdf` |
| `--list` | every kind, by group, with what it writes and what it is for |
| `--schema KIND` / `--example KIND` | a kind's fields then its example / the example alone |
| `--all DIR` | every spec under DIR (a `catalog` last, since it shows the others' outputs) |
| `--check DIR\|SPEC` | writes nothing; exit 1 and a `stale:` line for each output that is not what its spec makes now |
| `--preview` | also a PNG of each SVG and PDF page made, in `_preview/` |
| `--strict` | exit 1 when the check finds anything (as `RICH_CONTENT_STRICT=1` does, without stopping) |

Every spec may say `theme:` (a theme's name, or a style file relative to the
spec; else `rich-content.json` above it, as for a script) and `out:` (where
to write, relative to the spec, with or without the suffix). A document
kind takes `format: html | pdf | [html, pdf]`. A key no kind reads is an
error naming the nearest key it does read, and the make writes nothing.
Exit codes: 0 made, 1 a finding under `--strict` or a stale output, 2 a spec
that cannot be made.

YAML reads `on`, `off`, `yes`, `no` as true and false: no kind uses them as
keys, and a value meant as text in a mapping that holds them is quoted. An
edge or a message written as text with a `:` in it is quoted (`"a -> b:
GET /x"`).

**Adding a kind.** One module in `scripts/tools/make/kinds/` (a name with a
hyphen is the module's with an underscore; a module starting with `_` is a
helper, not a kind), with:

- a docstring that is its field reference -- `--schema` prints it;
- `PURPOSE` (one line, for `--list`), `GROUP` (`diagrams`, `charts`,
  `documents`, `learning` or `from the repository`) and `OUTPUT` (`svg`,
  `html`, `pdf`, `html|pdf`);
- one of `draw(spec) -> Canvas | Figure` (a figure: written as SVG, and
  usable as a figure inside any document), `document(spec) -> Doc` (blocks,
  written by `tools.make.document` as a page or a PDF), or `build(spec, out)
  -> list[Path]` (anything else; `out` is the output path without suffix);
- its example, `examples/make/<kind>.yaml`, which the selftest makes.

A kind reads every key through its `Spec`: `get(key, default, kind,
choices)`, `need(key, …)`, `num`, `sub` (a nested mapping), `items` (a list,
each mapping in it a Spec), `mapping` (entries in order), `path` (a file
relative to the spec) -- so that what it never reads is reported. Raise
`SpecError` with where and what for a spec that cannot be made.

Shared parts: `tools.make.infer` (`box`: a box from `"Label"` or a mapping,
kind and icon guessed from its words; `edge`: `"a -> b: label"`, `-->`
dashed, `<->` both ways), `tools.make.layout` (`layered`: layers, few
crossings, groups kept together, cycles turned round; `Plan`: boxes placed,
edges routed square on tracks between the layers), and
`tools.make.document` (`Doc`, `common`, the block grammar its docstring
lists, written by `write` as a `Page` or as Typst through the package below,
with the `cmarker` package for Markdown).

## Diagrams — `tools.svgkit`

```python
from tools.svgkit import Canvas, Sequence, save
c = Canvas(w, h, background=None)
…
save(c, __file__)                  # <script>.svg beside the script; or save(c, "path/name.svg")
```

`save` writes the SVG and prints what the overlap check finds (`check: …`).
`c.check()` returns the same list without saving.

### Components

`c.node(x, y, w, h, kind, label, sub=None, icon=None, shape="box", state="normal", count=None, layout="row", label_size=13, sub_size=10.5, tag=None) -> Box`

- `kind` — `client | edge | compute | cache | data | async | external`: sets the colours.
- `shape` — `box | cylinder` (a database) `| queue` (message slots on the right).
- `state` — `normal | dim` (not part of this story) `| focus` (the one to look at) `| fail` (broken: red, dashed, ✕ badge) `| warn` (needs a look, not broken: amber, dashed, ! badge) `| good` (settled, checked: green, a tick badge).
- `count=N` — a fleet: two cards stacked behind and a `×N` badge.
- `layout` — `row` (icon left of the text) or `stack` (icon above it).
- `tag` — a small uppercase label above the box ("NEW").
- `icon` — one of the skill's icons (below).

It returns a `Box` to connect arrows to: `.left .right .top .bottom` (points
on each side's middle), `.at(side, t)` (a point along a side, `t` from 0 to 1),
`.cx .cy .x2 .y2`, and `.x .y .w .h`.

`c.qr(data, x, y, size=104, color=None) -> Box` — a QR code for `data` (a URL), `size`
px square with its quiet margin of four modules included; dark modules on a
light square in every theme, since many scanners read no other way. Save it
alone (`save(c, …)`) to put it in a PDF or Markdown.

`c.region(x, y, w, h, title=None, color=None, fill="none", dash="4 4", icon=None) -> Box` —
a dashed group (a service, a VPC, a data centre). Draw it first; its title sits
inside the top left. Its border is `faint` and its title `muted`, or both `color`.

### Connections

`c.arrow(p1, p2, color=None, sw=1.6, dash=None, label=None, label_at=0.5, label_dy=-8, label_color=None, both=False, route="straight", via=None, head=True, step=None, step_color=None, label_bg=True, label_size=10.5, label_mono=False, gap=4)`

- `p1`, `p2` — points, usually `box.right`, `other.left`.
- `route` — `straight`, `hv` (horizontal then vertical), `vh`, `hvh`, `vhv`; or `via=[(x, y), …]` for given bends.
- `dash="5 4"` — the path not always taken (a miss, a fallback).
- `label` — sits on a white plate at `label_at` along the path, `label_dy` above it; `label_mono=True` for code.
- `step=n` — a numbered marker at the middle, for an order of events.
- `both=True` — heads at both ends; `head=False` — none.

`c.line(x1, y1, x2, y2, stroke=None, sw=1.0, dash=None, layer="edges", cap="round")` (stroke `rule`) and
`c.path(d, stroke=None, sw=1.0, fill="none", dash=None, layer="edges")` (stroke `ink`) for anything else.
`color=None` everywhere means the theme's colour for that part: an arrow's is `muted`.

### Labels and marks

- `c.text(x, y, s, size=12, weight=400, color=None, anchor="start", family=None, layer="labels", italic=False, letter_spacing=None)` — `y` is the baseline; `anchor` is `start | middle | end`; `color` defaults to the theme's `ink`, `family` to its label font (`c.th.mono` for code).
- `c.lines(x, y, lines, size=12, …, leading=1.3)` — several lines.
- `c.paragraph(x, y, s, width, size=12, …)` — wrapped to `width`; returns its height.
- `c.chip(x, y, s, tone="neutral", size=10.5, anchor="start", icon=None, mono=True) -> Box` — a metric pill (`"p99 212 ms"`); `tone` is `good | bad | warn | info | neutral`; `anchor="end"` puts its right edge at `x`.
- `c.badge(x, y, s, color, size=9.5, anchor="end")` — a small filled tag.
- `c.step(x, y, n, color=None, r=9)` — a numbered circle.
- `c.icon(name, x, y, size=20, color=None, stroke=2.0)` — an icon on its own.
- `c.rect(…)`, `c.circle(…)` — plain shapes.

`text_width(s, size, weight=400, family=None)` measures a string with the
real font, to place things beside it (`family=None` means the current theme's
label font).

### Sequence diagrams

```python
seq = Sequence(c, [("Browser", "client", "monitor"), ("API", "compute", "server")],
               x0=70, spacing=180, top=16, box_w=136, box_h=46, bottom=None)
seq.msg(0, 1, y, "GET /orders/42")                          # numbered automatically
seq.msg(1, 0, y, "200 OK", ret=True, tone="good")           # a return: dashed
seq.msg(1, 1, y, "validate")                                # a call to itself
seq.msg(1, 2, y, "SELECT …", mono=True, note="the slow one") # note: italic, under the arrow
seq.msg(1, 3, y, "SELECT …", label_at=0.75)                 # passes lifeline 2: label in the last gap
seq.span(1, y1, y2)                                         # activation bar on lifeline 1
seq.bracket(0, y1, y2, "≈ 158 ms", side="left")
```

Participants are `(label, kind, icon)`. `y` grows down the page; leave about
36 px between messages, and about 50 px after one with a `note`. Size the
canvas to the last message plus 30.

A message's label sits midway between its two lifelines. When the message
passes another participant's lifeline, midway is on that lifeline, and the
check reports `has a line through it`: set `label_at` (0 at the sender, 1 at
the receiver) to put the label in a gap -- for one lifeline skipped, `0.75`
puts it between the skipped one and the receiver, `0.25` between the sender
and the skipped one. A long label beside a step marker (the numbered circle
near the sender) runs into it; shorten it and move the rest to `note`.

### Icons

The skill draws its own, one `<name>.svg` each in `icons/`:
`book-open`, `bot`, `clock`, `cloud`, `code`, `cog`, `credit-card`,
`database`, `file-text`, `files`, `globe`, `hammer`, `hard-drive`,
`landmark`, `mail`, `monitor`, `network`, `octagon-x`, `pencil`, `send`,
`server`, `shield`, `smartphone`, `terminal`, `users`, `zap` (a cache).
A name not there stops the build and lists them. A new icon is drawn for the
skill -- an original drawing, never one copied from an icon set -- on the same
24 px grid, stroked 2 with round caps and joins, as the others are; the
selftest refuses an icon that carries another set's notice.

## Charts — `tools.chartstyle`

```python
from tools.chartstyle import C, plt, save_chart
fig, ax = plt.subplots(figsize=(6.4, 2.6))    # inches; 6.4 wide fills an A4 column
ax.plot(x, y, color=C["blue"])
save_chart(fig, __file__)                     # <script>.svg beside it; or save_chart(fig, "path/name.svg")
```

Importing it styles matplotlib in the theme: its label font, colours, grid
and frame, its six series colours as the colour cycle, left-aligned titles,
and SVG text that stays text; `use_theme` afterwards restyles it. `C` holds
the theme's `ink muted faint rule paper accent`, the six kind colours by
technical's hue names -- `blue` (compute) `teal` (cache) `green` (data)
`orange` (async) `violet` (edge) `slate` (client), in that order of preference
-- and `good bad warn` with their `_fill`s (meaning). In another theme `C["blue"]`
is that theme's compute colour, whatever its hue.

`save_chart` lays the figure out, checks it — text on text, a legend over a
title or over the data, a label sitting on a line or across the edge of a bar
or a shaded area — then writes it with a tight box and closes it. A label
wholly inside a bar is fine; one across its edge is not.

From data: read with pandas (`pd.read_csv`, `pd.read_excel(path, sheet_name=…)`
through openpyxl), chart with **seaborn** -- box plots, violins, histograms,
heatmaps, regressions -- which draws on the same matplotlib, so its charts come
out in the theme. Import it after `tools.chartstyle`, never call
`sns.set_theme()`, and give it the theme's colours: `palette=C_SERIES` (the six
series colours, in order) or `cmap=sequential("async")` (the page's colour to a
kind's) or `cmap=diverging()` (blue, page, orange: a middle that means "as
expected" -- not green and red, which merge for colour-blind readers).

```python
import seaborn as sns
from tools.chartstyle import C_SERIES, plt, save_chart, sequential
sns.boxplot(data=df, x="p99_ms", y="endpoint", hue="endpoint", palette=C_SERIES[:3], legend=False, ax=ax)
sns.heatmap(pivot, cmap=sequential("async"), ax=ax, cbar_kws={"label": "p99, ms"})
```

Habits that pass the check and read well: label a line at its end
(`ax.text(x_last + small, y_last, "p99", va="center")`) instead of a legend;
put a threshold's label just above its line at the left; set `ylim` with
headroom for labels above bars; `ax.set_axisbelow(True)` keeps the grid behind
bars.

## PDFs — the `@local/rich-content` Typst package

```typst
#import "@local/rich-content:0.1.0": *
#show: report.with(title: "…", eyebrow: "…", footer: "…", paper: "a4", dense: false)
```

- `report` — page (A4, margins, page numbers `n / total` with `footer` beside them), the theme's text, heading, label and code fonts and colours; prints `eyebrow` in small capitals and `title` as the level-1 heading. `dense: true` tightens margins, type and spacing, the same look, for a page that must hold a lot.
- `#beside(a, b, widths: auto, gutter: 14pt)` — blocks side by side, top-aligned: a chart beside the text that explains it. `widths` like `(1.2fr, 1fr)`.
- `#callout("Title", tone: "info")[body]` — `tone` is `info | good | warn | bad`.
- `#data-table(header, rows, numeric: (), columns: auto)` — `header` a tuple of content, `rows` a tuple of tuples; columns named in `numeric` are right-aligned with tabular figures. Wrap it in `#figure(…, caption: […])` for a numbered table.
- `colour(key)`, `signal(key)`, `theme` — the palette, for anything custom (`theme.kinds.cache.stroke`).
- Code blocks (` ```python `) are highlighted in the theme's colours -- `render pdf` passes a syntax theme made from it -- framed, without ligatures (`->` stays two characters). Any `table`, one from Markdown included, is set in the house style.
- Figures: `#figure(image("name.svg", width: 100%), caption: […])`.

**From Markdown.** `render.markdown_pdf(md, out=None, title=None, eyebrow=None,
footer=None, dense=False)`, or `python -m tools.render md file.md`, sets a
Markdown file as a PDF in the house style with Typst's **cmarker** package:
headings, lists, tables, code, images relative to the `.md`. The first `#
heading` becomes the title unless `title` is given. The page is set from a
`_render_md_*.typ` beside the file, deleted after.

Compile with `python -m tools.render pdf doc.typ` (or `tools.render.pdf(path)`
from a script) -- only so, since it passes the theme: the venv's fonts only, the package path set, the Typst root at
the git checkout the file is in -- or the file's own folder when it is in none,
as in a temporary folder -- and Typst's own diagnostic -- file, line, caret --
when it fails. Inside the root, `image()` takes paths relative to the `.typ`
or absolute from the root (`"/docs/figures/x.svg"`).

**Fitting a page.** A one-pager is planned, not squeezed: `dense: true`; each
figure's canvas no taller than its content; a chart `beside` its explanation
rather than above it; captions of one sentence. After each build, render it
and count the PNGs -- `doc.png` alone means one page. Keep `$…$` out of
captions and body text unless you want math type: Typst sets it in its math
font. Join a number and its unit with a non-breaking space (`100~%`) so a line
never breaks between them.

## HTML — `tools.html`

```python
from tools.html import Page
page = Page("Title", eyebrow="Weekly report", lead="One paragraph under the title.")
page.kpis([("Requests", "1.24 M", "+8 % on week 41", "good"), …])   # tone: good | warn | bad | info | neutral
page.h2("Section")
page.p("Text, with <code>inline markup</code>.")
page.figure(canvas_or_matplotlib_figure, "Caption: what to notice.")
page.row((fig_a, "Caption A."), (fig_b, "Caption B."))           # side by side; stacked on a phone
page.callout("Watch", "…", tone="warn")
page.table(["Endpoint", "p99"], [["<code>GET /x</code>", "212 ms"]], numeric=(1,))
page.steps([(canvas_1, "A miss", "…"), (canvas_2, "The fill", "…")], "One key read twice.")
page.save(__file__.replace("build.py", "report.py"))              # -> report.html
```

- `frame(df, numeric=None, index=False, decimals=1)` — a pandas DataFrame as a table: columns of numbers (found by their type) right-aligned and grouped by thousands, fractions all to `decimals` places.
- `code(src, language=None, caption=None)` — source highlighted in the theme's colours (Pygments); plain when the language is unknown.
- `markdown(text, base=None)` — Markdown (markdown-it-py) set as the page is: its top headings as `h2`, tables in cards, code highlighted, and images relative to `base` embedded -- an SVG inline (it keeps the page's fonts and scrolls on a phone), others as data.
- `figure(obj, caption=None, min_width="560px")` — `obj` is a `Canvas`, a matplotlib figure, a path to an `.svg`, or SVG markup; it is checked as it goes in. Below `min_width` the figure scrolls sideways in its card instead of shrinking its text out of reach; `None` lets it shrink.
- `row(*figures)` — figures shrink to fit, so keep them small (charts about 4.2 in wide).
- `table` — cells are HTML; on a phone the table scrolls inside its card.
- `p`, `callout`, `table` cells take HTML: escape user text yourself.
- `save(target, footer=None)` — a script's `__file__` means `<script>.html` beside it.
- `Page(…, contents=True)` — each `h2` gets an anchor, and the page a contents bar of them: a card above the title on a narrow screen, a column held in view beside the text from 1220 px, the section being read marked. Printed, it is left out.
- `steps(frames, caption=None, min_width="560px")` — a process the reader steps through: `frames` is `[(figure, title, html), …]`, one shown at a time under Previous, Next and a numbered button for each, the arrow keys turning them when the figure has the focus. Draw every frame on the same canvas size with the same positions, changing only what the step changes, so the eye sees what moved. Each figure is checked as `figure` checks one. Printed or with scripts off, the frames stand one under the other with their titles and text.

- `chat(turns, caption=None, you="You", them="Claude")` — a conversation, to show what someone says and what comes back: `turns` is `[("you", html), ("them", html), …]`, yours at the right in the accent colour, the other's at the left in a card. A turn holds HTML: `<p>`, `<code>`, and `<pre>` for an answer laid out as text, which keeps its lines and columns and scrolls sideways in its turn where it is wider. Escape your own text.
- `image(path, caption=None, alt=None)` — a picture embedded as data, in a card across the column: a screenshot, a photo. WebP or JPEG keep the page light; cut a screenshot to about the width it is shown at (900 to 1000 px). `alt` defaults to the caption's text.

- `annotated(path, marks, caption=None, alt=None)` — a screenshot with numbered markers on it and their legend under it: `marks` is `[(x, y, html), …]`, x and y in the picture's own pixels. The markers are placed in percent, so they stay on their places at any width. Measure the places on the page at the width the screenshot was taken, and scale them to the width it is kept at.
- `diff(before, after, caption=None, labels=("Before", "After"), context=2)` — a text before and after a change, side by side (one under the other on a phone): each line taken out marked on the left, each put in marked on the right, long runs of unchanged lines folded to a line that says how many. Long lines wrap.
- `cards(items, kicker=None)` — links as cards in a grid: `items` is `[(href, title, html), …]`, `kicker` an optional small line above each title ("Chapter 3").

A page with `contents` or `steps` carries one small inline script of its own and nothing fetched; a page with neither has no script at all.

### A site of pages — `tools.html.Site`

```python
from tools.html import Site
site = Site("Using the product", "docs/manual")           # the folder it writes
home = site.page("index", "Welcome", lead="…")             # the first page is the home
one = site.page("01-start", "Start here", eyebrow="Chapter 1")
one.h2("…"); one.chat(…); one.annotated(…)                 # each is a Page, with every block above
site.save(footer="…")                                      # every page
```

Each page carries the site's navigation -- the home page, then every other page numbered, the one being read open on its own sections, folded into a button on a narrow screen -- and a link to the page before and after it. Each page links its fonts as a single page does, so the browser fetches them once for the whole site. The folder is the deliverable.

The file is one file: figures inline, the theme as CSS variables, and the
fonts linked from Google Fonts (`display=swap`, so the text shows at once). Behind
each family stand similar system fonts, declared as fallback faces (`src: local(…)`)
and sized -- size-adjust, ascent-, descent- and line-gap-override -- so their average
letter is as wide as the family's and their lines as tall: offline, or with Google
Fonts blocked, the page is set in them and the diagrams measured in the web font keep
their room (tools.webfonts; `python -m tools.webfonts` measures them again into
`themes/fallbacks.json`). An inline SVG, whose text names its family alone, gets the
same fallbacks from a rule of the page. A family set larger than its size (fonts.json
`scale`) is enlarged by font-size-adjust. A page carries no font; only a PDF embeds
its fonts.

## `python -m tools.render`

| Command | Does |
|---|---|
| `pdf doc.typ [-o out.pdf] [--root DIR] [--theme NAME]` | compile, as above; the theme is the document's project's unless named |
| `md file.md [-o out.pdf] [--title T] [--eyebrow E] [--footer F] [--dense] [--theme NAME]` | Markdown to a PDF in the house style |
| `png file.pdf file.svg … [--dpi 144] [-o DIR]` | a PNG per PDF page and per SVG, into `_preview/` beside each: `name.png` for a one-page PDF, `name-p01.png`, … for more (last run's pages of that PDF are removed first); SVGs are set by Typst, so their fonts are right. `--dpi 288` to look closely at where a line meets a label |
| `sheet doc.pdf [--per 12] [--cols 4] [--dpi 60]` | contact sheets of a long PDF, into `_preview/` |
| `check doc.pdf …` | overlapping or off-page text in a PDF; exits 1 when it finds any |

## The check — `tools.check`

Runs by itself in `save`, `save_chart` and `Page.figure`/`row`. It reports:
two labels overlapping; a label crossing a visible edge of a box it is not
inside (a box's edge counts when it has a stroke or a fill of its own; a label
carried on its own plate, as an arrow's is, is not crossing what lies under the
plate -- except a region's dashed border, which shows around the plate); a line
through a label (a lifeline, a rule), plate or no plate; a label running into a
dot or a step marker; a label off the canvas; in charts, a legend over text or data, a label
on a line or across the edge of a bar or a shaded area; in PDFs, text over
text and text off the page. `RICH_CONTENT_STRICT=1` makes any finding stop
the build.

It does not see crowding (two labels 3 px apart), a label nearer the wrong
thing, colour that carries meaning alone, or an arrow through a node. Those
are found by looking.

## Temporary files

Previews (`_preview/`) and the pages set while an SVG or Markdown renders
(`_render_*`, written into `_preview/` and deleted after) are made to look at
and thrown away. Each `_preview/` folder is made with a `.gitignore` of `*`,
so git ignores it, and everything in it, wherever in a checkout it is; never
commit one. The examples' outputs are committed; everything the kit writes
is reproducible -- a rebuild gives the same bytes -- so they change in git only
when what they show does. What is kept is a build script and what it writes.

## Licences

Everything the kit runs on is free to use, commercially too, and stays so:
typst (Apache-2.0), matplotlib (PSF-style), pypdfium2 (Apache-2.0 or BSD-3;
PDFium BSD-3), fontTools (MIT), Pillow (MIT-CMU), seaborn (BSD-3), pandas
(BSD-3), openpyxl (MIT), Pygments (BSD-2), markdown-it-py (MIT), segno (BSD-3), PyYAML (MIT),
the Typst package cmarker (MIT) and the fonts (SIL OFL
1.1, none with a reserved name or a trademark: Geist and Geist Mono, Public
Sans, Crimson Pro, EB Garamond, Atkinson Hyperlegible Next and Mono). The icons
are the skill's own drawings. Nothing copyleft, weak copyleft included:
PyMuPDF (AGPL) was replaced by pypdfium2, and Graphviz (EPL, its Windows build
LGPL libraries), which laid diagrams out, is gone -- diagrams are placed by
hand. A new dependency or font must be under such a licence too; the selftest
checks the packages, the fonts' own records, the icons, that PyMuPDF is
neither imported nor installed, and that Graphviz is not in the venv.
