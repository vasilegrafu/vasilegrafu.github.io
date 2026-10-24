"""
html — a self-contained HTML page in the same look as the diagrams, charts and PDFs.

Diagrams and charts are inlined as SVG, the theme becomes CSS variables, and the fonts are
embedded, cut down to the characters the page uses: one file that opens the same anywhere,
offline, with nothing beside it.

    from tools.html import Page
    page = Page("Orders service", "Week 42")
    page.kpis([("Requests", "1.2 M", "+8 % on last week", "good"), …])
    page.figure(canvas, "The request path.")          # an svgkit Canvas, a matplotlib Figure,
    page.row((fig_a, "Latency."), (fig_b, "Errors.")) # an .svg path, or SVG markup
    page.callout("Watch", "p99 crosses the budget at lunch.", tone="warn")
    page.table(["Endpoint", "p99"], [["GET /orders", "212 ms"]], numeric=(1,))
    page.frame(df)                                    # a pandas DataFrame as that table
    page.code(src, "python")                          # highlighted in the theme's colours
    page.markdown(Path("notes.md").read_text(), base=Path("."))   # Markdown, images embedded
    page.steps([(canvas_1, "Calm", "Nothing has changed."), …], "A change, step by step.")
    page.chat([("you", "write a PRD: …"), ("them", "Written: …")], "What you say, what comes back.")
    page.image("shots/overview.webp", "The overview, as it opens.")   # a screenshot, embedded
    page.annotated("shots/overview.webp", [(120, 80, "The menu"), …])  # numbered markers and their legend
    page.diff(before, after, "What the operation changed.")          # a file before and after
    page.cards([("chapter.html", "Title", "What it holds."), …])      # links as cards

    site = Site("The manual", "docs/manual")                          # pages that share their navigation:
    page = site.page("index", "Welcome")                              # each a Page; site.save() writes them
    site.save()                                                       # all, with one fonts.css they share
    page.save(__file__)                               # -> <name>.html beside the script

    Page("Title", contents=True)                      # a contents bar of the h2 headings

A page with steps or contents carries one small script of its own: the steps turn one at a time
under Previous and Next, the contents mark the section being read. Without it -- printed, or with
scripts off -- every step stands one under the other and the contents are a plain list of links.

A font cut down is, to its licence (the SIL OFL), a modified font. The kit's families reserve no
name and claim no trademark, so each is embedded under its own name; and each cut keeps its
copyright and licence records (name IDs 0, 13 and 14), which the OFL asks every copy to carry.
"""
from __future__ import annotations

import base64
import io
import re
from html import escape
from pathlib import Path
from typing import Any

from .svgkit import Canvas, out_path
from .theme import Theme, current, families, font_file


def tones(th: Theme) -> dict[str, tuple[str, str]]:
    sig = th.signal
    return {"info": (sig["info"], sig["info_fill"]), "good": (sig["good"], sig["good_fill"]),
            "warn": (sig["warn"], sig["warn_fill"]), "bad": (sig["bad"], sig["bad_fill"]),
            "neutral": (th.colour["muted"], th.colour["wash"])}


# ----------------------------------------------------------------------------------------------
# Fonts
# ----------------------------------------------------------------------------------------------
def _woff(path: Path, codepoints: set[int]) -> str:
    import logging

    from fontTools import subset
    from fontTools.ttLib import TTFont
    logging.getLogger("fontTools.subset").setLevel(logging.ERROR)   # not "meta NOT subset" for each face
    font = TTFont(str(path), recalcTimestamp=False)  # no time in it: a rebuilt page is the same file
    options = subset.Options()
    options.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14]   # the subsetter's default, and the licence and its URL
    sub = subset.Subsetter(options)
    sub.populate(unicodes=codepoints)
    sub.subset(font)
    font.flavor = "woff"                            # zlib-compressed; woff2 would need brotli
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def font_faces(text: str, fams: list[str]) -> str:
    """@font-face rules with every weight of each family embedded, holding only the characters in
    `text` (and printable ASCII, so a later edit by hand still renders)."""
    cps = {ord(ch) for ch in text if ord(ch) > 0x7E} | set(range(0x20, 0x7F))
    rules = []
    for family in fams:
        scale = families()[family].get("scale", 1)
        adjust = f"size-adjust:{scale * 100:g}%;" if scale != 1 else ""
        for key in families()[family]["files"]:
            italic = key.endswith("i")
            weight = int(key.rstrip("i"))
            data = _woff(font_file(family, weight, italic), cps)
            rules.append(f'@font-face{{font-family:"{family}";font-weight:{weight};'
                         f'font-style:{"italic" if italic else "normal"};'
                         f'font-display:block;{adjust}src:url(data:font/woff;base64,{data}) format("woff")}}')
    return "\n".join(rules)


_FONT_DECL = re.compile(r'(font-family\s*=\s*"[^"]*"|font-family\s*:\s*[^;"]*|font\s*:\s*[^;"]*)')


def families_in(markup: str) -> list[str]:
    """The registered families an SVG's text asks for."""
    decls = " ".join(_FONT_DECL.findall(markup))
    return [f for f in families() if f in decls]


# ----------------------------------------------------------------------------------------------
# Figures
# ----------------------------------------------------------------------------------------------
def svg_markup(obj: Any) -> str:
    """SVG text from an svgkit Canvas, a matplotlib Figure, a path to an .svg, or SVG markup."""
    if isinstance(obj, Canvas):
        return obj.to_svg()
    if hasattr(obj, "savefig"):                     # a matplotlib Figure
        buf = io.StringIO()
        obj.savefig(buf, format="svg", bbox_inches="tight", pad_inches=0.04, metadata={"Date": None})
        import matplotlib.pyplot as plt
        plt.close(obj)
        return buf.getvalue()
    if isinstance(obj, Path) or (isinstance(obj, str) and obj.endswith(".svg") and "<svg" not in obj):
        return Path(obj).read_text(encoding="utf-8")
    return str(obj)


def inline_svg(obj: Any, label: str | None = None, min_width: str | None = None) -> str:
    """SVG ready to sit in HTML: no XML prologue or metadata, and scaling with its column up to its
    own width, never past the size it was drawn at. `min_width` stops a wide diagram shrinking
    below legibility on a phone; its card then scrolls sideways instead."""
    svg = svg_markup(obj)
    svg = svg[svg.index("<svg"):]
    svg = re.sub(r"<metadata>.*?</metadata>\s*", "", svg, flags=re.S)
    tag = re.match(r"<svg\b[^>]*>", svg)
    if tag is None:
        raise ValueError("not SVG markup")
    old = tag.group(0)
    w = re.search(r'\swidth="([^"]+)"', old)
    width = w.group(1) if w else "100%"
    if re.fullmatch(r"[\d.]+", width):
        width += "px"
    new = re.sub(r'\s(width|height)="[^"]*"', "", old)[:-1]
    aria = f' role="img" aria-label="{escape(label)}"' if label else ""
    floor = f";min-width:min({width},{min_width})" if min_width else ""
    new += f' style="width:100%;height:auto;max-width:{width}{floor}"{aria}>'
    return new + svg[len(old):]


