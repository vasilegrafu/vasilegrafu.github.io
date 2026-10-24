"""A PDF with several kinds of object: a design note on how the orders service serves a read, with an
architecture diagram, a sequence diagram, two charts, a table and callouts. This script draws the four
figures beside itself, then sets report.typ into report.pdf:

    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\examples\\pdf\\build.py
    .venv\\Scripts\\python.exe -m tools.render png .claude\\skills\\rich-content\\examples\\pdf\\report.pdf
"""
from pathlib import Path

from tools import render
from tools.chartstyle import C, plt, save_chart
from tools.svgkit import Canvas, Sequence, save

HERE = Path(__file__).resolve().parent

# 1 -- architecture: where a read goes
c = Canvas(720, 276)
c.region(236, 14, 300, 232, "Orders service", icon="cloud")
user = c.node(4, 104, 130, 56, "client", "Browser", icon="monitor")
api = c.node(262, 104, 160, 56, "compute", "API", sub="3 instances", icon="server", count=3)
cache = c.node(574, 26, 142, 56, "cache", "Redis", sub="TTL 60 s", icon="zap")
db = c.node(574, 182, 142, 56, "data", "Postgres", icon="database", shape="cylinder")
queue = c.node(262, 188, 160, 48, "async", "Email queue", icon="mail")
c.arrow(user.right, api.left, label="GET /orders/42")
c.arrow(api.right, cache.left, label="1 · look up")
c.arrow(api.right, db.left, label="2 · on a miss", dash="5 4")
c.arrow(api.bottom, queue.top)
c.chip(cache.x2, cache.y2 + 8, "hit 91 %", tone="warn", anchor="end")
c.chip(db.x2, db.y2 + 12, "p99 38 ms", tone="neutral", anchor="end")
save(c, HERE / "architecture.svg")

# 2 -- sequence: a read that misses the cache
c = Canvas(720, 330)
seq = Sequence(c, [("Browser", "client", "monitor"), ("API", "compute", "server"),
                   ("Redis", "cache", "zap"), ("Postgres", "data", "database")],
               x0=84, spacing=184, box_w=132)
seq.msg(0, 1, 92, "GET /orders/42")
seq.msg(1, 2, 130, "GET order:42", mono=True)
seq.msg(2, 1, 162, "nil (a miss)", ret=True, tone="warn")
seq.msg(1, 3, 200, "SELECT … WHERE id = 42", mono=True, label_at=0.75)    # in the gap past Redis's lifeline
seq.msg(3, 1, 232, "1 row", ret=True, label_at=0.25)
seq.msg(1, 2, 268, "SET order:42 EX 60", mono=True, note="the next read is a hit")
seq.msg(1, 0, 306, "200 OK", ret=True, tone="good")
seq.span(1, 92, 306)
save(c, HERE / "sequence.svg")

# 3 -- line chart: response time over a day
hours = list(range(24))
p50 = [42 + 18 * (8 <= h <= 20) + (h % 5) for h in hours]
p99 = [v * 3.1 + 40 * (h in (12, 13, 19)) for h, v in zip(hours, p50)]
fig, ax = plt.subplots(figsize=(6.4, 2.5))
ax.plot(hours, p99, color=C["orange"])
ax.plot(hours, p50, color=C["blue"])
ax.axhline(200, color=C["bad"], lw=1, ls="--")
ax.text(0, 204, "budget 200 ms", color=C["bad"], ha="left", va="bottom", fontsize=8.5)
for series, name, color in ((p99, "p99", C["orange"]), (p50, "p50", C["blue"])):
    ax.text(23.4, series[-1], name, color=color, va="center", fontsize=8.5, fontweight=600)
ax.set_xlim(-0.5, 25)
ax.set_title("Response time over a day")
ax.set_xlabel("hour")
ax.set_ylabel("ms")
save_chart(fig, HERE / "latency.svg")

# 4 -- stacked bars: where the time of one read goes
parts = [("network", [8, 8], C["slate"]), ("cache", [2, 2], C["teal"]),
         ("database", [0, 34], C["green"]), ("serialise", [3, 4], C["violet"])]
fig, ax = plt.subplots(figsize=(6.4, 1.7))
left = [0.0, 0.0]
for name, ms, color in parts:
    ax.barh(["hit", "miss"], ms, left=left, color=color, height=0.55, label=name)
    left = [a + b for a, b in zip(left, ms)]
for y, total in enumerate(left):
    ax.text(total + 0.8, y, f"{total:.0f} ms", va="center", fontsize=8.5, fontweight=600, color=C["ink"])
ax.invert_yaxis()
ax.set_xlim(0, 56)
ax.set_axisbelow(True)
ax.grid(axis="y", visible=False)
ax.set_title("Where the time of one read goes")
ax.set_xlabel("ms")
ax.legend(ncols=4, loc="upper left", bbox_to_anchor=(0, -0.42), fontsize=8)
save_chart(fig, HERE / "breakdown.svg")

render.pdf(HERE / "report.typ")
