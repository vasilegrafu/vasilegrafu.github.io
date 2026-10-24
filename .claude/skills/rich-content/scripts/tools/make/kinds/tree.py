"""
A tree from an indented outline: a folder tree, an org chart or a decision tree. Each line is one
item; an item indented under another is its child (any indent, used consistently).

  style:      folder (the default) | org | decision
  text:       the outline, as a block (text: |). In each line:
                "name  # comment"   a comment, set muted to the right (folder)
                "name/"             a folder (folder; set bold)
                "Label | sub"       a second, smaller line in the box (org, decision)
                "[yes] Label"       the label on the line into the item (decision, org)
                "Label !good"       a box's state: good | warn | fail | focus | dim (org, decision)
  direction:  down (the default) | right -- which way an org or decision tree grows
  kind:       the boxes' kind (org and decision questions): client | edge | compute | cache |
              data | async | external -- compute by default
  leaf:       the kind of a decision tree's answers (its items with no children): data by default
  box:        {w, h} -- every box's size; by default the widest label decides
"""
from __future__ import annotations

import re
from typing import Any

from ...svgkit import Canvas, text_width
from .. import Spec, SpecError
from ..infer import KINDS

PURPOSE = "a tree from an indented outline: a folder tree, an org chart, a decision tree"
GROUP = "diagrams"
OUTPUT = "svg"

MARGIN = 10
LINE = re.compile(r"^(?:\[(?P<edge>[^\]]*)\]\s*)?(?P<name>.*?)(?:\s+!(?P<state>good|warn|fail|focus|dim))?"
                  r"(?:\s+#\s?(?P<note>.*))?$")


def outline(text: str) -> list[dict[str, Any]]:
    """The items, each with its depth, its parent's index and what its line says."""
    items: list[dict[str, Any]] = []
    stack: list[tuple[int, int]] = []                    # (indent, item index)
    for no, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise SpecError(f"text, line {no}: indent with spaces, not tabs")
        indent = len(raw) - len(raw.lstrip(" "))
        while stack and stack[-1][0] >= indent:
            if stack[-1][0] > indent and (len(stack) < 2 or stack[-2][0] < indent):
                raise SpecError(f"text, line {no}: its indent ({indent}) matches no line above it")
            stack.pop()
        if not stack and items:
            raise SpecError(f"text, line {no}: a second root -- a tree has one item at the left")
        m = LINE.match(raw.strip())
        assert m
        name = m.group("name").strip()
        label, sub = (name.split(" | ", 1) + [None])[:2] if " | " in name else (name, None)
        items.append({"edge": m.group("edge"), "label": label.strip(), "sub": sub.strip() if sub else None,
                      "state": m.group("state") or "normal", "note": m.group("note"),
                      "parent": stack[-1][1] if stack else None, "depth": len(stack), "kids": []})
        if stack:
            items[stack[-1][1]]["kids"].append(len(items) - 1)
        stack.append((indent, len(items) - 1))
    if not items:
        raise SpecError("`text` is required: the outline, one item per line")
    return items


def draw(spec: Spec) -> Canvas:
    style = spec.get("style", "folder", str, ("folder", "org", "decision"))
    items = outline(str(spec.need("text", str)))
    if style == "folder":
        for k in ("direction", "kind", "leaf", "box"):
            spec.get(k)
        return folder(items)
    return boxes(items, style, spec.get("direction", "down", str, ("down", "right")),
                 spec.get("kind", "compute", str, KINDS), spec.get("leaf", "data", str, KINDS), spec.sub("box"))


# ----------------------------------------------------------------------------------------------
# A folder tree
# ----------------------------------------------------------------------------------------------
def folder(items: list[dict[str, Any]]) -> Canvas:
    from ...theme import current
    th = current()
    mono, size, row, step = th.mono, 12.0, 22.0, 22.0
    widths = []
    for it in items:
        bold = it["label"].endswith("/")
        widths.append(it["depth"] * step + text_width(it["label"], size, 600 if bold else 400, mono))
    note_x = MARGIN + max(widths) + 28
    notes = [text_width(it["note"], 11, 400) for it in items if it["note"]]
    width = (note_x + max(notes) if notes else MARGIN + max(widths)) + MARGIN
    height = MARGIN * 2 + row * len(items) - 6
    c = Canvas(width, height)
    base = [MARGIN + 13 + k * row for k in range(len(items))]
    for k, it in enumerate(items):
        x = MARGIN + it["depth"] * step
        bold = it["label"].endswith("/")
        c.text(x, base[k], it["label"], size, 600 if bold else 400, c.col("heading") if bold else c.col("ink"), family=mono)
        if it["note"]:
            c.text(note_x, base[k], it["note"], 11, 400, c.col("muted"))
        if it["kids"]:                                    # a stem down from the item, a tick to each child
            sx = x + 5
            last = it["kids"][-1]
            c.line(sx, base[k] + 5, sx, base[last] - 4, stroke=c.col("rule"), sw=1.2)
            for kid in it["kids"]:
                c.line(sx, base[kid] - 4, MARGIN + items[kid]["depth"] * step - 4, base[kid] - 4, stroke=c.col("rule"),
                       sw=1.2)
    return c