# ----------------------------------------------------------------------------------------------
# The page
# ----------------------------------------------------------------------------------------------
CSS = """
:root{--ink:%(ink)s;--muted:%(muted)s;--faint:%(faint)s;--rule:%(rule)s;--paper:%(paper)s;--wash:%(wash)s;
--heading:%(heading)s;--accent:%(accent)s;--text:%(f_text)s;--label:%(f_label)s;--head:%(f_heading)s;
--mono:%(f_mono)s;--radius:%(radius)spx;color-scheme:%(scheme)s}
*{box-sizing:border-box}
html{background:var(--wash)}
body{margin:0;background:var(--wash);color:var(--ink);font:%(body_size)s/1.6 var(--text);
-webkit-font-smoothing:antialiased}
main{max-width:860px;margin:0 auto;padding:40px 16px 64px}
header{margin-bottom:28px}
.eyebrow{font:600 12px/1.4 var(--label);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1,h2,h3{font-family:var(--head);color:var(--heading);line-height:1.25;margin:0}
h1{font-size:clamp(24px,6vw,30px);font-weight:%(heading_weight)s;margin-top:6px;overflow-wrap:anywhere}
h2{font-size:20px;font-weight:%(heading_weight)s;margin:40px 0 10px}
main h3{font:600 17px/1.35 var(--label);color:var(--heading);margin:28px 0 8px}
main h2+h3{margin-top:12px}
p{margin:0 0 14px}
code{font:500 .86em var(--mono);font-variant-ligatures:none;font-feature-settings:"calt" 0;background:var(--paper);border:1px solid var(--rule);
border-radius:min(4px,var(--radius));padding:1px 5px}
.card{background:var(--paper);border:1px solid var(--rule);border-radius:var(--card-radius);padding:18px}
:root{--card-radius:%(card_radius)spx}
figure{margin:18px 0 22px}
figure .card{display:flex;overflow-x:auto}
figure .card>svg{flex:none;margin:0 auto}
figcaption{font:400 13.5px/1.5 var(--label);color:var(--muted);margin-top:8px}
.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin:18px 0 22px}
.row figure{margin:0}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:8px 0 8px}
.kpi .label{font:600 12px/1.3 var(--label);letter-spacing:.05em;text-transform:uppercase;color:var(--muted)}
.kpi .value{font:700 28px/1.2 var(--label);color:var(--heading);font-variant-numeric:tabular-nums;margin:6px 0 2px}
.kpi .note{font:500 13px/1.4 var(--label)}
.callout{border-left:3px solid var(--tone);background:var(--tone-fill);border-radius:0 var(--card-radius) var(--card-radius) 0;
padding:12px 16px;margin:18px 0}
.callout .title{font:600 14px/1.4 var(--label);color:var(--tone);margin-bottom:2px}
.callout p:last-child{margin:0}
.table{overflow-x:auto;padding:4px 0}
table{width:100%%;min-width:540px;border-collapse:collapse;font:400 14.5px/1.45 var(--label)}
td code,.num{white-space:nowrap}
th{font-weight:600;color:var(--muted);text-align:left;font-size:13px;
padding:10px 14px;border-bottom:1px solid var(--rule)}
td{padding:9px 14px;border-bottom:1px solid var(--rule)}
tr:last-child td{border-bottom:0}
.num{text-align:right;font-variant-numeric:tabular-nums}
.tone-good{color:%(good)s}.tone-warn{color:%(warn)s}.tone-bad{color:%(bad)s}.tone-info{color:%(info)s}.tone-neutral{color:var(--muted)}
footer{margin-top:44px;font:400 13px/1.5 var(--label);color:var(--muted)}
pre.code{background:var(--paper);border:1px solid var(--rule);border-radius:min(8px,var(--card-radius));
padding:12px 14px;margin:16px 0;overflow-x:auto;font:400 13.5px/1.55 var(--mono);color:var(--ink);
font-variant-ligatures:none;font-feature-settings:"calt" 0}
pre.code code{font:inherit;background:none;border:0;padding:0}
.md img{max-width:100%%}
.mdfig{display:block;overflow-x:auto}
@media (forced-colors:active){
.card,.callout,pre.code{border:1px solid CanvasText}.callout{border-left-width:3px}
figure .card,.mdfig{forced-color-adjust:none;background:var(--paper)}}
.md h2{margin:34px 0 10px}.md h3{margin:24px 0 8px;font-size:17px}
.md .table{display:inline-block;max-width:100%%;margin:6px 0 18px}
.md table{width:auto;min-width:0}
.md ol,.md ul{padding-left:24px;margin:0 0 14px}
"""

CHAT_CSS = """
.chat{display:flex;flex-direction:column;gap:10px;margin:18px 0 6px}
.turn{max-width:min(88%,680px);min-width:0;padding:10px 14px;border-radius:14px;font:400 15px/1.5 var(--label);
overflow-wrap:anywhere}
.turn .who{font:600 11px/1.3 var(--label);letter-spacing:.06em;text-transform:uppercase;margin-bottom:3px;opacity:.8}
.turn.you{align-self:flex-end;background:var(--accent);color:var(--paper);border-bottom-right-radius:4px}
.turn.them{align-self:flex-start;background:var(--paper);border:1px solid var(--rule);border-bottom-left-radius:4px}
.turn p{margin:0 0 6px}.turn p:last-child{margin:0}
.turn pre{white-space:pre;overflow-x:auto;overflow-wrap:normal;font:400 13px/1.5 var(--mono);margin:6px 0 2px;
background:var(--wash);
border-radius:min(6px,var(--radius));padding:8px 10px;color:var(--ink);font-variant-ligatures:none}
.turn code{background:transparent;border-color:currentColor}
figure.talk{margin:18px 0 22px}
@media (forced-colors:active){.turn{border:1px solid CanvasText}}
"""

SHOT_CSS = """
figure .card.shot{display:block;padding:0;overflow:hidden}
.card.shot img{display:block;width:100%;height:auto}
"""

PINS_CSS = """
.pin-wrap{position:relative}
.pin{position:absolute;transform:translate(-50%,-50%);min-width:26px;height:26px;padding:0 6px;border-radius:13px;
background:var(--accent);color:var(--paper);font:700 13px/26px var(--label);text-align:center;
box-shadow:0 0 0 3px var(--paper),0 2px 6px rgba(0,0,0,.25)}
ol.pins{list-style:none;margin:12px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
gap:8px 18px;font:400 14px/1.45 var(--label)}
ol.pins li{display:flex;gap:10px;align-items:baseline}
ol.pins .n{flex:none;min-width:22px;height:22px;padding:0 5px;border-radius:11px;background:var(--accent);color:var(--paper);
font:700 12px/22px var(--label);text-align:center}
@media (max-width:600px){.pin{min-width:20px;height:20px;border-radius:10px;font-size:11px;line-height:20px;padding:0 4px}}
"""

DIFF_CSS = """
.diff{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:18px 0 6px}
.diff .side{min-width:0;background:var(--paper);border:1px solid var(--rule);border-radius:min(8px,var(--card-radius));
overflow:hidden}
.diff .head{font:600 12px/1.4 var(--label);letter-spacing:.06em;text-transform:uppercase;color:var(--muted);
padding:8px 12px;border-bottom:1px solid var(--rule);background:var(--wash)}
.diff pre{margin:0;padding:8px 0;overflow-x:auto;font:400 12.5px/1.6 var(--mono);font-variant-ligatures:none}
.diff pre span{display:block;padding:0 12px;white-space:pre-wrap;overflow-wrap:anywhere}
.diff .del{background:var(--bad-fill);box-shadow:inset 3px 0 var(--bad)}
.diff .add{background:var(--good-fill);box-shadow:inset 3px 0 var(--good)}
.diff .gap{color:var(--muted);font-style:italic}
figure.diffs{margin:18px 0 22px}
@media (max-width:760px){.diff{grid-template-columns:1fr}}
"""

