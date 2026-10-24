"""
make -- a file from a spec. A few lines of YAML say what to draw or write; a generator of the kit
draws or writes it, in the theme, checked as every output of the kit is. The spec is the source, as a
build script is: it sits beside what it makes, and making it again gives the same bytes.

    python -m tools.make path/to/name.yaml          # -> name.svg, name.html or name.pdf beside it
    python -m tools.make --list                     # every kind, by what it is for
    python -m tools.make --schema sequence          # a kind's fields, then its example
    python -m tools.make --example sequence         # the example alone, to start a spec from
    python -m tools.make --all DIR                  # every spec under DIR
    python -m tools.make --check DIR|SPEC …         # writes nothing; exit 1 when an output is stale
    python -m tools.make SPEC --preview             # and PNGs of what it made, in _preview/

A spec is a mapping whose `make:` names its kind. Every kind also takes `theme:` (a theme's name, or a
style file beside the spec) and `out:` (where to write, relative to the spec; its name without the
suffix by default). A key a kind does not read is an error that names the nearest key it does, so a
typo never passes as a default.

Each kind is one module of tools.make.kinds: its docstring is its reference, `PURPOSE` the line --list
prints, `GROUP` where it is listed, `OUTPUT` what it writes, and one of
  draw(spec) -> Canvas | Figure            a figure, written as SVG (and embeddable in a document)
  document(spec) -> Doc                    a document, written as HTML or PDF (`format:`)
  build(spec, out) -> list[Path]           anything else; `out` is the output path without suffix
Its example is examples/make/<kind>.yaml, which the selftest builds.
"""
from __future__ import annotations

import difflib
import importlib
import json
import pkgutil
from pathlib import Path
from types import ModuleType
from typing import Any

from ..theme import SKILL, Theme, load, resolve, use_theme

EXAMPLES = SKILL / "examples" / "make"
GROUPS = ("diagrams", "charts", "documents", "learning", "from the repository")


class SpecError(Exception):
    """A spec that cannot be made as it stands: the message says where and what."""


def _type_name(t: Any) -> str:
    names = {str: "text", int: "a whole number", float: "a number", bool: "true or false", list: "a list",
             dict: "a mapping"}
    if isinstance(t, tuple):
        return " or ".join(names.get(x, x.__name__) for x in t)
    return names.get(t, t.__name__)


class Spec:
    """A spec's mapping, read key by key. A key never read is one the kind does not know: unknown()
    names it, with the nearest key that was read."""

    def __init__(self, data: Any, where: str, base: Path):
        if not isinstance(data, dict):
            raise SpecError(f"{where}: expected a mapping, got {data!r}")
        self.data: dict[str, Any] = data
        self.where, self.base = where, base
        self.read: set[str] = set()
        self.children: list[Spec] = []

    def __contains__(self, key: str) -> bool:
        return key in self.data and self.data[key] is not None

    def _at(self, key: str) -> str:
        return f"{self.where}.{key}" if self.where else key

    def get(self, key: str, default: Any = None, kind: Any = None, choices: Any = None) -> Any:
        self.read.add(key)
        if key not in self.data or self.data[key] is None:
            return default
        v = self.data[key]
        if kind is not None:
            ok = isinstance(v, kind) and not (isinstance(v, bool) and kind in (int, float, (int, float)))
            if kind is float and isinstance(v, int) and not isinstance(v, bool):
                ok, v = True, float(v)
            if not ok:
                raise SpecError(f"{self._at(key)}: expected {_type_name(kind)}, got {v!r}")
        if choices is not None and v not in choices:
            raise SpecError(f"{self._at(key)}: {v!r} is not one of: {', '.join(map(str, choices))}")
        return v

    def need(self, key: str, kind: Any = None, choices: Any = None) -> Any:
        if key not in self:
            raise SpecError(f"{self.where or 'the spec'}: `{key}` is required")
        return self.get(key, kind=kind, choices=choices)

    def num(self, key: str, default: float | None = None) -> float | None:
        v = self.get(key, default, (int, float))
        return None if v is None else float(v)

    def wrap(self, value: Any, suffix: str) -> Spec:
        child = Spec(value, f"{self.where}{suffix}" if self.where else suffix.lstrip("."), self.base)
        self.children.append(child)
        return child

    def sub(self, key: str) -> Spec | None:
        v = self.get(key, kind=dict)
        return None if v is None else self.wrap(v, f".{key}")

    def items(self, key: str, default: list[Any] | None = None) -> list[Any]:
        """A list, each mapping in it a Spec of its own (read and checked as this one is), anything
        else as it is. A single item that is not a list is taken as a list of one."""
        v = self.get(key, default if default is not None else [])
        if not isinstance(v, list):
            v = [v]
        return [self.wrap(x, f".{key}[{i}]") if isinstance(x, dict) else x for i, x in enumerate(v)]

    def mapping(self, key: str) -> list[tuple[str, Any]]:
        """A mapping's entries in their order, a mapping value as a Spec."""
        v = self.get(key, {}, dict)
        return [(str(k), self.wrap(x, f".{key}.{k}") if isinstance(x, dict) else x) for k, x in v.items()]

    def path(self, key: str, must_exist: bool = True) -> Path | None:
        v = self.get(key, kind=str)
        if v is None:
            return None
        p = (self.base / v).resolve()
        if must_exist and not p.exists():
            raise SpecError(f"{self._at(key)}: no file {p}")
        return p

    def file(self, rel: str) -> Path:
        p = (self.base / rel).resolve()
        if not p.exists():
            raise SpecError(f"{self.where or 'the spec'}: no file {p}")
        return p

    def unknown(self) -> list[str]:
        found = []
        for key in self.data:
            if key not in self.read:
                near = difflib.get_close_matches(key, sorted(self.read), n=1, cutoff=0.6)
                hint = f" -- did you mean `{near[0]}`?" if near else (
                    f" -- it knows: {', '.join(sorted(self.read))}" if self.read else "")
                found.append(f"{self._at(key)}: unknown key{hint}")
        for c in self.children:
            found.extend(c.unknown())
        return found


