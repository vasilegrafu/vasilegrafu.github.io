"""
A decision laid out for the person who makes it: the question, what it rests on, the options scored
against weighted criteria, each option's case for and against, a recommendation -- and what would
change it. The scorecard is worked out from the scores; a recommendation that is not the top score is
said so, not hidden.

  title:           the decision, as a heading ("Which queue carries order events")
  question:        the question the reader answers (the lead, unless `lead:` is given)
  eyebrow, lead, footer, format (html | pdf | [html, pdf]), contents, dense: as every document
  context:         Markdown: why this is being decided now, what it rests on
  criteria:        name: weight, in order of importance -- or [{name, weight, note}]; weights are
                   relative (3 counts three times 1)
  options:         [{name, summary, scores: {criterion: 1-5}, pros: [...], cons: [...], effort, cost}]
                   every option scores every criterion, 1 (poor) to 5 (strong)
  recommendation:  {option, why}: the option recommended (one of the options' names) and why
  change_mind:     [what would change the recommendation]
  risks:           [risks of the recommended option]
  next:            [next steps, in order, once decided]
  decide_by:       when the decision is needed;  owner: who makes it
"""
from __future__ import annotations

from typing import Any

from .. import Spec, SpecError
from ..document import Doc, common

PURPOSE = "options scored against weighted criteria, a recommendation, and what would change it"
GROUP = "documents"
OUTPUT = "html|pdf"


def criteria_of(spec: Spec) -> list[tuple[str, float, str | None]]:
    raw = spec.get("criteria")
    out: list[tuple[str, float, str | None]] = []
    if isinstance(raw, dict):
        for name, w in spec.mapping("criteria"):
            if isinstance(w, Spec):
                out.append((name, float(w.num("weight", 1) or 1), w.get("note", kind=str)))
            elif isinstance(w, (int, float)) and not isinstance(w, bool):
                out.append((name, float(w), None))
            else:
                raise SpecError(f"criteria.{name}: a weight (a number) or {{weight, note}}")
    elif isinstance(raw, list):
        for k, c in enumerate(spec.items("criteria")):
            if isinstance(c, str):
                out.append((c, 1.0, None))
            elif isinstance(c, Spec):
                out.append((str(c.need("name")), float(c.num("weight", 1) or 1), c.get("note", kind=str)))
            else:
                raise SpecError(f"criteria[{k}]: a name, or {{name, weight, note}}")
    if not out:
        raise SpecError("`criteria` is required: name: weight, one per criterion")
    if any(w <= 0 for _, w, _ in out):
        raise SpecError("criteria: every weight is above 0")
    return out


def bullets(items: list[Any], numbered: bool = False) -> str:
    return "\n".join(f"{k + 1}. {x}" if numbered else f"- {x}" for k, x in enumerate(items))