CARDS_CSS = """
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;margin:18px 0 22px}
a.tile{display:block;text-decoration:none;color:var(--ink);background:var(--paper);border:1px solid var(--rule);
border-radius:var(--card-radius);padding:16px 18px;transition:border-color .15s}
a.tile:hover{border-color:var(--accent)}
a.tile .k{font:700 12px/1.3 var(--label);letter-spacing:.06em;text-transform:uppercase;color:var(--accent)}
a.tile .t{font:600 17px/1.3 var(--head);color:var(--heading);margin:4px 0 6px}
a.tile .d{font:400 14px/1.5 var(--label);color:var(--muted)}
"""

SITE_CSS = """
.topbar{border-bottom:1px solid var(--rule);background:var(--paper)}
.topbar a{display:block;max-width:1400px;margin:0 auto;padding:12px 16px;font:700 15px/1.3 var(--label);
color:var(--heading);text-decoration:none}
nav.toc ol.chapters{columns:auto;padding-left:22px}
nav.toc .home-link{margin:8px 0 2px;font:400 14px/1.45 var(--label)}
nav.toc .home-link .current>a{color:var(--accent);font-weight:700}
nav.toc .home-link ol.sections{margin-left:4px}
nav.toc ol.chapters>li{padding:3px 0}
nav.toc ol.chapters>li.current>a{color:var(--accent);font-weight:700}
nav.toc ol.sections{margin:4px 0 6px;padding-left:14px;list-style:none;border-left:2px solid var(--rule);font-size:13.5px}
nav.toc details summary{cursor:pointer;font:600 12px/1.4 var(--label);letter-spacing:.08em;text-transform:uppercase;
color:var(--muted)}
nav.pager{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:48px 0 0}
nav.pager a{display:block;text-decoration:none;background:var(--paper);border:1px solid var(--rule);
border-radius:var(--card-radius);padding:12px 16px;color:var(--muted);font:400 13px/1.4 var(--label)}
nav.pager a:hover{border-color:var(--accent)}
nav.pager a strong{display:block;color:var(--heading);font:600 15px/1.35 var(--label);margin-top:2px}
nav.pager a.next{text-align:right;grid-column:2}
@media (max-width:1219px){nav.toc ol.sections{display:none}}
@media print{.topbar,nav.pager{display:none}}
"""

CONTENTS_CSS = """
nav.toc{max-width:860px;margin:0 auto;padding:28px 16px 0}
nav.toc .card{padding:12px 16px}
nav.toc .toc-title{font:600 12px/1.4 var(--label);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
nav.toc ol{margin:6px 0 0;padding-left:22px;font:400 14px/1.45 var(--label);columns:2 240px;column-gap:28px}
nav.toc li{padding:2px 0;break-inside:avoid}
nav.toc a{color:var(--ink);text-decoration:none}
nav.toc a:hover{text-decoration:underline}
nav.toc a.here{color:var(--accent);font-weight:600}
h2[id]{scroll-margin-top:16px}
@media (min-width:1220px){
.frame{display:grid;grid-template-columns:250px minmax(0,860px);justify-content:center;column-gap:28px}
.frame main{margin:0;max-width:none}
nav.toc{position:sticky;top:0;align-self:start;max-height:100vh;overflow-y:auto;padding:40px 0 24px;margin:0}
nav.toc .card{background:none;border:0;padding:0}
nav.toc ol{columns:auto;padding-left:20px}}
@media print{nav.toc{display:none}.frame{display:block}}
"""

STEPS_CSS = """
.steps .card{display:block;padding:0;overflow:hidden}
.steps-bar{display:none;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 14px;border-bottom:1px solid var(--rule);
background:var(--wash)}
.js .steps-bar{display:flex}
.steps-bar button{font:600 13px/1 var(--label);color:var(--ink);background:var(--paper);border:1px solid var(--rule);
border-radius:min(6px,var(--radius));padding:8px 12px;cursor:pointer}
.steps-bar button:hover:not(:disabled){border-color:var(--accent);color:var(--accent)}
.steps-bar button:disabled{opacity:.45;cursor:default}
.steps-bar button:focus-visible,.steps:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.steps-dots{display:flex;gap:6px;margin:0 auto;padding:0;list-style:none}
.steps-dots button{width:30px;height:30px;padding:0;border-radius:50%;font-variant-numeric:tabular-nums}
.steps-dots button[aria-current="step"]{background:var(--accent);border-color:var(--accent);color:var(--paper)}
.step{padding:16px 18px 18px;border-top:1px solid var(--rule)}
.steps-bar+.step{border-top:0}
.js .step{display:none;border-top:0}
.js .step.on{display:block}
.step-title{font:600 16px/1.35 var(--label);color:var(--heading);margin:0 0 4px;display:flex;gap:10px;align-items:baseline}
.step-title .n{font:700 13px/1 var(--label);color:var(--accent);flex:none}
.step-text{font:400 15px/1.55 var(--text);margin:0 0 12px;max-width:72ch}
.step-text p{margin:0 0 8px}
.step-fig{display:flex;overflow-x:auto}
.step-fig>svg{flex:none;margin:0 auto}
@media (max-width:480px){.steps-bar{gap:6px;padding:8px 10px;flex-wrap:nowrap}.steps-bar .word{display:none}
.steps-dots{gap:4px}.steps-dots button{width:28px;height:28px}.step{padding:14px 12px 16px}}
@media print{.js .step{display:block}.js .steps-bar{display:none}}
"""

SCRIPT = """
(function(){
document.querySelectorAll(".steps").forEach(function(box){
  var steps=box.querySelectorAll(".step"),dots=box.querySelectorAll(".steps-dots button"),
      prev=box.querySelector("[data-step=prev]"),next=box.querySelector("[data-step=next]"),i=0;
  function show(n){
    i=Math.max(0,Math.min(steps.length-1,n));
    steps.forEach(function(s,k){s.classList.toggle("on",k===i);});
    dots.forEach(function(d,k){if(k===i){d.setAttribute("aria-current","step");}else{d.removeAttribute("aria-current");}});
    prev.disabled=i===0;next.disabled=i===steps.length-1;
  }
  prev.addEventListener("click",function(){show(i-1);});
  next.addEventListener("click",function(){show(i+1);});
  dots.forEach(function(d,k){d.addEventListener("click",function(){show(k);});});
  box.addEventListener("keydown",function(e){
    if(e.key==="ArrowRight"){show(i+1);e.preventDefault();}
    if(e.key==="ArrowLeft"){show(i-1);e.preventDefault();}
  });
  show(0);
});
var links=document.querySelectorAll('nav.toc a[href^="#"]');
document.querySelectorAll("nav.toc details").forEach(function(d){if(window.innerWidth>=1220){d.open=true;}});
if(links.length&&"IntersectionObserver" in window){
  var heads=Array.prototype.map.call(links,function(a){return document.getElementById(a.hash.slice(1));});
  function mark(){
    var at=0;
    heads.forEach(function(h,k){if(h&&h.getBoundingClientRect().top<window.innerHeight*0.35){at=k;}});
    links.forEach(function(a,k){a.classList.toggle("here",k===at);});
  }
  var watch=new IntersectionObserver(mark,{rootMargin:"0px 0px -60% 0px"});
  heads.forEach(function(h){if(h){watch.observe(h);}});
  window.addEventListener("scroll",mark,{passive:true});
  mark();
}
})();
"""