# ----------------------------------------------------------------------------------------------
# The kinds
# ----------------------------------------------------------------------------------------------
def all_kinds() -> dict[str, ModuleType]:
    """Every kind, by its name (the module's name, with - for _), in the order --list shows them."""
    pkg = importlib.import_module(f"{__name__}.kinds")
    found = {}
    for info in pkgutil.iter_modules(pkg.__path__):
        if info.name.startswith("_"):
            continue
        mod = importlib.import_module(f"{pkg.__name__}.{info.name}")
        found[info.name.replace("_", "-")] = mod
    return dict(sorted(found.items(), key=lambda kv: (GROUPS.index(kv[1].GROUP), kv[0])))


def kind(name: str) -> ModuleType:
    all_ = all_kinds()
    if name not in all_:
        near = difflib.get_close_matches(name, list(all_), n=1)
        raise SpecError(f"no kind `{name}`" + (f" -- did you mean `{near[0]}`?" if near else "")
                        + f"; there are: {', '.join(all_)}")
    return all_[name]


def example(name: str) -> Path:
    return EXAMPLES / f"{name}.yaml"


# ----------------------------------------------------------------------------------------------
# Reading and making
# ----------------------------------------------------------------------------------------------
def read(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        data = json.loads(text)
    else:
        import yaml
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise SpecError(f"{path.name}: not YAML: {e}") from None
    if not isinstance(data, dict) or "make" not in data:
        raise SpecError(f"{path.name}: a spec is a mapping with `make:` naming its kind")
    return _plain(data)


def _plain(v: Any) -> Any:
    """YAML's dates as ISO text (2026-10-23), as a spec means them, and keys as text."""
    import datetime
    if isinstance(v, dict):
        return {(k.isoformat() if isinstance(k, datetime.date) else k): _plain(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_plain(x) for x in v]
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    return v


def theme_of(spec: Spec) -> Theme:
    name = spec.get("theme", kind=str)
    return load(name, spec.base) if name else resolve(spec.base)


def drawn(spec: Spec) -> Any:
    """What a figure kind draws for this spec, in the theme in force."""
    mod = kind(spec.need("make", str))
    if not hasattr(mod, "draw"):
        raise SpecError(f"{spec.where or 'the spec'}: `{spec.get('make')}` is not a figure; a figure is one of: "
                        + ", ".join(k for k, m in all_kinds().items() if hasattr(m, "draw")))
    return mod.draw(spec)


def make(path: Path, out_dir: Path | None = None) -> list[Path]:
    """Make what the spec at `path` asks for. `out_dir` writes it there instead of beside the spec
    (what --check compares)."""
    path = path.resolve()
    spec = Spec(read(path), "", path.parent)
    name = spec.need("make", str)
    mod = kind(name)
    use_theme(theme_of(spec))
    out = output(path, spec.get("out", kind=str))
    if out_dir is not None:
        out = out_dir / out.name
    out.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(mod, "draw"):
        obj = mod.draw(spec)
        _unknown(spec)
        written = [save_figure(obj, out.with_suffix(".svg"))]
    elif hasattr(mod, "document"):
        from .document import write
        doc = mod.document(spec)
        written = write(doc, out, doc.formats(spec), spec)
    else:
        written = mod.build(spec, out)
    try:                                                 # a document's blocks are read as it is written
        _unknown(spec)
    except SpecError:
        for w in written:
            w.unlink(missing_ok=True)
        raise
    return written


def output(path: Path, out_rel: str | None) -> Path:
    """Where the spec at `path` writes: its `out:`, relative to it, or its own name; without suffix."""
    out = (path.parent / out_rel).resolve() if out_rel else path.with_suffix("")
    return out.with_suffix("") if out.suffix in (".svg", ".html", ".pdf") else out


def _unknown(spec: Spec) -> None:
    found = spec.unknown()
    if found:
        raise SpecError("\n".join(found))


def save_figure(obj: Any, target: Path) -> Path:
    """A Canvas or a matplotlib figure, written as SVG and checked."""
    from ..svgkit import Canvas, save
    if isinstance(obj, Canvas):
        return save(obj, target)
    if hasattr(obj, "savefig"):
        from ..chartstyle import save_chart
        return save_chart(obj, target)
    raise TypeError(f"not a figure: {obj!r}")


__all__ = ["Spec", "SpecError", "all_kinds", "kind", "make", "drawn", "read", "output", "save_figure", "example", "EXAMPLES"]
