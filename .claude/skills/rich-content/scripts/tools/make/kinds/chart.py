"""
A chart from numbers written in the spec or read from a CSV or Excel file, in the theme's style;
lines and bars labelled directly rather than through a legend where they can be.

  type:     line | bar | hbar | stacked | area | scatter | waterfall | heatmap
  title:    what to see (not what the axes are)
  x:        the categories or x values: a list -- or, with data:, a column's name
  series:   name: [values] in order, one per line or bar group -- or, with data:, a list of columns
  data:     a .csv, .xlsx or .xls file beside the spec (sheet: for a sheet of a workbook)
  xlabel, ylabel:  the axes' titles;  unit: put after each value written on a bar (" ms", " %")
  ylim:     [low, high];  size: [width, height] in inches (6.4 x 2.6 fills an A4 column)
  marks:    [{y, label}] a threshold across the chart, or [{x, label}] a moment along it
  values:   true writes each bar's value on it
  legend:   true puts a legend in place of labels at the lines' ends (when they would crowd)
  colors:   [series colour names], in the order of series: blue teal green orange violet slate
            (the theme's colours by technical's hue names), or good | bad | warn | muted

  waterfall:  steps: {Start: 100, Sales: +20, Costs: -15, End: total} -- "total" closes the run
  heatmap:    rows: [names], cols: [names], values: [[…] per row]; scale: sequential | diverging;
              kind: the kind whose colour a sequential scale ends in (compute, async, data, …)
  scatter:    series: {name: [[x, y], …]};  labels: [text per point of the first series]
"""
from __future__ import annotations

from typing import Any

from .. import Spec, SpecError

PURPOSE = "a chart -- line, bar, stacked, area, scatter, waterfall, heatmap -- from numbers or a file"
GROUP = "charts"
OUTPUT = "svg"

TYPES = ("line", "bar", "hbar", "stacked", "area", "scatter", "waterfall", "heatmap")


def _table(spec: Spec) -> tuple[list[Any], dict[str, list[Any]]]:
    """x and the series, from the spec or its data file."""
    data = spec.path("data")
    if data is None:
        x = spec.get("x", None, list)
        series = {str(k): v for k, v in spec.get("series", {}, dict).items()}
        for k, v in series.items():
            if not isinstance(v, list):
                raise SpecError(f"series.{k}: expected a list of values")
            if x is not None and len(v) != len(x):
                raise SpecError(f"series.{k}: {len(v)} values for {len(x)} x values")
        return (x if x is not None else list(range(1, 1 + max((len(v) for v in series.values()), default=0)))), series
    import pandas as pd
    if data.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(data, sheet_name=spec.get("sheet", 0))
    else:
        df = pd.read_csv(data)
    xcol = spec.need("x", str)
    if xcol not in df.columns:
        raise SpecError(f"x: no column `{xcol}` in {data.name}; it has: {', '.join(map(str, df.columns))}")
    cols = spec.get("series", None)
    if cols is None:
        cols = [c for c in df.columns if c != xcol and pd.api.types.is_numeric_dtype(df[c])]
    if isinstance(cols, str):
        cols = [cols]
    for col in cols:
        if col not in df.columns:
            raise SpecError(f"series: no column `{col}` in {data.name}")
    return df[xcol].tolist(), {str(col): df[col].tolist() for col in cols}


