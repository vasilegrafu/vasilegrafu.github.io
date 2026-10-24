"""
Flashcards to print and cut: a grid of cards on each page, the fronts on one page and their backs
on the next, each row mirrored left to right, so that printed on both sides (flipped on the long
edge) every back lands behind its front. Text too long for a card is set smaller until it fits.

  title:      a small line at the top of every card (the deck's name)
  cards:      [{front, back}] -- Markdown; or
  questions:  questions in the Trainings model (as the quiz kind takes them); or
  from:       a Trainings question file (questions/chNN.js), read with Node: the front is the
              question with its material (and its options, items or pairs), the back the right
              answer and the takeaway;  lessons:, levels:, ids: keep only these
  grid:       [columns, rows] on a page (2 x 4 by default)
  paper:      a4 (the default) | us-letter;  margin: in mm (10)
  backs:      false prints the fronts alone, one side only (true by default)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import Spec, SpecError
from ..document import Typst, compile_typst, ts, typst_work
from ._questions import TYPST_HELPERS, Paper, answer_text, info, load

PURPOSE = "flashcards to print double-sided and cut: fronts, then their backs mirrored to line up"
GROUP = "learning"
OUTPUT = "pdf"

PAPERS = {"a4": (210.0, 297.0), "us-letter": (215.9, 279.4)}

HEAD = """#import "@local/rich-content:0.1.0": *
#import "@preview/cmarker:0.1.10"
#set document(title: {title}, date: none)
#set page(paper: {paper}, margin: {margin}mm, footer: none, header: none,
  fill: if theme.at("dark", default: false) {{ colour("paper") }} else {{ auto }})
#set text(font: serif, size: 10pt * scale-of(serif), fill: colour("ink"))
#set par(justify: false, leading: 0.55em, spacing: 0.75em)
#show raw: set text(font: mono, size: 0.84em, ligatures: false, features: (calt: 0))
#let code-theme = sys.inputs.at("rich-content-code", default: none)
#set raw(theme: if code-theme == none {{ auto }} else {{ bytes(code-theme) }})
#show raw.where(block: true): it => block(fill: colour("paper"), stroke: 0.5pt + colour("rule"),
  radius: calc.min(3pt, radius), inset: (x: 6pt, y: 5pt), width: 100%, it)
#show table: set text(font: sans, size: 0.85em)
// the body at the largest size, down to `low`, at which it fits the room it is given
#let fit(body, high: 12pt, low: 5.5pt) = layout(room => {{
  let s = high
  while s > low and measure(block(width: room.width, text(size: s, body))).height > room.height {{
    s -= 0.5pt
  }}
  text(size: s, body)
}})
#let card(kicker, body, back: false) = block(width: 100%, height: 100%, inset: (x: 6mm, top: 5mm, bottom: 6mm),
  {{
    text(font: sans, size: 6.5pt, weight: "semibold", tracking: 0.06em,
         fill: if back {{ signal("good") }} else {{ colour("muted") }}, upper(kicker))
    v(2.5mm)
    block(height: 1fr, width: 100%, align(horizon, fit(body)))
  }})
#let sheet(cells, cols, rows, h) = grid(columns: (1fr,) * cols, rows: (h,) * rows,
  stroke: (paint: colour("faint"), thickness: 0.5pt, dash: "dashed"), ..cells)
"""


def _cards(spec: Spec, t: Typst) -> list[tuple[str, str, str, str]]:
    """(front kicker, front, back kicker, back) as Typst markup, in order."""
    title = spec.get("title", "", str)
    p = Paper(t)
    if "from" in spec or "questions" in spec:
        if "cards" in spec:
            raise SpecError("`cards` with `from` or `questions`: give one")
        out = []
        qs = load(spec)
        cases = [q["id"] for q in qs if q["format"] == "case"]
        if cases:                                          # a case of two to four steps is a page, not a card
            from ...check import report
            report([f"{', '.join(cases)}: a case is set very small on a card; leave it out (ids:, levels:) "
                    f"or give the cards more room (grid: [1, 2])"], "flashcards")
        for q in qs:
            front = p.body(q, card=True)
            back = p.md(answer_text(q))
            if q.get("takeaway"):
                back += f"\n\n#takeaway[{p.md(q['takeaway'])}]"
            kick = " · ".join(x for x in (title, info(q)) if x)
            out.append((kick, front, " · ".join(x for x in (title, q.get("id") or "", "answer") if x), back))
        return out
    cards = spec.items("cards")
    if not cards:
        raise SpecError("`cards` is required ([{front, back}]), or `from:` a Trainings file")
    out = []
    for k, c in enumerate(cards):
        if not isinstance(c, Spec):
            raise SpecError(f"cards[{k}]: {{front, back}}")
        front, back = str(c.need("front")), str(c.need("back"))
        out.append((f"{title} · {k + 1}" if title else str(k + 1), p.md(front),
                    f"{title} · {k + 1} · answer" if title else f"{k + 1} · answer", p.md(back)))
    return out


def build(spec: Spec, out: Path) -> list[Path]:
    grid = spec.get("grid", [2, 4], list)
    if len(grid) != 2 or not all(isinstance(x, int) and 1 <= x <= 8 for x in grid):
        raise SpecError("grid: [columns, rows], each from 1 to 8")
    cols, rows = grid
    paper = spec.get("paper", "a4", str, tuple(PAPERS))
    margin = spec.num("margin", 10.0) or 10.0
    backs = spec.get("backs", True, bool)
    target = out.with_suffix(".pdf")
    with typst_work(spec, target) as work:
        t = Typst(work, spec.base)
        cards = _cards(spec, t)
        height = (PAPERS[paper][1] - 2 * margin) / rows
        per = cols * rows
        src = [HEAD.format(title=ts(str(spec.get("title", "Flashcards"))), paper=ts(paper), margin=f"{margin:g}"),
               TYPST_HELPERS]
        for start in range(0, len(cards), per):
            chunk: list[Any] = cards[start:start + per]
            chunk += [None] * (per - len(chunk))
            fronts = [("[]" if c is None else f"card({ts(c[0])}, [\n{c[1]}\n])") for c in chunk]
            if start:
                src.append("#pagebreak()")
            src.append(f"#sheet(({', '.join(fronts)},), {cols}, {rows}, {height:.2f}mm)")
            if backs:
                # each row mirrored: the back of the card at column c prints at column cols-1-c
                mirrored = []
                for r in range(rows):
                    row = chunk[r * cols:(r + 1) * cols]
                    mirrored += list(reversed(row))
                cells = [("[]" if c is None else f"card({ts(c[2])}, [\n{c[3]}\n], back: true)") for c in mirrored]
                src.append("#pagebreak()")
                src.append(f"#sheet(({', '.join(cells)},), {cols}, {rows}, {height:.2f}mm)")
        return [compile_typst(work, "\n\n".join(src) + "\n", target)]
