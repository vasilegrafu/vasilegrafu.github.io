"""
What a change to one ID of a product specification reaches, in waves, read from the specification as the
product-specs skill wrote it: what the ID stands on (spec.py --impact), then the pages that turn stale when it
changes -- each page reviewed against it, in reviewed.json -- then the pages reviewed against those, which
turn stale in their turn if correcting the first wave changes what they say, and so on.

  specs:     the product-specs folder (the one holding model/, site/ and reviewed.json)
  id:        the ID that changes: R4, B1, N1, SC3 (an element or a criterion, SC3.13, counts as its page)
  depth:     how many waves to follow, 1 to 4 (2)
  stands_on: false leaves out the column of what the ID stands on (true)
  labels:    false leaves the arrows of the first wave unlabelled; later waves never carry labels (true)
  limit:     at most this many boxes in a column (10); past it, the first by ID are kept and one box
             says how many more there are

Each box is "ID · name", coloured by its kind of page (its kind written under it); the changed ID is in
focus, the first wave marked to be read (warn), later waves plain. The figure is as true as the folder's
model: run spec.py --write on the folder first if its pages have changed since.
"""
from __future__ import annotations

from .. import Spec, SpecError
from . import _specs
from .flow import figure

PURPOSE = "what a change to a product-specs ID turns stale, wave by wave, from the specification itself"
GROUP = "from the repository"
OUTPUT = "svg"

WIDTH = 250


def draw(spec: Spec):
    natural = _specs.natural
    model = _specs.load(spec)
    ref = str(spec.need("id"))
    depth = spec.get("depth", 2, int)
    if not 1 <= depth <= 4:
        raise SpecError("depth: 1 to 4")
    stands_on = spec.get("stands_on", True, bool)
    labels = spec.get("labels", True, bool)
    limit = spec.get("limit", 10, int)
    page = model.page(ref)
    _specs.known(model, page, "id")
    text = _specs.impact_text(model, ref)

    # the waves: what was reviewed against the change, then against what that reached, …
    waves: list[list[str]] = []
    seen = {page}
    front = {page}
    for _ in range(depth):
        nxt = sorted((p for p, against in model.against.items() if p not in seen and front & set(against)), key=natural)
        if not nxt:
            break
        waves.append(nxt)
        seen |= set(nxt)
        front = set(nxt)
    if not waves:
        raise SpecError(f"id: no page was reviewed against {page}; a change to it turns nothing stale "
                        f"(spec.py --impact {ref} says what names it)")

    columns: list[tuple[str, list[str]]] = []
    rel_of: dict[str, str] = {}
    if stands_on:
        held = []
        for line in _specs.section(text, "What it stands on"):
            rel, _, rest = line.partition(": ")
            for item in rest.split("; "):
                target = item.split(",", 1)[0].strip()
                if target in model.kind and target not in held:
                    held.append(target)
                    rel_of[target] = rel
        if held:
            columns.append(("Stands on", sorted(held, key=natural)))
    columns.append(("The change", [page]))
    for k, w in enumerate(waves):
        columns.append(("Turns stale" if k == 0 else f"Wave {k + 1}: stale if wave {k} changes", w))

    def rels(a: str, b: str) -> str:
        """How page a stands on page b, in the words of the model's edges."""
        found = sorted({r for x, r, y in model.edges if r != "has" and model.page(x) == a and model.page(y) == b})
        return ", ".join(f"{r} it" for r in found) if found else "reviewed against it"

    def within(a: str, b: str) -> str | None:
        parts = sorted({x.split(".", 1)[1] for x, r, y in model.edges
                        if r != "has" and "." in x and model.page(x) == a and model.page(y) == b}, key=natural)
        if not parts:
            return None
        word = "elements" if model.kind_of(a) == "screen" else "parts"
        return f"{model.kind_of(a)} · {word} {', '.join(parts)}"

    nodes, edges, groups, member = [], [], [], {}
    shown_by_col: list[list[str]] = []
    for col, (title, ids) in enumerate(columns):
        kept = ids[:limit]
        more = len(ids) - len(kept)
        g = len(groups)
        shown = []
        for row, i in enumerate(kept):
            is_change = i == page
            state = "focus" if is_change else ("warn" if title == "Turns stale" else "normal")
            sub = None
            if title == "Turns stale":
                sub = within(i, page)
            nodes.append(_specs.node(model, i, WIDTH, state, sub, at=[col]))
            member[i] = g
            shown.append(i)
        if more:
            mid = f"more{col}"
            nodes.append({"id": mid, "label": f"+{more} more", "sub": "past the limit", "kind": "compute",
                          "icon": None, "shape": "box", "state": "dim", "count": None, "tag": None,
                          "at": [col]})
            member[mid] = g
        groups.append({"title": title if title != "Turns stale" else f"Turns stale: {len(ids)}",
                       "nodes": shown + ([f"more{col}"] if more else []), "icon": None, "color": None})
        shown_by_col.append(shown)

    first = 1 if stands_on and columns[0][0] == "Stands on" else 0
    if first:
        for i in shown_by_col[0]:
            edges.append(_specs.edge(i, page, rel_of.get(i) if labels else None, dash=True) | {"head": False})
    for k in range(first + 1, len(columns)):
        for i in shown_by_col[k]:
            for j in shown_by_col[k - 1]:
                if j in model.against.get(i, {}):
                    lab = rels(i, j) if (labels and k == first + 1) else None
                    edges.append(_specs.edge(j, i, lab, color=None if k == first + 1 else "muted"))
    return figure(nodes, edges, groups, member, "right", w=WIDTH, h=58, gap_m=88, gap_c=26)
