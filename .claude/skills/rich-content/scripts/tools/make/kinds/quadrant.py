"""
A 2x2: items placed by two measures on a square split into four, each quadrant named in its corner.
Each item's label goes in the first place round its dot where it meets no other label, dot, name or
line.

  x:          the measure across: "Effort" -- or {label, low, high}: the words at its two ends
  y:          the measure up: the same
  quadrants:  four names: [top left, top right, bottom left, bottom right]
  items:      [{label, x, y, tone}] -- or [label, x, y]; tone good | bad | warn | info colours its dot
  range:      {x: [low, high], y: [low, high]} -- the scale x and y are given in (0 to 1 by default)
  size:       the square's side in px (420)
"""
from __future__ import annotations

from ...svgkit import Canvas, text_width
from .. import Spec, SpecError

PURPOSE = "a 2x2: items placed by two measures, the four quadrants named"
GROUP = "diagrams"
OUTPUT = "svg"

Box = tuple[float, float, float, float]


def axis(spec: Spec, key: str) -> tuple[str, str | None, str | None]:
    v = spec.get(key)
    if v is None:
        raise SpecError(f"`{key}` is required: the measure's name, or {{label, low, high}}")
    if isinstance(v, Spec) or isinstance(v, dict):
        s = v if isinstance(v, Spec) else spec.wrap(v, f".{key}")
        return str(s.need("label")), s.get("low", kind=str), s.get("high", kind=str)
    return str(v), None, None


def _hits(a: Box, b: Box) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def draw(spec: Spec) -> Canvas:
    xl, xlo, xhi = axis(spec, "x")
    yl, ylo, yhi = axis(spec, "y")
    names = [str(q) for q in spec.get("quadrants", [], list)]
    if names and len(names) != 4:
        raise SpecError("quadrants: four names -- top left, top right, bottom left, bottom right")
    rng = spec.sub("range")
    rx = [float(v) for v in (rng.get("x", [0, 1], list) if rng else [0, 1])]
    ry = [float(v) for v in (rng.get("y", [0, 1], list) if rng else [0, 1])]
    items = []
    for k, it in enumerate(spec.items("items")):
        if isinstance(it, Spec):
            items.append((str(it.need("label")), float(it.need("x", (int, float))), float(it.need("y", (int, float))),
                          it.get("tone", None, str, ("good", "bad", "warn", "info"))))
        elif isinstance(it, list) and len(it) in (3, 4):
            items.append((str(it[0]), float(it[1]), float(it[2]), it[3] if len(it) == 4 else None))
        else:
            raise SpecError(f"items[{k}]: {{label, x, y, tone}} or [label, x, y]")
    S = spec.num("size", 420) or 420

    side = [text_width(t, 10, 500) for t in (ylo, yhi) if t]
    left = 18 + (max(side) + 10 if side else 0)
    top = 30
    c = Canvas(left + S + 24, top + S + 50)
    x0, y0, x1, y1 = left, top, left + S, top + S
    muted, rule = c.col("muted"), c.col("rule")

    def X(v: float) -> float:
        return x0 + (v - rx[0]) / (rx[1] - rx[0]) * S

    def Y(v: float) -> float:
        return y1 - (v - ry[0]) / (ry[1] - ry[0]) * S

    for k, (label, vx, vy, _) in enumerate(items):
        if not (min(rx) <= vx <= max(rx) and min(ry) <= vy <= max(ry)):
            raise SpecError(f"items[{k}] ({label}): {vx}, {vy} lies outside the range {rx}, {ry}")
    c.rect(x0, y0, S, S, fill=c.col("wash"), rx=c._rx(6), layer="bg")
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    c.line(mx, y0 + 6, mx, y1 - 6, stroke=rule, sw=1, dash="4 4", layer="regions")
    c.line(x0 + 6, my, x1 - 6, my, stroke=rule, sw=1, dash="4 4", layer="regions")
    c.arrow((x0, y1), (x1 + 14, y1), color=muted, sw=1.3, gap=0)
    c.arrow((x0, y1), (x0, y0 - 14), color=muted, sw=1.3, gap=0)
    c.text(mx, y1 + 34, xl, 11.5, 600, c.col("ink"), "middle")
    c.text(x0 + 12, y0 - 6, yl, 11.5, 600, c.col("ink"))          # beside the tip of the axis it names
    if xlo:
        c.text(x0, y1 + 16, xlo, 10, 500, muted)
    if xhi:
        c.text(x1, y1 + 16, xhi, 10, 500, muted, "end")
    if ylo:
        c.text(x0 - 8, y1 - 4, ylo, 10, 500, muted, "end")
    if yhi:
        c.text(x0 - 8, y0 + 10, yhi, 10, 500, muted, "end")

    taken: list[Box] = [(mx - 1, y0, mx + 1, y1), (x0, my - 1, x1, my + 1)]
    for k, name in enumerate(names):
        right, bottom = k % 2 == 1, k >= 2
        w = text_width(name.upper(), 10, 700) + 0.9 * len(name)
        tx = x1 - 12 if right else x0 + 12
        ty = y1 - 12 if bottom else y0 + 20
        c.text(tx, ty, name.upper(), 10, 700, muted, "end" if right else "start", letter_spacing=0.9)
        bx = tx - w if right else tx
        taken.append((bx - 4, ty - 12, bx + w + 4, ty + 4))
    dots = [(X(vx), Y(vy)) for _, vx, vy, _ in items]
    for px, py in dots:
        taken.append((px - 6, py - 6, px + 6, py + 6))
    for (label, vx, vy, tone), (px, py) in zip(items, dots):
        colour = c.th.signal[tone] if tone else c.th.kinds["compute"]["stroke"]
        c.circle(px, py, 5, fill=colour, stroke=c.col("paper"), sw=1.5, layer="top")
        tw = text_width(label, 11, 500)
        tries = [(px + 10, py + 4, "start"), (px - 10, py + 4, "end"), (px, py - 10, "middle"), (px, py + 18, "middle"),
                 (px + 8, py - 8, "start"), (px + 8, py + 16, "start"), (px - 8, py - 8, "end"), (px - 8, py + 16, "end")]
        best, best_n = None, 1e9
        for tx, ty, anchor in tries:
            bx = tx - tw if anchor == "end" else tx - tw / 2 if anchor == "middle" else tx
            box = (bx - 2, ty - 10, bx + tw + 2, ty + 3)
            inside = box[0] >= x0 + 2 and box[2] <= x1 - 2 and box[1] >= y0 + 2 and box[3] <= y1 - 2
            n = sum(1 for t in taken if _hits(box, t)) + (0 if inside else 5)
            if n < best_n:
                best, best_n = (tx, ty, anchor, box), n
            if n == 0:
                break
        assert best
        tx, ty, anchor, box = best
        c.text(tx, ty, label, 11, 500, c.col("ink"), anchor)
        taken.append(box)
    return c

