"""
check — find what a reader would see as broken before anyone has to look: labels that collide,
a label crossing the edge of a box, a legend over a title or over the data, a label sitting on a
line or a bar, text off the canvas or the page.

It runs by itself: svgkit's save(), chartstyle's save_chart() and html.Page's figures check what
they write and print what they find; render.py's `check` command does the same for a PDF. It is a
net, not a substitute for looking -- a colour that does not read, a figure that says the wrong
thing, an arrow through a node are still found only by rendering the result and reading it.

Set RICH_CONTENT_STRICT=1 to make anything it finds stop the build.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

Rect = tuple[float, float, float, float]          # x0, y0, x1, y1
TOL = 1.0                                         # an overlap smaller than this, either way, is no overlap


def _overlap(a: Rect, b: Rect, tol: float = TOL) -> bool:
    return min(a[2], b[2]) - max(a[0], b[0]) > tol and min(a[3], b[3]) - max(a[1], b[1]) > tol


def _contains(outer: Rect, inner: Rect, tol: float = 0.5) -> bool:
    return (outer[0] - tol <= inner[0] and outer[1] - tol <= inner[1]
            and inner[2] <= outer[2] + tol and inner[3] <= outer[3] + tol)


def _edge_cuts(r: Rect, box: Rect, tol: float = TOL) -> bool:
    """Does one of r's four edges run through box -- inside it by more than tol, and along it by
    more than tol? An edge that only grazes a text's ascender or descender space does not count."""
    hx = min(r[2], box[2]) - max(r[0], box[0]) > tol           # a horizontal edge spans the box
    vy = min(r[3], box[3]) - max(r[1], box[1]) > tol           # a vertical edge spans the box
    return ((hx and any(box[1] + tol < y < box[3] - tol for y in (r[1], r[3])))
            or (vy and any(box[0] + tol < x < box[2] - tol for x in (r[0], r[2]))))


def _letters(r: Rect) -> Rect:
    """A text's box trimmed to its letters: renderers report ascender to descender plus line gap;
    the middle 70 % is where the ink is, so lines set close together do not count as touching."""
    pad = (r[3] - r[1]) * 0.15
    return (r[0], r[1] + pad, r[2], r[3] - pad)


def _short(s: str, n: int = 40) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[: n - 1] + "…"


FOUND: list[str] = []                   # every finding reported in this run, for a caller that counts them


def report(issues: list[str], where: str) -> list[str]:
    """Print what was found, under the name of what it was found in; stop when strict."""
    for i in issues:
        print(f"check: {where}: {i}", file=sys.stderr)
        FOUND.append(f"{where}: {i}")
    if issues and os.environ.get("RICH_CONTENT_STRICT") == "1":
        raise SystemExit(f"check: {len(issues)} problem(s) in {where} (RICH_CONTENT_STRICT=1)")
    return issues


# ----------------------------------------------------------------------------------------------
# Diagrams: svgkit records each text's box and each box it draws
# ----------------------------------------------------------------------------------------------
REGIONS = 1                                       # svgkit's layer index for regions: dashed group borders