_FALLBACK = {"serif": "Georgia,serif", "sans-serif": "system-ui,sans-serif", "monospace": "ui-monospace,monospace"}


def stylesheet(th: Theme) -> str:
    def stack(role: str) -> str:
        fam = th.fonts[role]
        return f'"{fam}",{_FALLBACK[families()[fam]["generic"]]}'
    serif_text = families()[th.text]["generic"] == "serif"
    return CSS % {
        **th.colour, **{k: th.signal[k] for k in ("good", "warn", "bad", "info")},
        "f_text": stack("text"), "f_label": stack("label"), "f_heading": stack("heading"), "f_mono": stack("mono"),
        "heading_weight": th.fonts.get("heading_weight", 700),
        "body_size": "17px" if serif_text else "16px",
        "radius": th.shape["radius"], "card_radius": min(12, th.shape["region_radius"]),
        "scheme": "dark" if th.dark else "light",
    }


class Page:
    def __init__(self, title: str, eyebrow: str | None = None, lead: str | None = None,
                 theme: Theme | None = None, contents: bool = False):
        """The page is in `theme`, by default the current one when it is rendered. With `contents`,
        each h2 gets an anchor and the page a contents bar of them: above the text on a narrow
        screen, beside it, held in view, on a wide one."""
        self.title, self.eyebrow, self.lead, self.theme = title, eyebrow, lead, theme
        self.contents = contents
        self.parts: list[str] = []
        self.heads: list[tuple[str, str]] = []           # (anchor, text) of each h2, for the contents
        self.stepped = False
        self.talked = False
        self.shown = False
        self.pinned = False
        self.diffed = False
        self.carded = False
        self.site: Site | None = None                    # the site the page belongs to, when it is one of many
        self.slug = ""

    @property
    def th(self) -> Theme:
        return self.theme or current()

    # -- text -----------------------------------------------------------------------------------
    def h2(self, text: str):
        if not self.contents:
            self.parts.append(f"<h2>{escape(text)}</h2>")
            return
        anchor = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
        taken = {a for a, _ in self.heads}
        n, base = 2, anchor
        while anchor in taken:
            anchor, n = f"{base}-{n}", n + 1
        self.heads.append((anchor, text))
        self.parts.append(f'<h2 id="{anchor}">{escape(text)}</h2>')

    def p(self, html: str):
        """A paragraph; `html` may hold inline markup (<code>, <em>, <strong>)."""
        self.parts.append(f"<p>{html}</p>")

    def html(self, html: str):
        self.parts.append(html)

    # -- figures --------------------------------------------------------------------------------
    @staticmethod
    def _checked(obj: Any, label: str | None) -> None:
        from .check import figure_issues, report
        where = f"figure \"{(label or 'untitled')[:50]}\""
        if isinstance(obj, Canvas):
            report(obj.check(), where)
        elif hasattr(obj, "savefig"):
            report(figure_issues(obj), where)

    @staticmethod
    def _figure(obj: Any, caption: str | None, min_width: str | None = None) -> str:
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        label = re.sub(r"<[^>]+>", "", caption) if caption else None
        Page._checked(obj, label)
        return f'<figure><div class="card">{inline_svg(obj, label, min_width)}</div>{cap}</figure>'

    def figure(self, obj: Any, caption: str | None = None, min_width: str | None = "560px"):
        """A figure across the column. Below `min_width` it scrolls sideways in its card rather
        than shrinking its text out of reach; None lets it shrink all the way."""
        self.parts.append(self._figure(obj, caption, min_width))

    def row(self, *figures: tuple[Any, str | None]):
        """Figures side by side, stacking on a narrow screen: row((fig, "caption"), …)."""
        self.parts.append('<div class="row">' + "".join(self._figure(o, c, None) for o, c in figures) + "</div>")

    def steps(self, frames: list[tuple[Any, str, str]], caption: str | None = None,
              min_width: str | None = "560px"):
        """A process the reader steps through: [(figure, title, html), …], one frame shown at a
        time under Previous, Next and a numbered button for each; the arrow keys turn them when
        the figure has the focus. Each figure is checked as a figure is. Printed or without
        scripts, the frames stand one under the other, each with its title and its text."""
        self.stepped = True
        total = len(frames)
        dots = "".join(f'<li><button type="button" aria-label="Step {k + 1} of {total}: {escape(title)}">{k + 1}'
                       f"</button></li>" for k, (_, title, _) in enumerate(frames))
        bar = ('<div class="steps-bar"><button type="button" data-step="prev" aria-label="Previous step">'
               '\u2190<span class="word"> Previous</span></button>'
               f'<ol class="steps-dots">{dots}</ol>'
               '<button type="button" data-step="next" aria-label="Next step"><span class="word">Next </span>\u2192'
               '</button></div>')
        body = []
        for k, (obj, title, html) in enumerate(frames):
            label = f"Step {k + 1}: {title}"
            self._checked(obj, label)
            body.append(f'<div class="step" aria-live="polite"><h3 class="step-title"><span class="n">{k + 1}/{total}</span>'
                        f'{escape(title)}</h3><div class="step-text"><p>{html}</p></div>'
                        f'<div class="step-fig">{inline_svg(obj, label, min_width)}</div></div>')
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        self.parts.append(f'<figure class="steps" tabindex="0"><div class="card">{bar}{"".join(body)}</div>{cap}</figure>')

    def image(self, path: str | Path, caption: str | None = None, alt: str | None = None):
        """A picture -- a screenshot, a photo -- embedded in the page as data, in a card across the
        column. WebP or JPEG keep a page light: a screenshot is best cut to the width it is shown at."""
        p = Path(path)
        kind = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".webp": "webp", ".gif": "gif"}[p.suffix.lower()]
        data = base64.b64encode(p.read_bytes()).decode("ascii")
        said = alt if alt is not None else (re.sub(r"<[^>]+>", "", caption) if caption else "")
        size = ""
        try:
            from PIL import Image                       # its size, so the page does not jump as it loads
            with Image.open(p) as im:
                size = f' width="{im.width}" height="{im.height}"'
        except Exception:
            pass
        self.shown = True
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        self.parts.append(f'<figure><div class="card shot"><img src="data:image/{kind};base64,{data}" '
                          f'alt="{escape(said)}"{size} loading="lazy" decoding="async"></div>{cap}</figure>')

    def annotated(self, path: str | Path, marks: list[tuple[float, float, str]], caption: str | None = None,
                  alt: str | None = None):
        """A screenshot with numbered markers on it and their legend under it: `marks` is [(x, y, html), …],
        x and y in the picture's own pixels, the html what that place is. The markers stay on their places at
        any width, being placed in percent of the picture."""
        from PIL import Image
        p = Path(path)
        with Image.open(p) as im:
            w, h = im.size
        kind = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".webp": "webp"}[p.suffix.lower()]
        data = base64.b64encode(p.read_bytes()).decode("ascii")
        said = alt if alt is not None else (re.sub(r"<[^>]+>", "", caption) if caption else "")
        pins = "".join(f'<span class="pin" style="left:{x / w * 100:.2f}%;top:{y / h * 100:.2f}%" aria-hidden="true">'
                       f"{k + 1}</span>" for k, (x, y, _) in enumerate(marks))
        legend = "".join(f'<li><span class="n">{k + 1}</span><span>{html}</span></li>' for k, (_, _, html) in enumerate(marks))
        self.shown = self.pinned = True
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        self.parts.append(f'<figure><div class="card shot"><div class="pin-wrap"><img src="data:image/{kind};base64,'
                          f'{data}" alt="{escape(said)}" width="{w}" height="{h}" loading="lazy" decoding="async">'
                          f'{pins}</div></div><ol class="pins">{legend}</ol>{cap}</figure>')

    def diff(self, before: str, after: str, caption: str | None = None, labels: tuple[str, str] = ("Before", "After"),
             context: int = 2):
        """A text before and after a change, side by side -- one under the other on a phone -- each line taken
        out marked on the left and each put in marked on the right; runs of unchanged lines longer than twice
        `context` are folded to a line that says how many."""
        import difflib
        a, b = before.splitlines(), after.splitlines()
        left: list[str] = []
        right: list[str] = []

        def line(kind: str, text: str) -> str:
            return f'<span class="{kind}">{escape(text) or " "}</span>'
        for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
            if tag == "equal":
                run = a[i1:i2]
                if len(run) > 2 * context + 1:
                    keep_head = run[:context] if left else []
                    keep_tail = run[-context:] if i2 < len(a) else []
                    folded = len(run) - len(keep_head) - len(keep_tail)
                    for side in (left, right):
                        side.extend(line("same", t) for t in keep_head)
                        side.append(line("gap", f"… {folded} unchanged line{'s' if folded != 1 else ''} …"))
                        side.extend(line("same", t) for t in keep_tail)
                else:
                    for side in (left, right):
                        side.extend(line("same", t) for t in run)
                continue
            gone, came = a[i1:i2], b[j1:j2]
            for k in range(max(len(gone), len(came))):
                left.append(line("del", gone[k]) if k < len(gone) else line("same", ""))
                right.append(line("add", came[k]) if k < len(came) else line("same", ""))
        self.diffed = True
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        self.parts.append(f'<figure class="diffs"><div class="diff"><div class="side"><div class="head">'
                          f'{escape(labels[0])}</div><pre>{"".join(left)}</pre></div><div class="side"><div class="head">'
                          f'{escape(labels[1])}</div><pre>{"".join(right)}</pre></div></div>{cap}</figure>')

    def cards(self, items: list[tuple[str, str, str]], kicker: list[str] | None = None):
        """Links as cards: [(href, title, html), …], each card a link, `kicker` an optional small line above
        each title (a chapter's number)."""
        self.carded = True
        tiles = "".join(f'<a class="tile" href="{escape(href)}">'
                        + (f'<div class="k">{escape(kicker[k])}</div>' if kicker else "")
                        + f'<div class="t">{escape(title)}</div><div class="d">{html}</div></a>'
                        for k, (href, title, html) in enumerate(items))
        self.parts.append(f'<div class="cards">{tiles}</div>')

    def chat(self, turns: list[tuple[str, str]], caption: str | None = None, you: str = "You",
             them: str = "Claude"):
        """A conversation: [("you", html), ("them", html), …], your turns at the right, the other's at
        the left, each named. A turn's html may hold <p>, <code> and <pre> for an answer laid out as
        text; escape your own text."""
        self.talked = True
        body = "".join(f'<div class="turn {side}"><div class="who">{escape(you if side == "you" else them)}</div>'
                       f"{html}</div>" for side, html in turns)
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        self.parts.append(f'<figure class="talk"><div class="chat">{body}</div>{cap}</figure>')

    # -- blocks ---------------------------------------------------------------------------------
    def callout(self, title: str, html: str, tone: str = "info"):
        """A coloured aside; the colours are given by name and filled in from the theme."""
        self.parts.append(f'<aside class="callout" data-tone="{tone}">'
                          f'<div class="title">{escape(title)}</div><p>{html}</p></aside>')

    def kpis(self, items: list[tuple[str, str, str, str]]):
        """Stat tiles: [(label, value, note, tone), …], tone being good | warn | bad | info | neutral."""
        tiles = "".join(f'<div class="kpi card"><div class="label">{escape(lab)}</div>'
                        f'<div class="value">{escape(val)}</div>'
                        f'<div class="note tone-{tone}">{escape(note)}</div></div>'
                        for lab, val, note, tone in items)
        self.parts.append(f'<div class="kpis">{tiles}</div>')

    def table(self, header: list[str], rows: list[list[str]], numeric: tuple[int, ...] = ()):
        """Cells are HTML. Columns named in `numeric` are right-aligned with figures that line up."""
        def cls(i: int) -> str:
            return ' class="num"' if i in numeric else ""
        head = "".join(f"<th{cls(i)}>{escape(h)}</th>" for i, h in enumerate(header))
        body = "".join("<tr>" + "".join(f"<td{cls(i)}>{c}</td>" for i, c in enumerate(r)) + "</tr>" for r in rows)
        self.parts.append(f'<div class="table card"><table><thead><tr>{head}</tr></thead>'
                          f"<tbody>{body}</tbody></table></div>")

    def frame(self, df: Any, numeric: tuple[int, ...] | None = None, index: bool = False, decimals: int = 1):
        """A pandas DataFrame as a table: columns of numbers -- found by their type unless `numeric`
        names them -- right-aligned, grouped by thousands, a column of fractions all to `decimals`
        places; the index left out unless asked."""
        import numbers
        if index:
            df = df.reset_index()
        cols = list(df.columns)
        if numeric is None:
            numeric = tuple(i for i, c in enumerate(cols) if str(df[c].dtype).startswith(("int", "float", "Int", "Float")))
        fractions = {i for i, c in enumerate(cols) if str(df[c].dtype).lower().startswith("float")}
        nnbsp = chr(0x202F)                              # a narrow no-break space between thousands

        def cell(i: int, v: Any) -> str:
            if isinstance(v, bool) or not isinstance(v, numbers.Number):
                return escape(str(v))
            f = float(v)  # pyright: ignore[reportArgumentType]
            text = f"{f:,.{decimals}f}" if i in fractions else f"{int(f):,}"
            return text.replace(",", nnbsp)
        rows = [[cell(i, v) for i, v in enumerate(row)] for row in df.itertuples(index=False)]
        self.table([str(c) for c in cols], rows, numeric)

    def code(self, src: str, language: str | None = None, caption: str | None = None):
        """Source code, highlighted in the theme's colours (Pygments) when it knows the language."""
        from .code import highlight
        block = highlight(src, language)
        self.parts.append(f"<figure>{block}<figcaption>{caption}</figcaption></figure>" if caption else block)

    def markdown(self, text: str, base: Path | None = None):
        """Markdown, set as the rest of the page is: its top headings as h2 (the page's title is the
        only h1), tables in cards, code highlighted, and images beside it -- relative to `base`
        -- embedded: an SVG inline, so it keeps the page's fonts, anything else as data."""
        from markdown_it import MarkdownIt

        from .code import highlight
        md = MarkdownIt("commonmark", {"highlight": lambda src, lang, _attrs: highlight(src, lang or None)})
        md.enable("table")
        tokens = md.parse(text)
        levels = [int(t.tag[1]) for t in tokens if t.type == "heading_open"]
        shift = 2 - min(levels) if levels else 0          # its top headings become h2, under the title
        for tok in tokens:
            if tok.type in ("heading_open", "heading_close"):
                tok.tag = f"h{min(6, int(tok.tag[1]) + shift)}"
            for child in tok.children or []:
                if child.type == "image" and base is not None:
                    src = str(child.attrs.get("src", ""))
                    path = (base / src) if src and "://" not in src and not src.startswith("data:") else None
                    if path and path.exists():
                        if path.suffix.lower() == ".svg":
                            child.type = "html_inline"           # scrolls in its own box on a phone, as figures do
                            child.content = f'<span class="mdfig">{inline_svg(path, child.content or None, "480px")}</span>'
                        else:
                            kind = "jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else path.suffix.lower()[1:]
                            child.attrs["src"] = (f"data:image/{kind};base64,"
                                                  + base64.b64encode(path.read_bytes()).decode("ascii"))
        html = md.renderer.render(tokens, md.options, {})
        html = html.replace("<table>", '<div class="table card"><table>').replace("</table>", "</table></div>")
        self.parts.append(f'<div class="md">{html}</div>')

    # -- output ---------------------------------------------------------------------------------
    def body(self, footer: str | None = None) -> tuple[str, str, bool]:
        """The page's body, the styles it needs beyond the theme's, and whether it needs its script."""
        eyebrow = f'<div class="eyebrow">{escape(self.eyebrow)}</div>' if self.eyebrow else ""
        lead = f"<p>{self.lead}</p>" if self.lead else ""
        foot = f"<footer>{footer}</footer>" if footer else ""
        pager = self.site.pager(self.slug) if self.site else ""
        body = (f"<main><header>{eyebrow}<h1>{escape(self.title)}</h1>{lead}</header>"
                + "\n".join(self.parts) + pager + foot + "</main>")
        extra_css = ""
        sections = "".join(f'<li><a href="#{a}">{escape(text)}</a></li>' for a, text in self.heads)
        if self.site:
            body = (f'<div class="topbar"><a href="{self.site.home}">{escape(self.site.title)}</a></div>'
                    f'<div class="frame"><nav class="toc" aria-label="Chapters"><div class="card"><details>'
                    f'<summary>Chapters</summary>{self.site.chapters(self.slug, sections)}</details>'
                    f'</div></nav>{body}</div>')
            extra_css += CONTENTS_CSS + SITE_CSS
        elif self.contents and self.heads:
            body = (f'<div class="frame"><nav class="toc" aria-label="Contents"><div class="card">'
                    f'<div class="toc-title">Contents</div><ol>{sections}</ol></div></nav>{body}</div>')
            extra_css += CONTENTS_CSS
        if self.stepped:
            extra_css += STEPS_CSS
        script_wanted = bool(extra_css)                   # only contents and steps have behaviour
        for wanted, css in ((self.talked, CHAT_CSS), (self.shown, SHOT_CSS), (self.pinned, PINS_CSS),
                            (self.diffed, DIFF_CSS), (self.carded, CARDS_CSS)):
            if wanted:
                extra_css += css
        return body, extra_css, script_wanted

    def render(self, footer: str | None = None, fonts_href: str | None = None) -> str:
        """The whole page. With `fonts_href` the page links that stylesheet for its fonts, as the pages of a
        site share one, in place of carrying them itself."""
        th = self.th
        body, extra_css, script_wanted = self.body(footer)
        script, head_script = "", ""
        if script_wanted:
            head_script = '<script>document.documentElement.classList.add("js")</script>'
            script = f"<script>{SCRIPT}</script>"
        fams = list(dict.fromkeys(th.families_used() + families_in(body)))
        tone_css = "".join(f'.callout[data-tone="{k}"]{{--tone:{c};--tone-fill:{f}}}' for k, (c, f) in tones(th).items())
        if 'class="code"' in body:
            from .code import css as code_css
            tone_css += "\n" + code_css(th, "pre.code")
        sig = th.signal
        tone_css += (f":root{{--good:{sig['good']};--good-fill:{sig['good_fill']};--bad:{sig['bad']};"
                     f"--bad-fill:{sig['bad_fill']}}}") if self.diffed else ""
        fonts = (f'<link rel="stylesheet" href="{escape(fonts_href)}">' if fonts_href else "")
        faces = "" if fonts_href else font_faces(body, fams) + "\n"
        title = f"{self.title} -- {self.site.title}" if self.site and self.slug != self.site.home_slug else self.title
        return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                f"<title>{escape(title)}</title>{head_script}{fonts}<style>{faces}{stylesheet(th)}"
                f"{tone_css}{extra_css}</style></head><body>{body}{script}</body></html>\n")

    def save(self, target: str | Path, footer: str | None = None) -> Path:
        p = out_path(target, ".html")
        p.write_text(self.render(footer), encoding="utf-8")
        return p


