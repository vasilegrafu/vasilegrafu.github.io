"""
The neighbourhood of one ID in a product specification: the IDs its edges reach, and the edges between them,
each labelled by its relation, as the model the product-specs skill wrote holds them (model/edges.tsv).
Laid out by the flow kind: an edge runs from what names to what is named.

  specs:      the product-specs folder (the one holding model/)
  around:     the ID in the middle: SC3, R4, N1
  depth:      1 (the default): what it names and what names it; 2: and what those name and are named by
  relations:  only these relations: [shows, leads to, about] (all but `has` by default)
  leave:      relations to leave out ([has]; `has` ties a page to its own elements and parts)
  elements:   true keeps an element or a part (SC3.13) as its own box; by default it counts as its page
  limit:      at most this many boxes besides the one in the middle (14), shared between the two sides
              (half each; what one side does not use goes to the other), the first ring before the second;
              on each side those tied by the most relations are kept, then by ID, and one box says how
              many more there are -- narrow with relations: or leave: to see the rest
  direction:  right (the default) | down

Drawn as a star: what names the ID on its left, what it names on its right (an ID tied both ways on the
right, its arrow with two heads, "names / named by"); at depth 2 the next ring further out, each box tied by
the one arrow it hangs from -- ties between neighbours are left out, or the figure would be a tangle. Each
box is "ID · name", coloured by its kind of page (its kind written under it); the ID in the middle is in
focus. Two IDs tied by more than one relation share one arrow with every relation on it.
"""
from __future__ import annotations

from .. import Spec, SpecError
from . import _specs
from .flow import figure

PURPOSE = "the IDs around one ID of a product specification, and how each is tied to it"
GROUP = "from the repository"
OUTPUT = "svg"

WIDTH = 240


def draw(spec: Spec):
    natural = _specs.natural
    model = _specs.load(spec)
    elements = spec.get("elements", False, bool)
    centre = str(spec.need("around"))
    _specs.known(model, centre if elements else model.page(centre), "around")
    if not elements:
        centre = model.page(centre)
    depth = spec.get("depth", 1, int, (1, 2))
    only = spec.get("relations", None, list)
    leave = set(spec.get("leave", ["has"], list))
    limit = spec.get("limit", 14, int)
    direction = spec.get("direction", "right", str, ("right", "down"))
    rels_known = {r for _, r, _ in model.edges}
    for r in (only or []) + sorted(leave):
        if r not in rels_known:
            raise SpecError(f"relations: no relation `{r}` in the model; there are: {', '.join(sorted(rels_known))}")

    def end(x: str) -> str:
        return x if elements else model.page(x)

    pairs: dict[tuple[str, str], set[str]] = {}
    for a, r, b in model.edges:
        if r in leave or (only and r not in only):
            continue
        a, b = end(a), end(b)
        if a != b:
            pairs.setdefault((a, b), set()).add(r)
    near: dict[str, set[str]] = {}
    for a, b in pairs:
        near.setdefault(a, set()).add(b)
        near.setdefault(b, set()).add(a)
    if centre not in near:
        raise SpecError(f"around: {centre} has no edges" + (" of those relations" if only or leave != {"has"} else ""))

    # a star: what names the middle on its left, what it names on its right, each tied to it by one arrow;
    # at depth 2, what names those further left and what those name further right, each by its one tie
    def rels(a: str, b: str) -> str:
        return ", ".join(sorted(pairs.get((a, b), ())))

    out1 = sorted((b for (a, b) in pairs if a == centre), key=lambda x: (-len(pairs[(centre, x)]), natural(x)))
    in1 = sorted((a for (a, b) in pairs if b == centre and a not in out1),
                 key=lambda x: (-len(pairs[(x, centre)]), natural(x)))
    placed = {centre, *out1, *in1}
    out2: list[tuple[str, str]] = []                      # (box, the box it hangs from)
    in2: list[tuple[str, str]] = []
    if depth == 2:
        for x in out1:
            for (a, b) in sorted(pairs, key=lambda p: natural(p[1])):
                if a == x and b not in placed:
                    out2.append((b, x))
                    placed.add(b)
        for x in in1:
            for (a, b) in sorted(pairs, key=lambda p: natural(p[0])):
                if b == x and a not in placed:
                    in2.append((a, x))
                    placed.add(a)
    # the limit shared between the two sides, so neither is crowded out: half each, what one does not use
    # going to the other; the next ring only after the first
    n_in = min(len(in1), max(limit // 2, limit - len(out1)))
    n_out = min(len(out1), limit - n_in)
    order = [(x, "out1") for x in out1[:n_out]] + [(x, "in1") for x in in1[:n_in]]
    order += [(x, "out1") for x in out1[n_out:]] + [(x, "in1") for x in in1[n_in:]]
    order += [(x, "out2") for x, _ in out2] + [(x, "in2") for x, _ in in2]
    kept = dict(order[:limit])
    more = len(order) - len(kept)
    parent = dict(out2 + in2)
    col = {"in2": 0, "in1": 1, "out1": 3, "out2": 4}

    nodes = [_specs.node(model, centre, WIDTH, "focus", at=[2])]
    edges = []
    for x, side in order[:limit]:
        if side in ("out2", "in2") and parent[x] not in kept:
            continue
        nodes.append(_specs.node(model, x, WIDTH, at=[col[side]]))
        if side == "out1":
            back = pairs.get((x, centre))
            e = _specs.edge(centre, x, rels(centre, x) + (f" / {', '.join(sorted(back))}" if back else ""))
            e["both"] = bool(back)
            edges.append(e)
        elif side == "in1":
            edges.append(_specs.edge(x, centre, rels(x, centre)))
        elif side == "out2":
            edges.append(_specs.edge(parent[x], x, rels(parent[x], x), color="muted"))
        else:
            edges.append(_specs.edge(x, parent[x], rels(x, parent[x]), color="muted"))
    if more > 0:
        nodes.append({"id": "more", "label": f"+{more} more", "sub": "past the limit", "kind": "compute", "icon": None,
                      "shape": "box", "state": "dim", "count": None, "tag": None, "at": [3 if out1 else 1]})
    return figure(nodes, edges, [], {}, direction, w=WIDTH, h=58)
