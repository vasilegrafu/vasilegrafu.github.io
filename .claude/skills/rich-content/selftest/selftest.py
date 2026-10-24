"""
selftest — prove the rich-content kit, from the venv that will use it:

    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\selftest\\selftest.py
    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\selftest\\selftest.py --update-golden

1. ready      setup.py --check says everything the skill needs is there.
2. examples   each example builds with RICH_CONTENT_STRICT=1 (so any check finding fails it) and
              writes what it should: a diagram, a chart, a PDF, an HTML page, charts and a
              table from a CSV (pandas, seaborn), and a Markdown handout as a PDF
              and a page (cmarker, markdown-it-py) with highlighted code (Pygments) and a QR code
              (segno); the PDFs pass `render check` and render to their pages, in _preview/; the
              HTML pages are one file each, figures inline, fonts linked from Google Fonts with
              fallback faces behind them and none embedded, nothing else fetched; an
              Excel file reads back as it was written (openpyxl).
   specs      tools.make: every kind says what it is for, what it writes and its fields, and has an
              example; every example spec in examples/make makes its files, strict (impact and
              spec-graph only where the product-specs skill is beside this one), the PDFs pass
              `render check`, the pages fetch nothing but their fonts; a key a kind does not know is refused with
              the nearest one it does; a block of a page only is refused in a PDF.
3. golden     the example diagrams come out byte for byte as golden/ holds them, so a change to the
              kit that moves a pixel is seen. --update-golden takes what they are now, after you
              have looked at them and they are right.
4. the check  finds each overlap in a set of figures made to have one -- most of them overlaps
              that were first found by eye -- and finds nothing in a set made to look close but
              be right: labels inside bars, labels beside their lines, a wash's edge, two
              same-colour rects that make one band, a label moved into the gap between lifelines.
5. themes     every style in both modes -- twelve themes -- loads, names fonts that are there, meets
              WCAG AA contrast (its own bar where it sets one: AAA for accessible), and keeps its
              first four chart colours apart for typical, protan, deutan and tritan vision; a
              project's rich-content.json (with a mode), RICH_CONTENT_THEME and "extends" choose
              and make a theme; examples/themes builds every example in every theme, strict, each
              one-pager on one page; every HTML page links registered families, each with its
              fallback faces, and embeds none; themes/fallbacks.json is as the fonts measure (on
              Windows, where the system fonts it measures are).
6. licences   every package the kit imports, and each Typst package, is under a licence free for
              any use, PyMuPDF (AGPL) is neither imported nor installed, Graphviz (EPL, with LGPL
              libraries) is not in the venv, every font -- by
              fonts.json and by the font file's own records -- is OFL with no reserved name and no
              trademark, and every icon is one of the skill's own drawings.
7. leftovers  every preview and temporary page is one git ignores (each _preview/ folder
              carries a .gitignore of its own), no temporary page is left, the
              selftest's own _preview/ folders are deleted once checked, and a
              rebuild writes the examples' outputs -- which are committed -- byte for
              byte as before, so they change only when what they show does.

Prints a line per step and a last line, `selftest: N passed, M failed`; exits 1 on any failure.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
EX = SKILL / "examples"
GOLDEN = Path(__file__).resolve().parent / "golden"
PY = sys.executable

passed: list[str] = []
failed: list[str] = []
t0 = time.time()


def ok(name: str, good: bool, why: str = "") -> bool:
    (passed if good else failed).append(name)
    print(f"  {'pass' if good else 'FAIL'}  {name}" + (f" -- {why}" if why and not good else ""), flush=True)
    return good


FONT_HOSTS = ("https://fonts.googleapis.com", "https://fonts.gstatic.com")


def fetched(html: str) -> list[str]:
    """What a page loads from elsewhere, its fonts from Google Fonts aside."""
    urls = [a or b for a, b in re.findall(r'(?:src|href)="(https?:[^"]+)"|url\((https?:[^)]+)\)', html)]
    return [u for u in urls if not u.startswith(FONT_HOSTS)]


def links_fonts(html: str) -> bool:
    """The page links its fonts from Google Fonts, with fallback faces, and embeds none."""
    return ('href="https://fonts.googleapis.com/css2?' in html and "fallback" in html and "src:local(" in html
            and "data:font/" not in html)


def run(*args: str | Path, strict: bool = False) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    if strict:
        env["RICH_CONTENT_STRICT"] = "1"
    return subprocess.run([PY, *map(str, args)], capture_output=True, text=True, encoding="utf-8", env=env)


def step(title: str):
    print(f"{title}  ({time.time() - t0:.0f} s)", flush=True)


# 1 ---------------------------------------------------------------------------------------------
step("1 ready")
r = run(SKILL / "scripts" / "setup.py", "--check")
if not ok("setup.py --check", r.returncode == 0, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr):
    print(r.stdout)
    print("selftest: stopped -- run scripts/setup.py first")
    raise SystemExit(1)

# 2 ---------------------------------------------------------------------------------------------
step("2 examples")
builds = {
    "diagram": (EX / "diagram" / "diagram.py", ["diagram.svg"]),
    "chart": (EX / "chart" / "chart.py", ["chart.svg"]),
    "pdf": (EX / "pdf" / "build.py", ["architecture.svg", "sequence.svg", "latency.svg", "breakdown.svg",
                                       "report.pdf"]),
    "html": (EX / "html" / "build.py", ["report.html"]),
    "data": (EX / "data" / "build.py", ["spread.svg", "heatmap.svg", "report.html"]),
    "markdown": (EX / "markdown" / "build.py", ["path.svg", "qr.svg", "handout.pdf", "handout.html"]),
    "explainer": (EX / "explainer" / "build.py", ["explainer.html"]),
}
for name, (script, outputs) in builds.items():
    for o in outputs:
        (script.parent / o).unlink(missing_ok=True)
    r = run(script, strict=True)
    findings = [line for line in (r.stderr + r.stdout).splitlines() if line.startswith("check:")]
    ok(f"{name} builds clean", r.returncode == 0 and not findings,
       "; ".join(findings) or r.stderr.strip()[-300:])
    missing = [o for o in outputs if not (script.parent / o).exists()]
    ok(f"{name} writes {', '.join(outputs)}", not missing, f"missing {missing}")

pdf = EX / "pdf" / "report.pdf"
r = run("-m", "tools.render", "check", pdf)
ok("report.pdf passes render check", r.returncode == 0, r.stdout.strip())
preview = pdf.parent / "_preview"
for old in preview.glob("report-p*.png"):
    old.unlink()
r = run("-m", "tools.render", "png", pdf, "--dpi", "60")
pages = sorted(preview.glob("report-p*.png"))
ok("report.pdf renders to 2 pages", r.returncode == 0 and len(pages) == 2, f"{len(pages)} pages; {r.stderr[-200:]}")

html = (EX / "html" / "report.html").read_text(encoding="utf-8")
external = fetched(html)
ok("report.html fetches nothing but its fonts", not external, f"{external[:3]}")
ok("report.html links its fonts from Google Fonts, with fallback faces, and embeds none", links_fonts(html),
   f"{html.count('data:font/')} embedded")
ok("report.html inlines its 4 figures", html.count("<svg") == 4, f"{html.count('<svg')} svg elements")

handout = EX / "markdown" / "handout.pdf"
r = run("-m", "tools.render", "check", handout)
ok("handout.pdf (Markdown, set by cmarker) passes render check", r.returncode == 0, r.stdout.strip())
page = (EX / "markdown" / "handout.html").read_text(encoding="utf-8")
ok("handout.html: code highlighted, its figure and QR code inline, a table, nothing fetched but its fonts",
   'class="code"' in page and '<span class="k">def</span>' in page and page.count("<svg") == 2
   and "<table>" in page and not fetched(page),
   f"code: {'class="code"' in page}, svgs: {page.count('<svg')}, table: {'<table>' in page}")
explainer = (EX / "explainer" / "explainer.html").read_text(encoding="utf-8")
anchors = re.findall(r'<h2 id="([^"]+)">', explainer)
listed = re.findall(r'<nav class="toc"[^>]*>.*?</nav>', explainer, flags=re.S)
ok("explainer.html: a contents bar that lists each h2 by its anchor",
   len(anchors) == 3 and bool(listed) and all(f'href="#{a}"' in listed[0] for a in anchors),
   f"anchors {anchors}, contents {'found' if listed else 'missing'}")
ok("explainer.html: three steps, each its figure inline, with Previous, Next and a button each, and the script",
   explainer.count('class="step"') == 3 and explainer.count("<svg") == 3 and 'data-step="next"' in explainer
   and len(re.findall(r'aria-label="Step \d of 3: ', explainer)) == 3 and "classList.add(\"js\")" in explainer
   and not fetched(explainer),
   f"steps {explainer.count('class=\"step\"')}, svgs {explainer.count('<svg')}")
ok("a page with neither contents nor steps carries no script", "<script" not in html)
r = run("-c", r'''
import base64, pathlib, tempfile
from tools.html import Page
png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
with tempfile.TemporaryDirectory() as tmp:
    shot = pathlib.Path(tmp) / "shot.png"
    shot.write_bytes(png)
    page = Page("Talk")
    page.chat([("you", "write a PRD"), ("them", "<pre>Written: 3 requirements</pre>")], "A conversation.")
    page.image(shot, "A screenshot.")
    out = page.render()
assert out.count('class="turn you"') == 1 and out.count('class="turn them"') == 1, "the two turns"
assert 'src="data:image/png;base64,' in out and 'alt="A screenshot."' in out and 'width="1" height="1"' in out, "the image"
assert "<script" not in out, "a conversation and an image need no script"
print("ok")
''')
ok("a conversation and an embedded image: two turns, the picture as data with its size and alt, no script",
   r.returncode == 0 and r.stdout.strip().endswith("ok"), (r.stderr or r.stdout)[-300:])
r = run("-c", r'''
import base64, pathlib, re, tempfile
from tools.html import Site
png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
with tempfile.TemporaryDirectory() as tmp:
    folder = pathlib.Path(tmp) / "site"
    shot = pathlib.Path(tmp) / "shot.png"
    shot.write_bytes(png)
    site = Site("Manual", folder)
    home = site.page("index", "Welcome")
    home.h2("Start"); home.cards([("01-one.html", "One", "the first")], ["Chapter 1"])
    one = site.page("01-one", "One")
    one.h2("A change"); one.diff("a\nb\nc\n", "a\nB\nc\n", "b becomes B")
    one.annotated(shot, [(0.5, 0.5, "the only pixel")], "A screenshot, marked.")
    two = site.page("02-two", "Two")
    two.h2("End")
    written = site.save(footer="f")
    pages = {p.name: p.read_text(encoding="utf-8") for p in written}
    nothing_else = sorted(p.name for p in pathlib.Path(folder).iterdir()) == sorted(pages)
assert sorted(pages) == ["01-one.html", "02-two.html", "index.html"], sorted(pages)
assert nothing_else and all('href="https://fonts.googleapis.com/css2?' in t and "data:font/" not in t
                            for t in pages.values()), "fonts"
t = pages["01-one.html"]
assert 'class="home-link"' in t and '<ol class="chapters">' in t and t.count('aria-current="page"') == 1, "the navigation"
assert 'class="prev" href="index.html"' in t and 'class="next" href="02-two.html"' in t, "previous and next"
assert '<ol class="sections"><li><a href="#a-change">' in t, "the page open on its sections"
assert t.count('class="del"') == 1 and t.count('class="add"') == 1, "the diff"
assert t.count('class="pin"') == 1 and 'left:50.00%;top:50.00%' in t and "the only pixel" in t, "the marker"
assert 'class="tile" href="01-one.html"' in pages["index.html"], "the cards"
print("ok")
''')
ok("a site: pages that each link their fonts, nothing beside them, the navigation with the page open, previous and next, a diff, a marked "
   "screenshot, cards", r.returncode == 0 and r.stdout.strip().endswith("ok"), (r.stderr or r.stdout)[-300:])
data_page = (EX / "data" / "report.html").read_text(encoding="utf-8")
ok("data report: a DataFrame as a table, numbers right-aligned and grouped",
   '<td class="num">688\u202f635</td>' in data_page, "the summary's first count is not there as 688 635")
r = run("-c", r'''
import tempfile, pandas as pd
from pathlib import Path
from openpyxl import Workbook
with tempfile.TemporaryDirectory() as tmp:
    book = Path(tmp) / "b.xlsx"
    wb = Workbook(); ws = wb.active; ws.title = "week"
    for row in (["day", "requests"], ["Mon", 182], ["Fri", 236]):
        ws.append(row)
    wb.save(book)
    df = pd.read_excel(book, sheet_name="week")
print(df.to_dict("list"))
''')
ok("an Excel sheet reads back as written", r.stdout.strip() == "{'day': ['Mon', 'Fri'], 'requests': [182, 236]}",
   r.stdout.strip() + r.stderr.strip()[-200:])

# 2, specs ---------------------------------------------------------------------------------------
step("2 specs (tools.make)")
MAKE = EX / "make"
r = run("-c", r'''
import inspect
from tools.make import all_kinds, example
for name, mod in all_kinds().items():
    doc = inspect.cleandoc(mod.__doc__ or "")
    how = [f for f in ("draw", "document", "build") if hasattr(mod, f)]
    print(name, mod.GROUP, mod.OUTPUT, len(doc.splitlines()), len(how), example(name).exists(), sep="\t")
''')
kinds = [line.split("\t") for line in r.stdout.strip().splitlines()]
bad = [k[0] for k in kinds if int(k[3]) < 3 or k[4] != "1" or k[5] != "True"]
ok(f"every kind ({len(kinds)}) has a purpose, a group, an output, its fields, one way to make it and an example",
   r.returncode == 0 and len(kinds) >= 4 and not bad, (r.stderr[-300:] or f"lacking: {bad}"))


def here(spec: Path) -> bool:
    """Whether what the spec reads is here: impact and spec-graph read the product-specs skill's
    shop example, which a copy of rich-content without that skill does not have."""
    m = re.search(r"^specs:\s*(\S+)", spec.read_text(encoding="utf-8"), re.M)
    return not m or (spec.parent / m.group(1)).exists()


# a catalog shows what the others made, so it is made after them
specs = sorted(MAKE.glob("*.yaml"), key=lambda p: (p.stem == "catalog", p.name))
away = [p.name for p in specs if not here(p)]
specs = [p for p in specs if here(p)]
if away:
    print(f"  skip  {', '.join(away)}: what they read is not here (the product-specs skill)", flush=True)
r = run("-m", "tools.make", *specs, "--strict", strict=True)
findings = [line for line in (r.stderr + r.stdout).splitlines() if line.startswith(("check:", "spec:"))]
made = [Path(line[6:].strip()) for line in r.stdout.splitlines() if line.startswith("made: ")]
ok(f"every example spec ({len(specs)}) makes its files clean ({len(made)} files)",
   r.returncode == 0 and not findings and len(made) >= len(specs), "; ".join(findings[:4]) or r.stderr.strip()[-300:])
for f in made:
    if f.suffix == ".pdf":
        rc = run("-m", "tools.render", "check", f)
        ok(f"{f.name} passes render check", rc.returncode == 0, rc.stdout.strip()[-200:])
pages = [f for f in made if f.suffix == ".html"]
fetching = [f.name for f in pages if fetched(f.read_text(encoding="utf-8"))
            or not links_fonts(f.read_text(encoding="utf-8"))]
ok(f"the pages specs make fetch nothing but their fonts, linked ({len(pages)} pages)", bool(pages) and not fetching,
   ", ".join(fetching))
r = run("-c", r'''
import pathlib, tempfile
from tools.make import SpecError, make
with tempfile.TemporaryDirectory() as tmp:
    spec = pathlib.Path(tmp) / "x.yaml"
    spec.write_text("make: flow\nnodes: {a: A, b: B}\nedges: [a -> b]\ndirecton: down\n", encoding="utf-8")
    try:
        make(spec)
        print("made")
    except SpecError as e:
        print(e)
    spec.write_text("make: doc\ntitle: T\nformat: pdf\nblocks: [{chat: [[you, hi]]}]\n", encoding="utf-8")
    try:
        make(spec)
        print("made")
    except SpecError as e:
        print(e)
''')
lines = r.stdout.strip().splitlines()
ok("a misspelt key is refused with the nearest one the kind knows",
   bool(lines) and "directon" in lines[0] and "did you mean `direction`" in lines[0], r.stdout.strip() + r.stderr[-200:])
ok("a block of a page only is refused in a PDF", len(lines) > 1 and "for a page" in lines[-1],
   r.stdout.strip() + r.stderr[-200:])

# 3 ---------------------------------------------------------------------------------------------
step("3 golden")
diagrams = [EX / "diagram" / "diagram.svg", EX / "pdf" / "architecture.svg", EX / "pdf" / "sequence.svg"]
if "--update-golden" in sys.argv:
    GOLDEN.mkdir(exist_ok=True)
    for d in diagrams:
        shutil.copy(d, GOLDEN / d.name)
    print(f"  golden/ now holds {', '.join(d.name for d in diagrams)}")
for d in diagrams:
    g = GOLDEN / d.name
    ok(f"{d.name} matches golden", g.exists() and g.read_bytes() == d.read_bytes(),
       "no golden file" if not g.exists() else "differs: look at it, then --update-golden if it is right")

# 4 ---------------------------------------------------------------------------------------------
step("4 the check")
probe = r'''
import sys
from tools.chartstyle import C, plt
from tools.check import figure_issues
from tools.svgkit import Canvas, Sequence

def report(name, issues):
    print(f"{name}\t{len(issues)}\t{' | '.join(issues)}")

# must be found ---------------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.4, 1.7))           # the breakdown chart as it first was
left = [0, 0]
for name, ms in (("network", [8, 8]), ("cache", [2, 2]), ("database", [0, 34]), ("serialise", [3, 4])):
    ax.barh(["hit", "miss"], ms, left=left, height=0.55, label=name); left = [a + b for a, b in zip(left, ms)]
ax.set_title("Where the time of one read goes")
ax.legend(ncols=4, loc="lower right", bbox_to_anchor=(1, 1.02), fontsize=8)
report("bad:legend-on-title", figure_issues(fig)); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 2.6))
ax.plot(range(24), [130 + h for h in range(24)]); ax.text(12, 142, "p99")
report("bad:label-on-line", figure_issues(fig)); plt.close(fig)

fig, ax = plt.subplots(figsize=(4, 2.6))
ax.bar(["a", "b"], [10, 50], width=0.4); ax.text(0, 9, "a label far too long for its bar", ha="center")
report("bad:label-across-bar", figure_issues(fig)); plt.close(fig)

c = Canvas(300, 80)
c.text(10, 40, "first label", 12); c.text(60, 42, "second label", 12)
report("bad:labels-overlap", c.check())

c = Canvas(300, 80)
n = c.node(10, 10, 90, 50, "compute", "API")
c.text(60, 40, "a note across its edge", 11)
report("bad:label-across-node", c.check())

c = Canvas(200, 60)
c.text(150, 30, "runs off the right", 12)
report("bad:off-canvas", c.check())

c = Canvas(640, 160)                                 # the URL-shortener sequence as first drawn
seq = Sequence(c, [("API", "compute", "server"), ("Cache", "cache", "zap"), ("DB", "data", "database")],
               x0=80, spacing=230, box_w=130)
seq.msg(0, 2, 100, "SELECT … WHERE code = 'x7Kp2'", mono=True)
report("bad:lifeline-through-label", c.check())

c = Canvas(640, 160)
seq = Sequence(c, [("Browser", "client", "monitor"), ("API", "compute", "server")], x0=80, spacing=200,
               box_w=130)
seq.msg(1, 0, 100, "302 Found · Location: the long URL", ret=True)     # its right end under marker 1
report("bad:label-into-step-marker", c.check())

c = Canvas(420, 120)
c.region(150, 10, 200, 100, "Service")
a = c.node(10, 40, 100, 40, "client", "Browser"); b = c.node(220, 40, 100, 40, "compute", "API")
c.arrow(a.right, b.left, label="GET /orders/42 now")
report("bad:label-on-region-border", c.check())

# must not be found -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(4, 2.6))
ax.bar(["a", "b"], [50, 80], width=0.6); ax.text(1, 40, "80", ha="center", color="white")
ax.set_ylim(0, 100)
report("good:label-inside-bar", figure_issues(fig)); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 2.6))
ax.plot(range(24), [130 + h for h in range(24)]); ax.axhline(200, ls="--")
ax.text(0, 204, "budget 200 ms", va="bottom"); ax.text(23.4, 153, "p99", va="center"); ax.set_xlim(-0.5, 25)
ax.set_ylim(100, 240)
report("good:labels-beside-lines", figure_issues(fig)); plt.close(fig)

c = Canvas(420, 120)
c.region(200, 10, 200, 100, "Service")
a = c.node(10, 40, 70, 40, "client", "Browser"); b = c.node(260, 40, 100, 40, "compute", "API")
c.arrow(a.right, b.left, label="GET /x", label_at=0.33)               # label well before the border
report("good:arrow-label-clear-of-region", c.check())

c = Canvas(640, 160)
seq = Sequence(c, [("API", "compute", "server"), ("Cache", "cache", "zap"), ("DB", "data", "database")],
               x0=80, spacing=230, box_w=130)
seq.msg(0, 2, 100, "SELECT … WHERE code", mono=True, label_at=0.75)
report("good:label-in-the-gap", c.check())

c = Canvas(300, 80)
c.rect(10, 10, 120, 30, fill="#2563EB", opacity=0.1); c.rect(124, 10, 120, 30, fill="#15803D", opacity=0.1)
c.text(14, 30, "kettleandcrumb", 12); c.text(128, 30, "/products/42", 12)
report("good:wash-edges", c.check())

c = Canvas(260, 120)
c.rect(10, 10, 240, 100, fill="#FFF8EC", stroke="#B45309", rx=10)
c.rect(10, 10, 240, 30, fill="#B45309", rx=10); c.rect(10, 28, 240, 12, fill="#B45309")
c.text(22, 30, "1  17:20 the header band", 12, 700, "#FFFFFF")
report("good:same-colour-band", c.check())

c = Canvas(640, 200)
seq = Sequence(c, [("Browser", "client", "monitor"), ("API", "compute", "server"), ("DB", "data", "database")],
               x0=80, spacing=230, box_w=130)
seq.msg(0, 1, 92, "GET /x"); seq.msg(1, 2, 130, "SELECT …", mono=True, note="a note under it")
seq.msg(2, 1, 180, "rows", ret=True); seq.span(1, 92, 186)
report("good:sequence", c.check())
'''
r = run("-c", probe)
lines = [(ln.split("\t") + ["", ""])[:3] for ln in r.stdout.splitlines() if "\t" in ln]
ok("the probe runs", r.returncode == 0 and len(lines) == 16, r.stderr.strip()[-400:])
for name, count, what in lines:
    want_found = name.startswith("bad:")
    found = int(count) > 0
    ok(f"check {'finds' if want_found else 'passes'} {name[name.index(':') + 1:]}",
       found == want_found, what or "nothing found")

# 5 ---------------------------------------------------------------------------------------------
step("5 themes")
r = run("-c", r'''
from tools.theme import load, names, contrast_issues, colour_vision_issues, font_file
for n in names():
    th = load(n)
    missing = [f"{th.fonts[r]}" for r in ("text", "heading", "label", "mono") if not font_file(th.fonts[r]).exists()]
    issues = missing + contrast_issues(th) + colour_vision_issues(th)
    print(f"{n}\t{len(issues)}\t{' | '.join(issues)}")
''')
rows = [ln.split("\t") for ln in r.stdout.splitlines() if "\t" in ln]
ok("the twelve themes load: six styles, light and dark", r.returncode == 0 and len(rows) >= 12,
   f"{len(rows)} themes; " + r.stderr.strip()[-300:])
for name, count, what in rows:
    ok(f"{name}: fonts there, contrast WCAG, chart colours apart for colour-blind readers", count == "0", what)

import json  # noqa: E402
import tempfile  # noqa: E402
with tempfile.TemporaryDirectory() as tmp:
    proj = Path(tmp) / "proj"
    (proj / "deep").mkdir(parents=True)
    (proj / "rich-content.json").write_text('{"theme": "brand.json", "mode": "dark"}', encoding="utf-8")
    (proj / "brand.json").write_text(json.dumps({"name": "brand", "extends": "corporate",
                                                 "modes": {"dark": {"colour": {"accent": "#FF5A6E"}}}}),
                                     encoding="utf-8")
    probe_theme = r'''
import sys
from pathlib import Path
from tools.theme import resolve
th = resolve(Path(sys.argv[1]))
print(th.name, th.colour["accent"], th.label)
'''
    r = run("-c", probe_theme, proj / "deep")
    ok("a project's rich-content.json chooses its theme and mode, which extend a skill style",
       r.stdout.split() == ["brand-dark", "#FF5A6E", "Public", "Sans"], r.stdout + r.stderr[-200:])
    env_r = subprocess.run([PY, "-c", probe_theme, str(proj / "deep")], capture_output=True, text=True,
                           env={**os.environ, "RICH_CONTENT_THEME": "editorial-dark"})
    ok("RICH_CONTENT_THEME wins over the project's file", env_r.stdout.split()[:1] == ["editorial-dark"],
       env_r.stdout + env_r.stderr[-200:])

gallery = EX / "themes"
r = run(gallery / "build.py", strict=True)
findings = [line for line in (r.stderr + r.stdout).splitlines() if line.startswith("check:")]
ok("every example builds in every theme, strict", r.returncode == 0 and not findings,
   "; ".join(findings) or r.stderr.strip()[-300:])
theme_dirs = sorted(d for d in gallery.iterdir() if d.is_dir())
for d in theme_dirs:
    ok(f"{d.name}: the one-pager is one page", (d / "onepager.png").exists() and not list(d.glob("onepager-p*.png")),
       "more than one page")

r = run("-c", r"""
import re, sys
from pathlib import Path
from tools.theme import families
from tools.webfonts import measured
bad, linked = [], 0
for page in sys.argv[1:]:
    html = Path(page).read_text(encoding="utf-8")
    where = f"{Path(page).parent.name}/{Path(page).name}"
    if "data:font/" in html:
        bad.append(f"{where}: embeds a font")
    for query in re.findall(r'href="https://fonts\.googleapis\.com/css2\?([^"]+)"', html):
        for fam in (f.replace("+", " ") for f in re.findall(r"family=([^:&]+)", query)):
            linked += 1
            if fam not in families():
                bad.append(f"{where}: {fam} is not a family fonts.json lists")
            for local in measured()[fam]["fallbacks"]:
                if f'font-family:"{fam} fallback {local}"' not in html:
                    bad.append(f"{where}: no fallback face {local} for {fam}")
