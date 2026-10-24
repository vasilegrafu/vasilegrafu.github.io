"""
render — turn Typst sources into PDFs, and PDFs and SVG figures into PNGs to look at.
Borrowed from ai-workbench-learning's manual build (tools/build.py), without the manual.

    python -m tools.render pdf report.typ [-o report.pdf] [--root DIR] [--theme NAME]
    python -m tools.render md handout.md [-o handout.pdf] [--title T] [--eyebrow E] [--theme NAME]
    python -m tools.render png report.pdf figure.svg … [--dpi 144] [-o DIR] [--theme NAME]
    python -m tools.render sheet report.pdf [--per 12] [--cols 4] [--dpi 60] [-o DIR]

pdf    compiles with the venv's fonts only (system fonts ignored, so a page looks the same on every
       machine), and with the skill's typst/ folder as the package path, so a document anywhere can
       `#import "@local/rich-content:0.1.0": *` for the house style, set in the theme (tools.theme:
       --theme, else RICH_CONTENT_THEME, else a rich-content.json in or above the document's folder,
       else technical). The Typst root defaults to the git checkout the file is in (its folder when
       it is in none), so a document may use figures from elsewhere in the checkout.
png    one PNG per PDF page -- name.png for a one-page PDF, name-p01.png, name-p02.png, … for more,
       last run's pages of that PDF removed first; an SVG goes through a Typst page cut to its size,
       so its text is set in the theme's fonts rather than a viewer's fallback font. To look
       closely at where a line meets a label, raise --dpi (288 shows a pixel as four).
md     a Markdown file set as a PDF in the house style (Typst's cmarker package): its first
       `# heading` is the title unless --title gives one; images are relative to the .md.
sheet  contact sheets of a PDF, `per` pages to an image, for checking layout and page breaks.
check  what a reader would see as broken in a PDF: text that overlaps text, text off the page.
       Exits 1 when it finds anything. (Diagrams and charts are checked when they are saved.)

    python -m tools.render check report.pdf

A PDF is written beside its .typ. PNGs and sheets are previews, to look at and throw away: they
go into a _preview/ folder beside the file they show, unless -o names a folder. So do the _render_*
pages set while an SVG or Markdown renders, deleted after. Each _preview/ folder holds a
.gitignore of its own that ignores everything in it, itself included, so nothing made only to be
looked at is ever committed, wherever in a checkout it is made.
Run with the root .venv's python (see SETUP.md, "Rich content").
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import re
import sys as _sys

from .svgkit import PACKAGES
from .theme import current, font_dir, resolve, use_theme

PREVIEW = "_preview"                                # where previews go; each holds a .gitignore of "*"


def font_paths() -> list[str]:
    return [str(font_dir())]


def package_cache() -> str:
    """Where setup.py puts the Typst packages the house style uses (cmarker), so a compile never
    fetches one."""
    return str(Path(_sys.prefix) / "share" / "typst" / "packages")


def _inputs() -> dict[str, str]:
    from .code import tm_theme
    return {"rich-content-theme": current().typst(), "rich-content-code": tm_theme()}


def _root_for(p: Path) -> Path:
    """The git checkout `p` is in, else its folder."""
    for d in p.parents:
        if (d / ".git").exists():
            return d
    return p.parent


def pdf(src: Path, out: Path | None = None, root: Path | None = None,
        extra_inputs: dict[str, str] | None = None) -> Path:
    import typst
    src = src.resolve()
    out = (out or src.with_suffix(".pdf")).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        _, warnings = typst.compile_with_warnings(str(src), output=str(out), root=str(root or _root_for(src)),
                                                  font_paths=font_paths(), ignore_system_fonts=True,
                                                  package_path=str(PACKAGES), package_cache_path=package_cache(),
                                                  sys_inputs={**_inputs(), **(extra_inputs or {})})
    except typst.TypstError as e:                   # the message alone says what, the diagnostic says where
        raise SystemExit(getattr(e, "diagnostic", None) or str(e)) from None
    for w in warnings:
        print(f"warning: {w.message}", file=sys.stderr)
    print(f"pdf: {out}")
    return out


MARKDOWN_PAGE = """#import "@local/rich-content:0.1.0": *
#import "@preview/cmarker:0.1.10"
#show: report.with(title: sys.inputs.at("md-title", default: none),
                   eyebrow: sys.inputs.at("md-eyebrow", default: none),
                   footer: sys.inputs.at("md-footer", default: none),
                   dense: sys.inputs.at("md-dense", default: "") == "1")
