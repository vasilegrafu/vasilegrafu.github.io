"""
layout -- where boxes go when a spec does not say, and how the lines between them run.

Boxes are put in layers along the flow (left to right, or top to bottom): each a layer after every
box that points at it, a box that only points on moved up beside what it points at. An edge across
several layers keeps a slot in each it passes, so it runs between the boxes, not through them. The
boxes of a layer are ordered to cross as few edges as can be found in a few sweeps, members of a
group kept together; then each is moved as near the boxes it joins as the ones beside it allow, so
most edges run straight.

Edges run square: out of a box's far side, across to a track in the gap before the next layer, along
it, and in. Edges that close a cycle run back round a lane outside the boxes; an edge from a box to
itself is a loop on its top. Coordinates are worked out along the flow (`m`) and across it (`c`) and
turned into x and y at the end, so both directions share every rule.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..svgkit import text_width


@dataclass
class Layered:
    layer: dict[str, int]
    pos: dict[str, float]                               # across the flow, in slots
    chains: dict[int, list[str]]                        # edge index -> the dummies it passes, in order
    dummies: dict[str, tuple[int, float]] = field(default_factory=dict)   # dummy -> (layer, pos)
    back: set[int] = field(default_factory=set)         # edges against the flow, or within a layer
    loops: set[int] = field(default_factory=set)        # edges from a box to itself
    layers: int = 1


def layered(nodes: list[str], edges: list[tuple[str, str]], fixed: dict[str, int] | None = None,
            groups: dict[str, int] | None = None, rows: dict[str, float] | None = None,
            sweeps: int = 8) -> Layered:
    fixed, groups, rows = fixed or {}, groups or {}, rows or {}
    loops = {i for i, (a, b) in enumerate(edges) if a == b}
    out: dict[str, list[tuple[int, str]]] = {n: [] for n in nodes}
    for i, (a, b) in enumerate(edges):
        if i not in loops:
            out[a].append((i, b))

    # 1. cycles: an edge back to a box still being walked is turned round for the layering
    reversed_: set[int] = set()
    state: dict[str, int] = {}

    def walk(n: str) -> None:
        state[n] = 1
        for i, m in out[n]:
            if state.get(m) == 1:
                reversed_.add(i)
            elif m not in state:
                walk(m)
        state[n] = 2

    for n in nodes:
        if n not in state:
            walk(n)
    dag = [(b, a) if i in reversed_ else (a, b) for i, (a, b) in enumerate(edges)]
    succ: dict[str, list[str]] = {n: [] for n in nodes}
    pred: dict[str, list[str]] = {n: [] for n in nodes}
    for i, (a, b) in enumerate(dag):
        if i not in loops:
            succ[a].append(b)
            pred[b].append(a)

    # 2. layers: the longest path from a source; a source that feeds only later boxes moves up to them
    order, indeg = [], {n: len(pred[n]) for n in nodes}
    ready = [n for n in nodes if indeg[n] == 0]
    while ready:
        n = ready.pop(0)
        order.append(n)
        for m in succ[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                ready.append(m)
    layer: dict[str, int] = {}
    for n in order:
        layer[n] = fixed.get(n, max((layer[p] + 1 for p in pred[n]), default=0))
    for n in reversed(order):
        if n not in fixed and not pred[n] and succ[n]:
            layer[n] = max(layer[n], min(layer[s] for s in succ[n]) - 1)
    if fixed:                                            # what a fixed box leaves behind it follows on
        for n in order:
            if n not in fixed:
                layer[n] = max([layer[n]] + [layer[p] + 1 for p in pred[n]])
    low = min(layer.values(), default=0)
    layer = {n: v - low for n, v in layer.items()}

    back = {i for i, (a, b) in enumerate(edges) if i not in loops and layer[b] <= layer[a]}
    # 3. an edge across layers keeps a slot in each it passes
    chains: dict[int, list[str]] = {}
    members: dict[int, list[str]] = {}
    for n in nodes:
        members.setdefault(layer[n], []).append(n)
    dlayer: dict[str, int] = {}
    links: list[tuple[str, str]] = []                    # between neighbouring layers, for the ordering
    for i, (a, b) in enumerate(edges):
        if i in loops:
            continue
        if i in back:
            if abs(layer[a] - layer[b]) == 1:
                links.append((b, a))
            continue
        chain, prev = [], a
        for L in range(layer[a] + 1, layer[b]):
            d = f"\0{i}.{L}"
            dlayer[d] = L
            members.setdefault(L, []).append(d)
            chain.append(d)
            links.append((prev, d))
            prev = d
        links.append((prev, b))
        chains[i] = chain
    n_layers = max(members) + 1 if members else 1
    lay = [members.get(L, []) for L in range(n_layers)]
    for L in range(n_layers):                            # boxes given a row keep the order of their rows
        if any(n in rows for n in lay[L]):
            base = list(lay[L])                          # sort() empties the list while it sorts
            lay[L].sort(key=lambda n: rows.get(n, base.index(n)))
    up: dict[str, list[str]] = {}
    down: dict[str, list[str]] = {}
    for a, b in links:
        down.setdefault(a, []).append(b)
        up.setdefault(b, []).append(a)

    def crossings(ls: list[list[str]]) -> int:
        total = 0
        for L in range(len(ls) - 1):
            at = {n: k for k, n in enumerate(ls[L + 1])}
            es = sorted((k, at[m]) for k, n in enumerate(ls[L]) for m in down.get(n, []) if m in at)
            for x in range(len(es)):
                for y in range(x + 1, len(es)):
                    if es[x][0] < es[y][0] and es[x][1] > es[y][1]:
                        total += 1
        return total

    def sort_layer(L: int, ref: list[str], nbrs: dict[str, list[str]]) -> None:
        if all(n in rows for n in lay[L] if not n.startswith("\0")) and rows:
            return
        at = {n: k for k, n in enumerate(ref)}
        bary = {}
        for k, n in enumerate(lay[L]):
            ps = [at[m] for m in nbrs.get(n, []) if m in at]
            bary[n] = sum(ps) / len(ps) if ps else float(k)
        gbary: dict[int, list[float]] = {}
        for n in lay[L]:
            if n in groups:
                gbary.setdefault(groups[n], []).append(bary[n])
        gkey = {g: sum(v) / len(v) for g, v in gbary.items()}
        lay[L].sort(key=lambda n: (gkey[groups[n]] if n in groups else bary[n],
                                   groups.get(n, -1), bary[n]))
        # in a run of equal barycentres, members of a group go in the middle, beside what they join
        ns, out_, k = lay[L], [], 0
        while k < len(ns):
            j = k
            key = gkey[groups[ns[k]]] if ns[k] in groups else bary[ns[k]]
            while j < len(ns) and abs((gkey[groups[ns[j]]] if ns[j] in groups else bary[ns[j]]) - key) < 1e-9:
                j += 1
            run = ns[k:j]
            inside = [n for n in run if n in groups]
            rest = [n for n in run if n not in groups]
            half = len(rest) // 2
            out_ += rest[:half] + inside + rest[half:]
            k = j
        lay[L] = out_

    best, best_x = [list(x) for x in lay], crossings(lay)
    for s in range(sweeps):
        if best_x == 0 and s >= 2:
            break
        if s % 2 == 0:
            for L in range(1, n_layers):
                sort_layer(L, lay[L - 1], up)
        else:
            for L in range(n_layers - 2, -1, -1):
                sort_layer(L, lay[L + 1], down)
        x = crossings(lay)
        if x <= best_x:
            best, best_x = [list(y) for y in lay], x
    lay = best
    # a group across layers: its boxes in each layer moved, together, level with the group elsewhere,
    # so the region drawn round it takes in no box of another
    for g in sorted(set(groups.values())):
        where_ = {L: [n for n in lay[L] if groups.get(n) == g] for L in range(n_layers)}
        if sum(1 for v in where_.values() if v) < 2 or rows:
            continue
        for L, mine in where_.items():
            if not mine:
                continue
            others = [k - (len(lay[M]) - 1) / 2 for M, ns in where_.items() if M != L for k, n in enumerate(lay[M])
                      if n in ns]
            target = sum(others) / len(others) + (len(lay[L]) - 1) / 2
            rest = [n for n in lay[L] if n not in mine]
            best_at = min(range(len(rest) + 1), key=lambda s: (abs(s + (len(mine) - 1) / 2 - target), s))
            lay[L] = rest[:best_at] + mine + rest[best_at:]

    # 4. across the flow: each box as near what it joins as its neighbours allow
    pos: dict[str, float] = {}
    widest = max(len(x) for x in lay) if lay else 1
    for L, ns in enumerate(lay):
        for k, n in enumerate(ns):
            pos[n] = k + (widest - len(ns)) / 2

    def gap(a: str, b: str) -> float:
        return 0.55 if a.startswith("\0") or b.startswith("\0") else 1.0

    def settle(ns: list[str], want: list[float]) -> list[float]:
        """The positions nearest `want` that keep the order and the gaps (pool adjacent violators)."""
        offs = [0.0]
        for k in range(1, len(ns)):
            offs.append(offs[-1] + gap(ns[k - 1], ns[k]))
        blocks: list[list[float]] = []                   # [sum, count]
        for k in range(len(ns)):
            blocks.append([want[k] - offs[k], 1.0])
            while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] > blocks[-1][0] / blocks[-1][1]:
                s_, c_ = blocks.pop()
                blocks[-1][0] += s_
                blocks[-1][1] += c_
        z = []
        for s_, c_ in blocks:
            z.extend([s_ / c_] * int(c_))
        return [z[k] + offs[k] for k in range(len(ns))]

    if not rows:
        for it in range(12):
            seq = range(n_layers) if it % 2 == 0 else range(n_layers - 1, -1, -1)
            for L in seq:
                ns = lay[L]
                want = []
                for n in ns:
                    nb = [pos[m] for m in up.get(n, []) + down.get(n, [])]
                    want.append(sum(nb) / len(nb) if nb else pos[n])
                for n, v in zip(ns, settle(ns, want)):
                    pos[n] = v
        # last, one sweep along the flow against what comes before alone: a chain runs straight
        for L in range(1, n_layers):
            ns = lay[L]
            want = []
            for n in ns:
                nb = [pos[m] for m in up.get(n, [])]
                want.append(sum(nb) / len(nb) if nb else pos[n])
            for n, v in zip(ns, settle(ns, want)):
                pos[n] = v
    else:
        for n in nodes:
            if n in rows:
                pos[n] = float(rows[n])
        for L, ns in enumerate(lay):                     # dummies and boxes without a row fill in between
            for k, n in enumerate(ns):
                if n not in rows:
                    nb = [pos[m] for m in up.get(n, []) + down.get(n, []) if m in pos]
                    pos[n] = sum(nb) / len(nb) if nb else float(k)
            for n, v in zip(ns, settle(ns, [pos[n] for n in ns])):
                pos[n] = v
    low_p = min(pos.values(), default=0.0)
    pos = {n: round((v - low_p) * 4) / 4 for n, v in pos.items()}
    dummies = {d: (dlayer[d], pos.pop(d)) for d in dlayer}
    return Layered(layer={n: layer[n] for n in nodes}, pos=pos, chains=chains, dummies=dummies,
                   back=back, loops=loops, layers=n_layers)


# ----------------------------------------------------------------------------------------------
# Placing and routing
# ----------------------------------------------------------------------------------------------
@dataclass
class Rect:
    m0: float
    c0: float
    m1: float
    c1: float

    @property
    def mc(self) -> float: return (self.m0 + self.m1) / 2
    @property
    def cc(self) -> float: return (self.c0 + self.c1) / 2


@dataclass
class Route:
    points: list[tuple[float, float]]                   # in m, c
    label_seg: int                                      # which segment carries the label
    edge: int


class Plan:
    """Boxes of size (w, h) placed by a Layered, in direction "right" (left to right) or "down"."""

    def __init__(self, lay: Layered, sizes: dict[str, tuple[float, float]], direction: str,
                 edges: list[tuple[str, str]], labels: list[str | None], gap_c: float = 36, gap_m: float = 64,
                 label_size: float = 10.5):
        self.lay, self.direction, self.edges, self.labels = lay, direction, edges, labels
        self.across = direction == "down"
        self.gap_c = gap_c
        # along the flow a box is its w (right) or h (down); across, the other
        along = {n: (wh[1] if self.across else wh[0]) for n, wh in sizes.items()}
        wide = {n: (wh[0] if self.across else wh[1]) for n, wh in sizes.items()}
        self.wide = max(wide.values(), default=40)
        self.slot = self.wide + gap_c
        thick = max(along.values(), default=40)
        self.depth = [max([along[n] for n in lay.layer if lay.layer[n] == L] or [thick]) for L in range(lay.layers)]
        # the gap after each layer is as wide as the widest label that runs across it needs
        need = [gap_m] * max(lay.layers - 1, 1)
        for i, (a, b) in enumerate(edges):
            lab = labels[i]
            if not lab or i in lay.back or i in lay.loops:
                continue
            L = lay.layer[a]
            if L < len(need):
                w = text_width(lab, label_size, 500) if not self.across else label_size + 8
                need[L] = max(need[L], w + 62)
        self.gaps = need
        self.m_of: list[float] = []
        m = 0.0
        for L in range(lay.layers):
            self.m_of.append(m)
            m += self.depth[L] + (self.gaps[L] if L < len(self.gaps) else 0)
        self.rect: dict[str, Rect] = {}
        for n, L in lay.layer.items():
            a_, w_ = along[n], wide[n]
            m0 = self.m_of[L] + (self.depth[L] - a_) / 2
            c0 = self.c_mid(lay.pos[n]) - w_ / 2
            self.rect[n] = Rect(m0, c0, m0 + a_, c0 + w_)

    def c_mid(self, pos: float) -> float:
        """The middle, across the flow, of slot `pos`."""
        return pos * self.slot + self.wide / 2

    def xy(self, m: float, c: float) -> tuple[float, float]:
        return (c, m) if self.across else (m, c)

    def box_xywh(self, n: str) -> tuple[float, float, float, float]:
        r = self.rect[n]
        x0, y0 = self.xy(r.m0, r.c0)
        x1, y1 = self.xy(r.m1, r.c1)
        return x0, y0, x1 - x0, y1 - y0

    def _track(self, g: int, t: int, near: str) -> float:
        """Track t of the gap after layer g (-1: before the first layer; the last: after it), counted
        from the target's side of the gap (near "dst") or the source's ("src")."""
        n = self.lay.layers
        if g < 0:
            return self.m_of[0] - 18 - t * 9
        if g >= n - 1:
            return self.m_of[n - 1] + self.depth[n - 1] + 18 + t * 9
        if near == "src":
            return self.m_of[g] + self.depth[g] + 18 + t * 9
        return self.m_of[g + 1] - 18 - t * 9

    def routes(self) -> list[Route]:
        lay = self.lay
        same = {i for i in lay.back if lay.layer[self.edges[i][0]] == lay.layer[self.edges[i][1]]}
        # an edge against the flow runs round a lane below every box, or above them all, whichever
        # has fewer boxes in the way; an end with nothing between it and its lane leaves or enters
        # the box by that side, straight; another goes by the gap beside its layer
        looped = {self.edges[i][0] for i in lay.loops}

        def clear(n: str, low: bool) -> bool:
            r = self.rect[n]
            for o, ro in self.rect.items():
                if o != n and lay.layer[o] == lay.layer[n] and (ro.c0 >= r.c1 if low else ro.c1 <= r.c0):
                    return False
            return low or n not in looped

        lane_of: dict[int, str] = {}
        direct: dict[tuple[int, str], bool] = {}
        for i in sorted(lay.back - same):
            a, b = self.edges[i]
            cost = {side: (not clear(a, side == "low")) + (not clear(b, side == "low")) for side in ("low", "high")}
            side = "low" if cost["low"] <= cost["high"] else "high"
            lane_of[i] = side
            direct[(i, "src")] = clear(a, side == "low")
            direct[(i, "dst")] = clear(b, side == "low")
        # ports: the edges on each side of a box, spread in the order of what they reach
        ends: dict[tuple[str, str], list[tuple[float, int, str]]] = {}

        def toward(i: int, src: bool) -> float:
            a, b = self.edges[i]
            chain = lay.chains.get(i, [])
            if i in lay.back:                                 # its lane: past every box on that side
                return 1e9 if lane_of[i] == "low" else -1e9
            if src:
                return self.c_mid(lay.dummies[chain[0]][1]) if chain else self.rect[b].cc
            return self.c_mid(lay.dummies[chain[-1]][1]) if chain else self.rect[a].cc

        for i, (a, b) in enumerate(self.edges):
            if i in lay.loops or i in same:
                continue
            if i in lay.back:
                for n, role, other in ((a, "src", b), (b, "dst", a)):
                    if direct[(i, role)]:
                        ends.setdefault((n, lane_of[i]), []).append((self.rect[other].mc, i, role))
                    else:
                        ends.setdefault((n, "out" if role == "src" else "in"), []).append((toward(i, role == "src"), i, role))
                continue
            ends.setdefault((a, "out"), []).append((toward(i, True), i, "src"))
            ends.setdefault((b, "in"), []).append((toward(i, False), i, "dst"))
        port: dict[tuple[int, str], float] = {}
        for (n, side), es in ends.items():
            es.sort()
            r = self.rect[n]
            k = len(es)
            step = min(0.22, 0.64 / k) if k > 1 else 0
            lo, hi = (r.m0, r.m1) if side in ("low", "high") else (r.c0, r.c1)
            for j, (_, i, role) in enumerate(es):
                port[(i, role)] = lo + (hi - lo) * (0.5 + (j - (k - 1) / 2) * step)

        # each edge as hops (m, c) and the gaps its turns fall in
        bottom = max((r.c1 for r in self.rect.values()), default=0)
        top = min((r.c0 for r in self.rect.values()), default=0) - (22 if looped else 0)
        plans: list[tuple[int, list[Any], int]] = []        # (edge, points with ("T", key) turns, label segment)
        pending: dict[tuple[int, str], list[tuple[float, float, tuple[int, int]]]] = {}
        # how far out each lane runs: past the boxes and the lanes before it, with room for its label --
        # above the lane where the lane runs along the flow, across it (as wide as it is) where it runs down
        reach = {"low": bottom, "high": top}
        size = 10.5

        def half(i: int) -> float:
            lab = self.labels[i] if i < len(self.labels) else None
            if not lab:
                return 6
            return text_width(lab, size, 500) / 2 + 8 if self.across else size + 10

        def lane_at(i: int, side: str) -> float:
            out = half(i) if self.across or side == "low" else 6
            k = 1 if side == "low" else -1
            cl = reach[side] + k * (max(out, 6) + 12)
            reach[side] = cl + k * (half(i) if self.across else (6 if side == "low" else half(i)))
            return cl
        fwd = [i for i in range(len(self.edges)) if i not in lay.back and i not in lay.loops]
        outdeg = {n: sum(1 for i in fwd if self.edges[i][0] == n) for n in self.rect}
        indeg = {n: sum(1 for i in fwd if self.edges[i][1] == n) for n in self.rect}
        for i, (a, b) in enumerate(self.edges):
            ra, rb = self.rect[a], self.rect[b]
            if i in lay.loops:
                m_l, m_r = ra.m0 + (ra.m1 - ra.m0) * 0.3, ra.m0 + (ra.m1 - ra.m0) * 0.7
                plans.append((i, [(m_l, ra.c0), (m_l, ra.c0 - 22), (m_r, ra.c0 - 22), (m_r, ra.c0)], 1))
                continue
            if i in same:
                upper, lower = (ra, rb) if ra.c0 < rb.c0 else (rb, ra)
                pts = [(ra.mc, ra.c1 if ra is upper else ra.c0), (rb.mc, rb.c0 if rb is lower else rb.c1)]
                plans.append((i, pts, 0))
                continue
            ca, cb = port[(i, "src")], port[(i, "dst")]
            if i in lay.back:
                side = lane_of[i]
                cl = lane_at(i, side)
                edge_a = ra.c1 if side == "low" else ra.c0
                edge_b = rb.c1 if side == "low" else rb.c0
                pts = []
                if direct[(i, "src")]:
                    pts += [(ca, edge_a), (ca, cl)]
                else:
                    ka = (i, 0)
                    pending.setdefault((lay.layer[a], "src"), []).append((min(ca, cl), max(ca, cl), ka))
                    pts += [(ra.m1, ca), ("T", ka, ca), ("T", ka, cl)]
                if direct[(i, "dst")]:
                    pts += [(cb, cl), (cb, edge_b)]
                else:
                    kb = (i, 1)
                    pending.setdefault((lay.layer[b] - 1, "dst"), []).append((min(cb, cl), max(cb, cl), kb))
                    pts += [("T", kb, cl), ("T", kb, cb), (rb.m0, cb)]
                plans.append((i, pts, 1 if direct[(i, "src")] else 2))
                continue
            hops: list[tuple[float, float, int]] = [(ra.m1, ca, lay.layer[a])]
            for d in lay.chains.get(i, []):
                L, p = lay.dummies[d]
                c = self.c_mid(p)
                hops.append((self.m_of[L], c, L))
                hops.append((self.m_of[L] + self.depth[L], c, L))
            hops.append((rb.m0, cb, lay.layer[b]))
            if len(hops) == 2 and abs(ca - cb) <= 12 and rb.c0 + 8 <= ca <= rb.c1 - 8:
                hops[-1] = (rb.m0, ca, lay.layer[b])
            # a box that fans out turns its edges near itself, so each label sits by its target, alone;
            # one that many edges reach turns them near itself, so each label sits by its source
            near = "src" if outdeg[a] > indeg[b] else "dst"
            pts: list[Any] = [(hops[0][0], hops[0][1])]
            for k in range(1, len(hops)):
                p, q = hops[k - 1], hops[k]
                if abs(p[1] - q[1]) >= 0.5:
                    key = (i, k)
                    pending.setdefault((p[2], near), []).append((min(p[1], q[1]), max(p[1], q[1]), key))
                    pts += [("T", key, p[1]), ("T", key, q[1])]
                pts.append((q[0], q[1]))
            plans.append((i, pts, -1 if near == "src" else 0))

        # tracks: verticals that overlap in one gap each get their own, from the far side of the gap back
        track: dict[tuple[int, int], float] = {}
        for (g, near), segs in pending.items():
            segs.sort(key=lambda s: (s[0], s[1]))
            ends_at: list[float] = []
            for c0, c1, key in segs:
                for t, e in enumerate(ends_at):
                    if e + 6 < c0:
                        ends_at[t] = c1
                        break
                else:
                    t = len(ends_at)
                    ends_at.append(c1)
                track[key] = self._track(g, t, near)
        routes = []
        for i, pts, seg in plans:
            real = _dedupe([(track[p[1]], p[2]) if p[0] == "T" else p for p in pts])
            routes.append(Route(real, len(real) - 2 if seg == -1 else seg, i))
        return routes


def _dedupe(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for p in pts:
        if out and abs(out[-1][0] - p[0]) < 0.01 and abs(out[-1][1] - p[1]) < 0.01:
            continue
        out.append(p)
    # drop a middle point on a straight run
    k = 1
    while k < len(out) - 1:
        a, b, c = out[k - 1], out[k], out[k + 1]
        if (abs(a[0] - b[0]) < 0.01 and abs(b[0] - c[0]) < 0.01) or (abs(a[1] - b[1]) < 0.01 and abs(b[1] - c[1]) < 0.01):
            out.pop(k)
        else:
            k += 1
    return out


def label_at(points: list[tuple[float, float]], seg: int) -> float:
    """The fraction along a path at the middle of segment `seg`."""
    import math
    lens = [math.dist(points[k], points[k + 1]) for k in range(len(points) - 1)]
    total = sum(lens) or 1
    seg = max(0, min(seg, len(lens) - 1))
    return (sum(lens[:seg]) + lens[seg] / 2) / total


def longest_along(points: list[tuple[float, float]], across: bool) -> int:
    """The segment that runs along the flow and is longest: where a label fits best."""
    import math
    best, best_len = 0, -1.0
    for k in range(len(points) - 1):
        (_, c0), (_, c1) = points[k], points[k + 1]
        if abs(c0 - c1) < 0.5:
            L = math.dist(points[k], points[k + 1])
            if L > best_len:
                best, best_len = k, L
    return best


__all__ = ["layered", "Layered", "Plan", "Route", "Rect", "label_at", "longest_along"]