def svg_canvas_issues(w: float, h: float,
                      texts: list[tuple[float, float, float, float, str, tuple[int, int]]],
                      shapes: list[tuple[float, float, float, float, bool, tuple[int, int], str, str | None]],
                      lines: list[tuple[float, float, float, float]] = (),  # type: ignore[assignment]
                      circles: list[tuple[float, float, float, float]] = (),  # type: ignore[assignment]
                      ) -> list[str]:
    issues: list[str] = []
    boxes = [(t[:4], t[4], t[5]) for t in texts]
    for i, (a, sa, _) in enumerate(boxes):
        for b, sb, _ in boxes[i + 1:]:
            if _overlap(a, b):
                issues.append(f'"{_short(sa)}" overlaps "{_short(sb)}"')
    for box, s, z in boxes:
        if box[0] < -TOL or box[1] < -TOL or box[2] > w + TOL or box[3] > h + TOL:
            issues.append(f'"{_short(s)}" runs off the canvas ({w:g} x {h:g})')
        for sh in shapes:
            r, zs, fill, stroke = sh[:4], sh[5], sh[6], sh[7]
            if not _edge_cuts(r, box):
                continue
            # an edge nobody sees: no stroke, and no fill or the same fill on both sides. (Any fill
            # shows an edge, however translucent; sh[4], "opaque", is about what it hides.)
            painted = fill not in ("none", "transparent")
            if not stroke and (not painted or any(p is not sh and p[6] == fill and _contains(p[:4], box)
                                                  for p in shapes)):
                continue
            # a label on a plate painted later is carried over the edge -- except a region's
            # dashed border, which still reads as running into the label around the plate
            carried = zs[0] != REGIONS and any(p[4] and p[5] > zs and _contains(p[:4], box)
                                               for p in shapes if p is not sh)
            if not carried:
                owner = next((t for t, _, _ in boxes if _contains(r, t) and t is not box), None)
                named = next((s2 for t2, s2, _ in boxes if t2 is owner), None) if owner else None
                what = f'the box of "{_short(named)}"' if named else f"a box at {r[0]:.0f},{r[1]:.0f}"
                issues.append(f'"{_short(s)}" crosses the edge of {what}')
        # a line through a label -- a lifeline, a rule -- shows above and below even a plate
        if any(_seg_hits_rect((x1, y1), (x2, y2), box) for x1, y1, x2, y2 in lines):
            issues.append(f'"{_short(s)}" has a line through it')
        # a dot or a step marker touching a label it does not hold
        for cb in circles:
            if _overlap(box, cb) and not _contains(cb, box):
                issues.append(f'"{_short(s)}" runs into a marker at {(cb[0] + cb[2]) / 2:.0f},{(cb[1] + cb[3]) / 2:.0f}')
                break
    return issues


# ----------------------------------------------------------------------------------------------
# Charts: lay the figure out, then compare what it drew
# ----------------------------------------------------------------------------------------------
def _seg_hits_rect(p: tuple[float, float], q: tuple[float, float], r: Rect) -> bool:
    """Liang-Barsky: does the segment p-q pass through the rectangle r (shrunk by TOL)?"""
    x0, y0, x1, y1 = r[0] + TOL, r[1] + TOL, r[2] - TOL, r[3] - TOL
    if x0 >= x1 or y0 >= y1:
        return False
    dx, dy = q[0] - p[0], q[1] - p[1]
    t0, t1 = 0.0, 1.0
    for pk, qk in ((-dx, p[0] - x0), (dx, x1 - p[0]), (-dy, p[1] - y0), (dy, y1 - p[1])):
        if pk == 0:
            if qk < 0:
                return False
            continue
        t = qk / pk
        if pk < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return False
    return True


