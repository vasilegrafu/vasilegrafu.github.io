"""
A page of everything of someone else's a checkout uses, under what licence, and whether it may be used: what
the checkout's own third_party.py finds, read by running its build() -- the same reading its --check makes,
so the page and the check never disagree. Its sections become the page's, its verdicts the tiles and a
count by source, its exceptions callouts with their reasons.

  script:   the licence script, relative to the spec (third_party.py at the top of the checkout by default)
  only:     all (the default) lists every row; problems lists only the rows not allowed outright -- a short
            page when the long tables are known to be fine
  title, eyebrow, lead, footer, format (html | pdf | [html, pdf]): as for the doc kind ("Third-party
            licences" by default)

It reads what is installed in the venv that runs tools.make and what git tracks, so the page moves when a
package is added or updated: make it again then (and --check calls it stale until then).
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
from collections import Counter
from pathlib import Path

from .. import Spec, SpecError
from ..document import Doc, common

PURPOSE = "the licences of everything a checkout uses, from its third_party.py: tiles, tables, exceptions"
GROUP = "from the repository"
OUTPUT = "html|pdf"

VERDICTS = {"ok": "allowed", "excused": "excused", "NOT ALLOWED": "not allowed"}


def script_of(spec: Spec) -> Path:
    given = spec.path("script")
    if given:
        return given
    r = subprocess.run(["git", "-C", str(spec.base), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    top = Path(r.stdout.strip()) if r.returncode == 0 else spec.base
    found = top / "third_party.py"
    if not found.exists():
        raise SpecError(f"script: no third_party.py at {top}; name it with script:")
    return found


def sections(text: str) -> list[dict]:
    """The notices as sections: heading, level, its paragraphs, its tables (header, rows)."""
    out: list[dict] = []
    cur: dict | None = None
    para: list[str] = []
    table: list[list[str]] | None = None

    def cells(line: str) -> list[str]:
        parts = re.split(r"(?<!\\)\|", line.strip())[1:-1]
        return [p.strip().replace("\\|", "|") for p in parts]

    def flush() -> None:
        nonlocal para, table
        if cur is not None and para:
            cur["text"].append(" ".join(para))
        if cur is not None and table:
            cur["tables"].append((table[0], table[2:]))
        para, table = [], None

    for line in text.splitlines():
        m = re.match(r"^(#{1,3}) (.*)$", line)
        if m:
            flush()
            cur = {"level": len(m.group(1)), "title": m.group(2), "text": [], "tables": []}
            out.append(cur)
        elif line.startswith("|"):
            if para:
                flush()
            table = (table or []) + [cells(line)]
        elif not line.strip():
            flush()
        elif table is None:
            para.append(line.strip())
    flush()
    return out


def document(spec: Spec) -> Doc:
    script = script_of(spec)
    only = spec.get("only", "all", str, ("all", "problems"))
    load = importlib.util.spec_from_file_location("_third_party_for_licences", script)
    if load is None or load.loader is None:
        raise SpecError(f"script: cannot load {script}")
    module = importlib.util.module_from_spec(load)
    load.loader.exec_module(module)
    if not hasattr(module, "build"):
        raise SpecError(f"script: {script.name} has no build(); it is not the licence script")
    text, ledger = module.build()
    spec.data.setdefault("title", "Third-party licences")
    doc = common(spec)
    secs = [s for s in sections(text) if s["level"] >= 2]

    # verdicts by source: each section's tables whose last column is the verdict
    count: dict[str, Counter] = {}
    for s in secs:
        if s["title"] == "Exceptions":
            continue
        source = s["title"].split(":")[0].replace("Compiled into wheels", "Wheels (SBOM)")
        for header, rows in s["tables"]:
            if header and header[-1] == "":
                for r in rows:
                    count.setdefault(source, Counter())[VERDICTS.get(r[-1], r[-1])] += 1
    total = Counter()
    for c in count.values():
        total.update(c)
    rows_all = total["allowed"] + total["excused"] + total["not allowed"]      # the rows judged
    unjudged = sum(total.values()) - rows_all          # e.g. a wheel's optional part not in this build
    if doc.eyebrow is None:
        doc.eyebrow = f"From {script.name}"
    if doc.lead is None:
        doc.lead = (f"Everything of someone else's this checkout uses, as `{script.name}` finds it: {rows_all:,} "
                    f"rows in {len(count)} sources. Allowed is a permissive licence; anything else is excused "
                    "for a reason given below, or not allowed.")
    blocks: list[dict] = [
        {"kpis": [["Rows checked", f"{rows_all:,}", f"in {len(count)} sources"
                   + (f"; {unjudged} more not in this build" if unjudged else ""), "neutral"],
                  ["Allowed", f"{total['allowed']:,}", "a permissive licence", "good"],
                  ["Excused", f"{total['excused']:,}", f"by {len(ledger.excused)} exceptions", "warn" if total["excused"] else "good"],
                  ["Not allowed", f"{total['not allowed']:,}", "fails the check" if total["not allowed"] else "none",
                   "bad" if total["not allowed"] else "good"]]},
        {"table": {"header": ["Source", "Rows", "Allowed", "Excused", "Not allowed"],
                   "rows": [[src, str(sum(c.values())), str(c["allowed"]), str(c["excused"]), str(c["not allowed"])]
                            for src, c in count.items()],
                   "numeric": [1, 2, 3, 4]},
         "caption": "Every row the script judges, by where it comes from."},
    ]
    for p in ledger.problems:
        blocks.append({"callout": p, "title": "Not allowed", "tone": "bad"})
    exceptions = next((s for s in secs if s["title"] == "Exceptions"), None)
    if exceptions and exceptions["tables"]:
        blocks.append({"h2": "Exceptions"})
        blocks.append({"p": exceptions["text"][0] if exceptions["text"] else "What is excused, and why."})
        header, rows = exceptions["tables"][0]
        for where, what, lic, n, why in rows:
            blocks.append({"callout": f"{why} ({n} row{'s' if n != '1' else ''}, under {where}.)",
                           "title": f"{re.sub(r'`', '', what)} · {lic}", "tone": "warn"})
    for s in secs:
        if s["title"] == "Exceptions" or not s["tables"]:
            continue
        shown = []
        for header, rows in s["tables"]:
            verdict = bool(header) and header[-1] == ""
            if only == "problems":
                rows = [r for r in rows if verdict and r[-1] != "ok"]
            if not rows:
                continue
            head = list(header[:-1]) + ["Verdict"] if verdict else list(header)
            body = [list(r[:-1]) + [VERDICTS.get(r[-1], r[-1])] if verdict else list(r) for r in rows]
            numeric = [i for i, h in enumerate(head) if h in ("Packages", "Rows")]
            shown.append({"table": {"header": head, "rows": body, "numeric": numeric}})
        if not shown:
            continue
        blocks.append({("h2" if s["level"] == 2 else "h3"): s["title"].replace("`", "")})
        if s["text"]:
            blocks.append({"p": s["text"][0]})
        blocks += shown
    doc.blocks = blocks
    doc.contents = doc.contents or "contents" not in spec.data
    return doc