def draw(spec: Spec) -> Any:
    from ...chartstyle import C, plt
    kind = spec.get("type", "line", str, TYPES)
    title = spec.get("title", kind=str)
    size = spec.get("size", None, list) or ([6.4, 3.2] if kind == "heatmap" else [6.4, 2.6])
    fig, ax = plt.subplots(figsize=(float(size[0]), float(size[1])))
    unit = spec.get("unit", "", str)
    names = ["blue", "teal", "green", "orange", "violet", "slate"]
    wanted = spec.get("colors", None, list)

    def col(k: int) -> str:
        name = wanted[k] if wanted and k < len(wanted) else names[k % len(names)]
        if name not in C:
            raise SpecError(f"colors: no colour `{name}`; there are: {', '.join(names + ['good', 'bad', 'warn', 'muted'])}")
        return C[name]

    if kind == "waterfall":
        _waterfall(ax, spec, C, unit)
    elif kind == "heatmap":
        _heatmap(ax, spec, unit)
    else:
        x, series = _table(spec)
        if not series:
            raise SpecError("`series` is required: name: [values]")
        labels = spec.get("labels", None, list)
        legend = spec.get("legend", False, bool)
        values = spec.get("values", False, bool)
        if kind in ("line", "area"):
            xs = list(range(len(x))) if any(isinstance(v, str) for v in x) else x
            ends = []
            for k, (name, ys) in enumerate(series.items()):
                if kind == "area":
                    ax.fill_between(xs, ys, alpha=0.18, color=col(k), lw=0)
                ax.plot(xs, ys, color=col(k), label=name, marker="o" if len(xs) <= 12 else None, ms=3.5)
                ends.append((ys[-1], name, col(k)))
            if xs is not x:
                ax.set_xticks(xs, [str(v) for v in x])
            if len(series) > 1 and not legend:
                _end_labels(ax, xs[-1], ends)
            elif legend:
                ax.legend(frameon=False)
        elif kind in ("bar", "hbar", "stacked"):
            import numpy as np
            pos = np.arange(len(x))
            n = len(series)
            width = 0.72 / (1 if kind == "stacked" else n)
            base = np.zeros(len(x))
            for k, (name, ys) in enumerate(series.items()):
                ys_ = np.array(ys, dtype=float)
                if kind == "stacked":
                    bars = ax.bar(pos, ys_, width, bottom=base, color=col(k), label=name)
                    base += ys_
                elif kind == "hbar":
                    bars = ax.barh(pos + (k - (n - 1) / 2) * width, ys_, width, color=col(k), label=name)
                else:
                    bars = ax.bar(pos + (k - (n - 1) / 2) * width, ys_, width, color=col(k), label=name)
                if values and kind != "stacked":
                    ax.bar_label(bars, labels=[_fmt(v) + unit for v in ys_], padding=3, fontsize=8.5, color=C["ink"])
            if kind == "hbar":
                ax.set_yticks(pos, [str(v) for v in x])
                ax.invert_yaxis()
                ax.grid(axis="y", visible=False)
                ax.set_xlim(0, max(max(v) for v in series.values()) * 1.15)
            else:
                ax.set_xticks(pos, [str(v) for v in x])
                ax.grid(axis="x", visible=False)
                top = base.max() if kind == "stacked" else max(max(v) for v in series.values())
                ax.set_ylim(0, top * (1.18 if values else 1.08))
            if n > 1:
                ax.legend(frameon=False, ncols=n, loc="lower left", bbox_to_anchor=(0, 1.0))
            ax.set_axisbelow(True)
        elif kind == "scatter":
            for k, (name, pts) in enumerate(series.items()):
                if not all(isinstance(p, list) and len(p) == 2 for p in pts):
                    raise SpecError(f"series.{name}: a scatter's points are [x, y] pairs")
                ax.scatter([p[0] for p in pts], [p[1] for p in pts], color=col(k), s=22, label=name, zorder=3)
            if labels:
                first = next(iter(series.values()))
                for p, text in zip(first, labels):
                    ax.annotate(str(text), (p[0], p[1]), xytext=(5, 4), textcoords="offset points", fontsize=8.5,
                                color=C["ink"])
            if len(series) > 1:
                ax.legend(frameon=False)
    for k, m in enumerate(spec.items("marks")):
        if not isinstance(m, Spec):
            raise SpecError(f"marks[{k}]: expected {{y, label}} or {{x, label}}")
        label = m.get("label", "", str)
        if "y" in m:
            y = m.num("y")
            ax.axhline(y, color=C["bad"], lw=1, ls=(0, (4, 3)), zorder=1)
            ax.text(0.005, y, f" {label}", transform=ax.get_yaxis_transform(), va="bottom", ha="left",
                    fontsize=8.5, color=C["bad"])
        else:
            xv = m.need("x")
            if kind in ("line", "area"):
                x, _ = _table(spec) if "series" in spec.data or "data" in spec.data else ([], {})
                xv = x.index(xv) if x and xv in x and any(isinstance(v, str) for v in x) else xv
            ax.axvline(xv, color=C["muted"], lw=1, ls=(0, (4, 3)), zorder=1)
            ax.text(xv, 1.0, f" {label}", transform=ax.get_xaxis_transform(), va="top", ha="left", fontsize=8.5,
                    color=C["muted"])
    from matplotlib.ticker import FuncFormatter
    for axis in (ax.yaxis, ax.xaxis):                  # thousands grouped, as tables write them
        if kind != "heatmap" and not (axis is ax.xaxis and kind in ("bar", "stacked", "waterfall", "line", "area"))                 and not (axis is ax.yaxis and kind == "hbar"):
            axis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}" if abs(v) >= 1000 else f"{v:g}"))
    ylim = spec.get("ylim", None, list)
    if ylim:
        ax.set_ylim(float(ylim[0]), float(ylim[1]))
    if spec.get("xlabel", kind=str):
        ax.set_xlabel(spec.get("xlabel"))
    if spec.get("ylabel", kind=str):
        ax.set_ylabel(spec.get("ylabel"))
    if title:
        ax.set_title(title, pad=22 if kind in ("bar", "stacked") and len(spec.get("series", {}) or {}) > 1 else 8)
    return fig