# ----------------------------------------------------------------------------------------------
# An org chart or a decision tree
# ----------------------------------------------------------------------------------------------
def boxes(items: list[dict[str, Any]], style: str, direction: str, kind: str, leaf: str, size: Spec | None) -> Canvas:
    across = direction == "right"                      # levels run along m; siblings spread along c
    need = max(text_width(it["label"], 13, 600) + 28 for it in items)
    subs = [text_width(it["sub"], 10.5, 400) + 28 for it in items if it["sub"]]
    bw = (size.num("w") if size else None) or min(max([need] + subs + [100]), 200)
    bh = (size.num("h") if size else None) or (56 if any(it["sub"] for it in items) or max([need] + subs) > bw else 46)
    along, wide = (bw, bh) if across else (bh, bw)
    labels = [it["edge"] for it in items if it["edge"]]
    if across:
        gap_m = max([64] + [text_width(lab, 10.5, 500) + 56 for lab in labels])
    else:
        gap_m = 74 if labels else 46
    gap_c = 20 if across else 22
    # breadth of each subtree, from the leaves up; a parent centred over its children
    breadth: dict[int, float] = {}

    def measure(i: int) -> float:
        kids = items[i]["kids"]
        breadth[i] = max(wide, sum(measure(k) for k in kids) + gap_c * (len(kids) - 1)) if kids else wide
        return breadth[i]

    measure(0)
    centre: dict[int, float] = {}

    def place(i: int, c0: float) -> None:
        kids = items[i]["kids"]
        if not kids:
            centre[i] = c0 + breadth[i] / 2
            return
        total = sum(breadth[k] for k in kids) + gap_c * (len(kids) - 1)
        x = c0 + (breadth[i] - total) / 2
        for k in kids:
            place(k, x)
            x += breadth[k] + gap_c
        centre[i] = (centre[kids[0]] + centre[kids[-1]]) / 2

    place(0, 0)
    depth = max(it["depth"] for it in items) + 1
    m_of = [L * (along + gap_m) for L in range(depth)]

    def xy(m: float, cc: float) -> tuple[float, float]:
        return (m, cc) if across else (cc, m)

    w_all = (m_of[-1] + along) if across else breadth[0]
    h_all = breadth[0] if across else (m_of[-1] + along)
    c = Canvas(w_all + 2 * MARGIN, h_all + 2 * MARGIN + 6)
    o = MARGIN
    for i, it in enumerate(items):
        m0 = m_of[it["depth"]]
        c0 = centre[i] - wide / 2
        x, y = xy(m0, c0)
        k = leaf if style == "decision" and not it["kids"] else kind
        c.node(x + o, y + o + 6, bw, bh, k, it["label"], sub=it["sub"], state=it["state"])
    for i, it in enumerate(items):
        if it["parent"] is None:
            continue
        p = it["parent"]
        m_p, m_k = m_of[items[p]["depth"]] + along, m_of[it["depth"]]
        # with labels the turn is near the parent, so the stretch into each child is long enough for its own
        mid = m_p + 16 if labels else m_k - gap_m / 2
        a = xy(m_p, centre[p])
        via = [xy(mid, centre[p]), xy(mid, centre[i])]
        b = xy(m_k, centre[i])
        pts = [(a[0] + o, a[1] + o + 6)] + [(v[0] + o, v[1] + o + 6) for v in via] + [(b[0] + o, b[1] + o + 6)]
        lab = it["edge"]
        at = _frac(pts, len(pts) - 2) if lab else 0.5
        c.arrow(pts[0], pts[-1], via=pts[1:-1], head=style == "decision", label=lab or None, label_at=at,
                label_dy=4 if not across else -8, color=c.col("muted") if style == "decision" else c.col("faint"),
                sw=1.4 if style == "decision" else 1.2)
    return c


def _frac(pts: list[tuple[float, float]], seg: int) -> float:
    from ..layout import label_at
    return label_at(pts, seg)
