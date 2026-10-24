"""
A database diagram: each table a box of its columns -- keys marked, types to the right, a nullable
one with a ? -- laid out by its foreign keys, a table to the left of the ones it refers to. Each
reference runs from its column to the column it names, a crow's foot at the many end and a bar at
the one.

  tables:   name: {column: "type [pk] [fk table.column] [null]", …}
            or a column as {type, pk, fk, null}; columns keep their order
  source:   a .sql file instead (or as well): its CREATE TABLE statements -- columns, PRIMARY KEY,
            REFERENCES, FOREIGN KEY … REFERENCES, and ALTER TABLE … ADD FOREIGN KEY
  only:     [table names] -- draw these alone (from a large source)
  types:    false leaves the types out
"""
from __future__ import annotations

import re
from typing import Any

from ...svgkit import Canvas, text_width
from .. import Spec, SpecError
from ..layout import layered

PURPOSE = "a database diagram: tables, their columns and keys, the references between them"
GROUP = "diagrams"
OUTPUT = "svg"

MARGIN, HEAD, ROW, PAD = 12, 28, 21, 10
GAP_C = 34                                   # between tables of one column of tables
SLOT = 14                                    # where a reference passes through a column
KEYWORDS = {"not", "null", "primary", "references", "default", "unique", "check", "constraint", "generated",
            "collate", "auto_increment", "autoincrement", "identity", "on", "comment"}


# ----------------------------------------------------------------------------------------------
# Reading
# ----------------------------------------------------------------------------------------------
def _name(s: str) -> str:
    s = s.strip().strip('`"[]')
    return s.split(".")[-1].strip('`"[]')


def _split(body: str) -> list[str]:
    parts, depth, cur = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


def from_sql(text: str) -> dict[str, list[dict[str, Any]]]:
    text = re.sub(r"--[^\n]*|/\*.*?\*/", "", text, flags=re.S)
    tables: dict[str, list[dict[str, Any]]] = {}
    for m in re.finditer(r"create\s+table\s+(?:if\s+not\s+exists\s+)?([\w.`\"\[\]]+)\s*\(", text, re.I):
        depth, i = 1, m.end()
        while i < len(text) and depth:
            depth += {"(": 1, ")": -1}.get(text[i], 0)
            i += 1
        name = _name(m.group(1))
        cols: list[dict[str, Any]] = []
        for part in _split(text[m.end():i - 1]):
            low = part.lower()
            words = low.split()
            if not words:
                continue
            if words[0] in ("constraint", "primary", "foreign", "unique", "check", "index", "key"):
                pk = re.search(r"primary\s+key\s*\(([^)]*)\)", part, re.I)
                if pk:
                    for col in pk.group(1).split(","):
                        for c in cols:
                            if c["name"] == _name(col):
                                c["pk"], c["null"] = True, False
                fk = re.search(r"foreign\s+key\s*\(([^)]*)\)\s*references\s+([\w.`\"\[\]]+)\s*(?:\(([^)]*)\))?", part, re.I)
                if fk:
                    for k, col in enumerate(fk.group(1).split(",")):
                        ref = (fk.group(3) or "id").split(",")
                        for c in cols:
                            if c["name"] == _name(col):
                                c["fk"] = f"{_name(fk.group(2))}.{_name(ref[min(k, len(ref) - 1)])}"
                continue
            tokens = part.split()
            col = {"name": _name(tokens[0]), "type": "", "pk": False, "fk": None, "null": True}
            kind = []
            for tok in tokens[1:]:
                if tok.lower().split("(")[0] in KEYWORDS:
                    break
                kind.append(tok)
            col["type"] = " ".join(kind).lower()
            if re.search(r"primary\s+key", low):
                col["pk"], col["null"] = True, False
            if re.search(r"not\s+null", low):
                col["null"] = False
            ref = re.search(r"references\s+([\w.`\"\[\]]+)\s*(?:\(([^)]*)\))?", part, re.I)
            if ref:
                col["fk"] = f"{_name(ref.group(1))}.{_name(ref.group(2) or 'id')}"
            cols.append(col)
        tables[name] = cols
    for m in re.finditer(r"alter\s+table\s+(?:only\s+)?([\w.`\"\[\]]+)\s+add\s+(?:constraint\s+\S+\s+)?foreign\s+key\s*"
                         r"\(([^)]*)\)\s*references\s+([\w.`\"\[\]]+)\s*(?:\(([^)]*)\))?", text, re.I):
        for c in tables.get(_name(m.group(1)), []):
            if c["name"] == _name(m.group(2)):
                c["fk"] = f"{_name(m.group(3))}.{_name(m.group(4) or 'id')}"
    return tables


