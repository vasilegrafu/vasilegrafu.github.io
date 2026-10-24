"""
A diagram of boxes and arrows -- an architecture, a request flow, a pipeline -- laid out by itself:
boxes in columns along the flow, as few crossings as it finds, arrows routed square between them.

  nodes:      id: "Label"  -- or id: {label, sub, kind, icon, shape, state, count, tag, at}
              kind, icon and shape are guessed from the words when not given ("Postgres" is a
              database cylinder, "Redis" a cache, "Orders queue" a queue, "Browser" a client).
              kind: client | edge | compute | cache | data | async | external
              state: normal | dim | focus | fail | warn | good;  icon: false for none
              at: [column, row] pins a box (0-based); boxes without one are placed around it
  edges:      "a -> b: label"   --> dashed (a path not always taken), <-> both ways, -- no head;
              a label in `backticks` is set as code. Or {from, to, label, dash, both, head, color,
              step}; color: good | bad | warn | info | accent | muted | ink
  groups:     [{title, nodes: [ids], icon, color}] -- a dashed region round its boxes
  direction:  right (the default) | down
  numbered:   true numbers the edges in the order written (a step marker on each)
  box:        {w, h} -- every box's size; by default the widest label decides
  gap:        {along, across} -- the space between columns (at least) and between rows

The figure is checked as it is drawn. A label that collides is usually a gap too small for it:
give the gap more room, or shorten the label.
"""
from __future__ import annotations

from typing import Any

from ...svgkit import Canvas, text_width
from .. import Spec, SpecError
from ..infer import box, colour, edge
from ..layout import Plan, label_at, layered

PURPOSE = "boxes and arrows (an architecture, a request flow, a pipeline), laid out by itself"
GROUP = "diagrams"
OUTPUT = "svg"

MARGIN = 10


def parse(spec: Spec) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    nodes = [box(i, v, spec, f".nodes.{i}", extra=("at",)) for i, v in spec.mapping("nodes")]
    if not nodes:
        raise SpecError("`nodes` is required: id: Label, one per box")
    known = {n["id"] for n in nodes}
    edges = []
    for k, e in enumerate(spec.items("edges")):
        if isinstance(e, str) and "->" in e and e.count("->") > 1 and ":" not in e:
            parts = [p.strip() for p in e.split("->")]           # a -> b -> c: a chain
            for a, b in zip(parts, parts[1:]):
                edges.append(edge(f"{a} -> {b}", spec, f".edges[{k}]", known, extra=("step",)))
            continue
        edges.append(edge(e, spec, f".edges[{k}]", known, extra=("step",)))
    return nodes, edges


def draw(spec: Spec) -> Canvas:
    return figure(**read(spec))


def read(spec: Spec) -> dict[str, Any]:
    """What figure() takes, read from a flow spec (the explainer draws one figure per frame from it)."""
    nodes, edges = parse(spec)
    direction = spec.get("direction", "right", str, ("right", "down"))
    numbered = spec.get("numbered", False, bool)
    size = spec.sub("box")
    gap = spec.sub("gap")
    groups = []
    member: dict[str, int] = {}
    for gi, g in enumerate(spec.items("groups")):
        if not isinstance(g, Spec):
            raise SpecError(f"groups[{gi}]: expected {{title, nodes: [...]}}")
        ids = [str(x) for x in g.need("nodes", list)]
        for n in ids:
            if n not in {x["id"] for x in nodes}:
                raise SpecError(f"{g.where}.nodes: no box `{n}`")
            member[n] = gi
        groups.append({"title": g.get("title", kind=str), "nodes": ids, "icon": g.get("icon", kind=str),
                       "color": g.get("color", kind=str)})
    return {"nodes": nodes, "edges": edges, "groups": groups, "member": member, "direction": direction,
            "numbered": numbered, "w": size.num("w") if size else None, "h": size.num("h") if size else None,
            "gap_m": gap.num("along", 64) if gap else 64, "gap_c": gap.num("across", None) if gap else None}


def node_size(nodes: list[dict[str, Any]], w: float | None, h: float | None) -> tuple[float, float]:
    need = max(text_width(n["label"], 13, 600) + (30 if n["icon"] else 0) + 24
               + (48 if n["shape"] == "queue" else 0) for n in nodes)
    subs = [text_width(n["sub"], 10.5, 400) + (30 if n["icon"] else 0) + 24 for n in nodes if n["sub"]]
    need = max([need] + subs)
    width = w or min(max(need, 120), 210)
    wraps = need > width
    height = h or (58 if any(n["sub"] for n in nodes) or wraps else 50)
    return width, height


