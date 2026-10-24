"""
document -- a document as a list of blocks, written as an HTML page (tools.html.Page) or a PDF (Typst,
in the house style). Every document kind builds a Doc; the doc kind takes its blocks from the spec.

A block is a mapping whose first key says what it is:

  h2: text | h3: text              a heading
  p: text                          a paragraph; Markdown inline (**bold**, `code`, [links](…))
  md: text | md: notes.md          Markdown: paragraphs, lists, tables, code, images
  kpis: [[label, value, note, tone], …]     stat tiles; tone good | warn | bad | info | neutral
  callout: text, title:, tone:     an aside; tone info | good | warn | bad
  table: {header: [...], rows: [[...]], numeric: [column numbers]}  -- or table: data.csv,
         columns: [names], decimals: 1 (a file's numbers right-aligned, grouped by thousands)
  figure: other.yaml | {make: …, …} | drawing.svg, caption:, width: 80%   a figure; a spec inline
         or in a file is drawn by its kind
  row: [{figure: …, caption: …}, …]  figures side by side
  columns: [[blocks], [blocks]]    blocks side by side
  code: text | code: file.py, lang:, caption:   highlighted code
  image: shot.webp, caption:, alt:            a picture
  qr: https://…, caption:          a QR code
  pagebreak: true                  (PDF) the next block starts a page
  HTML only: steps: [{figure, title, text}] · chat: [[you|them, text]], you:, them: ·
             annotated: shot.webp, marks: [[x, y, text]] · diff: {before, after}, labels: ·
             cards: [[href, title, text]], kicker: [...]

Every block takes `caption:` where a caption makes sense. Text is Markdown, and is escaped: a spec
cannot inject HTML or Typst.
"""
from __future__ import annotations

import html as H
import re
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import Spec, SpecError, drawn, read, save_figure

BLOCKS = ("h2", "h3", "p", "md", "kpis", "callout", "table", "figure", "row", "columns", "code", "image", "qr",
          "pagebreak", "steps", "chat", "annotated", "diff", "cards", "html")
HTML_ONLY = ("steps", "chat", "annotated", "diff", "cards", "html")
TONES = ("good", "warn", "bad", "info", "neutral")


class Raw(str):
    """Markup a kind made itself, to go into a page as it is (a spec's text never is)."""


@dataclass
class Doc:
    title: str
    eyebrow: str | None = None
    lead: str | None = None                             # Markdown inline
    blocks: list[Any] = field(default_factory=list)     # Specs (from a spec) or mappings (from a kind)
    contents: bool = False
    footer: str | None = None
    dense: bool = False
    columns: int = 1                                    # a PDF's text columns
    paper: str = "a4"
    default: str = "html"
    allowed: tuple[str, ...] = ("html", "pdf")
    extra_typst: str = ""                               # set before the blocks of a PDF

    def formats(self, spec: Spec) -> list[str]:
        f = spec.get("format", self.default)
        fs = f if isinstance(f, list) else [f]
        for x in fs:
            if x not in self.allowed:
                raise SpecError(f"format: {x!r} is not one of: {', '.join(self.allowed)}")
        return fs


def common(spec: Spec, default: str = "html", allowed: tuple[str, ...] = ("html", "pdf")) -> Doc:
    """A Doc with what every document spec may say: title, eyebrow, lead, footer, contents, dense, paper."""
    return Doc(title=str(spec.need("title")), eyebrow=spec.get("eyebrow", kind=str), lead=spec.get("lead", kind=str),
               footer=spec.get("footer", kind=str), contents=spec.get("contents", False, bool),
               dense=spec.get("dense", False, bool), paper=spec.get("paper", "a4", str, ("a4", "us-letter", "a5")),
               default=default, allowed=allowed)


