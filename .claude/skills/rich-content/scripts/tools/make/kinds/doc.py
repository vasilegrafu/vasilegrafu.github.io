"""
A document -- a report, a design note, a handout, a one-pager -- as an HTML page, a PDF or both, from
blocks written in the spec, a Markdown file, or both. Figures are other specs (a file, or inline),
drawn as the document is made.

  title:     the title (from a Markdown source's first `# heading` when not given)
  eyebrow:   the small line above it;  lead: a paragraph under it (Markdown inline)
  footer:    the line at the foot of a page or every PDF page
  format:    html (the default) | pdf | [html, pdf]
  template:  page (the default) | report (a contents bar on the page) | one-pager (dense: a PDF
             that must hold a lot on one page)
  contents:  true gives the page a contents bar of its h2s;  dense: true tightens a PDF
  source:    a Markdown file whose text comes first (before any blocks)
  blocks:    the body, one block each -- see the blocks below

Blocks (each a mapping whose first key says what it is):

  h2: text | h3: text              a heading
  p: text                          a paragraph; Markdown inline (**bold**, `code`, [links](…))
  md: text | md: notes.md          Markdown: paragraphs, lists, tables, code, images
  kpis: [[label, value, note, tone], …]     stat tiles; tone good | warn | bad | info | neutral
  callout: text, title:, tone:     an aside; tone info | good | warn | bad
  table: {header, rows, numeric: [column numbers]} -- or table: data.csv, columns:, decimals:
  figure: chart.yaml | {make: …} | drawing.svg, caption:, width: 80% (PDF)
  row: [{figure: …, caption: …}, …]          figures side by side
  columns: [[blocks], [blocks]]    blocks side by side
  code: text | code: file.py, lang:, caption:
  image: shot.webp, caption:, alt:
  qr: https://…, caption:
  pagebreak: true                  (PDF) the next block starts a page
  page only: steps: [{figure, title, text}] · chat: [[you|them, text]], you:, them: ·
             annotated: shot.webp, marks: [[x, y, text]] · diff: {before, after}, labels: ·
             cards: [[href, title, text]], kicker: [...]
"""
from __future__ import annotations

import re

from .. import Spec, SpecError
from ..document import Doc, common

PURPOSE = "a page or PDF from blocks and Markdown: a report, a design note, a handout, a one-pager"
GROUP = "documents"
OUTPUT = "html|pdf"


def document(spec: Spec) -> Doc:
    source = spec.path("source")
    text = source.read_text(encoding="utf-8") if source else ""
    if "title" not in spec:
        first = re.match(r"\s*#\s+(.+?)\s*\n", text)
        if not first:
            raise SpecError("`title` is required (or a `source` whose first line is a `# heading`)")
        spec.data["title"], text = first.group(1), text[first.end():]
    template = spec.get("template", "page", str, ("page", "report", "one-pager"))
    doc = common(spec, default="pdf" if template == "one-pager" else "html")
    if template == "report" and "contents" not in spec:
        doc.contents = True
    if template == "one-pager" and "dense" not in spec:
        doc.dense = True
    blocks: list = []
    if text.strip():
        blocks.append({"md": text})
    blocks += spec.items("blocks")
    if not blocks:
        raise SpecError("a document needs `blocks` or a `source`")
    doc.blocks = [b if isinstance(b, Spec) else spec.wrap(b, ".source") for b in blocks]
    if source:
        for b in doc.blocks:                                 # a source's images are relative to it
            if b.where == "source":
                b.base = source.parent
    return doc
