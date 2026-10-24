"""
A slide deck as one HTML file: 16:9 slides in the look of the pages, scaled to the window, turned
with the arrow keys, space, a click or a swipe; the address keeps the slide (deck.html#4); printed,
one slide a page. A cover comes first, made from the deck's title.

  title:      the deck's title (the cover's);  subtitle: under it;  eyebrow: the small line above it
  footer:     a line at the foot of every slide
  cover:      false leaves the cover out
  slides:     one each:
    title, subtitle (Markdown inline), kicker (a small line above the title)
    layout:   content (the default) | two-column | section (a divider) | statement (one large
              figure or sentence: the title, with the subtitle under it) | title (another cover)
    points:   [bullets] -- the commonest body
    figure:   chart.yaml | {make: …} | drawing.svg, with caption: -- sized to fit the slide
    blocks:   [blocks] as in a document: p, md, kpis, callout, table, figure, row, code, qr, chat,
              steps, diff, image, annotated, cards
    left, right:  [blocks] -- a two-column slide's columns (points: and figure: go on the left)
    notes:    what to say; kept in the file, not shown
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import Spec, SpecError
from ..document import html_block, inline

PURPOSE = "a slide deck as one HTML file: covers, dividers, points, figures, two columns, statements"
GROUP = "documents"
OUTPUT = "html"

LAYOUTS = ("content", "two-column", "section", "statement", "title")


def fill(page: Any, blocks: list[Any], parent: Spec, where: str) -> None:
    for k, b in enumerate(blocks):
        html_block(page, b, parent, f"{where}[{k}]")


def build(spec: Spec, out: Path) -> list[Path]:
    from ...html import Deck
    title = str(spec.need("title"))
    deck = Deck(title, footer=spec.get("footer", kind=str))
    if spec.get("cover", True, bool):
        sub = spec.get("subtitle", kind=str)
        deck.slide(title, inline(sub) if sub else None, layout="title", kicker=spec.get("eyebrow", kind=str))
    else:
        spec.get("subtitle")
        spec.get("eyebrow")
    entries = spec.items("slides")
    if not entries:
        raise SpecError("`slides` is required: [{title, points}, …]")
    for k, s in enumerate(entries):
        if not isinstance(s, Spec):
            raise SpecError(f"slides[{k}]: {{title, points}} or {{title, blocks}}")
        layout = s.get("layout", "content", str, LAYOUTS)
        sub = s.get("subtitle", kind=str)
        notes = s.get("notes", kind=str)
        slide = deck.slide(s.get("title", kind=str) if "title" in s else None, inline(sub) if sub else None,
                           layout=layout, kicker=s.get("kicker", kind=str), notes=inline(notes) if notes else None)
        points = s.get("points", None, list)
        if points:
            html_block(slide, {"md": "\n".join(f"- {p}" for p in points)}, s, ".points")
        if "figure" in s:
            fig = {"figure": s.get("figure")}
            if "caption" in s:
                fig["caption"] = s.get("caption", kind=str)
            html_block(slide, fig, s, ".figure")
        else:
            s.get("caption")
        fill(slide, s.items("blocks"), s, ".blocks")
        left, right = s.items("left"), s.items("right")
        if (left or right) and layout != "two-column":
            raise SpecError(f"{s.where}: left and right are for layout: two-column")
        fill(slide, left, s, ".left")
        if slide.right is not None:
            fill(slide.right, right, s, ".right")
    return [deck.save(out.with_suffix(".html"))]