class Site:
    """Pages that belong together, written as a folder: each a Page with the site's navigation -- every
    chapter by its title, the one being read open on its own sections -- a link to the one before and after
    it, and one stylesheet of fonts, fonts.css, which every page links, so that the fonts are carried once
    for the whole site and cached by the browser, cut down to the characters every page uses.

        site = Site("Using the skill", "docs/manual")
        home = site.page("index", "Welcome", lead="…")    # the first page added is the home
        one = site.page("01-start", "Start here")
        one.h2("…"); one.chat(…)
        site.save(footer="…")
    """

    def __init__(self, title: str, folder: str | Path, theme: Theme | None = None):
        self.title, self.folder, self.theme = title, Path(folder), theme
        self.pages: list[Page] = []

    @property
    def home_slug(self) -> str:
        return self.pages[0].slug if self.pages else "index"

    @property
    def home(self) -> str:
        return f"{self.home_slug}.html"

    def page(self, slug: str, title: str, eyebrow: str | None = None, lead: str | None = None) -> Page:
        page = Page(title, eyebrow=eyebrow, lead=lead, theme=self.theme, contents=True)
        page.site, page.slug = self, slug
        self.pages.append(page)
        return page

    def chapters(self, current: str, sections: str) -> str:
        """The home page by itself, then the others numbered from 1: the one being read open on its sections."""
        def item(page: Page, tag: str) -> str:
            here = page.slug == current
            inner = f'<ol class="sections">{sections}</ol>' if here and sections else ""
            return (f'<{tag} class="{"current" if here else ""}"><a href="{page.slug}.html"'
                    f'{" aria-current=\"page\"" if here else ""}>{escape(page.title)}</a>{inner}</{tag}>')
        home, rest = self.pages[0], self.pages[1:]
        return (f'<div class="home-link">{item(home, "div")}</div>'
                f'<ol class="chapters">{"".join(item(page, "li") for page in rest)}</ol>')

    def pager(self, current: str) -> str:
        slugs = [p.slug for p in self.pages]
        i = slugs.index(current)
        prev = self.pages[i - 1] if i > 0 else None
        nxt = self.pages[i + 1] if i + 1 < len(self.pages) else None
        links = ""
        if prev:
            links += f'<a class="prev" href="{prev.slug}.html">\u2190 Previous<strong>{escape(prev.title)}</strong></a>'
        if nxt:
            links += f'<a class="next" href="{nxt.slug}.html">Next \u2192<strong>{escape(nxt.title)}</strong></a>'
        return f'<nav class="pager" aria-label="Pages">{links}</nav>'

    def save(self, footer: str | None = None) -> list[Path]:
        """Every page, and fonts.css with every face they use, cut to the characters of all of them."""
        th = self.theme or current()
        self.folder.mkdir(parents=True, exist_ok=True)
        bodies = [page.body(footer)[0] for page in self.pages]
        text = "".join(bodies)
        fams = list(dict.fromkeys(th.families_used() + families_in(text)))
        (self.folder / "fonts.css").write_text(font_faces(text, fams) + "\n", encoding="utf-8")
        written = []
        for page in self.pages:
            out = self.folder / f"{page.slug}.html"
            out.write_text(page.render(footer, fonts_href="fonts.css"), encoding="utf-8")
            written.append(out)
        return written



