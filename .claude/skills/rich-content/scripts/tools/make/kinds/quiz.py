"""
A quiz on paper -- or on a page -- from questions in the Trainings model (ai-workbench-learning,
Trainings/QUESTION-STANDARD.md, section 2): every one of the eleven formats set so it can be answered
with a pen, then an answer key on a new page, with why each answer is right and what to remember.

  title:      the quiz's title;  eyebrow:, lead:, footer: as a document's
  format:     pdf (the default) | html (answers folded under each question) | [pdf, html]
  key:        false leaves the answer key out (true by default)
  dense:      true tightens the PDF;  paper: a4 (the default) | us-letter | a5
  questions:  the questions, written here, each in the Trainings model:
              id, lesson, level (beginner | intermediate | advanced | expert), type,
              format, material, q (Markdown), takeaway, why -- and the format's own fields:
                choice-one, choice-many   options: [{t, ok: true, why}]
                short-answer              accept: [...], compare, traps: [{text, why}]
                numeric                   answer, unit, tolerance: {kind: absolute | relative, value}
                spot                      faulty: [part numbers], notes: {number: why}
                fill-gaps                 gaps: [{choices, answer, why}] -- {{1}}, {{2}} in the material
                order                     items (in the right order; shown shuffled), orderBy
                classify                  groups: [{name, items}]
                match                     pairs: [[left, right]]
                free-response             model (Markdown), points: [...]
                case                      scenario, steps: [questions of the other formats]
              material: {kind: none | code (lang, text) | text (text) | list (items) |
                         dialogue (turns: [{who, says}]) | table (columns, rows)}
  from:       a Trainings question file (questions/chNN.js) instead -- read with Node
  lessons:, levels:, ids:   keep only these questions (of either)

The order, classify and match formats are shuffled on paper, the same way each time (by the
question's id), and the key says the right order by the letters shown.
"""
from __future__ import annotations

import html as H
from pathlib import Path

from .. import Spec
from ..document import TYPST_HEAD, Typst, compile_typst, inline, ts, typst_work
from ._questions import TYPST_HELPERS, Paper, Web, info, load

PURPOSE = "a quiz to print (or a page): questions in the eleven Trainings formats, and an answer key"
GROUP = "learning"
OUTPUT = "pdf|html"


def build(spec: Spec, out: Path) -> list[Path]:
    title = str(spec.get("title", "Quiz"))
    eyebrow, lead, footer = spec.get("eyebrow", kind=str), spec.get("lead", kind=str), spec.get("footer", kind=str)
    fmt = spec.get("format", "pdf")
    formats = fmt if isinstance(fmt, list) else [fmt]
    for f in formats:
        if f not in ("pdf", "html"):
            from .. import SpecError
            raise SpecError(f"format: {f!r} is not one of: pdf, html")
    with_key = spec.get("key", True, bool)
    dense = spec.get("dense", False, bool)
    paper = spec.get("paper", "a4", str, ("a4", "us-letter", "a5"))
    qs = load(spec)
    written = []
    if "pdf" in formats:
        written.append(_pdf(qs, spec, out.with_suffix(".pdf"), title, eyebrow, lead, footer, with_key, dense, paper))
    if "html" in formats:
        written.append(_html(qs, out.with_suffix(".html"), title, eyebrow, lead, footer, with_key))
    return written


def _pdf(qs, spec: Spec, target: Path, title, eyebrow, lead, footer, with_key, dense, paper) -> Path:
    with typst_work(spec, target) as work:
        t = Typst(work, spec.base)
        p = Paper(t)
        src = [TYPST_HEAD.format(title=ts(title), eyebrow=ts(eyebrow) if eyebrow else "none",
                                 footer=ts(footer) if footer else "none", dense="true" if dense else "false",
                                 paper=ts(paper)), TYPST_HELPERS]
        if lead:
            src.append(f"#block(below: 1em, text(size: 1.06em, fill: colour(\"muted\"), {t.md(lead)}))")
        for n, q in enumerate(qs, 1):                     # a question kept on one page; a case may break
            src.append(f"#block(width: 100%, above: 2em, below: 0.6em, breakable: {'true' if q['format'] == 'case' else 'false'})[\n"
                       f"#qhead({ts(str(n))}, {ts(info(q))})\n\n{p.body(q)}\n]")
        if with_key:
            src.append("#pagebreak()\n#heading(level: 2, \"Answer key\")")
            for n, q in enumerate(qs, 1):
                src.append(f"#khead({ts(str(n))})")
                src.append(p.key(q))
        return compile_typst(work, "\n\n".join(src) + "\n", target)


def _html(qs, target: Path, title, eyebrow, lead, footer, with_key) -> Path:
    from ...html import Page
    w = Web()
    page = Page(title, eyebrow=eyebrow, lead=inline(lead) if lead else None, contents=len(qs) > 3)
    for n, q in enumerate(qs, 1):
        page.h2(f"Question {n}")
        about = info(q)
        page.html((f'<p class="caption">{H.escape(about)}</p>' if about else "") + w.body(q))
        if with_key:
            page.html(f'<details class="card" style="padding:10px 14px;margin:12px 0 4px"><summary>'
                      f'<strong>Answer</strong></summary>{w.key(q)}</details>')
    return page.save(target, footer=H.escape(footer) if footer else None)
