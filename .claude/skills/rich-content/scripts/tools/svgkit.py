"""
svgkit — the diagram kit, borrowed from ai-workbench-learning's System Design manual.

One visual language for every architecture diagram, request flow, before/after figure,
failure timeline and decision tree. Colours, fonts and shapes come from the theme (tools.theme,
shared with charts, HTML pages and the Typst package) the canvas is made in; icons from the skill's
own set (icons/); text is real SVG text, measured with fontTools so boxes fit their labels -- and
recorded, so save() can say where two labels collide.

Typical use, in any <name>.py run with the venv's python:

    from tools.svgkit import Canvas, save
    c = Canvas(640, 240)
    app = c.node(40, 90, 150, 56, "compute", "App server", icon="server")
    db  = c.node(420, 90, 150, 56, "data", "Database", icon="database", shape="cylinder")
    c.arrow(app.right, db.left, label="SELECT …")
    save(c, __file__)          # -> <name>.svg beside the script
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

from .theme import SKILL, Theme, current, font_file, use_theme
from .theme import font_dir as _font_dir  # noqa: F401  (chartstyle, html and render take it from here too)

PACKAGES = SKILL / "typst"                       # Typst's package_path: local/rich-content/<version>/
PACKAGE = PACKAGES / "local" / "rich-content" / "0.1.0"


# ----------------------------------------------------------------------------------------------
# Text measurement
# ----------------------------------------------------------------------------------------------
ICONS = SKILL / "icons"                          # the skill's own drawings, one <name>.svg each


@lru_cache(maxsize=None)
def _metrics(family: str, weight: int):
    from fontTools.ttLib import TTFont
    font = TTFont(str(font_file(family, weight)), lazy=True)
    cmap = font.getBestCmap() or {}
    hmtx = font["hmtx"]
    upm: int = getattr(font["head"], "unitsPerEm")   # set when the table is read, so not declared
    default = hmtx[cmap.get(ord("n"), ".notdef")][0]
    return cmap, hmtx, upm, default


def text_width(s: str, size: float, weight: int = 400, family: str | None = None) -> float:
    """The width of s set in `family` (the current theme's label font when None)."""
    cmap, hmtx, upm, default = _metrics(family or current().label, weight)
    units = sum(hmtx[cmap[ord(ch)]][0] if ord(ch) in cmap else default for ch in s)
    return units * size / upm


def wrap(s: str, width: float, size: float, weight: int = 400, family: str | None = None) -> list[str]:
    """Greedy word wrap to a pixel width."""
    lines, cur = [], ""
    for word in s.split():
        trial = f"{cur} {word}".strip()
        if cur and text_width(trial, size, weight, family) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


# ----------------------------------------------------------------------------------------------
# Icons
# ----------------------------------------------------------------------------------------------
@lru_cache(maxsize=None)
def _icon_body(name: str) -> str:
    path = ICONS / f"{name}.svg"
    if not path.exists():
        raise ValueError(f"no icon {name!r}; the skill has {', '.join(sorted(p.stem for p in ICONS.glob('*.svg')))}")
    svg = path.read_text(encoding="utf-8")
    m = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S)
    if m is None:
        raise ValueError(f"not an SVG icon: {name}")
    return re.sub(r"\s+", " ", m.group(1)).strip()


def icon_svg(name: str, x: float, y: float, size: float, color: str, stroke: float = 2.0) -> str:
    s = size / 24
    return (
        f'<g transform="translate({x:.2f},{y:.2f}) scale({s:.4f})" fill="none" stroke="{color}" '
        f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{_icon_body(name)}</g>'
    )