# ----------------------------------------------------------------------------------------------
# Slides
# ----------------------------------------------------------------------------------------------
DECK_CSS = """
:root{--on:{on}}
html,body{height:100%}
body{overflow:hidden}
main.deck{max-width:none;margin:0;padding:0;position:fixed;inset:0}
.slide{position:absolute;left:50%;top:50%;width:1280px;height:720px;margin:-360px 0 0 -640px;transform:scale(var(--s,1));
background:var(--paper);border:1px solid var(--rule);box-shadow:0 12px 40px rgba(0,0,0,.08);display:none;
flex-direction:column;overflow:hidden;font:400 26px/1.45 var(--label);color:var(--ink)}
.slide.on{display:flex}
html:not(.js) body{overflow:auto}
html:not(.js) main.deck{position:static}
html:not(.js) .slide{display:flex;position:relative;left:auto;top:auto;margin:24px auto;transform:none}
.slide .inner{flex:1;display:flex;flex-direction:column;padding:52px 80px 0;min-height:0}
.slide .kicker{font:700 16px/1.3 var(--label);letter-spacing:.08em;text-transform:uppercase;color:var(--accent);
margin-bottom:10px}
.slide h2.st{font:{heading_weight} 44px/1.15 var(--head);color:var(--heading);margin:0 0 4px}
.slide .sub{font:400 24px/1.4 var(--label);color:var(--muted);margin:4px 0 0}
.slide .body{flex:1;min-height:0;margin-top:26px}
.slide .body>:first-child{margin-top:0}
.slide .body p{margin:0 0 18px}
.slide .body h2{font-size:30px;margin:0 0 12px}
.slide .body h3{font:600 26px/1.3 var(--label);color:var(--heading);margin:0 0 10px}
.slide .body ul,.slide .body ol{margin:0 0 18px;padding-left:34px}
.slide .body li{margin:0 0 10px}
.slide .md{font:inherit}
.slide .cols{display:grid;grid-template-columns:1fr 1fr;gap:48px}
.slide .cols>div{min-width:0}
.slide figure{margin:0 0 10px}
.slide figure .card{padding:14px;justify-content:center}
.slide figcaption{font-size:18px;margin-top:10px}
.slide .kpis{grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;margin:0 0 18px}
.slide .kpi .label{font-size:16px}.slide .kpi .value{font-size:50px;margin:10px 0 4px}.slide .kpi .note{font-size:19px}
.slide .callout{padding:16px 22px;margin:0 0 18px}.slide .callout .title{font-size:19px}
.slide .table{padding:0}
.slide table{font-size:21px;min-width:0}.slide th{font-size:17px;padding:10px 16px}.slide td{padding:10px 16px}
.slide pre.code{font-size:19px;margin:0 0 18px}
.slide .foot{display:flex;justify-content:space-between;gap:24px;padding:0 80px 24px;font:400 15px/1 var(--label);
color:var(--muted)}
.slide .progress{position:absolute;left:0;bottom:0;height:4px;background:var(--accent)}
.slide.l-title .inner{justify-content:center;padding-left:96px;box-shadow:inset 12px 0 var(--accent)}
.slide.l-title h2.st{font-size:66px;max-width:1040px}
.slide.l-title .sub{font-size:30px;max-width:980px;margin-top:14px}
.slide.l-section{background:var(--accent)}
.slide.l-section .inner{justify-content:center}
.slide.l-section h2.st{color:var(--on);font-size:62px}
.slide.l-section .kicker,.slide.l-section .sub,.slide.l-section .foot{color:var(--on)}
.slide.l-section .progress{background:var(--on)}
.slide.l-statement .inner{justify-content:center;align-items:center;text-align:center}
.slide.l-statement h2.st{font-size:110px;line-height:1.02;max-width:1100px;letter-spacing:-.01em}
.slide.l-statement .sub{font-size:32px;max-width:900px;margin-top:18px}
.slide.l-statement .body{flex:none;margin-top:30px}
.notes{display:none}
@media print{@page{size:1280px 720px;margin:0}
html,body{height:auto;overflow:visible;background:none}
main.deck{position:static}
.slide,.js .slide{display:flex!important;position:relative;left:0;top:0;margin:0;transform:none;border:0;box-shadow:none;
break-after:page}}
@media (forced-colors:active){.slide{border:1px solid CanvasText}}
"""

