"""
A sequence diagram: who sends what to whom, in order, down the page. Lifelines are spaced by the
labels between them; a message that passes a lifeline puts its label in a gap; the canvas fits.

  actors:    id: "Label" -- or id: {label, kind, icon}; kind and icon guessed from the words
  messages:  in order, each one of
             "a -> b: label"        a call (numbered)
             "b --> a: label"       a return (dashed)
             "a -> a: label"        a call to itself
             "== text"              a divider across every lifeline: a phase, a pause
             and a message may end with "| a note" (set small, under it) and "[good]", "[bad]" or
             "[warn]" (its colour); a label in `backticks` is set as code.
             Or {from, to, label, ret, note, tone, mono}.
  spans:     [[actor, first message, last message], …] -- an activation bar (messages count from 1)
  brackets:  [{actor, from, to, text, side}] -- a bracket beside a lifeline over messages from..to,
             side left (the default) or right: a time, a round trip
  gap:       the space between two messages (36)
"""
from __future__ import annotations

import re
from typing import Any

from ...svgkit import Canvas, Sequence, text_width
from .. import Spec, SpecError
from ..infer import box

PURPOSE = "who sends what to whom, in order: a request flow, a handshake, a protocol"
GROUP = "diagrams"
OUTPUT = "svg"

BOX_W, BOX_H, TOP = 136, 46, 12
MSG = re.compile(r"^\s*([^\s:<>-][^\s:<>]*?)\s*(-->|->)\s*([^\s:<>-][^\s:<>]*?)\s*(?::\s*(.*?))?\s*$")


def message(value: Any, spec: Spec, k: int, known: list[str]) -> dict[str, Any]:
    where = f".messages[{k}]"
    if isinstance(value, str) and value.lstrip().startswith("=="):
        return {"divider": value.strip().lstrip("=").strip().rstrip("=").strip()}
    if isinstance(value, str):
        text, note, tone = value, None, None
        m = re.search(r"\s*\[(good|bad|warn)\]\s*$", text)
        if m:
            tone, text = m.group(1), text[:m.start()]
        if " | " in text:
            text, note = text.split(" | ", 1)
        m = MSG.match(text)
        if not m:
            raise SpecError(f"messages[{k}]: {value!r} is not a message (\"a -> b: label\", \"b --> a: label\" or \"== text\")")
        a, arrow, b, label = m.groups()
        msg = {"from": a, "to": b, "label": label or "", "ret": arrow == "-->", "note": note, "tone": tone,
               "mono": False}
    else:
        s = value if isinstance(value, Spec) else spec.wrap(value, where)
        if "divider" in s:
            return {"divider": str(s.get("divider"))}
        msg = {"from": str(s.need("from")), "to": str(s.need("to")), "label": str(s.get("label", "")),
               "ret": bool(s.get("ret", False, bool)), "note": s.get("note", kind=str),
               "tone": s.get("tone", None, str, ("good", "bad", "warn")), "mono": bool(s.get("mono", False, bool))}
    lab = msg["label"]
    if len(lab) > 1 and lab.startswith("`") and lab.endswith("`"):
        msg["label"], msg["mono"] = lab[1:-1], True
    for end in (msg["from"], msg["to"]):
        if end not in known:
            raise SpecError(f"messages[{k}]: no actor `{end}`; there are: {', '.join(known)}")
    return msg