# ----------------------------------------------------------------------------------------------
# Reading blocks
# ----------------------------------------------------------------------------------------------
def block_of(b: Any, parent: Spec, where: str) -> tuple[str, Spec]:
    s = b if isinstance(b, Spec) else parent.wrap(b, where) if isinstance(b, dict) else None
    if s is None:
        raise SpecError(f"{parent.where}{where}: a block is a mapping, like {{p: text}} or {{h2: text}}")
    keys = [k for k in s.data if k in BLOCKS]
    if len(keys) != 1:
        first = next(iter(s.data), "")
        import difflib
        near = difflib.get_close_matches(first, BLOCKS, n=1)
        raise SpecError(f"{s.where}: a block names one of {', '.join(BLOCKS)}"
                        + (f" -- did you mean `{near[0]}`?" if near else ""))
    return keys[0], s


def text_or_file(s: Spec, key: str, suffixes: tuple[str, ...]) -> tuple[str, Path | None]:
    """A block's text, or the text of the file it names (one line ending in one of `suffixes`)."""
    v = s.get(key)
    if v is None:
        return "", None
    v = str(v)
    if "\n" not in v and v.strip().lower().endswith(suffixes):
        p = s.file(v.strip())
        return p.read_text(encoding="utf-8"), p
    return v, None


def figure_obj(s: Spec, key: str = "figure") -> Any:
    """The figure a block names: a spec file, a spec inline, or an .svg file (its path)."""
    v = s.get(key)
    if isinstance(v, (Spec, dict)):
        inner = v if isinstance(v, Spec) else s.wrap(v, f".{key}")
        if "make" not in inner and "obj" in inner:
            return inner.get("obj")
        return drawn(inner)
    if not isinstance(v, str) and v is not None and (hasattr(v, "to_svg") or hasattr(v, "savefig")):
        return v                                          # a Canvas or a figure, from a kind's own blocks
    if not isinstance(v, str):
        raise SpecError(f"{s.where}.{key}: a spec file, a spec inline ({{make: …}}) or an .svg file")
    p = s.file(v)
    if p.suffix == ".svg":
        return p
    if p.suffix in (".yaml", ".yml", ".json"):
        inner = Spec(read(p), p.name, p.parent)
        obj = drawn(inner)
        found = inner.unknown()
        if found:
            raise SpecError("\n".join(found))
        return obj
    raise SpecError(f"{s.where}.{key}: {p.name} is not a figure (.svg or a spec)")


def table_of(s: Spec) -> tuple[list[str], list[list[str]], tuple[int, ...], bool]:
    """header, rows (cells as Markdown inline), numeric columns, and whether cells are already text."""
    v = s.get("table")
    if isinstance(v, str):
        p = s.file(v)
        import pandas as pd
        df = pd.read_excel(p) if p.suffix.lower() in (".xlsx", ".xls") else pd.read_csv(p)
        cols = s.get("columns", None, list)
        if cols:
            missing = [c for c in cols if c not in df.columns]
            if missing:
                raise SpecError(f"{s.where}.columns: no column {', '.join(map(str, missing))} in {p.name}")
            df = df[cols]
        decimals = int(s.get("decimals", 1, int))
        numeric = tuple(i for i, c in enumerate(df.columns) if pd.api.types.is_numeric_dtype(df[c]))

        def cell(i: int, x: Any) -> str:
            if i in numeric and isinstance(x, float) and not x.is_integer():
                return f"{x:,.{decimals}f}"
            if i in numeric:
                return f"{x:,.0f}" if isinstance(x, (int, float)) else str(x)
            return str(x)
        rows = [[cell(i, x) for i, x in enumerate(r)] for r in df.itertuples(index=False)]
        return [str(c) for c in df.columns], rows, numeric, True
    t = v if isinstance(v, Spec) else s.wrap(v, ".table") if isinstance(v, dict) else None
    if t is None:
        raise SpecError(f"{s.where}.table: {{header, rows, numeric}} or a .csv / .xlsx file")
    header = [str(h) for h in t.need("header", list)]
    rows = [[("" if c is None else str(c)) for c in r] for r in t.need("rows", list)]
    for k, r in enumerate(rows):
        if len(r) != len(header):
            raise SpecError(f"{t.where}.rows[{k}]: {len(r)} cells for {len(header)} columns")
    numeric = tuple(int(i) for i in t.get("numeric", [], list))
    return header, rows, numeric, False