print(len(bad), linked, "; ".join(sorted(set(bad))[:5]))
""", EX / "html" / "report.html", gallery / "themes.html", *[d / "page.html" for d in theme_dirs])
ok("every HTML page links registered families from Google Fonts, each with its fallback faces, and embeds none",
   r.stdout.startswith("0 ") and r.stdout.split()[1] != "0", r.stdout.strip() + r.stderr.strip()[-300:])
if Path("C:/Windows/Fonts/arial.ttf").exists():
    r = run("-c", "from tools.webfonts import measure, measured; print(measure() == measured())")
    ok("themes/fallbacks.json is as the fonts measure (python -m tools.webfonts writes it)",
       r.stdout.strip() == "True", r.stdout.strip() + r.stderr.strip()[-300:])

# 6 ---------------------------------------------------------------------------------------------
step("6 licences")
FREE = ("Apache", "BSD", "MIT", "PSF", "Python Software Foundation", "HPND", "ISC", "MPL")
r = run("-c", r'''
import importlib.metadata as md
for name in ("typst", "matplotlib", "pypdfium2", "fonttools", "pillow", "numpy", "seaborn", "pandas", "openpyxl",
             "pygments", "markdown-it-py", "mdurl", "segno", "et-xmlfile", "pyyaml"):
    m = md.metadata(name)
    lic = m.get("License-Expression") or " ".join(c for c in (m.get_all("Classifier") or []) if c.startswith("License"))
    lic = lic or (m.get("License") or "")[:120]
    print(f"{name}\t{' '.join(lic.split())}")
''')
for line in r.stdout.splitlines():
    name, lic = line.split("\t")
    ok(f"{name} is free to use: {lic[:50]}", any(f in lic for f in FREE) and "GPL" not in lic, lic)
used = [str(f.relative_to(SKILL)) for f in SKILL.rglob("*.py")
        if re.search(r"^\s*(import|from)\s+(pymupdf|fitz)\b", f.read_text(encoding="utf-8"), re.M)]
ok("nothing imports PyMuPDF (AGPL)", not used, ", ".join(used))
r = run("-c", "import importlib.util as u; print(any(u.find_spec(m) for m in ('pymupdf', 'fitz')))")
ok("PyMuPDF (AGPL) is not installed in the venv", r.stdout.strip() == "False",
   "installed: .venv\\Scripts\\python.exe -m pip uninstall pymupdf" + r.stderr[-200:])
r = run("-c", "import sys; from pathlib import Path; print((Path(sys.prefix) / 'tools' / 'graphviz').exists())")
ok("Graphviz (EPL, with LGPL libraries) is not in the venv", r.stdout.strip() == "False",
   "there: delete .venv\\tools\\graphviz" + r.stderr[-200:])
fonts_json = json.loads((SKILL / "themes" / "fonts.json").read_text(encoding="utf-8"))
not_ofl = [k for k, v in fonts_json.items() if not k.startswith("_") and v["licence"] != "OFL-1.1"]
ok("every font family is OFL-1.1", not not_ofl, ", ".join(not_ofl))
r = run("-c", r'''
import json
from pathlib import Path
from fontTools.ttLib import TTFont
from tools.theme import families, font_dir
bad = []
for fam, f in families().items():
    for file in f["files"].values():
        name = TTFont(str(font_dir() / f["folder"] / file), lazy=True)["name"]
        record = name.getDebugName(13) or ""
        if "Open Font License" not in record:
            bad.append(f"{file}: {record[:40]!r}")
        if "reserved font name" in f"{name.getDebugName(0)} {record}".lower():
            bad.append(f"{file}: reserves a name")
        if name.getDebugName(7):
            bad.append(f"{file}: trademark {name.getDebugName(7)[:40]!r}")
print(len(bad), "; ".join(bad[:3]))
''')
ok("every font file's own licence record is the OFL, with no reserved name and no trademark",
   r.stdout.startswith("0 "), r.stdout.strip() + r.stderr[-200:])
r = run("-c", "from tools.svgkit import ICONS; print(ICONS)")
icons = sorted((SKILL / "icons").glob("*.svg"))
HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">')
foreign = [p.name for p in icons if not p.read_text(encoding="utf-8").startswith(HEAD)
           or re.search(r"lucide|feather|licen[cs]e|copyright", p.read_text(encoding="utf-8"), re.I)]
ok(f"every icon is the skill's own drawing ({len(icons)} in icons/, the only folder svgkit reads)",
   Path(r.stdout.strip()) == SKILL / "icons" and len(icons) > 0 and not foreign,
   r.stdout.strip() + " " + ", ".join(foreign))
toml = sorted((Path(PY).resolve().parent.parent / "share" / "typst" / "packages").rglob("typst.toml"))
lic = {t.parent.parent.name: re.search(r'license\s*=\s*"([^"]+)"', t.read_text(encoding="utf-8")) for t in toml}
ok("each Typst package is under a free licence: " + ", ".join(f"{k} {m.group(1) if m else '?'}" for k, m in lic.items()),
   bool(lic) and all(m and any(f in m.group(1) for f in FREE) for m in lic.values()), str(lic))

# 7 ---------------------------------------------------------------------------------------------
step("7 leftovers")
previews = [f for f in SKILL.rglob("*") if f.is_file() and "_preview" in f.parts]
rel = [f.relative_to(SKILL).as_posix() for f in previews]
# NUL-separated: Windows would turn a "\n" written to git into "\r\n", and git would read "x.png\r"
r = subprocess.run(["git", "check-ignore", "--no-index", "--stdin", "-z"], input="\0".join(rel) + "\0",
                   capture_output=True, text=True, cwd=SKILL)
ignored = set(r.stdout.split("\0"))
kept = [f for f in rel if f not in ignored]
ok(f"every preview is ignored by git ({len(previews)} files in _preview/ folders)", bool(previews) and not kept,
   ", ".join(kept[:5]) or "no previews were made")
temp = [str(f.relative_to(SKILL)) for f in SKILL.rglob("_render_*")]
ok("no temporary render page is left behind", not temp, ", ".join(temp))

again = {name: builds[name] for name in ("chart", "pdf", "html", "data", "markdown", "explainer")}
before = {script.parent / o: (script.parent / o).read_bytes() for script, outs in again.values() for o in outs}
for script, _ in again.values():
    run(script)
changed = [str(f.relative_to(SKILL)) for f, b in before.items() if f.read_bytes() != b]
ok(f"a rebuild writes the committed outputs byte for byte the same ({len(before)} files)", not changed,
   ", ".join(changed[:5]))
r = run("-m", "tools.make", "--check", *specs)
ok("the example specs' outputs are what they make now (tools.make --check)", r.returncode == 0,
   (r.stdout + r.stderr).strip()[-300:])

# last, as the rebuild and the check above make previews too: the selftest's own previews go, once
# checked, so the skill's folder is left as committed
for d in [d for d in SKILL.rglob("_preview") if d.is_dir()]:
    shutil.rmtree(d, ignore_errors=True)
left = [d.relative_to(SKILL).as_posix() for d in SKILL.rglob("_preview")]
ok("the selftest's previews are deleted once checked", not left, ", ".join(left[:3]))

print(f"selftest: {len(passed)} passed, {len(failed)} failed  ({time.time() - t0:.0f} s)")
raise SystemExit(1 if failed else 0)
