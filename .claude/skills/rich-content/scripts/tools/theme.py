"""
theme — the look every output is made in. A theme is a style and a mode: `corporate-dark` is the
corporate style -- its fonts, corners, lines and chart style -- in its dark colours. Each style is
one JSON file in the skill's themes/ folder (or a project's own), holding what its modes share and,
under "modes", each mode's colours; a bare style name means its light mode.

Which theme, the first found winning:
  1. use_theme("corporate-dark") in a build script, before drawing (or a path to a style file,
     with mode= for its mode);
  2. RICH_CONTENT_THEME=corporate-dark in the environment, for one run;
  3. rich-content.json, holding {"theme": "corporate", "mode": "dark"} (or "theme":
     "corporate-dark"), in the script's folder or one above it, up to the checkout's root: a
     project's look, set once;
  4. technical-light.

A style of a project's own starts from a skill style and changes only what differs, in either mode:
    {"name": "acme", "extends": "corporate", "modes": {"light": {"colour": {"accent": "#C8102E"}}}}

Fonts are named by family; themes/fonts.json says where each family's files are, its licence,
and the name its licence reserves.
"""
from __future__ import annotations

import json
import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent.parent                       # .claude/skills/rich-content
THEMES = SKILL / "themes"
FONTS = THEMES / "fonts.json"
DEFAULT = "technical"
MODES = ("light", "dark")
PROJECT_FILE = "rich-content.json"


def font_dir() -> Path:
    """MANUALS_FONTS when set (the activated venv sets it), else the running venv's share/fonts,
    where scripts/setup.py puts them."""
    env = os.environ.get("MANUALS_FONTS")
    if env:
        return Path(env)
    return Path(sys.prefix) / "share" / "fonts"