def items4(v: Any, where: str) -> list[tuple[str, str, str, str]]:
    out = []
    for k, it in enumerate(v or []):
        if isinstance(it, Spec):
            it = [it.get("label", ""), it.get("value", ""), it.get("note", ""), it.get("tone", "neutral")]
        if not isinstance(it, list) or not 2 <= len(it) <= 4:
            raise SpecError(f"{where}[{k}]: [label, value, note, tone]")
        it = [str(x) for x in it] + ["", "neutral"][len(it) - 2:]
        if it[3] not in TONES:
            raise SpecError(f"{where}[{k}]: tone {it[3]!r} is not one of {', '.join(TONES)}")
        out.append((it[0], it[1], it[2], it[3]))
    return out


# ----------------------------------------------------------------------------------------------
# HTML
# ----------------------------------------------------------------------------------------------
def inline(md: str) -> str:
    from markdown_it import MarkdownIt
    return MarkdownIt("commonmark", {"html": False}).renderInline(md or "")


def html_page(doc: Doc, parent: Spec) -> Any:
    from ..html import Page
    page = Page(doc.title, eyebrow=doc.eyebrow, lead=inline(doc.lead) if doc.lead else None, contents=doc.contents)
    for k, b in enumerate(doc.blocks):
        html_block(page, b, parent, f".blocks[{k}]")
    return page


