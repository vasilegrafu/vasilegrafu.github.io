"""An HTML page with several kinds of object: the orders service's week, with stat tiles, an
architecture diagram, two charts side by side, a sequence diagram, a callout and a table. One
file, report.html, with the figures inlined and the fonts linked:

    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\examples\\html\\build.py
"""
from tools.chartstyle import C, plt
from tools.html import Page
from tools.svgkit import Canvas, Sequence

page = Page("Orders service, week 42", eyebrow="Weekly report",
            lead="Traffic grew and errors stayed low, but checkout leaned on retries all week: the payment "
                 "provider timed out on one charge in fifty.")

page.kpis([
    ("Requests", "1.24 M", "+8 % on week 41", "good"),
    ("p99 latency", "212 ms", "over the 200 ms budget", "bad"),
    ("Error rate", "0.21 %", "-0.04 pt", "good"),
    ("Cache hit rate", "91.4 %", "down from 94 %", "warn"),
])

# -- the system, with the part that misbehaved marked
page.h2("Where the trouble was")
c = Canvas(740, 250)
c.region(160, 14, 380, 222, "Orders service", icon="cloud")
user = c.node(4, 98, 126, 56, "client", "Browser", icon="monitor")
api = c.node(180, 98, 140, 56, "compute", "API", sub="3 instances", icon="server", count=3)
cache = c.node(416, 30, 108, 50, "cache", "Redis", icon="zap")
db = c.node(416, 170, 108, 50, "data", "Postgres", icon="database", shape="cylinder")
pay = c.node(586, 98, 150, 56, "external", "Payments", sub="third party", icon="credit-card", state="fail")
c.arrow(user.right, api.left)
c.arrow(api.right, cache.left)
c.arrow(api.right, db.left)
c.arrow(api.right, pay.left, label="POST /charges", label_at=0.5, color=C["bad"])
c.chip(pay.cx, pay.y2 + 12, "timeouts 2 %", tone="bad", anchor="middle", icon="clock")
page.figure(c, "The payment provider, outside our service, was the part that misbehaved; "
               "everything inside the dashed line held its budget except at lunch.")

# -- two charts side by side
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
requests = [182, 190, 188, 201, 214, 146, 121]
fig_a, ax = plt.subplots(figsize=(4.2, 2.6))
bars = ax.bar(days, requests, color=C["blue"], width=0.62)
bars[4].set_color(C["orange"])
ax.text(4, requests[4] + 9, "peak", ha="center", fontsize=8.5, color=C["orange"], fontweight=600)
ax.set_axisbelow(True)
ax.grid(axis="x", visible=False)
ax.set_ylim(0, 240)
ax.set_title("Requests per day (thousands)")

timeouts = [1.4, 1.9, 2.2, 2.6, 2.4, 1.7, 1.5]
fig_b, ax = plt.subplots(figsize=(4.2, 2.6))
ax.plot(days, timeouts, color=C["bad"], marker="o", markersize=4)
ax.axhline(1.0, color=C["muted"], lw=1, ls="--")
ax.text(6.1, 1.06, "agreed 1 %", ha="right", va="bottom", fontsize=8.5, color=C["muted"])
ax.set_ylim(0, 3)
ax.set_title("Payment timeouts (% of charges)")

page.row((fig_a, "Friday's peak was the busiest day of the quarter."),
         (fig_b, "Timeouts stayed above the agreed 1 % all week."))

# -- a sequence diagram of what a timeout costs
page.h2("What a timeout costs a customer")
c = Canvas(640, 330)
seq = Sequence(c, [("Browser", "client", "monitor"), ("API", "compute", "server"),
                   ("Payments", "external", "credit-card")], x0=90, spacing=230, box_w=140)
seq.msg(0, 1, 92, "POST /checkout")
seq.msg(1, 2, 132, "charge, key k-81f3", mono=True)
seq.msg(2, 1, 168, "no answer in 3 s", ret=True, tone="bad")
seq.msg(1, 2, 210, "charge, key k-81f3", mono=True, note="the same key: never charged twice")
seq.msg(2, 1, 262, "approved", ret=True, tone="good")
seq.msg(1, 0, 300, "201 Created", ret=True, tone="good")
seq.span(1, 92, 300)
page.figure(c, "A retry with the same idempotency key turns a timeout into a slower checkout, "
               "not a double charge.")
page.callout("Watch", "Every timeout adds 3 s to a checkout. At 2 % of charges that is about "
             "1 100 customers a week waiting twice as long to pay.", tone="warn")

# -- the busiest endpoints
page.h2("Endpoints")
page.table(
    ["Endpoint", "Requests", "p50", "p99", "Errors"],
    [
        ["<code>GET /orders/{id}</code>", "612 000", "44 ms", '<span class="tone-bad">212 ms</span>', "0.08 %"],
        ["<code>POST /checkout</code>", "54 000", "390 ms", '<span class="tone-bad">3.4 s</span>',
         '<span class="tone-warn">0.9 %</span>'],
        ["<code>GET /orders?customer=</code>", "148 000", "61 ms", "180 ms", "0.05 %"],
        ["<code>GET /orders/{id}/lines</code>", "96 000", "39 ms", "121 ms", "0.02 %"],
    ],
    numeric=(1, 2, 3, 4),
)

page.save(__file__.replace("build.py", "report.py"),
          footer="Built by .claude/skills/rich-content/examples/html/build.py with tools.html.")
