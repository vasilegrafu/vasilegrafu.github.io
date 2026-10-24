"""A chart in the same look as the diagrams. Run it, and chart.svg appears beside it; render it to
see it with its fonts:

    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\examples\\chart\\chart.py
    .venv\\Scripts\\python.exe -m tools.render png .claude\\skills\\rich-content\\examples\\chart\\chart.svg
"""
from tools.chartstyle import C, plt, save_chart

hours = list(range(24))
p50 = [42 + 18 * (8 <= h <= 20) + (h % 5) for h in hours]
p99 = [v * 3.1 + 40 * (h in (12, 13, 19)) for h, v in zip(hours, p50)]

fig, ax = plt.subplots(figsize=(6.4, 2.6))
ax.plot(hours, p99, color=C["orange"])
ax.plot(hours, p50, color=C["blue"])
ax.axhline(200, color=C["bad"], lw=1, ls="--")
ax.text(0, 204, "budget 200 ms", color=C["bad"], ha="left", va="bottom", fontsize=8.5)
ax.set_title("Response time over a day")
ax.set_xlabel("hour")
ax.set_ylabel("ms")
for series, name, color in ((p99, "p99", C["orange"]), (p50, "p50", C["blue"])):   # labels at the line ends
    ax.text(23.4, series[-1], name, color=color, va="center", fontsize=8.5, fontweight=600)
ax.set_xlim(-0.5, 25)
save_chart(fig, __file__)