def html_block(page: Any, b: Any, parent: Spec, where: str) -> None:
    kind, s = block_of(b, parent, where)
    cap = s.get("caption", kind=str)
    capi = inline(cap) if cap else None
    if kind in ("h2", "h3"):
        if kind == "h2":
            page.h2(str(s.get(kind)))
        else:
            page.html(f"<h3>{H.escape(str(s.get(kind)))}</h3>")
    elif kind == "p":
        page.p(inline(str(s.get("p"))))
    elif kind == "md":
        text, p = text_or_file(s, "md", (".md", ".markdown"))
        page.markdown(text, base=(p.parent if p else s.base))
    elif kind == "kpis":
        page.kpis(items4(s.items("kpis"), f"{s.where}.kpis"))
    elif kind == "callout":
        page.callout(s.get("title", "Note", str), inline(str(s.get("callout"))),
                     s.get("tone", "info", str, ("info", "good", "warn", "bad")))
    elif kind == "table":
        header, rows, numeric, plain = table_of(s)
        cell = (lambda x: H.escape(x)) if plain else inline
        page.table([H.escape(h) for h in header], [[cell(c) for c in r] for r in rows], numeric=numeric)
        if capi:                                            # captioned as a figure is
            page.parts[-1] = f"<figure>{page.parts[-1]}<figcaption>{capi}</figcaption></figure>"
    elif kind == "figure":
        obj = figure_obj(s)
        s.get("width")
        page.figure(obj, capi)
    elif kind == "row":
        figs = []
        for j, f in enumerate(s.items("row")):
            if not isinstance(f, Spec) or "figure" not in f:
                raise SpecError(f"{s.where}.row[{j}]: {{figure: …, caption: …}}")
            c = f.get("caption", kind=str)
            figs.append((figure_obj(f), inline(c) if c else None))
        page.row(*figs)
    elif kind == "columns":
        from ..html import Page
        cols = []
        for j, col in enumerate(s.get("columns", [], list)):
            sub = Page("")
            for i, inner in enumerate(col if isinstance(col, list) else [col]):
                html_block(sub, inner, s, f".columns[{j}][{i}]")
            cols.append("<div>" + "\n".join(sub.parts) + "</div>")
            for attr in ("stepped", "talked", "shown", "pinned", "diffed", "carded"):
                if getattr(sub, attr):                      # what a column used, the page needs the styles of
                    setattr(page, attr, True)
        page.html('<div class="row">' + "".join(cols) + "</div>")
    elif kind == "code":
        src, p = text_or_file(s, "code", (".py", ".js", ".ts", ".cs", ".sql", ".json", ".yaml", ".yml", ".sh",
                                          ".ps1", ".html", ".css", ".md", ".txt", ".java", ".go", ".rs", ".typ"))
        lang = s.get("lang", (p.suffix.lstrip(".") if p else None), str)
        page.code(src.rstrip("\n"), lang, capi)
    elif kind == "image":
        page.image(s.file(str(s.get("image"))), capi, s.get("alt", kind=str))
    elif kind == "qr":
        page.figure(_qr(str(s.get("qr"))), capi, min_width=None)
    elif kind == "pagebreak":
        s.get("pagebreak")
    elif kind == "steps":
        frames = []
        for j, f in enumerate(s.items("steps")):
            if not isinstance(f, Spec):
                raise SpecError(f"{s.where}.steps[{j}]: {{figure, title, text}}")
            frames.append((figure_obj(f), str(f.need("title")), inline(str(f.get("text", "")))))
        page.steps(frames, capi)
    elif kind == "chat":
        turns = []
        for j, t in enumerate(s.get("chat", [], list)):
            if not (isinstance(t, list) and len(t) == 2 and t[0] in ("you", "them")):
                raise SpecError(f"{s.where}.chat[{j}]: [you | them, text]")
            turns.append((t[0], _chat_html(str(t[1]))))
        page.chat(turns, capi, you=s.get("you", "You", str), them=s.get("them", "Claude", str))
    elif kind == "annotated":
        marks = [(float(m[0]), float(m[1]), inline(str(m[2]))) for m in s.need("marks", list)]
        page.annotated(s.file(str(s.get("annotated"))), marks, capi, s.get("alt", kind=str))
    elif kind == "diff":
        d = s.sub("diff")
        if d is None:
            raise SpecError(f"{s.where}.diff: {{before, after}}")
        before, _ = text_or_file(d, "before", (".md", ".txt", ".py", ".yaml", ".json", ".html", ".cs", ".js", ".ts"))
        after, _ = text_or_file(d, "after", (".md", ".txt", ".py", ".yaml", ".json", ".html", ".cs", ".js", ".ts"))
        labels = s.get("labels", ["Before", "After"], list)
        page.diff(before, after, capi, labels=(str(labels[0]), str(labels[1])))
    elif kind == "cards":
        items = []
        for j, c in enumerate(s.get("cards", [], list)):
            if not (isinstance(c, list) and len(c) == 3):
                raise SpecError(f"{s.where}.cards[{j}]: [href, title, text]")
            items.append((H.escape(str(c[0])), str(c[1]), inline(str(c[2]))))
        page.cards(items, kicker=s.get("kicker", None, list))
    elif kind == "html":
        v = s.get("html")
        if not isinstance(v, Raw):                          # made by a kind's own code, never written in a spec
            raise SpecError(f"{s.where}: an html block is made by kinds, not written in a spec")
        page.html(str(v))


def _chat_html(text: str) -> str:
    """A turn: Markdown, with a fenced block kept as laid-out text."""
    from markdown_it import MarkdownIt
    return MarkdownIt("commonmark", {"html": False}).render(text)


def _qr(data: str) -> Any:
    from ..svgkit import Canvas
    c = Canvas(120, 120)
    c.qr(data, 8, 8, 104)
    return c


