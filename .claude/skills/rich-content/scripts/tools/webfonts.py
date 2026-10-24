"""
webfonts — how an HTML page gets its fonts: linked from Google Fonts, with system fonts behind them
made to take the same room.

    from tools.webfonts import head, stack, adjust
    head(["Crimson Pro", "Geist"])    # the <link> tags and the fallback @font-face rules
    stack("Crimson Pro")              # '"Crimson Pro","Crimson Pro fallback Georgia",…,Georgia,serif'
    adjust("Crimson Pro")             # 'font-size-adjust:…' for a family set larger than its size

    python -m tools.webfonts          # measure again: writes themes/fallbacks.json

A page links its fonts and carries none of them; only a PDF embeds its fonts. When the link does not
answer -- offline, or blocked -- the page is set in the system fonts named after each family. Each of those
is declared as a fallback face, `src: local(…)`, sized and spaced (size-adjust, ascent-, descent- and
line-gap-override) so its average letter is as wide as the web font's and its lines as tall: the text
and the diagrams measured in the web font keep their room, and nothing moves when the web font arrives.

LOCALS is every system font a family may fall back to, by the names a browser finds it under (its
full name and its PostScript name, and those of the fonts made to its measure: Liberation and Arimo for
Arial, Liberation Serif and Tinos for Times New Roman, Liberation Mono and Cousine for Courier New, DejaVu
Sans Mono for Menlo). fonts.json names, per family, which of them, in order.
The measurements are read from the font files -- the web font's in the venv, the system font's on this
machine (Windows, or matplotlib's copy of DejaVu) -- so `python -m tools.webfonts` runs where they are,
and writes what it found to themes/fallbacks.json, which the pages are built from.

A family set larger than its nominal size (fonts.json `scale`, for a face with a small x-height) is
enlarged on a page by font-size-adjust, which scales the glyphs and not the em: line heights and
em sizes stay as they are, and the fallback is brought to the same x-height by it too, as its font file
declares that height (OS/2 sxHeight); size-adjust is then undone, as CSS has it. So the fallbacks of such a family
are fonts whose declared x-height brings them close to its width, and a little under it: Georgia (3.5 % narrower than
Crimson Pro and EB Garamond), then Times New Roman (5 %) -- not Palatino, which declares an x-height its x does not
reach and comes out 9.5 % narrower.
"""
from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

from .theme import FALLBACKS, families, font_file

WINDOWS = Path("C:/Windows/Fonts")
GOOGLE = "https://fonts.googleapis.com/css2"
GENERIC = {"serif": "Georgia,serif", "sans-serif": "system-ui,sans-serif", "monospace": "ui-monospace,monospace"}


def _names(*fonts: tuple[str, str]) -> list[str]:
    return [name for pair in fonts for name in pair]


