"""
A status report for a week or a month: where things stand at a glance, what moved, what is at risk,
how the milestones go, and what is needed from the reader. Figures given with what they were before
and what they aim at have their change and their colour worked out.

  title:       what is reported on ("Orders platform")
  period:      the week or month ("Week 43 · 20-24 October 2026"); the eyebrow, unless one is given
  overall:     done | on-track | at-risk | late -- the first tile
  summary:     Markdown: the state in a few sentences (one paragraph is set as the lead)
  compare:     what `previous` values are ("last week" by default)
  kpis:        [{label, value, unit, previous, target, better: higher | lower, note, tone}] -- the
               note ("−16 ms on last week · target 200 ms") and tone (good when the target is met,
               or when it moved the better way) are worked out unless given; or [label, value, note, tone]
  highlights:  [what went well or moved]
  risks:       [{risk, severity: high | medium | low, owner, mitigation}] -- highest first
  milestones:  [{name, due, state: done | on-track | at-risk | late, note}] -- drawn as a list with
               each state in its colour
  asks:        [decisions or help needed from the reader]
  figures:     [{figure: chart.yaml | {make: chart, …}, caption}] -- after the milestones
  eyebrow, lead, footer, format (html by default | pdf | [html, pdf]), contents, dense: as every document
"""
from __future__ import annotations

from typing import Any

from ...svgkit import Canvas, text_width
from .. import Spec, SpecError
from ..document import Doc, common

PURPOSE = "a weekly or monthly status: tiles worked out from targets, risks, milestones, asks"
GROUP = "documents"
OUTPUT = "html|pdf"

OVERALL = {"done": ("Done", "good"), "on-track": ("On track", "good"), "at-risk": ("At risk", "warn"),
           "late": ("Late", "bad")}
SEVERITY = {"high": 0, "medium": 1, "low": 2}


def number(v: float) -> str:
    if float(v).is_integer():
        return f"{v:,.0f}".replace(",", " ")
    return f"{v:,.1f}".replace(",", " ")


def tile(k: int, item: Any, compare: str) -> list[str]:
    if isinstance(item, list):
        return [str(x) for x in item]
    if not isinstance(item, Spec):
        raise SpecError(f"kpis[{k}]: {{label, value, previous, target}} or [label, value, note, tone]")
    label, value = str(item.need("label")), item.need("value")
    unit = item.get("unit", "", str)
    prev, target = item.num("previous"), item.num("target")
    better = item.get("better", "higher", str, ("higher", "lower"))
    note, tone = item.get("note", kind=str), item.get("tone", None, str, ("good", "warn", "bad", "info", "neutral"))
    shown = number(value) + unit if isinstance(value, (int, float)) and not isinstance(value, bool) else str(value)
    parts, auto = [], "neutral"
    if prev is not None and isinstance(value, (int, float)):
        d = float(value) - prev
        sign = "+" if d > 0 else "−" if d < 0 else "±"
        parts.append(f"{sign}{number(abs(d))}{unit} on {compare}")
        if d:
            auto = "good" if (d > 0) == (better == "higher") else "bad"
    if target is not None and isinstance(value, (int, float)):
        met = float(value) >= target if better == "higher" else float(value) <= target
        parts.append(f"target {number(target)}{unit}")
        auto = "good" if met else "bad"
    return [label, shown, note if note is not None else " · ".join(parts), tone or auto]


def milestones_figure(items: list[dict[str, Any]]) -> Canvas:
    names = {"done": ("Done", "good"), "on-track": ("On track", "info"), "at-risk": ("At risk", "warn"),
             "late": ("Late", "bad")}
    chip_w = max(text_width(n, 10.5, 600) for n, _ in names.values()) + 14 + 8
    due_w = max([text_width(str(m["due"] or ""), 11.5, 500) for m in items] + [0])
    name_w = max(text_width(m["name"], 13, 600) for m in items)
    note_w = max([text_width(m["note"] or "", 11, 400) for m in items] + [0])
    w = max(560, chip_w + 16 + max(name_w, note_w) + 32 + due_w + 8)
    rows = [44 if m["note"] else 32 for m in items]
    c = Canvas(w, sum(rows) + 8)
    y = 4
    for m, h in zip(items, rows):
        label, tone = names[m["state"]]
        c.chip(4, y + 6, label, tone=tone, mono=False)
        c.text(chip_w + 16, y + 20, m["name"], 13, 600)
        if m["note"]:
            c.text(chip_w + 16, y + 36, m["note"], 11, 400, c.col("muted"))
        if m["due"]:
            c.text(w - 4, y + 20, str(m["due"]), 11.5, 500, c.col("muted"), "end")
        y += h
        if m is not items[-1]:
            c.line(4, y, w - 4, y, sw=0.8)
    return c


