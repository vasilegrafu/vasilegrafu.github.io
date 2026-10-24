"""The themes side by side: for each style the skill carries, in its light and its dark mode, the same
diagram, chart, one-page PDF and HTML page -- and themes.html, one page that
shows them together, light beside dark, to choose a theme by looking. Each theme's files go in a
folder of its own beside this script; themes.html links to them.

    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\examples\\themes\\build.py

Serve the folder from a local server (python -m http.server) so the frames of each theme's HTML
page load.
"""
import base64
from html import escape
from pathlib import Path

from tools import render
from tools.chartstyle import C, plt, save_chart
from tools.html import Page, inline_svg
from tools.svgkit import Canvas, save
from tools.theme import Theme, load, styles, use_theme

HERE = Path(__file__).resolve().parent
ORDER = ["technical", "corporate", "editorial", "minimal", "accessible", "academic"]   # any other after

CODE = '''def get_order(order_id: int) -> Order:
    cached = redis.get(f"order:{order_id}")
    if cached is not None:              # a hit: 13 ms at p99
        return Order.parse(cached)
    return db.fetch_order(order_id)     # a miss: Postgres'''


def system():
    c = Canvas(884, 300)
    c.region(256, 14, 438, 272, "Orders service", icon="cloud")
    web = c.node(12, 136, 124, 48, "client", "Browser", icon="monitor")
    api = c.node(282, 132, 132, 56, "compute", "Orders API", sub="3 instances", icon="server", count=3)
    redis = c.node(556, 40, 124, 56, "cache", "Redis", sub="TTL 60 s", icon="zap")
    pg = c.node(556, 132, 124, 56, "data", "Postgres", icon="database", shape="cylinder")
    queue = c.node(552, 224, 132, 48, "async", "Email queue", icon="mail")
    mail = c.node(730, 224, 144, 48, "external", "Mail provider", icon="send")
    c.arrow(web.right, api.left, label="GET /orders/42")
    c.arrow(api.right, redis.left, label="1 · look up")
    c.arrow(api.right, pg.left, label="2 · on a miss", dash="5 4")
    c.arrow(api.right, queue.left)
    c.arrow(queue.right, mail.left)
    return c


def latency():
    hours = list(range(24))
    p50 = [42 + 18 * (8 <= h <= 20) + (h % 5) for h in hours]
    p99 = [v * 3.1 + 40 * (h in (12, 13, 19)) for h, v in zip(hours, p50)]
    fig, ax = plt.subplots(figsize=(4.6, 2.5))
    ax.plot(hours, p99, color=C["orange"])
    ax.plot(hours, p50, color=C["blue"])
    ax.axhline(200, color=C["bad"], lw=1, ls="--")
    ax.text(0, 204, "budget 200 ms", color=C["bad"], va="bottom", fontsize=8.5)
    for series, name, colour in ((p99, "p99", C["orange"]), (p50, "p50", C["blue"])):
        ax.text(23.4, series[-1], name, color=colour, va="center", fontsize=8.5, fontweight=600)
    ax.set_title("Response time over a day")
    ax.set_xlabel("hour")
    ax.set_ylabel("ms")
    ax.set_xlim(-0.5, 25.5)
    ax.set_ylim(0, 260)
    return fig


def requests():
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    counts = [182, 190, 186, 201, 236, 121, 118]
    fig, ax = plt.subplots(figsize=(4.6, 2.5))
    ax.set_axisbelow(True)
    bars = ax.bar(days, counts, width=0.62)                 # the theme's first series colour
    bars[4].set_color(C["accent"])
    ax.text(4, counts[4] + 8, "peak", ha="center", fontsize=8.5, color=C["accent"], fontweight=600)
    ax.set_ylim(0, 280)
    ax.set_title("Requests a day, thousands")
    return fig


ONE_PAGER = """#import "@local/rich-content:0.1.0": *
#show: report.with(title: "How the orders service serves a read", eyebrow: "Design note · {name}",
                   footer: "The {name} theme", dense: true)

A read of one order, `GET /orders/42`, is answered from Redis when it can be and from Postgres
when it cannot. This note shows the path, what a miss costs, and where the time goes.

#figure(image("system.svg", width: 100%), caption: [Three API instances behind one address;
Postgres only on a miss (the dashed arrow).])

#beside(widths: (1.2fr, 1fr),
  figure(image("latency.svg", width: 100%), caption: [p99 crosses the budget three times a day.]),
  [
    #callout("Key idea", tone: "info")[A miss is a slower read, not an error: the API fills the
    cache on its way back.]
    #data-table(([Read], [p50], [p99]), (([Hit], [9~ms], [13~ms]), ([Miss], [41~ms], [48~ms])),
                numeric: (1, 2))
  ],
)

```python
{code}
```
"""