def document(spec: Spec) -> Doc:
    doc = common(spec)
    question = str(spec.need("question"))
    if not doc.lead:
        doc.lead = question
    criteria = criteria_of(spec)
    names_c = [c[0] for c in criteria]
    total_w = sum(w for _, w, _ in criteria)
    options = []
    for k, o in enumerate(spec.items("options")):
        if not isinstance(o, Spec):
            raise SpecError(f"options[{k}]: {{name, summary, scores, pros, cons}}")
        name = str(o.need("name"))
        scores = o.get("scores", {}, dict)
        for c in scores:
            if c not in names_c:
                import difflib
                near = difflib.get_close_matches(str(c), names_c, n=1)
                raise SpecError(f"{o.where}.scores: no criterion `{c}`" + (f" -- did you mean `{near[0]}`?" if near else ""))
        missing = [c for c in names_c if c not in scores]
        if missing:
            raise SpecError(f"{o.where}.scores: no score for {', '.join(missing)}")
        for c, v in scores.items():
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not 1 <= v <= 5:
                raise SpecError(f"{o.where}.scores.{c}: a score from 1 to 5, not {v!r}")
        weighted = sum(scores[c] * w for c, w, _ in criteria) / total_w
        options.append({"name": name, "summary": o.get("summary", kind=str), "scores": scores, "total": weighted,
                        "pros": [str(x) for x in o.get("pros", [], list)], "cons": [str(x) for x in o.get("cons", [], list)],
                        "effort": o.get("effort"), "cost": o.get("cost")})
    if len(options) < 2:
        raise SpecError("`options`: a decision compares at least two")
    by = {o["name"]: o for o in options}
    rec = spec.sub("recommendation")
    if rec is None:
        raise SpecError("`recommendation` is required: {option, why}")
    chosen = str(rec.need("option"))
    if chosen not in by:
        raise SpecError(f"recommendation.option: no option `{chosen}`; there are: {', '.join(by)}")
    why = str(rec.get("why", ""))
    ranked = sorted(options, key=lambda o: -o["total"])
    top = ranked[0]["total"]
    runner = next(o for o in ranked if o["name"] != chosen)

    blocks: list[Any] = []
    tiles = [["Recommended", chosen, f"{by[chosen]['total']:.1f} of 5, weighted", "good"],
             ["Runner-up", runner["name"], f"{runner['total']:.1f} of 5", "neutral"]]
    if "decide_by" in spec or "owner" in spec:
        tiles.append(["Decide by", str(spec.get("decide_by", "—")), str(spec.get("owner", "") or ""), "info"])
    blocks.append({"kpis": tiles})
    context = spec.get("context", kind=str)
    if context:
        blocks += [{"h2": "Context"}, {"md": context}]

    blocks.append({"h2": "How the options score"})
    header = ["Criterion", "Weight"] + [o["name"] for o in options]
    rows = []
    for c, w, note in criteria:
        best = max(o["scores"][c] for o in options)
        rows.append([c + (f" ({note})" if note else ""), f"× {w:g}"]
                    + [(f"**{o['scores'][c]:g}**" if o["scores"][c] == best else f"{o['scores'][c]:g}") for o in options])
    rows.append(["**Weighted score**", ""] + [(f"**{o['total']:.1f}**" if abs(o["total"] - top) < 1e-9 else f"{o['total']:.1f}")
                                             for o in options])
    blocks.append({"table": {"header": header, "rows": rows, "numeric": list(range(1, len(header)))},
                   "caption": "Each criterion is scored 1 (poor) to 5 (strong); the best in each row is in bold. "
                              "The weighted score is out of 5."})
    blocks.append({"figure": chart(options, chosen),
                   "caption": "The weighted scores; the recommended option in colour."})

    blocks.append({"h2": "The options"})
    for o in options:
        blocks.append({"h3": o["name"] + (" (recommended)" if o["name"] == chosen else "")})
        facts = " · ".join(f"*{label}:* {o[key]}" for key, label in (("effort", "Effort"), ("cost", "Cost")) if o[key])
        if o["summary"] or facts:
            blocks.append({"p": " ".join(x for x in (o["summary"], f"({facts})" if facts and o["summary"] else facts) if x)})
        if o["pros"] or o["cons"]:
            blocks.append({"columns": [[{"md": "**For**\n\n" + (bullets(o["pros"]) or "- nothing noted")}],
                                       [{"md": "**Against**\n\n" + (bullets(o["cons"]) or "- nothing noted")}]]})

    blocks.append({"h2": "Recommendation"})
    blocks.append({"callout": why or f"{chosen} scores {by[chosen]['total']:.1f} of 5.", "title": f"We recommend {chosen}",
                   "tone": "good"})
    if by[chosen]["total"] < top - 1e-9:
        leader = ranked[0]
        blocks.append({"callout": f"{leader['name']} scores {leader['total']:.1f} against {by[chosen]['total']:.1f} for "
                                  f"{chosen}: the recommendation rests on more than the scorecard, as said above.",
                       "title": "Not the highest score", "tone": "warn"})
    for key, title, numbered in (("change_mind", "What would change our mind", False), ("risks", "Risks", False),
                                 ("next", "Next steps", True)):
        items = [str(x) for x in spec.get(key, [], list)]
        if items:
            blocks += [{"h2": title}, {"md": bullets(items, numbered)}]
    doc.blocks = blocks
    return doc


def chart(options: list[dict[str, Any]], chosen: str) -> Any:
    from ...chartstyle import C, plt
    n = len(options)
    fig, ax = plt.subplots(figsize=(6.4, 0.42 * n + 0.75))
    totals = [o["total"] for o in options]
    colours = [C["blue"] if o["name"] == chosen else C["slate"] for o in options]
    bars = ax.barh(range(n), totals, 0.58, color=colours)
    ax.set_yticks(range(n), [o["name"] for o in options])
    ax.invert_yaxis()
    ax.set_xlim(0, 5.5)
    ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    ax.bar_label(bars, labels=[f"{t:.1f}" for t in totals], padding=4, fontsize=9, color=C["ink"])
    top = max(options, key=lambda o: o["total"])
    ax.set_title(f"{chosen} scores highest" if top["name"] == chosen or top["total"] == next(
        o["total"] for o in options if o["name"] == chosen) else f"{top['name']} scores highest; {chosen} is recommended")
    return fig