def figure_issues(fig: Any) -> list[str]:
    import math
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.legend import Legend
    from matplotlib.text import Text

    old_canvas = fig.canvas
    renderer = FigureCanvasAgg(fig).get_renderer()
    try:
        fig.draw(renderer)

        def ext(a: Any) -> Rect:
            if isinstance(a, Text):            # Text's own extent: an annotation's adds its arrow
                b = Text.get_window_extent(a, renderer)
                return _letters((b.x0, b.y0, b.x1, b.y1))
            b = a.get_window_extent(renderer)
            return (b.x0, b.y0, b.x1, b.y1)

        legends = [lg for lg in fig.findobj(Legend) if lg.get_visible()]
        in_legend = {id(t) for lg in legends for t in lg.findobj(Text)}
        texts: list[tuple[Rect, str, Any, Any]] = []      # box, text, artist, its axes
        for ax in fig.axes:
            spine_x = (ax.bbox.x0 - 2, ax.bbox.x1 + 2)
            spine_y = (ax.bbox.y0 - 2, ax.bbox.y1 + 2)
            for t in ax.get_xticklabels():
                if t.get_visible() and t.get_text().strip():
                    r = ext(t)
                    if spine_x[0] <= (r[0] + r[2]) / 2 <= spine_x[1]:
                        texts.append((r, t.get_text(), t, None))
            for t in ax.get_yticklabels():
                if t.get_visible() and t.get_text().strip():
                    r = ext(t)
                    if spine_y[0] <= (r[1] + r[3]) / 2 <= spine_y[1]:
                        texts.append((r, t.get_text(), t, None))
            for t in (ax.title, ax._left_title, ax._right_title, ax.xaxis.label, ax.yaxis.label):
                if t.get_visible() and t.get_text().strip():
                    texts.append((ext(t), t.get_text(), t, None))
            for t in ax.texts:                              # labels placed among the data
                if t.get_visible() and t.get_text().strip():
                    texts.append((ext(t), t.get_text(), t, ax))
        for lg in legends:
            for t in lg.get_texts():
                if t.get_visible() and t.get_text().strip():
                    texts.append((ext(t), t.get_text(), t, None))
        for t in fig.texts:
            if t.get_visible() and t.get_text().strip():
                texts.append((ext(t), t.get_text(), t, None))

        issues: list[str] = []
        for i, (a, sa, _, _) in enumerate(texts):
            for b, sb, _, _ in texts[i + 1:]:
                if _overlap(a, b):
                    issues.append(f'"{_short(sa)}" overlaps "{_short(sb)}"')
        for lg in legends:
            box = ext(lg.get_frame())
            for r, s, t, _ in texts:
                if id(t) not in in_legend and _overlap(box, r):
                    issues.append(f'the legend overlaps "{_short(s)}"')

        def data_hits(r: Rect, ax: Any) -> str | None:
            for line in ax.lines:
                if not line.get_visible():
                    continue
                pts = line.get_transform().transform(line.get_path().vertices)
                for p, q in zip(pts[:-1], pts[1:]):
                    if any(math.isnan(v) for v in (*p, *q)):
                        continue
                    if _seg_hits_rect((p[0], p[1]), (q[0], q[1]), r):
                        return f"the line {line.get_label()!r}" if not line.get_label().startswith("_") else "a line"
                if len(pts) == 1 and _contains(r, (pts[0][0], pts[0][1], pts[0][0], pts[0][1])):
                    return "a point"
            bars = {id(p) for cont in ax.containers for p in cont if hasattr(p, "get_width")}
            for patch in ax.patches:                     # inside a bar is a label on it; across its edge is not
                if patch.get_visible() and _edge_cuts(ext(patch), r):
                    return "the edge of a bar" if id(patch) in bars else "the edge of a shaded area"
            return None

        for r, s, _, ax in texts:
            if ax is not None and (hit := data_hits(r, ax)):
                issues.append(f'"{_short(s)}" sits on {hit}')
        for lg in legends:
            ax = lg.axes if lg.axes in fig.axes else None
            if ax is not None and (hit := data_hits(ext(lg.get_frame()), ax)):
                issues.append(f"the legend covers {hit}")
        # nothing about the figure's edge: charts are saved with a tight box, which grows to
        # take in whatever lies outside it
        return issues
    finally:
        fig.set_canvas(old_canvas)


# ----------------------------------------------------------------------------------------------
# PDFs: the text Typst set, span by span
# ----------------------------------------------------------------------------------------------
def pdf_issues(path: Path) -> list[str]:
    import pypdfium2 as pdfium
    issues: list[str] = []
    pdf = pdfium.PdfDocument(str(path))
    try:
        for n in range(1, len(pdf) + 1):
            page = pdf[n - 1]
            pw, ph = page.get_size()
            tp = page.get_textpage()
            spans: list[tuple[Rect, str, int]] = []
            for i in range(tp.count_rects()):       # runs of text pdfium keeps together, line by line
                left, bottom, right, top = tp.get_rect(i)
                s = tp.get_text_bounded(left, bottom, right, top)
                if s.strip():
                    # pdfium's y runs up from the foot of the page; the rest of the check's runs down
                    spans.append((_letters((left, ph - top, right, ph - bottom)), s, round(ph - bottom)))
            for i, (a, sa, la) in enumerate(spans):
                if a[0] < -TOL or a[2] > pw + TOL or a[1] < -TOL or a[3] > ph + TOL:
                    issues.append(f'page {n}: "{_short(sa)}" runs off the page')
                for b, sb, lb in spans[i + 1:]:
                    if la != lb and _overlap(a, b):
                        issues.append(f'page {n}: "{_short(sa)}" overlaps "{_short(sb)}"')
    finally:
        pdf.close()
    return issues
