"""
An architecture decision record: what was decided, in what context, between which options, and what
follows from it -- the Nygard form with MADR's drivers and options. Numbered, dated and with its
status shown, so a reader knows at once whether it still holds.

  number:      the record's number (12 -> ADR-012)
  title:       the decision, short ("Use SQS FIFO for order events")
  status:      proposed | accepted | superseded | deprecated | rejected
  date:        when it took that status;  deciders: [names or roles]
  supersedes:  "ADR-007" (or a list);  superseded_by: "ADR-019" -- shown beside the status
  context:     Markdown: the forces at play, the problem
  drivers:     [what the decision must achieve or respect]
  options:     [{name, summary, pros: [...], cons: [...]}] -- the ones considered
  decision:    {option, why} -- the option chosen (one of the options' names) and why;
               or Markdown, when no options are listed
  consequences: {good: [...], bad: [...], neutral: [...]}
  links:       [{text, url}] or ["text: url"] -- related records, tickets, documents
  eyebrow, lead, footer, format (pdf by default | html | [html, pdf]): as every document
"""
from __future__ import annotations

from typing import Any

from .. import Spec, SpecError
from ..document import Doc, common

PURPOSE = "an architecture decision record: context, drivers, options, decision, consequences"
GROUP = "documents"
OUTPUT = "pdf|html"

STATUS = {"proposed": "info", "accepted": "good", "superseded": "warn", "deprecated": "bad", "rejected": "bad"}


def bullets(items: list[Any]) -> str:
    return "\n".join(f"- {x}" for x in items)


def links_of(spec: Spec) -> list[str]:
    out = []
    for k, item in enumerate(spec.items("links")):
        if isinstance(item, Spec):
            text, url = str(item.need("text")), str(item.need("url"))
        elif isinstance(item, str) and ": " in item:
            text, url = item.split(": ", 1)
        else:
            raise SpecError(f"links[{k}]: {{text, url}} or \"text: url\"")
        out.append(f"[{text.strip()}](<{url.strip()}>)")
    return out


def document(spec: Spec) -> Doc:
    number = spec.need("number", int)
    spec.data.setdefault("eyebrow", "Architecture decision record")
    doc = common(spec, default="pdf")
    doc.title = f"ADR-{number:03d}: {doc.title}"
    status = spec.need("status", str, tuple(STATUS))
    date = spec.get("date")
    deciders = [str(x) for x in spec.get("deciders", [], list)]

    def refs(key: str) -> list[str]:
        v = spec.get(key)
        return [] if v is None else [str(x) for x in (v if isinstance(v, list) else [v])]
    supersedes, superseded_by = refs("supersedes"), refs("superseded_by")
    if status == "superseded" and not superseded_by:
        raise SpecError("status superseded: say by which record, with `superseded_by`")

    note = f"since {date}" if date else ""
    if superseded_by:
        note = f"by {', '.join(superseded_by)}" + (f", {date}" if date else "")
    tiles = [["Status", status.capitalize(), note, STATUS[status]]]
    if supersedes:
        tiles.append(["Supersedes", ", ".join(supersedes), "no longer holds", "neutral"])
    blocks: list[Any] = [{"kpis": tiles}]
    if deciders:
        blocks.append({"p": "**Deciders:** " + ", ".join(deciders)})

    context = spec.need("context", str)
    blocks += [{"h2": "Context"}, {"md": context}]
    drivers = [str(x) for x in spec.get("drivers", [], list)]
    if drivers:
        blocks += [{"h2": "Decision drivers"}, {"md": bullets(drivers)}]

    options = []
    for k, o in enumerate(spec.items("options")):
        if not isinstance(o, Spec):
            raise SpecError(f"options[{k}]: {{name, summary, pros, cons}}")
        options.append({"name": str(o.need("name")), "summary": o.get("summary", kind=str),
                        "pros": [str(x) for x in o.get("pros", [], list)], "cons": [str(x) for x in o.get("cons", [], list)]})
    names = [o["name"] for o in options]

    raw = spec.get("decision")
    chosen, why = None, ""
    if isinstance(raw, dict):
        d = spec.sub("decision")
        assert d is not None
        chosen, why = str(d.need("option")), str(d.get("why", ""))
        if names and chosen not in names:
            raise SpecError(f"decision.option: no option `{chosen}`; there are: {', '.join(names)}")
    elif isinstance(raw, str):
        why = raw
    else:
        raise SpecError("`decision` is required: {option, why} -- or Markdown")

    if options:
        blocks.append({"h2": "Considered options"})
        blocks.append({"md": "\n".join(f"{k + 1}. {o['name']}" + (" (chosen)" if o["name"] == chosen else "")
                                       for k, o in enumerate(options))})
        for o in options:
            blocks.append({"h3": o["name"] + (" (chosen)" if o["name"] == chosen else "")})
            if o["summary"]:
                blocks.append({"p": o["summary"]})
            if o["pros"] or o["cons"]:
                blocks.append({"columns": [[{"md": "**Good**\n\n" + (bullets(o["pros"]) or "- nothing noted")}],
                                           [{"md": "**Bad**\n\n" + (bullets(o["cons"]) or "- nothing noted")}]]})

    blocks.append({"h2": "Decision"})
    title = f"Chosen: {chosen}" if chosen else "Decided"
    tone = {"accepted": "good", "proposed": "info"}.get(status, "warn")
    if status == "proposed":
        title = f"Proposed: {chosen}" if chosen else "Proposed"
    blocks.append({"callout": why or (chosen or ""), "title": title, "tone": tone})

    cons = spec.sub("consequences")
    if cons is not None:
        good = [str(x) for x in cons.get("good", [], list)]
        bad = [str(x) for x in cons.get("bad", [], list)]
        neutral = [str(x) for x in cons.get("neutral", [], list)]
        blocks.append({"h2": "Consequences"})
        cols = []
        if good:
            cols.append([{"md": "**Good, because**\n\n" + bullets(good)}])
        if bad:
            cols.append([{"md": "**Bad, because**\n\n" + bullets(bad)}])
        if len(cols) == 2:
            blocks.append({"columns": cols})
        elif cols:
            blocks.append(cols[0][0])
        if neutral:
            blocks.append({"md": "**Neither, but worth knowing**\n\n" + bullets(neutral)})
    links = links_of(spec)
    if links:
        blocks += [{"h2": "Links"}, {"md": bullets(links)}]
    doc.blocks = blocks
    return doc