def figure(nodes, edges, groups, member, direction="right", numbered=False, w=None, h=None, gap_m=64.0,
           gap_c=None) -> Canvas:
    ids = [n["id"] for n in nodes]
    by = {n["id"]: n for n in nodes}
    pairs = [(e["from"], e["to"]) for e in edges]
    fixed = {n["id"]: int(n["at"][0]) for n in nodes if n.get("at")}
    rows = {n["id"]: float(n["at"][1]) for n in nodes if n.get("at") and len(n["at"]) > 1}
    lay = layered(ids, pairs, fixed=fixed, groups=member, rows=rows)
    bw, bh = node_size(nodes, w, h)
    across = direction == "down"
    if gap_c is None:
        gap_c = (64 if groups else 36) if not across else (56 if groups else 40)
    labels = [e["label"] for e in edges]
    if numbered:                                       # a step marker beside the label needs room too
        labels = [(lab or "") + "    " for lab in labels]
    plan = Plan(lay, {i: (bw, bh) for i in ids}, direction, pairs, labels, gap_c=gap_c, gap_m=gap_m)
    routes = plan.routes()

    # everything in x, y; then the bounds, so the canvas fits what is drawn
    boxes = {i: plan.box_xywh(i) for i in ids}
    paths = {r.edge: [plan.xy(m, c) for m, c in r.points] for r in routes}
    segs = {r.edge: r.label_seg for r in routes}
    regions = []
    for g in groups:
        xs = [boxes[n] for n in g["nodes"]]
        x0 = min(b[0] for b in xs) - 16
        y0 = min(b[1] for b in xs) - 30
        x1 = max(b[0] + b[2] for b in xs) + 16 + max((10 for n in g["nodes"] if by[n]["count"]), default=0)
        y1 = max(b[1] + b[3] for b in xs) + 14
        regions.append((x0, y0, x1, y1, g))
    xs_all = [b[0] for b in boxes.values()] + [b[0] + b[2] + (10 if by[i]["count"] else 0) for i, b in boxes.items()]
    ys_all = [b[1] - (14 if by[i]["count"] or by[i]["tag"] else 0) for i, b in boxes.items()] + \
             [b[1] + b[3] for b in boxes.values()]
    for x0, y0, x1, y1, _ in regions:
        xs_all += [x0, x1]
        ys_all += [y0, y1]
    for k, pts in paths.items():
        xs_all += [p[0] for p in pts]
        ys_all += [p[1] for p in pts]
        lab = edges[k]["label"]
        if lab:
            tw = text_width(lab, 10.5, 500) / 2 + 8
            p, q = pts[segs[k]], pts[min(segs[k] + 1, len(pts) - 1)]
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            xs_all += [mx - tw, mx + tw]
            ys_all += [my - 22, my + 12]
    ox, oy = MARGIN - min(xs_all), MARGIN - min(ys_all)
    c = Canvas(max(xs_all) + ox + MARGIN, max(ys_all) + oy + MARGIN)

    for x0, y0, x1, y1, g in regions:
        c.region(x0 + ox, y0 + oy, x1 - x0, y1 - y0, g["title"], color=colour(c, g["color"], None) if g["color"] else None,
                 icon=g["icon"])
    for x0, y0, x1, y1, g in regions:                  # a box inside a region it does not belong to
        for i, (bx, by_, bw_, bh_) in boxes.items():
            if i not in g["nodes"] and bx < x1 and bx + bw_ > x0 and by_ < y1 and by_ + bh_ > y0:
                from ...check import report
                report([f"group {g['title'] or g['nodes']} takes in `{i}`, which is not in it: pin boxes with at:"],
                       "flow")
    drawn = {}
    for i in ids:
        n = by[i]
        x, y, w_, h_ = boxes[i]
        drawn[i] = c.node(x + ox, y + oy, w_, h_, n["kind"], n["label"], sub=n["sub"], icon=n["icon"],
                          shape=n["shape"], state=n["state"], count=n["count"], tag=n["tag"])
    for k, e in enumerate(edges):
        if e.get("hidden"):                            # keeps its room in the layout; nothing is drawn
            continue
        pts = [(x + ox, y + oy) for x, y in paths[k]]
        seg = segs[k]
        p, q = pts[seg], pts[min(seg + 1, len(pts) - 1)]
        horizontal = abs(p[1] - q[1]) < 0.5
        step = e.get("step") or ((k + 1) if numbered else None)
        col = colour(c, e["color"], None) if e["color"] else None
        lab_at = label_at(pts, seg)
        c.arrow(pts[0], pts[-1], via=pts[1:-1], color=col, dash="5 4" if e["dash"] else None,
                label=e["label"], label_at=lab_at, label_dy=-8 if horizontal else 4, both=e["both"],
                head=e["head"], label_mono=e["mono"])
        if step is not None:
            sx = pts[0][0] + (14 if pts[1][0] > pts[0][0] else -14 if pts[1][0] < pts[0][0] else 0)
            sy = pts[0][1] + (14 if pts[1][1] > pts[0][1] else -14 if pts[1][1] < pts[0][1] else 0)
            c.step(sx, sy, step, col or c.col("ink"))
    return c
