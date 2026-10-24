"""
A state machine: the states something passes through and the events that move it, laid out by
itself along the way forward; a transition that goes back runs round below, one to the same state
is a loop on its top.

  states:       id: "Label" -- or id: {label, sub, kind, state, icon}
                kind sets the colour (compute by default); state: normal | dim | focus | fail |
                warn | good, as a box's; no icon unless one is given
  transitions:  "a -> b: event" -- --> dashed (a path not always taken); or {from, to, label,
                dash, color}; a label in `backticks` is set as code
  initial:      the state it starts in: a filled dot with an arrow into it
  final:        [states] it can end in: drawn with a double border
  direction:    right (the default) | down
  box:          {w, h} -- every state's size; by default the widest label decides
"""
from __future__ import annotations

from typing import Any

from ...svgkit import Canvas, text_width
from .. import Spec, SpecError
from ..infer import KINDS, STATES, colour, edge
from ..layout import Plan, label_at, layered

PURPOSE = "a state machine: states, the events between them, where it starts and ends"
GROUP = "diagrams"
OUTPUT = "svg"

MARGIN = 10
START = "·start"                                       # the start dot: a box of its own, never a state's id
DOT = 18


def states_of(spec: Spec) -> list[dict[str, Any]]:
    out = []
    for ident, v in spec.mapping("states"):
        if isinstance(v, Spec):
            out.append({"id": ident, "label": str(v.get("label", ident)), "sub": v.get("sub", kind=str),
                        "kind": v.get("kind", "compute", str, KINDS), "state": v.get("state", "normal", str, STATES),
                        "icon": v.get("icon", None, str)})
        else:
            out.append({"id": ident, "label": str(ident if v is None else v), "sub": None, "kind": "compute",
                        "state": "normal", "icon": None})
    if not out:
        raise SpecError("`states` is required: id: Label, one per state")
    return out


def draw(spec: Spec) -> Canvas:
    states = states_of(spec)
    ids = [s["id"] for s in states]
    known = set(ids)
    trans = [edge(t, spec, f".transitions[{k}]", known) for k, t in enumerate(spec.items("transitions"))]
    initial = spec.get("initial", None, str)
    if initial is not None and initial not in known:
        raise SpecError(f"initial: no state `{initial}`; there are: {', '.join(ids)}")
    final = [str(f) for f in spec.get("final", [], list)]
    for f in final:
        if f not in known:
            raise SpecError(f"final: no state `{f}`; there are: {', '.join(ids)}")
    direction = spec.get("direction", "right", str, ("right", "down"))
    size = spec.sub("box")

    nodes = ([START] if initial else []) + ids
    edges = [(t["from"], t["to"]) for t in trans]
    labels = [t["label"] for t in trans]
    if initial:
        edges.append((START, initial))
        labels.append(None)
        trans = trans + [{"from": START, "to": initial, "label": None, "dash": False, "both": False, "head": True,
                          "color": None, "mono": False}]
    lay = layered(nodes, edges, fixed={START: 0} if initial else None)
    need = max(text_width(s["label"], 13, 600) + (30 if s["icon"] else 0) + 28 for s in states)
    subs = [text_width(s["sub"], 10.5, 400) + (30 if s["icon"] else 0) + 28 for s in states if s["sub"]]
    bw = (size.num("w") if size else None) or min(max([need] + subs + [110]), 210)
    bh = (size.num("h") if size else None) or (58 if any(s["sub"] for s in states) or max([need] + subs) > bw else 48)
    sizes = {i: (bw, bh) for i in ids}
    if initial:
        sizes[START] = (DOT, DOT)
    loops = any(a == b for a, b in edges)
    across = direction == "down"
    gap_c = (60 if loops else 40) if not across else (64 if loops else 44)
    plan = Plan(lay, sizes, direction, edges, labels, gap_c=gap_c, gap_m=56)
    routes = plan.routes()

    boxes = {i: plan.box_xywh(i) for i in nodes}
    paths = {r.edge: [plan.xy(m, c) for m, c in r.points] for r in routes}
    segs = {r.edge: r.label_seg for r in routes}
    ring = {f: 5 for f in final}
    xs_all = [b[0] - ring.get(i, 0) for i, b in boxes.items()] + [b[0] + b[2] + ring.get(i, 0) for i, b in boxes.items()]
    ys_all = [b[1] - ring.get(i, 0) for i, b in boxes.items()] + [b[1] + b[3] + ring.get(i, 0) for i, b in boxes.items()]
    for k, pts in paths.items():
        xs_all += [p[0] for p in pts]
        ys_all += [p[1] for p in pts]
        lab = labels[k]
        if lab:
            tw = text_width(lab, 10.5, 500) / 2 + 8
            p, q = pts[segs[k]], pts[min(segs[k] + 1, len(pts) - 1)]
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            xs_all += [mx - tw, mx + tw]
            ys_all += [my - 22, my + 12]
    ox, oy = MARGIN - min(xs_all), MARGIN - min(ys_all)
    c = Canvas(max(xs_all) + ox + MARGIN, max(ys_all) + oy + MARGIN)

    for s in states:
        x, y, w_, h_ = boxes[s["id"]]
        x, y = x + ox, y + oy
        if s["id"] in ring:                            # a final state: a second border round the first
            stroke = c.th.kinds[s["kind"]]["stroke"] if s["state"] in ("normal", "focus") else \
                {"good": c.th.signal["good"], "fail": c.th.signal["bad"], "warn": c.th.signal["warn"]}.get(
                    s["state"], c.col("faint"))
            r = c.th.shape["radius"]
            c.rect(x - 5, y - 5, w_ + 10, h_ + 10, stroke=stroke, sw=1.4, rx=r + 5 if r else 0)
        c.node(x, y, w_, h_, s["kind"], s["label"], sub=s["sub"], icon=s["icon"], state=s["state"])
    if initial:
        x, y, w_, h_ = boxes[START]
        c.circle(x + ox + w_ / 2, y + oy + h_ / 2, DOT / 2, fill=c.col("ink"))
    for k, t in enumerate(trans):
        pts = [(x + ox, y + oy) for x, y in paths[k]]
        seg = segs[k]
        p, q = pts[seg], pts[min(seg + 1, len(pts) - 1)]
        horizontal = abs(p[1] - q[1]) < 0.5
        col = colour(c, t["color"], None) if t["color"] else None
        c.arrow(pts[0], pts[-1], via=pts[1:-1], color=col, dash="5 4" if t["dash"] else None,
                label=t["label"], label_at=label_at(pts, seg), label_dy=-8 if horizontal else 4, both=t["both"],
                head=t["head"], label_mono=t["mono"])
    return c
