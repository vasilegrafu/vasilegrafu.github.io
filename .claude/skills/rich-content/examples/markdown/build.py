"""Markdown in, a handout out: handout.md, written by hand, set as a PDF in the house style
(Typst's cmarker) and as one HTML page, both with its figure, its table, its highlighted code and a
QR code. This script draws the two figures the Markdown names, then sets it both ways:

    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\examples\\markdown\\build.py

From a terminal, the PDF alone: python -m tools.render md handout.md
"""
from pathlib import Path

from tools import render
from tools.html import Page
from tools.svgkit import Canvas, save

HERE = Path(__file__).resolve().parent

c = Canvas(530, 124)
api = c.node(4, 35, 130, 54, "compute", "API", icon="server")
cache = c.node(290, 4, 140, 50, "cache", "Redis", sub="TTL 60 s", icon="zap")
db = c.node(290, 70, 140, 52, "data", "Postgres", icon="database", shape="cylinder")
c.arrow(api.right, cache.left, label="1 · look up")
c.arrow(api.right, db.left, label="2 · on a miss", dash="5 4")
c.chip(cache.x2 + 10, cache.cy - 9, "hit 91 %", tone="warn")
save(c, HERE / "path.svg")

q = Canvas(112, 112)
q.qr("https://example.com/notes/orders-cache", 0, 0, 112)
save(q, HERE / "qr.svg")

render.markdown_pdf(HERE / "handout.md", eyebrow="Handout · orders service", footer="Caching order reads")

text = (HERE / "handout.md").read_text(encoding="utf-8")
title, body = text.split("\n", 1)
page = Page(title.lstrip("# "), eyebrow="Handout · orders service")
page.markdown(body, base=HERE)
page.save(HERE / "handout.html")
print(f"html: {HERE / 'handout.html'}")
