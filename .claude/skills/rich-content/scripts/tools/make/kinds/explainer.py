"""
A page that teaches a process over one diagram: the reader steps through frames, and in each the same
boxes stand in the same places while what the step is about lights up -- a box in focus, one that
fails, an arrow that carries the step -- so the eye sees what changed.

  title:, eyebrow:, lead:, footer:, contents:   as a document's
  diagram:   the diagram: a flow spec's file (make: flow), or its fields inline (nodes, edges,
             groups, direction, numbered, box, gap -- see `--schema flow`)
  intro:     Markdown before the steps
  frames:    the steps, in order, each
               title:   the step's name
               text:    what happens in it (Markdown inline)
               focus:, fail:, warn:, good:, dim:   [box ids] in that state for this step
               rest:    dim -- every box the step does not name is dimmed (normal by default)
               highlight:   [edges] drawn in the accent colour -- or in `tone:` good | bad | warn | info
               dim_edges:   [edges] drawn faint;  hide_edges: [edges] not drawn
             an edge is named by its number in `edges` (from 1) or as "a -> b"
  caption:   a line under the steps
  after:     blocks after the steps (the doc kind's blocks: p, md, callout, table, figure, …)

Every frame is drawn from the same layout, so the boxes never move; the page is HTML only.
"""
from __future__ import annotations

import copy
from typing import Any

from .. import Spec, SpecError, read
from ..document import Doc, common
from . import flow

PURPOSE = "a page that steps through a process over one diagram, the same boxes lit step by step"
GROUP = "learning"
OUTPUT = "html"

STATES = ("focus", "fail", "warn", "good", "dim")


def _diagram(spec: Spec) -> tuple[dict[str, Any], Spec]:
    """What flow.figure needs, read from a flow spec's file or from the fields inline."""
    v = spec.get("diagram")
    if isinstance(v, str):
        p = spec.file(v)
        s = Spec(read(p), p.name, p.parent)
        if s.need("make", str) != "flow":
            raise SpecError(f"diagram: {p.name} is a `{s.get('make')}` spec; an explainer steps over a flow")
        s.get("theme")
        s.get("out")
    elif isinstance(v, dict):
        s = spec.wrap(v, ".diagram")
    else:
        raise SpecError("`diagram` is required: a flow spec's file, or nodes and edges inline")
    args = flow.read(s)
    return args, s


def _edge_index(ref: Any, edges: list[dict[str, Any]], where: str) -> list[int]:
    if isinstance(ref, int) and not isinstance(ref, bool):
        if not 1 <= ref <= len(edges):
            raise SpecError(f"{where}: no edge {ref}; they are numbered 1 to {len(edges)}")
        return [ref - 1]
    if isinstance(ref, str) and "->" in ref:
        a, b = (x.strip() for x in ref.split("->", 1))
        found = [k for k, e in enumerate(edges) if e["from"] == a and e["to"] == b]
        if not found:
            raise SpecError(f"{where}: no edge {a} -> {b}")
        return found
    raise SpecError(f"{where}: an edge is its number (from 1) or \"a -> b\"")


def _frame(f: Spec, base: dict[str, Any], k: int) -> tuple[Any, str, str]:
    nodes = copy.deepcopy(base["nodes"])
    edges = copy.deepcopy(base["edges"])
    ids = {n["id"] for n in nodes}
    named: set[str] = set()
    for state in STATES:
        for i in f.get(state, [], list):
            if str(i) not in ids:
                raise SpecError(f"{f.where}.{state}: no box `{i}`; there are: {', '.join(sorted(ids))}")
            named.add(str(i))
            for n in nodes:
                if n["id"] == str(i):
                    n["state"] = state
    rest = f.get("rest", "normal", str, ("normal", "dim"))
    if rest == "dim":
        for n in nodes:
            if n["id"] not in named:
                n["state"] = "dim"
    tone = f.get("tone", "accent", str, ("accent", "good", "bad", "warn", "info"))
    for key, colour in (("dim_edges", "faint"), ("hide_edges", None), ("highlight", tone)):
        for j, ref in enumerate(f.get(key, [], list)):
            for e in _edge_index(ref, edges, f"{f.where}.{key}[{j}]"):
                if colour is None:
                    edges[e]["hidden"] = True
                else:
                    edges[e]["color"] = colour
    canvas = flow.figure(nodes, edges, base["groups"], base["member"], base["direction"], base["numbered"],
                         base["w"], base["h"], base["gap_m"], base["gap_c"])
    return canvas, str(f.need("title")), str(f.get("text", ""))


def document(spec: Spec) -> Doc:
    doc = common(spec, default="html", allowed=("html",))
    base, inner = _diagram(spec)
    frames = []
    for k, f in enumerate(spec.items("frames")):
        if not isinstance(f, Spec):
            raise SpecError(f"frames[{k}]: {{title, text, focus, …}}")
        frames.append(_frame(f, base, k))
    if not frames:
        raise SpecError("`frames` is required: the steps, each {title, text, focus, …}")
    sizes = {(round(c.w, 2), round(c.h, 2)) for c, _, _ in frames}
    if len(sizes) > 1:                                  # the layout does not depend on states or colours
        raise SpecError(f"the frames came out in {len(sizes)} sizes; they must share one canvas")
    if isinstance(spec.get("diagram"), str):            # a file's own keys, checked as the spec's are
        found = inner.unknown()
        if found:
            raise SpecError("\n".join(found))
    blocks: list[Any] = []
    intro = spec.get("intro", kind=str)
    if intro:
        blocks.append({"md": intro})
    blocks.append({"steps": [{"figure": c, "title": t, "text": x} for c, t, x in frames],
                   "caption": spec.get("caption", kind=str)})
    blocks += spec.items("after")
    doc.blocks = blocks
    return doc