DECK_SCRIPT = """
(function(){
var slides=document.querySelectorAll(".slide"),n=slides.length,i=0,x0=null;
function fit(){document.documentElement.style.setProperty("--s",Math.min(innerWidth/1280,innerHeight/720)*0.96);}
function show(k,quiet){
  i=Math.max(0,Math.min(n-1,k));
  slides.forEach(function(s,j){s.classList.toggle("on",j===i);s.setAttribute("aria-hidden",j===i?"false":"true");});
  if(!quiet&&history.replaceState){history.replaceState(null,"","#"+(i+1));}
}
function fromHash(){var m=/^#(\\d+)$/.exec(location.hash);return m?parseInt(m[1],10)-1:0;}
addEventListener("resize",fit);
addEventListener("hashchange",function(){show(fromHash(),true);});
addEventListener("keydown",function(e){
  if(e.altKey||e.ctrlKey||e.metaKey){return;}
  var k=e.key;
  if(k==="ArrowRight"||k==="PageDown"||k===" "||k==="Enter"){show(i+1);e.preventDefault();}
  else if(k==="ArrowLeft"||k==="PageUp"||k==="Backspace"){show(i-1);e.preventDefault();}
  else if(k==="Home"){show(0);e.preventDefault();}
  else if(k==="End"){show(n-1);e.preventDefault();}
});
document.addEventListener("click",function(e){
  if(e.target.closest("a,button,pre,table,summary,input")||String(getSelection())){return;}
  show(e.clientX>innerWidth/3?i+1:i-1);
});
document.addEventListener("touchstart",function(e){x0=e.touches[0].clientX;},{passive:true});
document.addEventListener("touchend",function(e){
  if(x0===null){return;}
  var d=e.changedTouches[0].clientX-x0;
  if(Math.abs(d)>50){show(d<0?i+1:i-1);}
  x0=null;
},{passive:true});
fit();
show(fromHash(),true);
})();
"""

SLIDE_W, SLIDE_H = 1280, 720
SLIDE_LAYOUTS = ("title", "section", "content", "two-column", "statement")