@lru_cache(maxsize=None)
def families() -> dict[str, dict[str, Any]]:
    """Every font family a theme may name, as themes/fonts.json describes it."""
    data = json.loads(FONTS.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def font_file(family: str, weight: int = 400, italic: bool = False) -> Path:
    """The file for a family at the weight nearest to `weight`, upright or italic (upright when
    the family has no italic)."""
    fam = families().get(family)
    if fam is None:
        raise SystemExit(f"theme: no font family {family!r} in {FONTS.name}; it has {', '.join(families())}")
    files: dict[str, str] = fam["files"]
    keys = [k for k in files if k.endswith("i") == italic] or [k for k in files if not k.endswith("i")]
    key = min(keys, key=lambda k: abs(int(k.rstrip("i")) - weight))
    return font_dir() / fam["folder"] / files[key]


def _merge(base: dict[str, Any], over: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


class Theme:
    def __init__(self, data: dict[str, Any], path: Path):
        self.data, self.path = data, path
        self.name: str = data["name"]                 # style-mode: corporate-dark
        self.style: str = data["style"]
        self.mode: str = data["mode"]
        self.about: str = data.get("about", "")
        self.dark: bool = bool(data.get("dark"))
        self.colour: dict[str, str] = data["colour"]
        self.kinds: dict[str, dict[str, str]] = data["kinds"]
        self.signal: dict[str, str] = data["signal"]
        self.series: list[str] = data["series"]
        self.fonts: dict[str, Any] = data["fonts"]
        self.shape: dict[str, Any] = data["shape"]
        self.chart: dict[str, Any] = data["chart"]

    # the four roles a font plays
    @property
    def text(self) -> str: return self.fonts["text"]           # running text in PDFs and pages
    @property
    def heading(self) -> str: return self.fonts["heading"]
    @property
    def label(self) -> str: return self.fonts["label"]         # diagrams, charts, captions, tables
    @property
    def mono(self) -> str: return self.fonts["mono"]

    def families_used(self) -> list[str]:
        return list(dict.fromkeys((self.text, self.heading, self.label, self.mono)))

    def typst(self) -> str:
        """What the Typst package reads: the theme as JSON, passed in by render.pdf, with the scale
        of each family it uses (fonts.json)."""
        scale = {f: families()[f].get("scale", 1) for f in self.families_used()}
        return json.dumps({**{k: v for k, v in self.data.items() if k != "extends"}, "font_scale": scale})

    def __repr__(self) -> str:
        return f"Theme({self.name!r})"


def styles() -> list[str]:
    """The styles the skill carries."""
    return sorted(p.stem for p in THEMES.glob("*.json") if p != FONTS)


def names() -> list[str]:
    """The themes the skill carries: every style in each of its modes, style-mode."""
    out = []
    for s in styles():
        data = json.loads((THEMES / f"{s}.json").read_text(encoding="utf-8"))
        out += [f"{s}-{m}" for m in MODES if m in data.get("modes", {"light": {}})]
    return out


def _style_data(spec: str | Path, base: Path | None) -> tuple[dict[str, Any], Path]:
    """A style file's data, with what it extends merged under it, modes and all."""
    p = Path(spec)
    if p.suffix != ".json":
        p = THEMES / f"{spec}.json"
    elif not p.is_absolute():
        p = (base or Path.cwd()) / p
    if not p.exists():
        raise SystemExit(f"theme: no style {str(spec)!r}; the skill has {', '.join(styles())} "
                         f"(each as -light or -dark), or name a style file (.json)")
    data = json.loads(p.read_text(encoding="utf-8"))
    if "extends" in data:
        parent, _ = _style_data(data["extends"], p.parent)
        data = _merge(parent, data)
    return data, p


def load(spec: str | Path, base: Path | None = None, mode: str | None = None) -> Theme:
    """A theme: "corporate-dark", "corporate" (its light mode), or a style file (.json, relative to
    `base` when not absolute) in `mode`."""
    text = str(spec)
    if not text.endswith(".json"):
        for m in MODES:
            if text.endswith("-" + m):
                text, mode = text[: -len(m) - 1], mode or m
                break
    data, p = _style_data(text, base)
    mode = mode or "light"
    modes = data.get("modes", {"light": {}})
    if mode not in modes:
        raise SystemExit(f"theme: {data['name']} has no {mode} mode; it has {', '.join(modes)}")
    resolved = _merge({k: v for k, v in data.items() if k not in ("modes", "extends")}, modes[mode])
    resolved.update(name=f"{data['name']}-{mode}", style=data["name"], mode=mode, dark=mode == "dark")
    for role in ("text", "heading", "label", "mono"):
        font_file(resolved["fonts"][role])          # an unknown family is said now, not mid-drawing
    return Theme(resolved, p)


def project_theme(start: Path) -> tuple[str, Path, str | None] | None:
    """The theme a rich-content.json in `start` or a folder above it names, up to the checkout's
    root, with the folder it was found in and the mode it asks for."""
    for d in [start, *start.parents]:
        f = d / PROJECT_FILE
        if f.exists():
            data = json.loads(f.read_text(encoding="utf-8"))
            return data["theme"], d, data.get("mode")
        if (d / ".git").exists():
            break
    return None


def _script_dir() -> Path:
    f = getattr(sys.modules.get("__main__"), "__file__", None)
    return Path(f).resolve().parent if f else Path.cwd()


def resolve(start: Path | None = None) -> Theme:
    """The theme the environment or a project file asks for, from `start` (the running script's
    folder by default), else technical."""
    env = os.environ.get("RICH_CONTENT_THEME")
    if env:
        return load(env)
    found = project_theme((start or _script_dir()).resolve())
    if found:
        return load(found[0], found[1], found[2])
    return load(DEFAULT)


_current: Theme | None = None
_hooks: list[Callable[[Theme], None]] = []


def current() -> Theme:
    global _current
    if _current is None:
        _current = resolve()
    return _current


def use_theme(spec: str | Path | Theme, mode: str | None = None) -> Theme:
    """Make everything drawn from here on use this theme: "corporate-dark", a style file with its
    mode, or a Theme."""
    global _current
    _current = spec if isinstance(spec, Theme) else load(spec, _script_dir(), mode)
    for hook in _hooks:
        hook(_current)
    return _current


def on_theme(fn: Callable[[Theme], None]) -> Callable[[Theme], None]:
    """Call fn with the theme now and whenever it changes (chartstyle restyles matplotlib)."""
    _hooks.append(fn)
    fn(current())
    return fn


# ----------------------------------------------------------------------------------------------
# Contrast, as WCAG measures it
# ----------------------------------------------------------------------------------------------
def _lum(hex_colour: str) -> float:
    h = hex_colour.lstrip("#")
    def ch(i: int) -> float:
        v = int(h[i:i + 2], 16) / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * ch(0) + 0.7152 * ch(2) + 0.0722 * ch(4)


def contrast(a: str, b: str) -> float:
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


TEXT = 4.5                                        # WCAG AA for text; a style may ask for more


def contrast_issues(th: Theme) -> list[str]:
    """Each pair of colours the kit sets one on the other that falls short of WCAG AA for text,
    4.5:1 -- or of the style's own bar, as the accessible style's "contrast": {"text": 7} (AAA).
    Text is text on its page and card, on a kind's tint and a signal's tint, `on` on the colour
    under it -- and every colour the kit also writes in: the kinds, the series and the accent
    label lines and set code. `faint` is for what is dimmed or decoration only, and is held to
    nothing."""
    need = float(th.data.get("contrast", {}).get("text", TEXT))
    c, s = th.colour, th.signal
    pairs = {"ink on paper": (c["ink"], c["paper"]), "ink on wash": (c["ink"], c["wash"]),
             "muted on paper": (c["muted"], c["paper"]), "muted on wash": (c["muted"], c["wash"]),
             "heading on wash": (c["heading"], c["wash"]), "heading on paper": (c["heading"], c["paper"]),
             "on on ink": (c["on"], c["ink"]), "on on muted": (c["on"], c["muted"]),
             "accent on paper": (c["accent"], c["paper"])}
    for t in ("good", "bad", "warn", "info"):
        pairs[f"{t} on {t}_fill"] = (s[t], s[f"{t}_fill"])
        pairs[f"{t} on paper"] = (s[t], c["paper"])
        pairs[f"on on {t}"] = (c["on"], s[t])
    for k, v in th.kinds.items():
        pairs[f"ink on {k} fill"] = (c["ink"], v["fill"])
        pairs[f"on on {k} stroke"] = (c["on"], v["stroke"])
        pairs[f"{k} stroke on paper"] = (v["stroke"], c["paper"])
    for i, colour in enumerate(th.series, 1):
        pairs[f"series {i} on paper"] = (colour, c["paper"])
    return [f"{th.name}: {what} {fg} on {bg} is {r:.2f}:1, under {need:g}:1"
            for what, (fg, bg) in pairs.items() if (r := contrast(fg, bg)) < need]


# ----------------------------------------------------------------------------------------------
# Colour vision: the series must stay apart for readers who see colour differently
# ----------------------------------------------------------------------------------------------
_CVD = {                                          # Machado, Oliveira and Fernandes (2009), severity 1
    "protanopia": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
    "deuteranopia": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "tritanopia": ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900)),
}
SERIES_APART = 12.0                               # the least CIELAB distance between two series colours
SERIES_CHECKED = 4                                # a chart rarely needs more; past four, label lines directly