def draw(spec: Spec) -> Canvas:
    actors = [box(i, v, spec, f".actors.{i}") for i, v in spec.mapping("actors")]
    if not actors:
        raise SpecError("`actors` is required: id: Label, one per lifeline")
    ids = [a["id"] for a in actors]
    msgs = [message(v, spec, k, ids) for k, v in enumerate(spec.items("messages"))]
    step_gap = spec.num("gap", 36) or 36
    n = len(ids)
    at = {i: k for k, i in enumerate(ids)}

    def fam(m):
        from ...theme import current
        return current().mono if m.get("mono") else None

    # the gap between each pair of neighbouring lifelines: wide enough for the labels that sit in it
    need = [BOX_W + 24] * max(n - 1, 1)
    where_label: list[int | None] = []
    for m in msgs:
        if "divider" in m or m["from"] == m["to"]:
            where_label.append(None)
            continue
        a, b = at[m["from"]], at[m["to"]]
        lo, hi = min(a, b), max(a, b)
        gaps = list(range(lo, hi))
        g = gaps[(len(gaps) - 1) // 2] if a < b else gaps[len(gaps) // 2]
        where_label.append(g)
        tw = text_width(m["label"], 10.5, 500, fam(m))
        nw = text_width(m["note"], 9.5, 400) if m["note"] else 0
        # the step marker sits 20 px out from the sender, so the gap next to it holds it as well
        beside_sender = g == (a if a < b else a - 1)
        need[g] = max(need[g], max(tw + (62 if beside_sender else 30), nw + 24))

    brackets = []
    for k, b in enumerate(spec.items("brackets")):
        if not isinstance(b, Spec):
            raise SpecError(f"brackets[{k}]: expected {{actor, from, to, text}}")
        on = str(b.need("actor"))
        if on not in at:
            raise SpecError(f"brackets[{k}].actor: no actor `{on}`")
        brackets.append({"on": at[on], "from": int(b.need("from", int)), "to": int(b.need("to", int)),
                         "text": str(b.need("text")), "side": b.get("side", "left", str, ("left", "right"))})
    left = BOX_W / 2 + 8
    right = BOX_W / 2 + 8
    for b in brackets:
        w = text_width(b["text"], 10, 600, _mono()) + 44
        if b["side"] == "left" and b["on"] == 0:
            left = max(left, w)
        if b["side"] == "right" and b["on"] == n - 1:
            right = max(right, w)
        if b["side"] == "left" and b["on"] > 0:
            need[b["on"] - 1] = max(need[b["on"] - 1], w + BOX_W / 2)
        if b["side"] == "right" and b["on"] < n - 1:
            need[b["on"]] = max(need[b["on"]], w + BOX_W / 2)
    for m in msgs:                                     # a call to itself writes its label to the right
        if "divider" not in m and m["from"] == m["to"]:
            a = at[m["from"]]
            w = 42 + text_width(m["label"], 10.5, 500, fam(m)) + 10
            if a == n - 1:
                right = max(right, w)
            else:
                need[a] = max(need[a], w + 20)
    xs = [left]
    for k in range(n - 1):
        xs.append(xs[-1] + need[k])

    # down the page
    y = TOP + BOX_H + 34
    ys: list[float] = []
    for m in msgs:
        ys.append(y)
        if "divider" in m:
            y += 34
        elif m["from"] == m["to"]:
            y += max(step_gap, 40)
        else:
            y += step_gap + (14 if m["note"] else 0)
    height = y + 4
    width = xs[-1] + right
    for m in msgs:
        if "divider" in m:
            width = max(width, text_width(m["divider"], 10, 600) + 40)
    c = Canvas(width, height)
    seq = Sequence(c, [(a["label"], a["kind"], a["icon"]) for a in actors], top=TOP, box_w=BOX_W, box_h=BOX_H,
                   bottom=height - 6, xs=xs)
    numbers: list[int | None] = []
    count = 0
    for k, m in enumerate(msgs):
        if "divider" in m:
            yy = ys[k] - 4
            tw = text_width(m["divider"], 10, 600)
            # its label in the middle of a gap between lifelines, the widest nearest the centre, not on one
            g = max(range(max(n - 1, 1)), key=lambda j: (need[j] if n > 1 else 0) - abs(j - (n - 2) / 2) * 0.01)
            cx = (xs[g] + xs[g + 1]) / 2 if n > 1 else width / 2
            for x0, x1 in ((10, cx - tw / 2 - 10), (cx + tw / 2 + 10, width - 10)):
                c.line(x0, yy, x1, yy, stroke=c.col("rule"), sw=1, dash="2 3", layer="labels")
            c.rect(cx - tw / 2 - 8, yy - 9, tw + 16, 18, fill=c.col("wash"), stroke=c.col("rule"), sw=0.8,
                   rx=c._pill(18), layer="labels")
            c.text(cx, yy + 3.6, m["divider"], 10, 600, c.col("muted"), "middle")
            numbers.append(None)
            continue
        count += 1
        numbers.append(count)
        a, b = at[m["from"]], at[m["to"]]
        lab_at = None
        g = where_label[k]
        if g is not None and abs(a - b) > 1:
            mid = (xs[g] + xs[g + 1]) / 2
            sgn = 1 if b > a else -1
            lab_at = (mid - 8 * sgn - xs[a]) / (xs[b] - xs[a])
        seq.msg(a, b, ys[k], m["label"], ret=m["ret"], tone=m["tone"], note=m["note"], mono=m["mono"], label_at=lab_at)
    first = {num: ys[k] for k, num in enumerate(numbers) if num}
    for k, s in enumerate(spec.items("spans")):
        if not isinstance(s, list) or len(s) != 3 or s[0] not in at:
            raise SpecError(f"spans[{k}]: expected [actor, first message, last message]")
        y1, y2 = _y(first, s[1], f"spans[{k}]"), _y(first, s[2], f"spans[{k}]")
        seq.span(at[s[0]], y1 - 6, y2 + 6)
    for b in brackets:
        seq.bracket(b["on"], _y(first, b["from"], "brackets") - 6, _y(first, b["to"], "brackets") + 6, b["text"],
                    side=b["side"])
    return c


def _y(first: dict[int, float], n: Any, where: str) -> float:
    if n not in first:
        raise SpecError(f"{where}: no message {n}; they are numbered 1 to {max(first, default=0)}")
    return first[n]


def _mono() -> str:
    from ...theme import current
    return current().mono