def _fmt(v: float) -> str:
    return f"{v:,.0f}" if abs(v) >= 100 or float(v).is_integer() else f"{v:,.1f}"


def _end_labels(ax: Any, x_last: Any, ends: list[tuple[float, str, str]]) -> None:
    """Each line's name at its end, nudged apart where two ends are close."""
    lo, hi = ax.get_ylim()
    gap = (hi - lo) * 0.075
    placed: list[float] = []
    for y, name, colour in sorted(ends):
        y_ = max([y] + [p + gap for p in placed if p > y - gap])
        placed.append(y_)
        ax.annotate(name, (x_last, y), xytext=(8, (y_ - y) / (hi - lo) * ax.bbox.height * 0.75),
                    textcoords="offset points", va="center", fontsize=8.5, color=colour)


def _waterfall(ax: Any, spec: Spec, C: dict[str, str], unit: str) -> None:
    steps = spec.get("steps", None, dict)
    if not steps:
        raise SpecError("waterfall: `steps` is required: {Start: 100, Sales: +20, End: total}")
    names, bottoms, heights, colours, shown = [], [], [], [], []
    run = 0.0
    for k, (name, v) in enumerate(steps.items()):
        names.append(str(name))
        if v == "total" or (k == 0 and isinstance(v, (int, float))):
            if v != "total":
                run = float(v)
            bottoms.append(0)
            heights.append(run)
            colours.append(C["slate"])
            shown.append(_fmt(run) + unit)
            continue
        if not isinstance(v, (int, float)):
            raise SpecError(f"steps.{name}: a number (+20, -15) or total")
        bottoms.append(run if v >= 0 else run + v)
        heights.append(abs(v))
        colours.append(C["blue"] if v >= 0 else C["orange"])
        shown.append(("+" if v >= 0 else "−") + _fmt(abs(v)) + unit)
        run += v
    bars = ax.bar(range(len(names)), heights, 0.62, bottom=bottoms, color=colours)
    ax.bar_label(bars, labels=shown, padding=3, fontsize=8.5, color=C["ink"])
    for k in range(len(names) - 1):                    # a thin line from each bar's top to the next
        top = bottoms[k] + heights[k] if (colours[k] != C["orange"]) else bottoms[k]
        ax.plot([k + 0.31, k + 0.69], [top, top], color=C["muted"], lw=0.8)
    ax.set_xticks(range(len(names)), names)
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, max(b + h for b, h in zip(bottoms, heights)) * 1.15)
    ax.set_axisbelow(True)


def _heatmap(ax: Any, spec: Spec, unit: str) -> None:
    import numpy as np
    import seaborn as sns
    from ...chartstyle import diverging, sequential
    rows = [str(r) for r in spec.need("rows", list)]
    cols = [str(c) for c in spec.need("cols", list)]
    values = np.array(spec.need("values", list), dtype=float)
    if values.shape != (len(rows), len(cols)):
        raise SpecError(f"values: {values.shape[0]} rows of {values.shape[1] if values.ndim > 1 else '?'} for "
                        f"{len(rows)} rows of {len(cols)}")
    scale = spec.get("scale", "sequential", str, ("sequential", "diverging"))
    kind = spec.get("kind", "compute", str)
    cmap = diverging() if scale == "diverging" else sequential(kind)
    sns.heatmap(values, ax=ax, cmap=cmap, annot=True, fmt=".0f", annot_kws={"fontsize": 8},
                xticklabels=cols, yticklabels=rows, linewidths=1, linecolor=ax.figure.get_facecolor() or "white",
                cbar_kws={"label": unit.strip()} if unit else {})
    ax.tick_params(length=0)
    ax.set_yticklabels(rows, rotation=0)

