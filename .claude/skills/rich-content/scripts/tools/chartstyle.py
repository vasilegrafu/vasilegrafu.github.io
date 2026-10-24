"""
chartstyle — matplotlib defaults matching svgkit's diagrams: the theme's label font, its colours,
its grid and frame.

    from tools.chartstyle import plt, save_chart, C
    fig, ax = plt.subplots(figsize=(6.4, 2.8))
    ...
    save_chart(fig, __file__)          # -> <name>.svg beside the script

Text stays real text in the SVG (svg.fonttype = none); Typst renders it with the theme's font.
use_theme() after the import restyles matplotlib and refills C.

seaborn draws on the same matplotlib, so its charts come out in the theme too: import it after this
module, never call sns.set_theme() (it would put its own look back), and pass palette=C_SERIES or a
colour map from sequential() / diverging() where it takes one.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("svg")
import matplotlib.pyplot as plt  # noqa: E402
from cycler import cycler  # noqa: E402
from matplotlib import font_manager  # noqa: E402

from .svgkit import out_path  # noqa: E402
from .theme import Theme, current, families, font_dir, on_theme  # noqa: E402

for _fam in families().values():
    for _f in sorted((font_dir() / _fam["folder"]).glob("*.[ot]tf")):
        font_manager.fontManager.addfont(str(_f))

# the theme's colours by name: greys, the six series colours named after technical's hues (each
# is the colour of a kind of component: blue compute, teal cache, green data, orange async,
# violet edge, slate client), and the signals
C: dict[str, str] = {}
C_SERIES: list[str] = []                            # the theme's six series colours, in order


def sequential(kind: str = "compute"):
    """A colour map for one quantity, low to high: from the page's colour to a kind's colour."""
    from matplotlib.colors import LinearSegmentedColormap
    th = current()
    return LinearSegmentedColormap.from_list(f"{th.name}-{kind}", [th.colour["paper"], th.kinds[kind]["stroke"]])


def diverging():
    """A colour map for a quantity with a middle that means 'as expected': blue below, the page's
    colour in the middle, orange above -- not green and red, which merge for one reader in twelve."""
    from matplotlib.colors import LinearSegmentedColormap
    th = current()
    return LinearSegmentedColormap.from_list(f"{th.name}-diverging",
                                             [th.kinds["compute"]["stroke"], th.colour["paper"], th.kinds["async"]["stroke"]])


@on_theme
def _style(th: Theme) -> None:
    col, k, sig = th.colour, th.kinds, th.signal
    C_SERIES[:] = th.series
    C.clear()
    C.update({
        "ink": col["ink"], "muted": col["muted"], "faint": col["faint"], "rule": col["rule"],
        "paper": col["paper"], "accent": col["accent"],
        "blue": k["compute"]["stroke"], "teal": k["cache"]["stroke"], "green": k["data"]["stroke"],
        "orange": k["async"]["stroke"], "violet": k["edge"]["stroke"], "slate": k["client"]["stroke"],
        "bad": sig["bad"], "good": sig["good"], "warn": sig["warn"],
        "bad_fill": sig["bad_fill"], "good_fill": sig["good_fill"], "warn_fill": sig["warn_fill"],
    })
    frame = th.chart["frame"]                       # left-bottom | bottom | box
    grid = th.chart["grid"]                         # both | y | none
    ticks = 3.5 if th.chart.get("ticks") else 0     # tick marks, pointing in, as journals draw them
    background = col["paper"] if th.dark else "none"
    plt.rcParams.update({
        "svg.fonttype": "none",
        "svg.hashsalt": "rich-content",             # the same ids every run: a rebuilt chart is the same file
        "font.family": th.label,
        "font.size": 9.5,
        "font.weight": 400,
        "text.color": col["ink"],
        "axes.edgecolor": col["faint"],
        "axes.labelcolor": col["muted"],
        "axes.labelsize": 9.5,
        "axes.labelweight": 500,
        "axes.titlesize": 10.5,
        "axes.titleweight": 600,
        "axes.titlelocation": "left",
        "axes.titlepad": 10,
        "axes.titlecolor": col["heading"] if th.dark else col["ink"],
        "axes.spines.top": frame == "box",
        "axes.spines.right": frame == "box",
        "axes.spines.left": frame in ("left-bottom", "box"),
        "axes.linewidth": 0.8,
        "axes.grid": grid != "none",
        "axes.grid.axis": grid if grid != "none" else "both",
        "axes.prop_cycle": cycler(color=th.series),
        "grid.color": col["rule"],
        "grid.linewidth": 0.6,
        "grid.alpha": 0.9,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "xtick.major.size": ticks,
        "ytick.major.size": ticks,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.color": col["muted"] if not ticks else col["ink"],
        "ytick.color": col["muted"] if not ticks else col["ink"],
        "legend.frameon": False,
        "legend.fontsize": 8.5,
        "lines.linewidth": 2.0,
        "lines.solid_capstyle": "round",
        "figure.facecolor": background,
        "axes.facecolor": "none",
        "savefig.facecolor": background,
        "savefig.transparent": not th.dark,
    })


def save_chart(fig, target: str | Path, name: str | None = None):
    """Write the SVG, and print what check finds in the laid-out figure (stopping if strict)."""
    from .check import figure_issues, report
    p = out_path(target)
    if name:
        p = p.with_name(name + ".svg")
    issues = figure_issues(fig)
    fig.savefig(p, format="svg", bbox_inches="tight", pad_inches=0.04, metadata={"Date": None})
    plt.close(fig)
    report(issues, p.name)
    return p
