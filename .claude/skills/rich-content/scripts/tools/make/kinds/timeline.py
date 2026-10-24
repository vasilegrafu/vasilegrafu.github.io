"""
A timeline: milestones as dots on a dated axis, phases as bars in lanes under it, and today marked.
Milestone labels that would collide are lifted onto rows of their own; a phase's label sits in its
bar, or beside it when the bar is short.

  milestones:  [{date, label, tone}] -- or "2026-11-20: Beta"; tone good | bad | warn | info
  phases:      [{start, end, label, lane, kind}] -- a bar from start to end; phases of one lane
               share its row (moved to a second row where they overlap); kind colours the bar
               (client | edge | compute | cache | data | async | external), by lane by default
  today:       a date: a dashed line across the axis and the lanes
  width:       the figure's width in px (760)

Dates are written YYYY-MM-DD. The axis is marked by week or by month, whichever the span reads in.
"""
from __future__ import annotations

import datetime as dt
from typing import Any

from ...svgkit import Canvas, text_width
from .. import Spec, SpecError
from ..infer import KINDS

PURPOSE = "milestones and phases on a dated axis: a roadmap, a plan, a history"
GROUP = "diagrams"
OUTPUT = "svg"

MARGIN = 12
LANE_H, BAR_H = 30, 22
LEVEL_H = 34
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def date_of(v: Any, where: str) -> dt.date:
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    try:
        return dt.date.fromisoformat(str(v).strip())
    except ValueError:
        raise SpecError(f"{where}: {v!r} is not a date (YYYY-MM-DD)") from None


def milestones_of(spec: Spec) -> list[dict[str, Any]]:
    out = []
    for k, m in enumerate(spec.items("milestones")):
        where = f"milestones[{k}]"
        if isinstance(m, Spec) and "date" not in m and len(m.data) == 1:      # {2026-11-20: Beta}
            (d, label), = m.data.items()
            m.read.add(d)
            out.append({"date": date_of(d, where), "label": str(label), "tone": None})
        elif isinstance(m, Spec):
            out.append({"date": date_of(m.need("date"), where), "label": str(m.need("label")),
                        "tone": m.get("tone", None, str, ("good", "bad", "warn", "info"))})
        elif isinstance(m, str) and ":" in m:
            d, label = m.split(":", 1)
            out.append({"date": date_of(d, where), "label": label.strip(), "tone": None})
        else:
            raise SpecError(f"{where}: {{date, label}} or \"YYYY-MM-DD: label\"")
    return out


def phases_of(spec: Spec) -> list[dict[str, Any]]:
    out = []
    for k, p in enumerate(spec.items("phases")):
        if not isinstance(p, Spec):
            raise SpecError(f"phases[{k}]: {{start, end, label, lane}}")
        start, end = date_of(p.need("start"), f"phases[{k}].start"), date_of(p.need("end"), f"phases[{k}].end")
        if end < start:
            raise SpecError(f"phases[{k}]: it ends before it starts")
        out.append({"start": start, "end": end, "label": str(p.get("label", "")), "lane": str(p.get("lane", "") or ""),
                    "kind": p.get("kind", None, str, KINDS)})
    return out


def ticks(lo: dt.date, hi: dt.date) -> list[tuple[dt.date, str]]:
    span = (hi - lo).days
    out = []
    if span <= 100:                                    # weeks, from the first Monday
        d = lo + dt.timedelta(days=(7 - lo.weekday()) % 7)
        while d <= hi:
            out.append((d, f"{d.day} {MONTHS[d.month - 1]}"))
            d += dt.timedelta(days=7)
    else:                                              # months; every second or third when long
        every = 1 if span <= 400 else 3 if span <= 1200 else 12
        d = dt.date(lo.year, lo.month, 1)
        if d < lo:
            d = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
        while d <= hi:
            if (d.month - 1) % every == 0:
                year = d.month == 1 or not out
                out.append((d, f"{MONTHS[d.month - 1]} {d.year}" if year else MONTHS[d.month - 1]))
            d = dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return out