def _svg_px(markup: str) -> tuple[float, float] | None:
    """An SVG's drawn size in CSS pixels, from its width and height (px or pt)."""
    tag = re.match(r"<svg\b[^>]*>", markup[markup.find("<svg"):])
    if tag is None:
        return None
    size = []
    for key in ("width", "height"):
        m = re.search(rf'\s{key}="([\d.]+)(pt|px)?"', tag.group(0))
        if m is None:
            return None
        size.append(float(m.group(1)) * (4 / 3 if m.group(2) == "pt" else 1))
    return size[0], size[1]


class _Fitted(Page):
    """A Page whose figures are sized to fill a slide's room: up to twice the size they were drawn at."""

    room = (SLIDE_W - 160.0, 440.0)

    def figure(self, obj: Any, caption: str | None = None, min_width: str | None = None):
        label = re.sub(r"<[^>]+>", "", caption) if caption else None
        self._checked(obj, label)
        markup = svg_markup(obj)
        svg = inline_svg(markup, label)
        size = _svg_px(markup)
        if size:
            w, h = size
            room_w, room_h = self.room[0], self.room[1] - (44 if caption else 0)
            scale = min(2.0, room_w / w, room_h / h)       # drawn as vectors: larger reads better across a room
            svg = re.sub(r"max-width:[^;\"]+", f"max-width:{w * scale:.0f}px", svg, count=1)
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        self.parts.append(f'<figure><div class="card">{svg}</div>{cap}</figure>')


class Slide(_Fitted):
    """One slide of a Deck: a title, a subtitle, and blocks added as to a Page (p, markdown, figure,
    kpis, callout, table, code, row). A two-column slide takes its second column's blocks on `.right`."""

    def __init__(self, deck: Deck, title: str | None, subtitle: str | None, layout: str, kicker: str | None,
                 notes: str | None):
        if layout not in SLIDE_LAYOUTS:
            raise ValueError(f"layout {layout!r} is not one of {', '.join(SLIDE_LAYOUTS)}")
        super().__init__(title or "", theme=deck.theme)
        self.deck, self.subtitle, self.layout, self.kicker, self.notes = deck, subtitle, layout, kicker, notes
        half = (SLIDE_W - 160 - 48) / 2
        self.right: _Fitted | None = None
        if layout == "two-column":
            self.room = (half, 470.0)
            self.right = _Fitted("", theme=deck.theme)
            self.right.room = (half, 470.0)
        elif layout == "statement":
            self.room = (SLIDE_W - 160.0, 260.0)

    def markup(self, k: int, n: int, footer: str | None) -> str:
        kicker = f'<div class="kicker">{escape(self.kicker)}</div>' if self.kicker else ""
        title = f'<h2 class="st">{escape(self.title)}</h2>' if self.title else ""
        sub = f'<p class="sub">{self.subtitle}</p>' if self.subtitle else ""
        if self.right is not None:
            body = (f'<div class="body cols"><div>{"".join(self.parts)}</div>'
                    f'<div>{"".join(self.right.parts)}</div></div>')
        else:
            body = f'<div class="body">{"".join(self.parts)}</div>' if self.parts else ""
        notes = f'<aside class="notes">{self.notes}</aside>' if self.notes else ""
        name = f": {escape(self.title)}" if self.title else ""
        return (f'<section class="slide l-{self.layout}" aria-roledescription="slide" '
                f'aria-label="Slide {k + 1} of {n}{name}"><div class="inner">{kicker}{title}{sub}{body}</div>'
                f'<div class="foot"><span>{escape(footer or "")}</span><span>{k + 1} / {n}</span></div>'
                f'<div class="progress" style="width:{(k + 1) / n * 100:.2f}%"></div>{notes}</section>')


class Deck:
    """Slides in one self-contained HTML file, in the look of the pages: 16:9, 1280 by 720, scaled to
    the window; the arrow keys, space, a click or a swipe turn them; the address keeps the slide
    (deck.html#4); printed, one slide a page. Each slide is a Slide -- a Page -- so it takes the
    blocks a page does.

        deck = Deck("Order events on a queue", footer="Orders platform · November 2026")
        deck.slide("Order events on a queue", "Why, which, and when", layout="title")
        s = deck.slide("What it costs today", kicker="The problem")
        s.kpis([...]); s.figure(chart, "Polling costs more than the reads.")
        two = deck.slide("Kafka or SQS", layout="two-column"); two.p("…"); two.right.p("…")
        deck.slide("612 000", "order reads a day", layout="statement")
        deck.save("deck.html")

    Layouts: title (a cover), section (a divider in the accent colour), content, two-column,
    statement (one large figure or sentence). Without scripts, the slides stand one under the other.
    """

    def __init__(self, title: str, theme: Theme | None = None, footer: str | None = None):
        self.title, self.theme, self.footer = title, theme, footer
        self.slides: list[Slide] = []

    def slide(self, title: str | None = None, subtitle: str | None = None, layout: str = "content",
              kicker: str | None = None, notes: str | None = None) -> Slide:
        """A new slide at the end. `subtitle` and `notes` are HTML (escape your own text); notes are
        kept in the file, not shown."""
        s = Slide(self, title, subtitle, layout, kicker, notes)
        self.slides.append(s)
        return s

    def render(self) -> str:
        th = self.theme or current()
        n = len(self.slides)
        body = ('<main class="deck" aria-roledescription="slide deck">'
                + "".join(s.markup(k, n, self.footer) for k, s in enumerate(self.slides)) + "</main>")
        pages: list[Page] = [p for s in self.slides for p in (s, s.right) if p is not None]
        extra = ""
        for flag, css in (("stepped", STEPS_CSS), ("talked", CHAT_CSS), ("shown", SHOT_CSS), ("pinned", PINS_CSS),
                          ("diffed", DIFF_CSS), ("carded", CARDS_CSS)):
            if any(getattr(p, flag) for p in pages):
                extra += css
        tone_css = "".join(f'.callout[data-tone="{k}"]{{--tone:{c};--tone-fill:{f}}}' for k, (c, f) in tones(th).items())
        if 'class="code"' in body:
            from .code import css as code_css
            tone_css += "\n" + code_css(th, "pre.code")
        sig = th.signal
        if any(p.diffed for p in pages):
            tone_css += (f":root{{--good:{sig['good']};--good-fill:{sig['good_fill']};--bad:{sig['bad']};"
                         f"--bad-fill:{sig['bad_fill']}}}")
        deck_css = (DECK_CSS.replace("{on}", th.colour["on"])
                    .replace("{heading_weight}", str(th.fonts.get("heading_weight", 700))))
        script = (SCRIPT if any(p.stepped for p in pages) else "") + DECK_SCRIPT
        fams = list(dict.fromkeys(th.families_used() + families_in(body)))
        return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                f"<title>{escape(self.title)}</title>"
                '<script>document.documentElement.classList.add("js")</script>'
                f"<style>{font_faces(body, fams)}\n{stylesheet(th)}{tone_css}{extra}{deck_css}</style></head>"
                f"<body>{body}<script>{script}</script></body></html>\n")

    def save(self, target: str | Path) -> Path:
        p = out_path(target, ".html")
        p.write_text(self.render(), encoding="utf-8")
        return p


__all__ = ["Page", "Site", "Deck", "Slide", "inline_svg", "svg_markup", "font_faces", "stylesheet", "tones"]
