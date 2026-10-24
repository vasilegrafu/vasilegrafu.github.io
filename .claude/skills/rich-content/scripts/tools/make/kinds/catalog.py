"""
A page of every kind tools.make knows: what each is for, its fields, its example spec and what that
spec makes -- a figure shown as it is, a PDF by its first page, a page by a link. It is written from
the kinds and the examples as they are, so it is made after them (--all makes it last).

  examples:  the folder of example specs (examples/make by default, beside the kit)
  title:     the page's title
  fields:    true shows each kind's field reference under its example (folded)
"""
from __future__ import annotations

import html as H
import inspect
import os
from pathlib import Path

from .. import EXAMPLES, GROUPS, Spec, SpecError, all_kinds, read
from ..document import inline

PURPOSE = "a page of every kind: its purpose, its example spec and what it makes"
GROUP = "from the repository"
OUTPUT = "html"


def build(spec: Spec, out: Path) -> list[Path]:
    from ...html import Page
    folder = spec.path("examples") or EXAMPLES
    title = spec.get("title", "What tools.make can make", str)
    fields = spec.get("fields", True, bool)
    target = out.with_suffix(".html")
    # links are made relative to where the page is kept (where --check writes is a temporary folder)
    home = (spec.base / str(spec.data.get("out") or "catalog")).resolve().parent
    specs = {}
    for p in sorted(folder.glob("*.y*ml")):
        try:
            specs.setdefault(read(p)["make"], []).append(p)
        except SpecError:
            continue
    kinds = all_kinds()
    page = Page(title, eyebrow="rich-content · tools.make",
                lead=inline(f"{len(kinds)} kinds. A spec of a few lines names one; "
                            "`python -m tools.make spec.yaml` writes the file beside it, checked as everything "
                            "the kit makes is. `--schema KIND` prints a kind's fields and its example."),
                contents=True)
    for group in GROUPS:
        rows = [(n, m) for n, m in kinds.items() if m.GROUP == group]
        if not rows:
            continue
        page.h2(group[0].upper() + group[1:])
        page.table(["Kind", "Writes", "For"],
                   [[f"<code>{n}</code>", H.escape(m.OUTPUT), H.escape(m.PURPOSE)] for n, m in rows])
        for n, m in rows:
            page.html(f'<h3 id="kind-{n}">{H.escape(n)}</h3>')
            page.p(H.escape(m.PURPOSE[0].upper() + m.PURPOSE[1:]) + ".")
            for p in specs.get(n, []):
                src = p.read_text(encoding="utf-8")
                rel = os.path.relpath(p, home).replace(os.sep, "/")
                page.code(src.rstrip("\n"), "yaml", f'<a href="{H.escape(rel)}">{H.escape(p.name)}</a>, '
                                                   f"{len(src.splitlines())} lines")
                _show(page, p, target, home)
            if fields:
                doc = inspect.cleandoc(m.__doc__ or "")
                page.html(f'<details class="card fields"><summary>Fields of <code>{H.escape(n)}</code></summary>'
                          f'<pre class="code">{H.escape(doc)}</pre></details>')
    page.html("<style>details.fields{margin:10px 0 26px;padding:10px 14px}details.fields pre{white-space:pre-wrap;"
              "font-size:12.5px;margin:10px 0 0}details.fields summary{cursor:pointer;font:600 13px var(--label)}</style>")
    return [page.save(target, footer="Written by tools.make from its kinds and their examples")]


def _show(page, spec_path: Path, target: Path, home: Path) -> None:
    """What the example made: its SVG, its PDF's first page, or a link to its page."""
    data = read(spec_path)
    stem = (spec_path.parent / data["out"]).with_suffix("") if data.get("out") else spec_path.with_suffix("")
    svg, pdf, html_ = stem.with_suffix(".svg"), stem.with_suffix(".pdf"), stem.with_suffix(".html")
    if svg.exists():
        page.figure(svg, f"What <code>{H.escape(spec_path.name)}</code> makes.")
    if pdf.exists():
        shot = _first_page(pdf)
        rel = os.path.relpath(pdf, home).replace(os.sep, "/")
        page.image(shot, f'The first page of <a href="{H.escape(rel)}">{H.escape(pdf.name)}</a>.',
                   alt=f"The first page of {pdf.name}")
    if html_.exists() and html_.resolve() != (home / target.name).resolve():
        rel = os.path.relpath(html_, home).replace(os.sep, "/")
        page.cards([(H.escape(rel), html_.name, "The page it makes: open it to see it at full size.")])
    elif stem.is_dir():
        rel = os.path.relpath(stem / "index.html", home).replace(os.sep, "/")
        page.cards([(H.escape(rel), stem.name + "/", "The pages it makes.")])


def _first_page(pdf: Path) -> Path:
    """The PDF's first page as a WebP in _preview/ (git-ignored), 900 px wide."""
    import pypdfium2 as pdfium
    from ...render import _preview_dir
    out = _preview_dir(pdf, None) / f"{pdf.stem}-catalog.webp"
    doc = pdfium.PdfDocument(str(pdf))
    try:
        page = doc[0]
        scale = 900 / page.get_width()
        img = page.render(scale=scale).to_pil()
        img.save(out, "WEBP", quality=82, method=6)
    finally:
        doc.close()
    return out