# Each: the file it is measured from, and its names for regular, bold and italic.
LOCALS: dict[str, dict] = {
    "Segoe UI": {"file": WINDOWS / "segoeui.ttf",
                 "400": _names(("Segoe UI", "SegoeUI")),
                 "700": _names(("Segoe UI Bold", "SegoeUI-Bold")),
                 "400i": _names(("Segoe UI Italic", "SegoeUI-Italic"))},
    "Arial": {"file": WINDOWS / "arial.ttf",
              "400": _names(("Arial", "ArialMT"), ("Liberation Sans", "LiberationSans"), ("Arimo", "Arimo-Regular")),
              "700": _names(("Arial Bold", "Arial-BoldMT"), ("Liberation Sans Bold", "LiberationSans-Bold"),
                            ("Arimo Bold", "Arimo-Bold")),
              "400i": _names(("Arial Italic", "Arial-ItalicMT"), ("Liberation Sans Italic", "LiberationSans-Italic"),
                             ("Arimo Italic", "Arimo-Italic"))},
    "Verdana": {"file": WINDOWS / "verdana.ttf",
                "400": _names(("Verdana", "Verdana")),
                "700": _names(("Verdana Bold", "Verdana-Bold")),
                "400i": _names(("Verdana Italic", "Verdana-Italic"))},
    "DejaVu Sans": {"file": "DejaVuSans.ttf",
                    "400": _names(("DejaVu Sans", "DejaVuSans")),
                    "700": _names(("DejaVu Sans Bold", "DejaVuSans-Bold")),
                    "400i": _names(("DejaVu Sans Oblique", "DejaVuSans-Oblique"))},
    "Georgia": {"file": WINDOWS / "georgia.ttf",
                "400": _names(("Georgia", "Georgia")),
                "700": _names(("Georgia Bold", "Georgia-Bold")),
                "400i": _names(("Georgia Italic", "Georgia-Italic"))},
    "Times New Roman": {"file": WINDOWS / "times.ttf",
                        "400": _names(("Times New Roman", "TimesNewRomanPSMT"), ("Liberation Serif", "LiberationSerif"),
                                      ("Tinos", "Tinos-Regular")),
                        "700": _names(("Times New Roman Bold", "TimesNewRomanPS-BoldMT"),
                                      ("Liberation Serif Bold", "LiberationSerif-Bold"), ("Tinos Bold", "Tinos-Bold")),
                        "400i": _names(("Times New Roman Italic", "TimesNewRomanPS-ItalicMT"),
                                       ("Liberation Serif Italic", "LiberationSerif-Italic"),
                                       ("Tinos Italic", "Tinos-Italic"))},
    "Consolas": {"file": WINDOWS / "consola.ttf",
                 "400": _names(("Consolas", "Consolas")),
                 "700": _names(("Consolas Bold", "Consolas-Bold")),
                 "400i": _names(("Consolas Italic", "Consolas-Italic"))},
    "Menlo": {"file": "DejaVuSansMono.ttf",
              "400": _names(("Menlo Regular", "Menlo-Regular"), ("DejaVu Sans Mono", "DejaVuSansMono")),
              "700": _names(("Menlo Bold", "Menlo-Bold"), ("DejaVu Sans Mono Bold", "DejaVuSansMono-Bold")),
              "400i": _names(("Menlo Italic", "Menlo-Italic"), ("DejaVu Sans Mono Oblique", "DejaVuSansMono-Oblique"))},
    "Courier New": {"file": WINDOWS / "cour.ttf",
                    "400": _names(("Courier New", "CourierNewPSMT"), ("Liberation Mono", "LiberationMono"),
                                  ("Cousine", "Cousine-Regular")),
                    "700": _names(("Courier New Bold", "CourierNewPS-BoldMT"),
                                  ("Liberation Mono Bold", "LiberationMono-Bold"), ("Cousine Bold", "Cousine-Bold")),
                    "400i": _names(("Courier New Italic", "CourierNewPS-ItalicMT"),
                                   ("Liberation Mono Italic", "LiberationMono-Italic"),
                                   ("Cousine Italic", "Cousine-Italic"))},
}

# How often each letter, and the space, comes in English text: the average letter is weighed by it.
FREQUENCY = {" ": 18.3, "e": 10.3, "t": 7.5, "a": 6.5, "o": 6.2, "n": 5.7, "i": 5.7, "s": 5.3, "r": 5.0,
             "h": 5.0, "l": 3.3, "d": 3.3, "u": 2.3, "c": 2.2, "m": 2.0, "f": 2.0, "w": 1.7, "g": 1.6,
             "y": 1.4, "p": 1.5, "b": 1.3, "v": 0.8, "k": 0.6, "x": 0.1, "j": 0.1, "q": 0.1, "z": 0.1}


# ----------------------------------------------------------------------------------------------
# Measuring
# ----------------------------------------------------------------------------------------------
def _local_file(name: str) -> Path:
    f = LOCALS[name]["file"]
    if isinstance(f, Path):
        return f
    import matplotlib
    return Path(matplotlib.get_data_path()) / "fonts" / "ttf" / f


def _metrics(path: Path) -> dict[str, float]:
    """Per em: the average letter, weighed by FREQUENCY; the ascent, descent and line gap; the x-height."""
    from fontTools.ttLib import TTFont
    font = TTFont(str(path), lazy=True)
    upm = font["head"].unitsPerEm
    cmap, hmtx, hhea = font.getBestCmap(), font["hmtx"], font["hhea"]
    total = sum(FREQUENCY.values())
    avg = sum(hmtx[cmap[ord(ch)]][0] * w for ch, w in FREQUENCY.items()) / total
    os2 = font["OS/2"]
    x_height = getattr(os2, "sxHeight", 0) or 0
    return {"avg": avg / upm, "ascent": hhea.ascent / upm, "descent": -hhea.descent / upm,
            "line_gap": hhea.lineGap / upm, "x_height": x_height / upm}