def theme_page(th: Theme, folder: Path) -> Path:
    page = Page("Orders service, week 42", eyebrow=f"Weekly report · {th.name}", theme=th,
                lead="Traffic grew and errors stayed low, but checkout leaned on retries all week.")
    page.kpis([("Requests", "1.24 M", "+8 % on week 41", "good"), ("p99 latency", "212 ms", "over budget", "bad"),
               ("Cache hit rate", "91.4 %", "down from 94 %", "warn")])
    page.h2("Where a read goes")
    page.figure(folder / "system.svg", "Postgres answers only on a miss; emails leave through a queue.")
    page.row((latency(), "p99 crosses the budget at lunch."), (requests(), "Friday was the busiest day."))
    page.callout("Watch", "The hit rate fell three points; each point moves about 6 000 reads a day onto "
                 "Postgres.", tone="warn")
    page.code(CODE, "python", "The read, cache first.")
    page.table(["Endpoint", "Reads / day", "p99"],
               [["<code>GET /orders/{id}</code>", "612 000", "212 ms"],
                ["<code>GET /orders?customer=</code>", "148 000", "180 ms"]], numeric=(1, 2))
    return page.save(folder / "page.html")


def png_data(p: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode("ascii")


def build(name: str) -> tuple[Theme, Path, Path]:
    """Everything for one theme, in its folder; returns the theme, the folder and the PDF's preview."""
    th = use_theme(name)
    folder = HERE / name
    folder.mkdir(exist_ok=True)
    save(system(), folder / "system.svg")
    save_chart(latency(), folder / "latency.svg")
    (folder / "onepager.typ").write_text(ONE_PAGER.format(name=name, code=CODE), encoding="utf-8")
    pdf = render.pdf(folder / "onepager.typ")
    preview = render.png([pdf], dpi=80, out_dir=folder)[0]
    theme_page(th, folder)
    return th, folder, preview


def column(th: Theme, folder: Path, preview: Path) -> str:
    c, k, s = th.colour, th.kinds, th.signal
    swatch = ('<span title="{n} {v}" style="display:inline-block;width:22px;height:22px;border-radius:4px;'
              'background:{v};border:1px solid #0003;margin:0 3px 3px 0"></span>')
    swatches = ("".join(swatch.format(n=n, v=c[n]) for n in ("paper", "ink", "heading", "accent"))
                + " " + "".join(swatch.format(n=f"series {i + 1}", v=v) for i, v in enumerate(th.series[:4]))
                + " " + "".join(swatch.format(n=n, v=v["stroke"]) for n, v in k.items())
                + " " + "".join(swatch.format(n=n, v=s[n]) for n in ("good", "warn", "bad", "info")))
    name = th.name
    return (f'<div class="col"><h3>{escape(name)}</h3><p>{swatches}</p>'
            f'<figure><div class="card">{inline_svg(folder / "system.svg", f"{name}: a system")}</div></figure>'
            f'<figure><div class="card">{inline_svg(folder / "latency.svg", f"{name}: a chart")}</div></figure>'
            f'<figure><div class="card"><img src="{png_data(preview)}" alt="{name}: the one-page PDF" '
            f'style="width:100%;height:auto"></div><figcaption><a href="{name}/onepager.pdf">The one-page PDF</a>'
            f'</figcaption></figure>'
            f'<figure><div class="card" style="padding:0;overflow:hidden"><iframe loading="lazy" src="{name}/page.html" '
            f'title="{name}: the HTML page" style="width:100%;height:520px;border:0"></iframe></div>'
            f'<figcaption><a href="{name}/page.html">The HTML page</a></figcaption></figure></div>')


gallery = Page("The rich-content themes", eyebrow="Choosing a look",
               lead="Each style in its light and its dark mode: the same diagram, chart, one-page PDF and HTML "
                    "page. Pick one with <code>use_theme(\"corporate-dark\")</code> in a build script, or for a "
                    "whole project with a <code>rich-content.json</code> holding "
                    "<code>{\"theme\": \"corporate\", \"mode\": \"dark\"}</code>. Every theme passes WCAG AA "
                    "contrast (accessible, AAA), and its chart colours stay apart for colour-blind readers.",
               theme=load("technical-light"))
gallery.html("<style>.modes{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:20px}"
             ".modes h3{font-size:16px;margin:0 0 6px}.modes figure{margin:0 0 14px}</style>")

for style in sorted(styles(), key=lambda n: (ORDER.index(n) if n in ORDER else len(ORDER), n)):
    built = [build(f"{style}-{mode}") for mode in ("light", "dark")]
    th = built[0][0]
    gallery.h2(style.capitalize())
    gallery.p(escape(th.about))
    gallery.p(f"<strong>Text</strong> {th.text} · <strong>headings</strong> {th.heading} · "
              f"<strong>labels</strong> {th.label} · <strong>code</strong> {th.mono}")
    gallery.html('<div class="modes">' + "".join(column(*b) for b in built) + "</div>")

use_theme("technical-light")
print(f"html: {gallery.save(HERE / 'themes.html')}")