def _lin(hex_colour: str) -> tuple[float, float, float]:
    h = hex_colour.lstrip("#")
    def ch(i: int) -> float:
        v = int(h[i:i + 2], 16) / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    return ch(0), ch(2), ch(4)


def _lab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (min(1.0, max(0.0, v)) for v in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def seen_as(hex_colour: str, vision: str) -> tuple[float, float, float]:
    """A colour in CIELAB as a reader with `vision` sees it (or as anyone does, for "typical")."""
    rgb = _lin(hex_colour)
    if vision != "typical":
        m = _CVD[vision]
        rgb = tuple(sum(m[i][j] * rgb[j] for j in range(3)) for i in range(3))  # type: ignore[assignment]
    return _lab(rgb)  # type: ignore[arg-type]


def colour_vision_issues(th: Theme) -> list[str]:
    """The first SERIES_CHECKED series colours, pair by pair, must stay SERIES_APART in CIELAB for
    typical vision and for each of protanopia, deuteranopia and tritanopia -- so a chart's lines
    do not merge for one reader in twelve. Kinds are told apart by icon and label too, and signals
    by their words, so only the series are held to it."""
    out = []
    series = th.series[:SERIES_CHECKED]
    for vision in ("typical", *_CVD):
        seen = [seen_as(s, vision) for s in series]
        for i in range(len(seen)):
            for j in range(i + 1, len(seen)):
                d = sum((a - b) ** 2 for a, b in zip(seen[i], seen[j])) ** 0.5
                if d < SERIES_APART:
                    out.append(f"{th.name}: series {i + 1} {series[i]} and {j + 1} {series[j]} are {d:.1f} "
                               f"apart for {vision}, under {SERIES_APART:g}")
    return out


__all__ = ["Theme", "current", "use_theme", "load", "names", "styles", "resolve", "families", "font_file",
           "font_dir", "contrast", "contrast_issues", "colour_vision_issues", "on_theme"]