def measure() -> dict[str, dict]:
    """For each family: its x-height, and for each system font behind it, how to size and space it."""
    out: dict[str, dict] = {}
    for fam, entry in families().items():
        web = _metrics(font_file(fam))
        behind = {}
        for local in entry.get("fallbacks", []):
            sys_m = _metrics(_local_file(local))
            # A family a page enlarges by font-size-adjust has its fallback sized by it too, to the same x-height;
            # a browser may apply size-adjust after that as well, so the face gives none, and its line metrics
            # are those of the web font at the size the x-height brings the fallback to.
            k = web["avg"] / sys_m["avg"] if entry.get("scale", 1) == 1 else web["x_height"] / sys_m["x_height"]
            if entry.get("scale", 1) != 1:
                behind[local] = {"size_adjust": 100.0, "ascent": round(web["ascent"] / k * 100, 2),
                                 "descent": round(web["descent"] / k * 100, 2),
                                 "line_gap": round(web["line_gap"] / k * 100, 2)}
                continue
            behind[local] = {"size_adjust": round(k * 100, 2), "ascent": round(web["ascent"] / k * 100, 2),
                             "descent": round(web["descent"] / k * 100, 2),
                             "line_gap": round(web["line_gap"] / k * 100, 2)}
        out[fam] = {"x_height": round(web["x_height"], 4), "fallbacks": behind}
    return out


@lru_cache(maxsize=None)
def measured() -> dict[str, dict]:
    return {k: v for k, v in json.loads(FALLBACKS.read_text(encoding="utf-8")).items() if not k.startswith("_")}


# ----------------------------------------------------------------------------------------------
# What a page carries
# ----------------------------------------------------------------------------------------------
def _face_name(family: str, local: str) -> str:
    return f"{family} fallback {local}"


def stack(family: str) -> str:
    """The font-family list for a family: itself, its measured fallbacks, then the system's own."""
    names = [family] + [_face_name(family, local) for local in measured()[family]["fallbacks"]]
    return ",".join(f'"{n}"' for n in names) + "," + GENERIC[families()[family]["generic"]]


def href(fams: list[str]) -> str:
    """The Google Fonts stylesheet for these families, at the weights and styles fonts.json carries."""
    parts = []
    for fam in fams:
        keys = families()[fam]["files"]
        upright = sorted(int(k) for k in keys if not k.endswith("i"))
        italic = sorted(int(k[:-1]) for k in keys if k.endswith("i"))
        if italic:
            axes = "ital,wght@" + ";".join([f"0,{w}" for w in upright] + [f"1,{w}" for w in italic])
        else:
            axes = "wght@" + ";".join(str(w) for w in upright)
        parts.append(f"family={fam.replace(' ', '+')}:{axes}")
    return f"{GOOGLE}?{'&'.join(parts)}&display=swap"


def links(fams: list[str]) -> str:
    """The <link> tags that load the families: a connection opened early to both Google hosts, then the stylesheet."""
    return ('<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="{href(fams)}">')


def faces(fams: list[str]) -> str:
    """The fallback @font-face rules: each system font behind each family, regular, bold and italic."""
    rules = []
    for fam in fams:
        for local, m in measured()[fam]["fallbacks"].items():
            sizing = (f"size-adjust:{m['size_adjust']:g}%;ascent-override:{m['ascent']:g}%;"
                      f"descent-override:{m['descent']:g}%;line-gap-override:{m['line_gap']:g}%")
            for key, weight, style in (("400", "100 549", "normal"), ("700", "550 900", "normal"),
                                       ("400i", "100 900", "italic")):
                src = ",".join(f'local("{n}")' for n in LOCALS[local][key])
                rules.append(f'@font-face{{font-family:"{_face_name(fam, local)}";src:{src};'
                             f'font-weight:{weight};font-style:{style};{sizing}}}')
    return "\n".join(rules)


def head(fams: list[str]) -> tuple[str, str]:
    """What a page puts in its <head> for these families: the links, and the CSS of its fallback faces."""
    return links(fams), faces(fams)


def adjust(family: str) -> str:
    """font-size-adjust for a family set larger than its size, or none: it scales the glyphs, not the em."""
    scale = families()[family].get("scale", 1)
    return f"{measured()[family]['x_height'] * scale:.4f}" if scale != 1 else "none"


def main(argv: list[str]) -> int:
    data = {"_comment": "Written by `python -m tools.webfonts` (tools/webfonts.py says how): per family, its "
                        "x-height per em, and for each system font fonts.json puts behind it, the size-adjust "
                        "that makes its average letter as wide as the family's and the ascent, descent and "
                        "line-gap overrides that make its lines as tall, in per cent.",
            **measure()}
    FALLBACKS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"webfonts: wrote {FALLBACKS.name}, {len(data) - 1} families")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