# ----------------------------------------------------------------------------------------------
# PDF
# ----------------------------------------------------------------------------------------------
def ts(s: str) -> str:
    """A Typst string literal."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "") + '"'


class Typst:
    """Typst markup for a Doc's blocks; figures written as SVGs into `work`."""

    def __init__(self, work: Path, base: Path):
        self.work, self.base = work, base
        self.n = 0

    def md(self, text: str, base: Path | None = None) -> str:
        rel = Path(_rel(base or self.base, self.work)).as_posix()
        return (f"cmarker.render({ts(text)}, h1-level: 2, raw-typst: false, "
                f"scope: (image: (path, ..args) => image(if path.starts-with(\"/\") {{ path }} else "
                f"{{ {ts(rel + '/')} + path }}, ..args)))")

    def figure(self, obj: Any, width: str | None) -> str:
        self.n += 1
        if isinstance(obj, Path):
            dst = self.work / f"fig{self.n}.svg"
            shutil.copyfile(obj, dst)
        else:
            dst = save_figure(obj, self.work / f"fig{self.n}.svg")
        w = width or _fit(dst)
        return f"image({ts(dst.name)}, width: {w})"

    def blocks(self, blocks: list[Any], parent: Spec, where: str) -> str:
        return "\n\n".join(self.block(b, parent, f"{where}[{k}]") for k, b in enumerate(blocks))

    def block(self, b: Any, parent: Spec, where: str) -> str:
        kind, s = block_of(b, parent, where)
        cap = s.get("caption", kind=str)
        capt = f", caption: [#{self.md(cap)}]" if cap else ""
        if kind in HTML_ONLY:
            raise SpecError(f"{s.where}: a {kind} block is for a page; leave it out of a PDF (format: html)")
        if kind in ("h2", "h3"):
            return f"#heading(level: {kind[1]}, {ts(str(s.get(kind)))})"
        if kind == "p":
            return f"#{self.md(str(s.get('p')))}"
        if kind == "md":
            text, p = text_or_file(s, "md", (".md", ".markdown"))
            return f"#{self.md(text, p.parent if p else None)}"
        if kind == "kpis":
            items = items4(s.items("kpis"), f"{s.where}.kpis")
            return "#kpis(" + ", ".join(f"({ts(a)}, {ts(b)}, {ts(c)}, {ts(d)})" for a, b, c, d in items) + ")"
        if kind == "callout":
            tone = s.get("tone", "info", str, ("info", "good", "warn", "bad"))
            return f"#callout({ts(s.get('title', 'Note', str))}, tone: {ts(tone)})[#{self.md(str(s.get('callout')))}]"
        if kind == "table":
            header, rows, numeric, plain = table_of(s)
            cell = (lambda x: f"[#{ts(x)}]") if plain else (lambda x: f"[#{self.md(x)}]")
            head = "(" + ", ".join(f"[#{ts(h)}]" for h in header) + ",)"
            body = "(" + ", ".join("(" + ", ".join(cell(c) for c in r) + ",)" for r in rows) + ",)"
            num = "(" + ", ".join(str(i) for i in numeric) + ("," if len(numeric) == 1 else "") + ")"
            return f"#figure(data-table({head}, {body}, numeric: {num}){capt})"
        if kind == "figure":
            return f"#figure({self.figure(figure_obj(s), s.get('width', kind=str))}{capt})"
        if kind == "row":
            parts = []
            for j, f in enumerate(s.items("row")):
                if not isinstance(f, Spec) or "figure" not in f:
                    raise SpecError(f"{s.where}.row[{j}]: {{figure: …, caption: …}}")
                c = f.get("caption", kind=str)
                parts.append(f"figure({self.figure(figure_obj(f), '100%')}"
                             + (f", caption: [#{self.md(c)}]" if c else "") + ")")
            return "#beside(" + ", ".join(parts) + ")"
        if kind == "columns":
            cols = [self.blocks(col if isinstance(col, list) else [col], s, f".columns[{j}]")
                    for j, col in enumerate(s.get("columns", [], list))]
            return "#beside(" + ", ".join(f"[\n{c}\n]" for c in cols) + ")"
        if kind == "code":
            src, p = text_or_file(s, "code", (".py", ".js", ".ts", ".cs", ".sql", ".json", ".yaml", ".yml", ".sh",
                                              ".ps1", ".html", ".css", ".md", ".txt", ".java", ".go", ".rs", ".typ"))
            lang = s.get("lang", (p.suffix.lstrip(".") if p else None), str)
            body = f"raw(block: true, {'lang: ' + ts(lang) + ', ' if lang else ''}{ts(src.rstrip(chr(10)))})"
            return f"#figure(align(left, {body}){capt})" if cap else f"#{body}"
        if kind == "image":
            p = s.file(str(s.get("image")))
            s.get("alt")
            self.n += 1
            dst = self.work / f"img{self.n}{p.suffix}"
            shutil.copyfile(p, dst)
            return f"#figure(image({ts(dst.name)}, width: 100%){capt})"
        if kind == "qr":
            return f"#figure({self.figure(_qr(str(s.get('qr'))), '28%')}{capt})"
        if kind == "pagebreak":
            s.get("pagebreak")
            return "#pagebreak(weak: true)"
        raise SpecError(f"{s.where}: no PDF form for {kind}")