def column(name: str, v: Any, where: str, parent: Spec) -> dict[str, Any]:
    if isinstance(v, Spec):
        return {"name": name, "type": str(v.get("type", "") or ""), "pk": bool(v.get("pk", False, bool)),
                "fk": v.get("fk", None, str), "null": bool(v.get("null", False, bool))}
    words = str(v if v is not None else "").split()
    col = {"name": name, "type": "", "pk": False, "fk": None, "null": False}
    rest = []
    k = 0
    while k < len(words):
        w = words[k]
        if w.lower() == "pk":
            col["pk"] = True
        elif w.lower() == "null":
            col["null"] = True
        elif w.lower() == "fk":
            if k + 1 >= len(words) or "." not in words[k + 1]:
                raise SpecError(f"{parent.where}{where}: fk is followed by table.column")
            col["fk"] = words[k + 1]
            k += 1
        else:
            rest.append(w)
        k += 1
    col["type"] = " ".join(rest)
    return col


# ----------------------------------------------------------------------------------------------
# Drawing
# ----------------------------------------------------------------------------------------------
def draw(spec: Spec) -> Canvas:
    tables: dict[str, list[dict[str, Any]]] = {}
    src = spec.path("source")
    if src:
        tables.update(from_sql(src.read_text(encoding="utf-8")))
        if not tables:
            raise SpecError(f"source: no CREATE TABLE in {src.name}")
    for name, cols in spec.mapping("tables"):
        if not isinstance(cols, Spec):
            raise SpecError(f"tables.{name}: {{column: type, …}}")
        tables[name] = [column(str(cn), cols.wrap(cv, f".{cn}") if isinstance(cv, dict) else cv, f".tables.{name}.{cn}",
                               spec) for cn, cv in cols.data.items()]
        cols.read.update(cols.data)                         # every key is a column: none is unknown
    only = spec.get("only", None, list)
    if only:
        missing = [t for t in only if t not in tables]
        if missing:
            raise SpecError(f"only: no table {', '.join(missing)}; there are: {', '.join(tables)}")
        tables = {t: tables[t] for t in only}
    if not tables:
        raise SpecError("`tables` or `source` is required")
    show_types = spec.get("types", True, bool)
    refs = []                                              # (table, row, table, row)
    for t, cols in tables.items():
        for r, col in enumerate(cols):
            if col["fk"]:
                tt, tc = col["fk"].rsplit(".", 1)
                if tt not in tables:
                    if only:
                        continue
                    raise SpecError(f"tables.{t}.{col['name']}: fk to `{tt}`, which is not a table here")
                rows = [k for k, c in enumerate(tables[tt]) if c["name"] == tc]
                refs.append((t, r, tt, rows[0] if rows else 0))

    from ...theme import current
    th = current()
    mono = th.mono
    size: dict[str, tuple[float, float]] = {}
    for t, cols in tables.items():
        name_w = max([text_width(c["name"], 11, 500, mono) for c in cols] + [0])
        type_w = max([text_width(c["type"] + ("?" if c["null"] else ""), 10, 400, mono) for c in cols] + [0])
        w = max(text_width(t, 12, 700) + 2 * PAD, 30 + name_w + (18 + type_w if show_types else 0) + PAD)
        size[t] = (max(w, 150), HEAD + ROW * len(cols) + 6)

    names = list(tables)
    linked = [k for k, (a, _, b, _) in enumerate(refs) if a != b]
    lay = layered(names, [(refs[k][0], refs[k][2]) for k in linked])
    chain = {linked[i]: ds for i, ds in lay.chains.items()}         # a reference across columns: its slots
    n_layers = lay.layers
    # each column of tables stacked in its order -- with a thin slot where a reference passes
    # through it to a column further on -- the columns centred on the tallest
    cols_of = [sorted([t for t in names if lay.layer[t] == L] + [d for d, (DL, _) in lay.dummies.items() if DL == L],
                      key=lambda t: lay.dummies[t][1] if t in lay.dummies else lay.pos[t]) for L in range(n_layers)]

    def tall(t: str) -> float:
        return SLOT if t in lay.dummies else size[t][1]

    def between(a: str, b: str) -> float:
        return 10 if a in lay.dummies or b in lay.dummies else GAP_C

    heights = [sum(tall(t) for t in col) + sum(between(a, b) for a, b in zip(col, col[1:])) for col in cols_of]
    tallest = max(heights)
    # the gap after each column: room for the verticals that turn in it
    turns = [0] * n_layers
    for a, _, b, _ in refs:
        La, Lb = lay.layer[a], lay.layer[b]
        for g in range(min(La, Lb), max(La, Lb)):
            turns[g] += 1
    gap = [56 + 9 * k for k in turns]
    widths = [max([size[t][0] for t in col if t not in lay.dummies] or [40]) for col in cols_of]
    xs, x = [], MARGIN
    for L in range(n_layers):
        xs.append(x)
        x += widths[L] + gap[L]
    at: dict[str, tuple[float, float, float, float]] = {}
    for L, col in enumerate(cols_of):
        y = MARGIN + (tallest - heights[L]) / 2
        for k, t in enumerate(col):
            w = widths[L] if t in lay.dummies else size[t][0]
            at[t] = (xs[L] + (widths[L] - w) / 2, y, w, tall(t))
            y += tall(t) + (between(t, col[k + 1]) if k + 1 < len(col) else 0)
    same = sum(1 for a, _, b, _ in refs if lay.layer[a] == lay.layer[b])
    width = x - gap[-1] + MARGIN + (24 + 10 * same if same else 0)
    c = Canvas(width, tallest + 2 * MARGIN)

    def row_y(t: str, r: int) -> float:
        return at[t][1] + HEAD + ROW * r + ROW / 2 + 3

    # references: square, each vertical on a track of its own in the gap it turns in
    tracks: dict[int, list[list[tuple[float, float]]]] = {}

    def track(g: int, y1: float, y2: float) -> float:
        used = tracks.setdefault(g, [])                     # per track, the stretches it already carries
        lo, hi = min(y1, y2), max(y1, y2)
        k = next((j for j, spans in enumerate(used) if all(hi + 6 < s0 or lo - 6 > s1 for s0, s1 in spans)), len(used))
        if k == len(used):
            used.append([])
        used[k].append((lo, hi))
        return xs[g] + widths[g] + 22 + 9 * k

    order = sorted(range(len(refs)), key=lambda k: (lay.layer[refs[k][0]], row_y(refs[k][0], refs[k][1])))
    for k in order:
        a, ra, b, rb = refs[k]
        xa, _, wa, _ = at[a]
        xb, _, wb, _ = at[b]
        y1, y2 = row_y(a, ra), row_y(b, rb)
        La, Lb = lay.layer[a], lay.layer[b]
        if La == Lb:                                       # within a column: round its right side
            tx = track(La, y1, y2)                          # a track of the gap after it, like the rest
            pts = [(xa + wa, y1), (tx, y1), (tx, y2), (xb + wb, y2)]
            ends = ((1, 0), (1, 0))
        else:
            right = Lb > La
            # hops: out of the column, through each slot on the way, into the table it names
            hops = [((xa + wa) if right else xa, y1, La)]
            for d in chain.get(k, []):
                dx, dy, dw, dh = at[d]
                hops += [(dx, dy + dh / 2, lay.dummies[d][0]), (dx + dw, dy + dh / 2, lay.dummies[d][0])]
            hops.append((xb if right else xb + wb, y2, Lb))
            pts = [(hops[0][0], hops[0][1])]
            for (hx0, hy0, hl0), (hx1, hy1, hl1) in zip(hops, hops[1:]):
                if abs(hy0 - hy1) > 0.5:
                    tx = track(min(hl0, hl1) if hl0 != hl1 else hl0, hy0, hy1)
                    pts += [(tx, hy0), (tx, hy1)]
                pts.append((hx1, hy1))
            ends = ((1, 0) if right else (-1, 0), (-1, 0) if right else (1, 0))
        c.arrow(pts[0], pts[-1], via=pts[1:-1], head=False, color=c.col("muted"), sw=1.3, gap=0)
        _many(c, pts[0], ends[0])
        _one(c, pts[-1], ends[1])

    head_fill = th.kinds["data"]["stroke"]
    for t, cols in tables.items():
        x, y, w, h = at[t]
        c.rect(x, y, w, h, fill=c.col("paper"), stroke=c.col("faint"), sw=1.1, rx=c._rx(6))
        c.rect(x, y, w, HEAD, fill=head_fill, rx=c._rx(6))
        c.rect(x, y + HEAD - 6, w, 6, fill=head_fill)                 # square the header's lower corners
        c.text(x + PAD, y + 18.5, t, 12, 700, c.col("on"))
        for r, col in enumerate(cols):
            ry = row_y(t, r)
            if r % 2 == 1:
                c.rect(x + 1, ry - ROW / 2 - 3, w - 2, ROW, fill=c.col("wash"), layer="regions")
            mark = "PK" if col["pk"] else "FK" if col["fk"] else ""
            if mark:
                colour = c.th.signal["warn"] if mark == "PK" else c.th.kinds["compute"]["stroke"]
                c.text(x + PAD, ry + 0.5, mark, 8.5, 700, colour, family=mono)
            c.text(x + 30, ry + 1, col["name"], 11, 600 if col["pk"] else 500, c.col("ink"), family=mono)
            if show_types and col["type"]:
                c.text(x + w - PAD, ry + 1, col["type"] + ("?" if col["null"] else ""), 10, 400, c.col("muted"),
                       "end", family=mono)
    return c


def _many(c: Canvas, p: tuple[float, float], d: tuple[int, int]) -> None:
    """A crow's foot at a box's side: three lines meeting 10 px out."""
    x, y = p
    tip = x + 11 * d[0]
    c.path(f"M{tip:.2f},{y:.2f} L{x:.2f},{y - 6:.2f} M{tip:.2f},{y:.2f} L{x:.2f},{y:.2f} M{tip:.2f},{y:.2f} "
           f"L{x:.2f},{y + 6:.2f}", stroke=c.col("muted"), sw=1.3)


def _one(c: Canvas, p: tuple[float, float], d: tuple[int, int]) -> None:
    """One: a bar across the line, 7 px out from the box."""
    x, y = p
    bx = x + 7 * d[0]
    c.path(f"M{bx:.2f},{y - 6:.2f} L{bx:.2f},{y + 6:.2f}", stroke=c.col("muted"), sw=1.3)