// this page sits in _preview/, so an image the Markdown names beside itself is one folder up
#cmarker.render(read("{name}"), h1-level: 1, raw-typst: false,
                scope: (image: (path, ..args) => image(if path.starts-with("/") {{ path }} else {{ "../" + path }},
                                                       ..args)))
"""


def markdown_pdf(md: Path, out: Path | None = None, title: str | None = None, eyebrow: str | None = None,
                 footer: str | None = None, dense: bool = False) -> Path:
    """A Markdown file set as a PDF in the house style. Its first `# heading` becomes the title
    (and leaves the body) unless `title` is given. The page is set from a _render_md_<name>.typ
    in _preview/ beside the .md, deleted after; images resolve relative to the Markdown."""
    md = md.resolve()
    text = md.read_text(encoding="utf-8")
    first = re.match(r"\s*#\s+(.+?)\s*\n", text)
    if title is None and first:
        title, text = first.group(1), text[first.end():]
    work = _preview_dir(md, None)
    body = work / f"_render_md_{md.stem}.md"
    src = work / f"_render_md_{md.stem}.typ"
    body.write_text(text, encoding="utf-8")
    src.write_text(MARKDOWN_PAGE.format(name=body.name), encoding="utf-8")
    extra = {"md-title": title or md.stem, "md-eyebrow": eyebrow or "", "md-footer": footer or "",
             "md-dense": "1" if dense else ""}
    extra = {k: v for k, v in extra.items() if v}
    try:
        return pdf(src, out or md.with_suffix(".pdf"), extra_inputs=extra)
    finally:
        src.unlink(missing_ok=True)
        body.unlink(missing_ok=True)


def _svgs_to_pdf(svgs: list[Path]) -> Path:
    """Each SVG on a page of its own size, so its fonts are Typst's and nothing is scaled. The page
    source sits beside the first SVG, and the caller deletes it with the PDF. A dark theme's
    figures are set on its paper, everything else on white."""
    import typst
    src = _preview_dir(svgs[0], None) / "_render_svgs.typ"   # in _preview/, which ignores itself
    root = Path(os.path.commonpath([src, *svgs]))
    th = current()
    paper = f'rgb("{th.colour["paper"]}")' if th.dark else "white"
    body = [f'#set page(width: auto, height: auto, margin: 6pt, fill: {paper})']
    for i, s in enumerate(svgs):
        if i:
            body.append("#pagebreak()")
        body.append(f'#image("/{s.relative_to(root).as_posix()}")')
    src.write_text("\n".join(body), encoding="utf-8")
    out = src.with_suffix(".pdf")
    try:
        typst.compile(str(src), output=str(out), root=str(root), font_paths=font_paths(), ignore_system_fonts=True)
    finally:
        src.unlink()
    return out


def _pages(pdf_path: Path, dpi: int):
    """Each page of a PDF as a Pillow image at `dpi`, on white."""
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(str(pdf_path))
    try:
        for i in range(len(pdf)):
            # scale is a float in pypdfium2's docs and code; only its annotation says int
            yield pdf[i].render(scale=dpi / 72).to_pil().convert("RGB")  # pyright: ignore[reportArgumentType]
    finally:
        pdf.close()                                  # Windows keeps an open file from being deleted


def _preview_dir(f: Path, out_dir: Path | None) -> Path:
    """`out_dir`, or the _preview/ folder beside f -- made with a .gitignore that ignores all of it."""
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir
    d = f.parent / PREVIEW
    d.mkdir(parents=True, exist_ok=True)
    ignore = d / ".gitignore"
    if not ignore.exists():
        ignore.write_text("# made by the rich-content skill only to be looked at: never committed\n*\n",
                          encoding="utf-8")
    return d


def png(files: list[Path], dpi: int = 144, out_dir: Path | None = None) -> list[Path]:
    """PNGs of PDFs' pages and of SVGs, into _preview/ beside each file unless out_dir is given."""
    out_dir = out_dir.resolve() if out_dir else None
    files = [f.resolve() for f in files]
    written: list[Path] = []
    svgs = [f for f in files if f.suffix.lower() == ".svg"]
    for drive in dict.fromkeys(s.anchor for s in svgs):   # one Typst root per drive: a root spans one
        group = [s for s in svgs if s.anchor == drive]
        tmp = _svgs_to_pdf(group)
        try:
            for s, im in zip(group, list(_pages(tmp, dpi))):
                p = _preview_dir(s, out_dir) / f"{s.stem}.png"
                im.save(p)
                written.append(p)
        finally:
            tmp.unlink(missing_ok=True)
    for f in (f for f in files if f.suffix.lower() == ".pdf"):
        d = _preview_dir(f, out_dir)
        for old in [d / f"{f.stem}.png", *d.glob(f"{f.stem}-p[0-9][0-9].png")]:
            old.unlink(missing_ok=True)              # last time's pages, when the count has changed
        pages = list(_pages(f, dpi))
        for i, im in enumerate(pages, 1):
            p = d / (f"{f.stem}.png" if len(pages) == 1 else f"{f.stem}-p{i:02d}.png")
            im.save(p)
            written.append(p)
    for f in (f for f in files if f.suffix.lower() not in (".svg", ".pdf")):
        print(f"skipped, neither PDF nor SVG: {f}", file=sys.stderr)
    for p in written:
        print(f"png: {p}")
    return written