def _rel(base: Path, work: Path) -> str:
    import os
    return os.path.relpath(base, work)


def _fit(svg: Path) -> str:
    """An SVG's natural width as a share of the column, so a small figure is not blown up."""
    head = svg.read_text(encoding="utf-8")[:600]
    m = re.search(r'width="([\d.]+)(pt|px)?"', head)
    if not m:
        return "100%"
    w = float(m.group(1)) * (1 if m.group(2) == "pt" else 0.75)
    return f"{min(100, round(w / 470 * 100))}%"


TYPST_HEAD = """#import "@local/rich-content:0.1.0": *
#import "@preview/cmarker:0.1.10"
#show: report.with(title: {title}, eyebrow: {eyebrow}, footer: {footer}, dense: {dense}, paper: {paper})
"""


def pdf_source(doc: Doc, parent: Spec, work: Path) -> str:
    t = Typst(work, parent.base)
    head = TYPST_HEAD.format(title=ts(doc.title), eyebrow=ts(doc.eyebrow) if doc.eyebrow else "none",
                             footer=ts(doc.footer) if doc.footer else "none", dense="true" if doc.dense else "false",
                             paper=ts(doc.paper))
    lead = (f"#block(below: 1.3em, text(size: 1.06em, fill: colour(\"muted\"), {t.md(doc.lead)}))\n\n"
            if doc.lead else "")
    cols = f"#show: columns.with({doc.columns}, gutter: 16pt)\n\n" if doc.columns > 1 else ""
    return head + doc.extra_typst + "\n" + lead + cols + t.blocks(doc.blocks, parent, ".blocks") + "\n"


# ----------------------------------------------------------------------------------------------
# Writing
# ----------------------------------------------------------------------------------------------
def write(doc: Doc, out: Path, formats: list[str], spec: Spec) -> list[Path]:
    written = []
    if "html" in formats:
        page = html_page(doc, spec)
        written.append(page.save(out.with_suffix(".html"), footer=H.escape(doc.footer) if doc.footer else None))
    if "pdf" in formats:
        written.append(write_pdf(doc, out.with_suffix(".pdf"), spec))
    return written


@contextmanager
def typst_work(spec: Spec, target: Path) -> Iterator[Path]:
    """A folder to set a PDF's Typst source and figures in: _preview/_render_<name> beside the spec,
    inside the checkout (Typst's root), gone afterwards."""
    from ..render import _preview_dir
    work = _preview_dir(spec.base / "x", None) / f"_render_{target.stem}"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    try:
        yield work
    finally:
        shutil.rmtree(work, ignore_errors=True)


def compile_typst(work: Path, source: str, target: Path) -> Path:
    """Set `source` (written into `work`) as the PDF `target`, in the theme."""
    from ..render import pdf
    src = work / "doc.typ"
    src.write_text(source, encoding="utf-8")
    return pdf(src, target)


def write_pdf(doc: Doc, target: Path, spec: Spec) -> Path:
    with typst_work(spec, target) as work:
        return compile_typst(work, pdf_source(doc, spec, work), target)


__all__ = ["Doc", "Raw", "common", "write", "typst_work", "compile_typst", "html_page", "pdf_source", "inline", "ts", "BLOCKS"]