def bullets(items: list[Any], numbered: bool = False) -> str:
    return "\n".join(f"{k + 1}. {x}" if numbered else f"- {x}" for k, x in enumerate(items))


def document(spec: Spec) -> Doc:
    period = spec.get("period", kind=str)
    if period and "eyebrow" not in spec:
        spec.data["eyebrow"] = period
    doc = common(spec)
    summary = spec.get("summary", kind=str)
    blocks: list[Any] = []
    if summary and "\n\n" not in summary.strip() and not doc.lead:
        doc.lead, summary = summary.strip(), None
    compare = spec.get("compare", "last week", str)
    tiles = []
    overall = spec.get("overall", None, str, tuple(OVERALL))
    if overall:
        word, tone = OVERALL[overall]
        n_ms = len(spec.get("milestones", []) or [])
        done = sum(1 for m in (spec.data.get("milestones") or []) if isinstance(m, dict) and m.get("state") == "done")
        tiles.append(["Overall", word, f"{done} of {n_ms} milestones done" if n_ms else "", tone])
    tiles += [tile(k, it, compare) for k, it in enumerate(spec.items("kpis"))]
    if tiles:
        blocks.append({"kpis": tiles})
    if summary:
        blocks += [{"h2": "Summary"}, {"md": summary}]
    highlights = [str(x) for x in spec.get("highlights", [], list)]
    if highlights:
        blocks += [{"h2": "Highlights"}, {"md": bullets(highlights)}]

    risks = []
    for k, r in enumerate(spec.items("risks")):
        if isinstance(r, str):
            risks.append({"risk": r, "severity": "medium", "owner": "", "mitigation": ""})
            continue
        if not isinstance(r, Spec):
            raise SpecError(f"risks[{k}]: {{risk, severity, owner, mitigation}}")
        risks.append({"risk": str(r.need("risk")), "severity": r.get("severity", "medium", str, tuple(SEVERITY)),
                      "owner": str(r.get("owner", "") or ""), "mitigation": str(r.get("mitigation", "") or "")})
    if risks:
        risks.sort(key=lambda r: SEVERITY[r["severity"]])
        rows = [[r["risk"], ("**High**" if r["severity"] == "high" else r["severity"].capitalize()),
                 r["owner"], r["mitigation"]] for r in risks]
        blocks += [{"h2": "Risks"}, {"table": {"header": ["Risk", "Severity", "Owner", "Mitigation"], "rows": rows}}]

    ms = []
    for k, m in enumerate(spec.items("milestones")):
        if not isinstance(m, Spec):
            raise SpecError(f"milestones[{k}]: {{name, due, state, note}}")
        ms.append({"name": str(m.need("name")), "due": m.get("due"),
                   "state": m.need("state", str, ("done", "on-track", "at-risk", "late")), "note": m.get("note", kind=str)})
    if ms:
        counts = {s: sum(1 for m in ms if m["state"] == s) for s in ("done", "on-track", "at-risk", "late")}
        said = ", ".join(f"{n} {s.replace('-', ' ')}" for s, n in counts.items() if n)
        blocks += [{"h2": "Milestones"}, {"figure": milestones_figure(ms), "caption": f"{len(ms)} milestones: {said}."}]
    for k, f in enumerate(spec.items("figures")):
        if not isinstance(f, Spec) or "figure" not in f:
            raise SpecError(f"figures[{k}]: {{figure: chart.yaml, caption: …}}")
        blocks.append(f)
    asks = [str(x) for x in spec.get("asks", [], list)]
    if asks:
        blocks += [{"h2": "Needed from you"}, {"md": bullets(asks, True)}]
    if not blocks:
        raise SpecError("a status needs at least one of: kpis, summary, highlights, risks, milestones, asks")
    doc.blocks = blocks
    return doc