# ----------------------------------------------------------------------------------------------
# Geometry
# ----------------------------------------------------------------------------------------------
@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float
    pr: float = 0      # extra reach on the right / top (fleet cards stacked behind the box)
    pt: float = 0

    @property
    def cx(self): return self.x + self.w / 2
    @property
    def cy(self): return self.y + self.h / 2
    @property
    def left(self): return (self.x, self.cy)
    @property
    def right(self): return (self.x + self.w + self.pr, self.cy)
    @property
    def top(self): return (self.cx, self.y - self.pt)
    @property
    def bottom(self): return (self.cx, self.y + self.h)
    @property
    def x2(self): return self.x + self.w
    @property
    def y2(self): return self.y + self.h

    def at(self, side: str, t: float = 0.5):
        """Point on a side; t runs 0..1 left→right or top→bottom."""
        return {
            "left": (self.x, self.y + self.h * t),
            "right": (self.x2 + self.pr, self.y + self.h * t),
            "top": (self.x + self.w * t, self.y - self.pt),
            "bottom": (self.x + self.w * t, self.y2),
        }[side]


def _f(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


# ----------------------------------------------------------------------------------------------
# Canvas
# ----------------------------------------------------------------------------------------------
class Canvas:
    LAYERS = ("bg", "regions", "edges", "nodes", "labels", "top")

    def __init__(self, w: float, h: float, background: str | None = None, theme: str | Theme | None = None):
        """Everything drawn on the canvas is in `theme` -- a name, a file or a Theme -- or, by
        default, the current one (tools.theme). A dark theme's canvas has its paper behind it, so
        it reads anywhere."""
        self.th = current() if theme is None else (theme if isinstance(theme, Theme) else use_theme(theme))
        self.w, self.h = w, h
        self.background = background or (self.th.colour["paper"] if self.th.dark else None)
        self._layers: dict[str, list[str]] = {k: [] for k in self.LAYERS}
        # what check() reads: each text's box, and each box drawn (rects and cylinders), with the
        # order it paints in -- (layer, sequence) -- and whether it is filled, so it hides what is under it
        self._texts: list[tuple[float, float, float, float, str, tuple[int, int]]] = []
        # x0, y0, x1, y1, opaque (filled and hiding what is under it), (layer, seq), fill, stroke
        self._shapes: list[tuple[float, float, float, float, bool, tuple[int, int], str, str | None]] = []
        self._lines: list[tuple[float, float, float, float]] = []        # visible straight lines
        self._circles: list[tuple[float, float, float, float]] = []      # their boxes: dots, step markers
        self._seq = 0

    def _z(self, layer: str) -> tuple[int, int]:
        self._seq += 1
        return (self.LAYERS.index(layer), self._seq)

    def check(self) -> list[str]:
        """What a reader would see as broken: two labels that collide, a label that crosses the
        edge of a box it is not inside (unless something filled, painted later, carries it, as an
        arrow's label plate does), a label that runs off the canvas."""
        from .check import svg_canvas_issues
        return svg_canvas_issues(self.w, self.h, self._texts, self._shapes, self._lines, self._circles)

    def col(self, key: str) -> str:
        """A colour of the canvas's theme: ink, muted, faint, rule, paper, wash, heading, accent, on."""
        return self.th.colour[key]

    def _rx(self, r: float) -> float:
        """A corner of radius r, no rounder than the theme's corners."""
        return min(r, self.th.shape["radius"])

    def _pill(self, h: float) -> float:
        return h / 2 if self.th.shape["pills"] else self._rx(h / 2)

    # -- raw ------------------------------------------------------------------------------------
    def raw(self, svg: str, layer: str = "nodes"):
        self._layers[layer].append(svg)

    def to_svg(self) -> str:
        body = []
        if self.background:
            body.append(f'<rect width="{_f(self.w)}" height="{_f(self.h)}" fill="{self.background}"/>')
        for k in self.LAYERS:
            body.extend(self._layers[k])
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{_f(self.w)}" height="{_f(self.h)}" '
            f'viewBox="0 0 {_f(self.w)} {_f(self.h)}">\n' + "\n".join(body) + "\n</svg>\n"
        )

    # -- text -----------------------------------------------------------------------------------
    def text(self, x, y, s, size: float = 12, weight=400, color=None, anchor="start", family=None,
             layer="labels", italic=False, letter_spacing=None):
        family = family or self.th.label
        color = color or self.col("ink")
        style = ' font-style="italic"' if italic else ""
        ls = f' letter-spacing="{letter_spacing}"' if letter_spacing else ""
        if s.strip():
            tw = text_width(s, size, weight, family) + (letter_spacing or 0) * len(s)
            x0 = x - tw if anchor == "end" else (x - tw / 2 if anchor == "middle" else x)
            # cap height and, only where the text has them, descenders -- a sans label's, near enough for the rest
            down = 0.2 if any(ch in "gjpqyQ(),;[]{}|_@$" for ch in s) else 0.03
            self._texts.append((x0, y - 0.74 * size, x0 + tw, y + down * size, s, self._z(layer)))
        # a name with a word starting with a digit (a brand's "Sans 3") is CSS only when quoted
        fam = f"'{family}'" if any(w[0].isdigit() for w in family.split()) else family
        self.raw(
            f'<text x="{_f(x)}" y="{_f(y)}" font-family="{fam}" font-size="{_f(size)}" '
            f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}"{style}{ls}>{escape(s)}</text>',
            layer,
        )

    def lines(self, x, y, lines, size: float = 12, weight=400, color=None, anchor="start", family=None,
              leading=1.3, layer="labels"):
        for i, ln in enumerate(lines):
            self.text(x, y + i * size * leading, ln, size, weight, color, anchor, family, layer)

    def paragraph(self, x, y, s, width, size: float = 12, weight=400, color=None, family=None, leading=1.35,
                  anchor="start", layer="labels"):
        ls = wrap(s, width, size, weight, family or self.th.label)
        self.lines(x, y, ls, size, weight, color, anchor, family, leading, layer)
        return len(ls) * size * leading

    # -- shapes ---------------------------------------------------------------------------------
    def rect(self, x, y, w, h, fill="none", stroke=None, sw=1.0, rx: float = 0, dash=None, opacity=None,
             layer="nodes"):
        st = f' stroke="{stroke}" stroke-width="{_f(sw)}"' if stroke else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        filled = fill not in ("none", "transparent") and (opacity is None or opacity >= 0.9)
        wash = opacity is not None and opacity < 0.3 and not stroke     # a tint whose edge barely shows
        self._shapes.append((x, y, x + w, y + h, filled, self._z(layer), "none" if wash else fill, stroke))
        self.raw(f'<rect x="{_f(x)}" y="{_f(y)}" width="{_f(w)}" height="{_f(h)}" rx="{_f(rx)}" '
                 f'fill="{fill}"{st}{da}{op}/>', layer)

    def circle(self, cx, cy, r, fill="none", stroke=None, sw=1.0, layer="nodes", opacity=None):
        st = f' stroke="{stroke}" stroke-width="{_f(sw)}"' if stroke else ""
        op = f' opacity="{opacity}"' if opacity is not None else ""
        if fill not in ("none", "transparent") or stroke:
            self._circles.append((cx - r, cy - r, cx + r, cy + r))
        self.raw(f'<circle cx="{_f(cx)}" cy="{_f(cy)}" r="{_f(r)}" fill="{fill}"{st}{op}/>', layer)

    def line(self, x1, y1, x2, y2, stroke=None, sw=1.0, dash=None, layer="edges", cap="round"):
        stroke = stroke or self.col("rule")
        da = f' stroke-dasharray="{dash}"' if dash else ""
        if stroke not in (None, "none", "transparent"):
            self._lines.append((x1, y1, x2, y2))
        self.raw(f'<line x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" y2="{_f(y2)}" stroke="{stroke}" '
                 f'stroke-width="{_f(sw)}" stroke-linecap="{cap}"{da}/>', layer)

    def path(self, d, stroke=None, sw=1.0, fill="none", dash=None, layer="edges"):
        stroke = stroke or self.col("ink")
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{_f(sw)}" '
                 f'stroke-linecap="round" stroke-linejoin="round"{da}/>', layer)

    def icon(self, name, x, y, size: float = 20, color=None, stroke=2.0, layer="labels"):
        self.raw(icon_svg(name, x, y, size, color or self.col("ink"), stroke), layer)

    # -- components -----------------------------------------------------------------------------
    def node(self, x, y, w, h, kind, label, sub=None, icon=None, shape="box", state="normal",
             count=None, layout="row", label_size=13, sub_size=10.5, tag=None) -> Box:
        """
        A system component.
          kind   client | edge | compute | cache | data | async | external
          shape  box | cylinder | queue
          state  normal | dim | focus | fail | warn (needs a look) | good (settled)
          count  draw a fleet (stacked cards) with a ×N badge
          layout row (icon left of text) | stack (icon above text)
          tag    small uppercase label above the box (e.g. "NEW")
        """
        sh, SIG = self.th.shape, self.th.signal
        k = self.th.kinds[kind]
        stroke, fill = k["stroke"], k["fill"]
        text_c, sub_c, sw = self.col("ink"), self.col("muted"), sh["stroke"]
        rx = sh["radius"]
        dash = None
        bar = sh["nodes"] == "bar" and state in ("normal", "focus")    # an outline, its kind on a bar
        frame = self.col("faint") if bar else stroke
        if state == "dim":
            stroke, fill, text_c, sub_c, sw = (self.col("faint"), self.col("wash"), self.col("faint"),
                                               self.col("faint"), sh["stroke"] * 0.75)
            frame = stroke
        elif state == "fail":
            stroke, fill, dash = SIG["bad"], SIG["bad_fill"], "5 4"
            frame = stroke
        elif state == "warn":
            stroke, fill, dash = SIG["warn"], SIG["warn_fill"], "5 4"
            frame = stroke
        elif state == "good":
            stroke, fill = SIG["good"], SIG["good_fill"]
            frame = stroke
        elif state == "focus":
            sw = sh["stroke"] * 1.5
            self.rect(x - 6, y - 6, w + 12, h + 12, fill=fill, stroke=stroke, sw=1, rx=rx + 5 if rx else 0,
                      opacity=0.55, dash="2 3")
        if bar:
            fill = self.col("paper")

        b = Box(x, y, w, h)
        if count and count > 1:                       # fleet: two offset cards behind
            b.pr = b.pt = 10
            for i in (2, 1):
                self.rect(x + 5 * i, y - 5 * i, w, h, fill=self.col("paper"), stroke=frame, sw=1.0, rx=rx)
        if shape == "cylinder":
            self._cylinder(b, fill, frame, sw, dash)
        else:
            if sh["shadow"]:                          # soft offset shadow
                self.rect(x + 1.5, y + 2, w, h, fill=sh["shadow"] if state != "dim" else "none", rx=rx)
            self.rect(x, y, w, h, fill=fill, stroke=frame, sw=sw, rx=rx, dash=dash)
            if bar:
                self.rect(x, y, 4, h, fill=stroke)
            if shape == "queue":                      # message slots on the right
                for i in range(4):
                    sx = x2 = x + w - 14 - i * 9
                    self.line(sx, y + 9, x2, y + h - 9, stroke=stroke, sw=1.4, layer="nodes")

        icon_c = stroke
        top_pad = 7 if shape == "cylinder" else 0
        if layout == "stack":
            iy = y + top_pad + (h - top_pad) / 2 - (24 + 6 + label_size + (sub_size + 3 if sub else 0)) / 2
            if icon:
                self.icon(icon, b.cx - 12, iy, 24, icon_c)
            ty = iy + 30 + label_size * 0.8
            self.text(b.cx, ty, label, label_size, 600, text_c, "middle")
            if sub:
                self.text(b.cx, ty + sub_size + 4, sub, sub_size, 400, sub_c, "middle")
        else:
            qr = 48 if shape == "queue" else 0     # the four slots span 41 px, and a gap
            ix = x + 12
            tx = ix + (30 if icon else 0)
            avail = w - (tx - x) - 10 - qr
            fam = self.th.label
            lab = label if text_width(label, label_size, 600, fam) <= avail else wrap(label, avail, label_size, 600, fam)
            lab_lines = [lab] if isinstance(lab, str) else lab
            block = len(lab_lines) * label_size * 1.15 + ((sub_size + 4) if sub else 0)
            ty = y + top_pad + (h - top_pad) / 2 - block / 2 + label_size * 0.82
            if icon:
                self.icon(icon, ix, y + top_pad + (h - top_pad) / 2 - 11, 22, icon_c)
            self.lines(tx, ty, lab_lines, label_size, 600, text_c, leading=1.15)
            if sub:
                ss = sub_size                        # shrink a too-long sub-label to fit (not below 8 px)
                while ss > 8 and text_width(sub, ss, 400, fam) > avail:
                    ss -= 0.25
                self.text(tx, ty + (len(lab_lines) - 1) * label_size * 1.15 + sub_size + 5, sub,
                          ss, 400, sub_c)
        if count and count > 1:
            self.badge(x + w - 4, y - 10 - 5 * 2 + 4, f"×{count}", stroke)
        if state == "fail":
            self.circle(x + w - 2, y + 2, 10, fill=SIG["bad"], layer="top")
            self.icon("octagon-x", x + w - 9, y - 5, 14, self.col("on"), 2.4, layer="top")
        elif state == "warn":                       # an exclamation mark, drawn: a stroke and a dot
            cx, cy = x + w - 2, y + 2
            self.circle(cx, cy, 10, fill=SIG["warn"], layer="top")
            self.path(f"M{_f(cx)},{_f(cy - 5)} L{_f(cx)},{_f(cy + 1)} M{_f(cx)},{_f(cy + 4.6)} L{_f(cx)},{_f(cy + 4.8)}",
                      stroke=self.col("on"), sw=2.6, layer="top")
        elif state == "good":                       # a tick, drawn
            cx, cy = x + w - 2, y + 2
            self.circle(cx, cy, 10, fill=SIG["good"], layer="top")
            self.path(f"M{_f(cx - 4.5)},{_f(cy + 0.5)} L{_f(cx - 1.2)},{_f(cy + 3.8)} L{_f(cx + 4.8)},{_f(cy - 3.6)}",
                      stroke=self.col("on"), sw=2.4, layer="top")
        if tag:
            tw = text_width(tag, 8.5, 700, self.th.label) + 12
            self.rect(x + 10, y - 9, tw, 16, fill=stroke, rx=self._pill(16), layer="top")
            self.text(x + 10 + tw / 2, y + 2.6, tag, 8.5, 700, self.col("on"), "middle", layer="top",
                      letter_spacing=0.6)
        return b

    def _cylinder(self, b: Box, fill, stroke, sw, dash):
        e = 7  # ellipse ry
        x, y, w, h = b.x, b.y, b.w, b.h
        rx = w / 2
        self._shapes.append((x, y, x + w, y + h, fill not in ("none", "transparent"), self._z("nodes"), fill, stroke))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        body = (f"M{_f(x)},{_f(y + e)} L{_f(x)},{_f(y + h - e)} "
                f"A{_f(rx)},{e} 0 0 0 {_f(x + w)},{_f(y + h - e)} L{_f(x + w)},{_f(y + e)}")
        if self.th.shape["shadow"]:
            self.raw(f'<path d="M{_f(x + 1.5)},{_f(y + e + 2)} L{_f(x + 1.5)},{_f(y + h - e + 2)} '
                     f'A{_f(rx)},{e} 0 0 0 {_f(x + w + 1.5)},{_f(y + h - e + 2)} L{_f(x + w + 1.5)},{_f(y + e + 2)} Z" '
                     f'fill="{self.th.shape["shadow"]}"/>', "nodes")
        self.raw(f'<path d="{body} A{_f(rx)},{e} 0 0 0 {_f(x)},{_f(y + e)} Z" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{_f(sw)}"{da}/>', "nodes")
        self.raw(f'<ellipse cx="{_f(x + rx)}" cy="{_f(y + e)}" rx="{_f(rx)}" ry="{e}" fill="{fill}" '
                 f'stroke="{stroke}" stroke-width="{_f(sw)}"{da}/>', "nodes")

    def region(self, x, y, w, h, title=None, color=None, fill="none", dash="4 4", icon=None):
        """A dashed grouping box (tier, VPC, region, data centre): its border faint, its title
        muted (text needs the contrast a border does not), or both in `color`."""
        title_color = color or self.col("muted")
        color = color or self.col("faint")
        self.rect(x, y, w, h, fill=fill, stroke=color, sw=1.1, rx=self.th.shape["region_radius"], dash=dash,
                  layer="regions")
        if title:
            tx = x + 12
            if icon:
                self.icon(icon, tx, y + 7, 13, title_color, layer="regions")
                tx += 18
            self.text(tx, y + 17.5, title.upper(), 9, 700, title_color, layer="regions", letter_spacing=0.8)
        return Box(x, y, w, h)

    def badge(self, x, y, s, color, size=9.5, anchor="end"):
        mono = self.th.mono
        w = text_width(s, size, 700, mono) + 10
        bx = x - w if anchor == "end" else (x - w / 2 if anchor == "middle" else x)
        self.rect(bx, y, w, size + 7, fill=color, rx=self._pill(size + 7), layer="top")
        self.text(bx + w / 2, y + size + 1.8, s, size, 700, self.col("on"), "middle", mono, layer="top")

    def chip(self, x, y, s, tone="neutral", size=10.5, anchor="start", icon=None, mono=True) -> Box:
        """A metric pill: 'p99 200 ms'. tone: bad | good | warn | info | neutral."""
        SIG = self.th.signal
        color, fill = {
            "bad": (SIG["bad"], SIG["bad_fill"]), "good": (SIG["good"], SIG["good_fill"]),
            "warn": (SIG["warn"], SIG["warn_fill"]), "info": (SIG["info"], SIG["info_fill"]),
            "neutral": (self.col("muted"), self.col("wash")),
        }[tone]
        fam = self.th.mono if mono else self.th.label
        tw = text_width(s, size, 600, fam)
        iw = size + 4 if icon else 0
        w, h = tw + iw + 14, size + 9
        bx = x - w if anchor == "end" else (x - w / 2 if anchor == "middle" else x)
        self.rect(bx, y, w, h, fill=fill, stroke=color, sw=0.8, rx=self._pill(h), layer="top")
        if icon:
            self.icon(icon, bx + 7, y + (h - size) / 2, size, color, 2.2, layer="top")
        self.text(bx + 7 + iw, y + h / 2 + size * 0.36, s, size, 600, color, "start", fam, layer="top")
        return Box(bx, y, w, h)

    def qr(self, data: str, x: float, y: float, size: float = 104, color=None, layer="nodes") -> Box:
        """A QR code for `data` (a URL, usually) as a `size` px square at x, y, its quiet margin of
        four modules included. Dark modules on a light square in every theme -- many scanners
        cannot read one the other way round."""
        import segno
        matrix = segno.make(data, error="m", micro=False).matrix
        n = len(matrix)
        u = size / (n + 8)
        light = "#FFFFFF" if self.th.dark else self.col("paper")
        dark = color or (self.col("on") if self.th.dark else self.col("ink"))
        self.rect(x, y, size, size, fill=light, layer=layer)
        runs = []
        for r, row in enumerate(matrix):
            start = None
            for col, on in enumerate([*row, 0]):
                if on and start is None:
                    start = col
                elif not on and start is not None:
                    w = (col - start) * u
                    runs.append(f"M{_f(x + (start + 4) * u)},{_f(y + (r + 4) * u)}h{_f(w)}v{_f(u)}h{_f(-w)}z")
                    start = None
        self.raw(f'<path d="{"".join(runs)}" fill="{dark}" shape-rendering="crispEdges"/>', layer)
        return Box(x, y, size, size)

    def step(self, x, y, n, color=None, r=9):
        """A numbered step marker (for request flows)."""
        self.circle(x, y, r + 1.5, fill=self.col("paper"), layer="top")
        self.circle(x, y, r, fill=color or self.col("ink"), layer="top")
        self.text(x, y + r * 0.38, str(n), r * 1.15, 700, self.col("on"), "middle", layer="top")

    # -- edges ----------------------------------------------------------------------------------
    def arrow(self, p1, p2, color=None, sw=1.6, dash=None, label=None, label_at=0.5, label_dy=-8,
              label_color=None, both=False, route="straight", via=None, head=True, step=None,
              step_color=None, label_bg=True, label_size=10.5, label_mono=False, gap=4):
        """
        Directed edge. route: straight | hv (horizontal then vertical) | vh | points via=[...]
        step: draw a numbered marker at the midpoint (request-flow order).
        """
        color = color or self.col("muted")
        pts = [p1]
        if via:
            pts += list(via)
        elif route == "hv":
            pts.append((p2[0], p1[1]))
        elif route == "vh":
            pts.append((p1[0], p2[1]))
        elif route == "hvh":
            mx = (p1[0] + p2[0]) / 2
            pts += [(mx, p1[1]), (mx, p2[1])]
        elif route == "vhv":
            my = (p1[1] + p2[1]) / 2
            pts += [(p1[0], my), (p2[0], my)]
        pts.append(p2)
        pts = _shorten(pts, gap if both else 0, gap)
        d = "M" + " L".join(f"{_f(px)},{_f(py)}" for px, py in pts)
        self.path(d, stroke=color, sw=sw, dash=dash)
        if head:
            self._head(pts[-2], pts[-1], color, sw)
        if both:
            self._head(pts[1], pts[0], color, sw)
        mid = _point_along(pts, label_at)
        if step is not None:
            self.step(mid[0], mid[1], step, step_color or color)
        if label:
            lx, ly = mid[0], mid[1] + label_dy
            fam = self.th.mono if label_mono else self.th.label
            if label_bg:
                tw = text_width(label, label_size, 500, fam)
                self.rect(lx - tw / 2 - 4, ly - label_size + 1, tw + 8, label_size + 5, fill=self.col("paper"),
                          rx=self._rx(3), layer="labels")
            self.text(lx, ly + 1, label, label_size, 500, label_color or color, "middle", fam)
        return pts

    def _head(self, a, b, color, sw):
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        L, W = 6.5 + sw * 1.2, 3.6 + sw * 0.8
        p = [(b[0], b[1]),
             (b[0] - L * math.cos(ang) + W * math.sin(ang), b[1] - L * math.sin(ang) - W * math.cos(ang)),
             (b[0] - L * math.cos(ang) - W * math.sin(ang), b[1] - L * math.sin(ang) + W * math.cos(ang))]
        self.raw(f'<polygon points="{" ".join(f"{_f(x)},{_f(y)}" for x, y in p)}" fill="{color}"/>', "edges")