def sheet(src: Path, per: int = 12, cols: int = 4, dpi: int = 60, out_dir: Path | None = None) -> list[Path]:
    from PIL import Image
    src = src.resolve()
    out_dir = _preview_dir(src, out_dir.resolve() if out_dir else None)
    for old in out_dir.glob(f"{src.stem}-sheet-*.png"):
        old.unlink()
    written: list[Path] = []
    pages = list(_pages(src, dpi))
    for k in range(0, len(pages), per):
        chunk = range(k, min(k + per, len(pages)))
        ims = [pages[i] for i in chunk]
        w, h = ims[0].size
        rows = (len(ims) + cols - 1) // cols
        canvas = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 8) + 8), "#888888")
        for j, im in enumerate(ims):
            canvas.paste(im, (8 + (j % cols) * (w + 8), 8 + (j // cols) * (h + 8)))
        p = out_dir / f"{src.stem}-sheet-{chunk[0] + 1:03d}-{chunk[-1] + 1:03d}.png"
        canvas.save(p)
        written.append(p)
    for p in written:
        print(f"sheet: {p}")
    return written


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.render", description=(__doc__ or "").split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("pdf", help="compile a .typ to PDF")
    a.add_argument("src", type=Path)
    a.add_argument("-o", "--out", type=Path)
    a.add_argument("--root", type=Path)
    a.add_argument("--theme", help="a theme's name or file (default: the document's project's, else technical)")
    b = sub.add_parser("png", help="PDF pages and SVG figures to PNG, into _preview/")
    b.add_argument("files", type=Path, nargs="+")
    b.add_argument("--dpi", type=int, default=144)
    b.add_argument("-o", "--out", type=Path)
    b.add_argument("--theme", help="the theme a dark figure's paper comes from")
    m = sub.add_parser("md", help="a Markdown file to PDF in the house style")
    m.add_argument("src", type=Path)
    m.add_argument("-o", "--out", type=Path)
    m.add_argument("--title")
    m.add_argument("--eyebrow")
    m.add_argument("--footer")
    m.add_argument("--dense", action="store_true")
    m.add_argument("--theme", help="a theme's name or file (default: the file's project's, else technical)")
    c = sub.add_parser("sheet", help="contact sheets of a PDF")
    c.add_argument("src", type=Path)
    c.add_argument("--per", type=int, default=12)
    c.add_argument("--cols", type=int, default=4)
    c.add_argument("--dpi", type=int, default=60)
    c.add_argument("-o", "--out", type=Path)
    d = sub.add_parser("check", help="overlapping or off-page text in PDFs")
    d.add_argument("files", type=Path, nargs="+")
    args = ap.parse_args(argv)
    if args.cmd in ("pdf", "md", "png"):            # the theme of the file's project, not of this script
        first = args.files[0] if args.cmd == "png" else args.src
        use_theme(args.theme or resolve(first.resolve().parent))
    if args.cmd == "pdf":
        pdf(args.src, args.out, args.root)
    elif args.cmd == "md":
        markdown_pdf(args.src, args.out, args.title, args.eyebrow, args.footer, args.dense)
    elif args.cmd == "png":
        png(args.files, args.dpi, args.out)
    elif args.cmd == "sheet":
        sheet(args.src, args.per, args.cols, args.dpi, args.out)
    else:
        from .check import pdf_issues
        found = 0
        for f in args.files:
            issues = pdf_issues(f)
            for i in issues:
                print(f"check: {f.name}: {i}")
            found += len(issues)
            if not issues:
                print(f"check: {f.name}: nothing found")
        return 1 if found else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