def draw(spec: Spec) -> Canvas:
    stones = milestones_of(spec)
    phases = phases_of(spec)
    today = spec.get("today")
    today = date_of(today, "today") if today is not None else None
    width = spec.num("width", 760) or 760
    dates = [m["date"] for m in stones] + [p["start"] for p in phases] + [p["end"] for p in phases] + \
        ([today] if today else [])
    if not dates:
        raise SpecError("a timeline needs `milestones` or `phases`")
    lo, hi = min(dates), max(dates)
    pad = max(2, (hi - lo).days // 25)
    lo, hi = lo - dt.timedelta(days=pad), hi + dt.timedelta(days=pad)
    span = max((hi - lo).days, 1)

    lanes = list(dict.fromkeys(p["lane"] for p in phases))
    named = any(lanes)
    lane_w = (max(text_width(name, 11, 600) for name in lanes) + 18) if named else 0
    x0, x1 = MARGIN + lane_w, width - MARGIN

    def X(d: dt.date) -> float:
        return x0 + (d - lo).days / span * (x1 - x0)

    # milestones: each on the lowest row where its label meets no label, and no stem crosses it
    # each label is a flag to the right of its stem (to the left near the right edge)
    placed: list[dict[str, Any]] = []
    for m in sorted(stones, key=lambda m: m["date"], reverse=True):
        x = X(m["date"])
        lw = max(text_width(m["label"], 11, 600), text_width(_day(m["date"]), 9.5, 400))
        left = x + 6 if x + 6 + lw <= width - MARGIN else x - 6 - lw
        box = (min(left, x) - 4, max(left + lw, x) + 4)

        def clashes(level: int) -> int:
            n = sum(1 for p in placed if p["level"] == level and box[0] < p["box"][1] and p["box"][0] < box[1])
            n += sum(1 for p in placed if p["level"] > level and box[0] < p["x"] < box[1])    # a stem through it
            n += sum(1 for p in placed if p["level"] < level and p["box"][0] < x < p["box"][1])  # its stem through one
            return n

        level = min(range(8), key=lambda L: (clashes(L) > 0, clashes(L), L))
        placed.append({**m, "x": x, "left": left, "box": box, "level": level})
    levels = max((p["level"] for p in placed), default=-1) + 1
    axis_y = MARGIN + levels * LEVEL_H + (14 if levels else 4)

    # phases: by lane, a second row where two overlap (counting a label written beside its bar)
    rows: list[tuple[str, list[dict[str, Any]]]] = []
    for lane in lanes:
        mine: list[list[dict[str, Any]]] = []
        for p in sorted((p for p in phases if p["lane"] == lane), key=lambda p: p["start"]):
            a, b = X(p["start"]), max(X(p["end"]), X(p["start"]) + 4)
            tw = text_width(p["label"], 10.5, 600)
            inside = tw + 16 <= b - a
            reach = b if inside else b + 6 + tw
            p.update(a=a, b=b, inside=inside, reach=reach)
            for row in mine:
                if row[-1]["reach"] + 8 < a:
                    row.append(p)
                    break
            else:
                mine.append([p])
        for k, row in enumerate(mine):
            rows.append((lane if k == 0 else "", row))
    top = axis_y + 34
    height = top + len(rows) * LANE_H + (22 if today else 4) + MARGIN
    c = Canvas(width, height)

    # the axis and its marks
    c.line(x0, axis_y, x1, axis_y, stroke=c.col("muted"), sw=1.2)
    marks = ticks(lo, hi)
    last = -1e9
    for d, text in marks:
        x = X(d)
        tw = text_width(text, 9.5, 500)
        c.line(x, axis_y, x, axis_y + 5, stroke=c.col("muted"), sw=1)
        if x - tw / 2 > last + 8 and x + tw / 2 < width - 2 and x - tw / 2 > 2:
            c.text(x, axis_y + 18, text, 9.5, 500, c.col("muted"), "middle")
            last = x + tw / 2
        if rows:                                           # a faint guide down through the lanes
            c.path(f"M{x:.2f},{top - 6:.2f} L{x:.2f},{top + len(rows) * LANE_H - 4:.2f}", stroke=c.col("rule"),
                   sw=0.6, dash="1 3", layer="regions")      # behind the bars, which hide it
    # lanes and bars
    kinds = ["compute", "cache", "data", "async", "edge", "client"]
    for r, (lane, row) in enumerate(rows):
        y = top + r * LANE_H
        if lane:
            c.text(MARGIN, y + BAR_H / 2 + 4, lane, 11, 600, c.col("ink"))
        for p in row:
            k = c.th.kinds[p["kind"] or kinds[lanes.index(p["lane"]) % len(kinds)]]
            c.rect(p["a"], y, p["b"] - p["a"], BAR_H, fill=k["fill"], stroke=k["stroke"], sw=1.2, rx=min(4, c._rx(4)))
            if p["inside"]:
                c.text(p["a"] + 8, y + BAR_H / 2 + 3.8, p["label"], 10.5, 600, c.col("ink"))
            elif p["label"]:
                c.text(p["b"] + 6, y + BAR_H / 2 + 3.8, p["label"], 10.5, 600, c.col("ink"))
    # milestones: a stem, a dot on the axis, the label and its date
    for p in placed:
        colour = c.th.signal[p["tone"]] if p["tone"] else c.col("accent")
        label_base = MARGIN + (levels - 1 - p["level"]) * LEVEL_H + 12
        c.line(p["x"], label_base + 18, p["x"], axis_y - 6, stroke=colour, sw=1.1)
        c.circle(p["x"], axis_y, 5, fill=colour, stroke=c.col("paper"), sw=1.5, layer="top")
        c.text(p["left"], label_base, p["label"], 11, 600, c.col("ink"))
        c.text(p["left"], label_base + 13, _day(p["date"]), 9.5, 400, c.col("muted"))
    if today:
        x = X(today)
        y_end = top + len(rows) * LANE_H
        c.path(f"M{x:.2f},{axis_y - 8:.2f} L{x:.2f},{y_end:.2f}", stroke=c.th.signal["bad"], sw=1.2, dash="4 3",
               layer="regions")
        c.text(x, y_end + 14, "today", 9.5, 600, c.th.signal["bad"], "middle")
    return c


def _day(d: dt.date) -> str:
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"