def _shorten(pts, start_gap, end_gap):
    pts = [tuple(p) for p in pts]

    def move(p, q, d):
        L = math.dist(p, q)
        if L == 0:
            return p
        return (p[0] + (q[0] - p[0]) * d / L, p[1] + (q[1] - p[1]) * d / L)

    if start_gap:
        pts[0] = move(pts[0], pts[1], start_gap)
    if end_gap:
        pts[-1] = move(pts[-1], pts[-2], end_gap)
    return pts


def _point_along(pts, t):
    segs = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(segs) or 1
    target = total * t
    for i, L in enumerate(segs):
        if target <= L or i == len(segs) - 1:
            u = 0 if L == 0 else min(target / L, 1)
            return (pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u)
        target -= L
    return pts[-1]                                   # a single point: no segment to walk


# ----------------------------------------------------------------------------------------------
# Sequence diagrams (request flows)
# ----------------------------------------------------------------------------------------------
class Sequence:
    """
    Lifeline diagram. Participants are drawn as small nodes on top with dashed lifelines.
    Messages are numbered automatically; returns are dashed.
    """

    def __init__(self, c: Canvas, participants, x0=70, spacing=180, top=16, box_w=136, box_h=46,
                 bottom=None, xs=None):
        """Participants are (label, kind, icon), spaced `spacing` apart from x0 -- or at the
        centres `xs`, one each, where the gaps between them differ."""
        self.c, self.n = c, 0
        self.xs = []
        self.bottom = bottom or c.h - 10
        for i, (label, kind, icon) in enumerate(participants):
            cx = xs[i] if xs else x0 + i * spacing
            self.xs.append(cx)
            c.node(cx - box_w / 2, top, box_w, box_h, kind, label, icon=icon)
            c.line(cx, top + box_h + 4, cx, self.bottom, stroke=c.th.kinds[kind]["stroke"], sw=1.1,
                   dash="3 4", layer="regions")
        self.kinds = [p[1] for p in participants]

    def msg(self, a, b, y, label, ret=False, tone=None, note=None, mono=False, label_at=None):
        """A message from participant a to b at height y. The label sits midway; for a message
        that passes another participant's lifeline, `label_at` (0 at a, 1 at b) moves it into a
        gap between lifelines, since a lifeline through a label is what check() reports."""
        self.n += 1
        c, SIG = self.c, self.c.th.signal
        color = {"bad": SIG["bad"], "good": SIG["good"], "warn": SIG["warn"]}.get(
            tone or "", c.col("ink") if not ret else c.col("muted"))
        fam = c.th.mono if mono else c.th.label
        xa, xb = self.xs[a], self.xs[b]
        if a == b:                                   # self call
            d = f"M{_f(xa)},{_f(y)} L{_f(xa + 34)},{_f(y)} L{_f(xa + 34)},{_f(y + 18)} L{_f(xa + 4)},{_f(y + 18)}"
            self.c.path(d, stroke=color, sw=1.5, dash="5 4" if ret else None)
            self.c._head((xa + 34, y + 18), (xa + 4, y + 18), color, 1.5)
            self.c.step(xa - 16, y + 9, self.n, color)
            self.c.text(xa + 42, y + 13, label, 10.5, 500, color, family=fam)
            return
        sgn = 1 if xb > xa else -1
        self.c.arrow((xa + 6 * sgn, y), (xb - 2 * sgn, y), color=color, sw=1.5,
                     dash="5 4" if ret else None, gap=0)
        self.c.step(xa + 20 * sgn, y, self.n, color)
        lx = (xa + (xb - xa) * (0.5 if label_at is None else label_at)) + 8 * sgn
        tw = text_width(label, 10.5, 500, fam)
        self.c.rect(lx - tw / 2 - 4, y - 18, tw + 8, 14, fill=c.col("paper"), rx=c._rx(3), layer="labels")
        self.c.text(lx, y - 7, label, 10.5, 500, color, "middle", family=fam)
        if note:
            self.c.text(lx, y + 15, note, 9.5, 400, c.col("muted"), "middle", italic=True)

    def span(self, i, y1, y2, color=None):
        """Activation bar on a lifeline (work in progress)."""
        k = self.c.th.kinds[self.kinds[i]]
        self.c.rect(self.xs[i] - 4, y1, 8, y2 - y1, fill=k["fill"], stroke=color or k["stroke"], sw=1,
                    rx=self.c._rx(2), layer="edges")

    def bracket(self, i, y1, y2, text, side="left", color=None):
        color = color or self.c.col("muted")
        x = self.xs[i] + (-28 if side == "left" else 28)
        d = 6 if side == "right" else -6
        self.c.path(f"M{_f(x - d)},{_f(y1)} L{_f(x)},{_f(y1)} L{_f(x)},{_f(y2)} L{_f(x - d)},{_f(y2)}",
                    stroke=color, sw=1)
        self.c.text(x + (8 if side == "right" else -8), (y1 + y2) / 2 + 4, text, 10, 600, color,
                    "start" if side == "right" else "end", family=self.c.th.mono)


# ----------------------------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------------------------
def out_path(target: str | Path, suffix=".svg") -> Path:
    """A script's own path (__file__) means "beside the script, same name"; anything else is
    the output path itself."""
    p = Path(target).resolve()
    if p.suffix == ".py":
        p = p.with_suffix(suffix)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def save(c: Canvas, target: str | Path, name: str | None = None) -> Path:
    """Write the SVG, and print what check() finds in it (stopping if RICH_CONTENT_STRICT=1)."""
    from .check import report
    p = out_path(target)
    if name:
        p = p.with_name(name + ".svg")
    p.write_text(c.to_svg(), encoding="utf-8")
    report(c.check(), p.name)
    return p
