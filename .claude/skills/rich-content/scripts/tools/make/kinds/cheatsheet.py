"""
A cheat sheet: a dense reference to keep beside the keyboard -- sections of terms or commands, each with
what it does, and a snippet where one says it better. As a PDF it is set small in two or three
columns; as a page, its sections are cards in a grid that reflows to the width of the screen.

  title:     what it covers ("Git, the commands of a working week")
  sections:  [{title, items, md, code, lang}]
             items: [[term, what it does], …] -- or [{term, text, code, lang}]; `text` is Markdown
             inline, `code` a snippet shown under it
             md: Markdown after the items;  code + lang: a snippet closing the section
  terms:     code (the default: terms set as code -- commands, functions) | text (words, set bold)
  columns:   2 (the default) or 3: the PDF's columns
  eyebrow, lead, footer, paper: as every document;  format: pdf (the default) | html | [pdf, html]
"""
from __future__ import annotations

import html as H
from pathlib import Path
from typing import Any

from .. import Spec, SpecError
from ..document import Doc, Raw, common, inline, write

PURPOSE = "a dense reference: sections of terms or commands, in columns on paper, in cards on a page"
GROUP = "documents"
OUTPUT = "pdf|html"


def sections_of(spec: Spec) -> list[dict[str, Any]]:
    out = []
    for k, s in enumerate(spec.items("sections")):
        if not isinstance(s, Spec):
            raise SpecError(f"sections[{k}]: {{title, items}}")
        items = []
        for j, it in enumerate(s.items("items")):
            if isinstance(it, list) and len(it) >= 2 and all(isinstance(x, (str, int, float)) for x in it):
                # YAML splits an unquoted text at its commas: the rest of the list is the text
                items.append({"term": str(it[0]), "text": ", ".join(str(x) for x in it[1:]), "code": None,
                              "lang": None})
            elif isinstance(it, Spec):
                items.append({"term": str(it.need("term")), "text": str(it.get("text", "") or ""),
                              "code": it.get("code", kind=str), "lang": it.get("lang", kind=str)})
            else:
                raise SpecError(f"{s.where}.items[{j}]: [term, what it does] or {{term, text, code}}; got {it!r}")
        out.append({"title": str(s.need("title")), "items": items, "md": s.get("md", kind=str),
                    "code": s.get("code", kind=str), "lang": s.get("lang", kind=str)})
    if not out:
        raise SpecError("`sections` is required: [{title, items: [[term, what it does], …]}]")
    return out


def _term_md(term: str, as_code: bool) -> str:
    if as_code:
        ticks = "``" if "`" in term else "`"
        pad = " " if "`" in term else ""
        return f"{ticks}{pad}{term}{pad}{ticks}"
    return f"**{term}**"


def pdf_blocks(sections: list[dict[str, Any]], as_code: bool, cols: int) -> list[Any]:
    """The sections in `cols` columns, each section whole in one, the columns about as long as each
    other (Typst fills one column before it starts the next, which leaves a short sheet in one)."""
    per_line = 100 / cols                                # characters a line of a column holds, roughly

    def weight(s: dict[str, Any]) -> float:
        lines = 2.4
        for it in s["items"]:
            lines += 1 + len(it["term"] + it["text"]) / per_line
            if it["code"]:
                lines += it["code"].count("\n") + 2
        lines += len(s["md"] or "") / per_line
        return lines + (s["code"].count("\n") + 2 if s["code"] else 0)

    total = sum(weight(s) for s in sections)
    columns: list[list[Any]] = [[] for _ in range(cols)]
    filled, k = 0.0, 0
    for s in sections:                                   # in order, moving on once a column has its share
        if k < cols - 1 and filled > 0 and filled + weight(s) / 2 > total * (k + 1) / cols:
            k += 1
        columns[k] += section_blocks(s, as_code)
        filled += weight(s)
    return [{"columns": [c for c in columns if c]}]


def section_blocks(s: dict[str, Any], as_code: bool) -> list[Any]:
    blocks: list[Any] = [{"h2": s["title"]}]
    lines = [f"- {_term_md(it['term'], as_code)} {('— ' + it['text']) if it['text'] else ''}".rstrip()
             for it in s["items"]]
    if lines:
        blocks.append({"md": "\n".join(lines)})
    for it in s["items"]:
        if it["code"]:
            blocks.append({"code": it["code"], "lang": it["lang"]} if it["lang"] else {"code": it["code"]})
    if s["md"]:
        blocks.append({"md": s["md"]})
    if s["code"]:
        blocks.append({"code": s["code"], "lang": s["lang"]} if s["lang"] else {"code": s["code"]})
    return blocks


def html_blocks(sections: list[dict[str, Any]], as_code: bool) -> list[Any]:
    from markdown_it import MarkdownIt

    from ...code import highlight
    md = MarkdownIt("commonmark", {"html": False, "highlight": lambda src, lang, _a: highlight(src, lang or None)})
    md.enable("table")
    cards = []
    for s in sections:
        rows = []
        for it in s["items"]:
            term = f"<code>{H.escape(it['term'])}</code>" if as_code else f"<strong>{H.escape(it['term'])}</strong>"
            text = inline(it["text"]) if it["text"] else ""
            snippet = highlight(it["code"].rstrip("\n"), it["lang"]) if it["code"] else ""
            rows.append(f'<div style="margin:0 0 9px;font:400 14.5px/1.5 var(--label)">{term}'
                        f'{"<br>" if text else ""}<span style="color:var(--ink)">{text}</span>{snippet}</div>')
        extra = (f'<div class="md" style="font:400 14.5px/1.5 var(--label)">{md.render(s["md"])}</div>'
                 if s["md"] else "")
        extra += highlight(s["code"].rstrip("\n"), s["lang"]) if s["code"] else ""
        cards.append(f'<section class="card" style="padding:14px 16px;min-width:0">'
                     f'<h3 style="font:600 16px/1.3 var(--label);color:var(--heading);margin:0 0 10px">'
                     f'{H.escape(s["title"])}</h3>{"".join(rows)}{extra}</section>')
    # a snippet wraps in its card rather than scrolling inside a narrow one
    cards = [c.replace('<pre class="code">', '<pre class="code" style="white-space:pre-wrap;font-size:13px">')
             for c in cards]
    grid = ('<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));'
            'gap:14px;margin:8px 0 22px;align-items:start">' + "".join(cards) + "</div>")
    return [{"html": Raw(grid)}]


def build(spec: Spec, out: Path) -> list[Path]:
    doc = common(spec, default="pdf", allowed=("pdf", "html"))
    formats = doc.formats(spec)
    as_code = spec.get("terms", "code", str, ("code", "text")) == "code"
    cols = spec.get("columns", 2, int, (2, 3))
    sections = sections_of(spec)
    written = []
    if "pdf" in formats:
        paper = Doc(**{**doc.__dict__})
        paper.blocks = pdf_blocks(sections, as_code, cols)
        paper.dense = True
        size = "8.6pt" if cols == 3 else "9pt"
        paper.extra_typst = (f"#set text(size: {size})\n#set par(justify: false, spacing: 0.7em)\n"
                             "#set list(spacing: 0.55em, tight: true)\n")
        written += write(paper, out, ["pdf"], spec)
    if "html" in formats:
        page = Doc(**{**doc.__dict__})
        page.blocks = html_blocks(sections, as_code)
        written += write(page, out, ["html"], spec)
    return written
