"""python -m tools.make: make files from specs (see tools/make/__init__.py)."""
from __future__ import annotations

import argparse
import filecmp
import inspect
import sys
import tempfile
from pathlib import Path

from . import EXAMPLES, GROUPS, SpecError, all_kinds, example, kind, make, output, read


def specs_under(folder: Path) -> list[Path]:
    """Every spec under `folder`: a .yaml, .yml or .json file holding `make:`, outside _preview/."""
    found = []
    for p in sorted(folder.rglob("*")):
        if p.suffix not in (".yaml", ".yml", ".json") or "_preview" in p.parts or not p.is_file():
            continue
        try:
            read(p)
        except (SpecError, UnicodeDecodeError, ValueError):
            continue
        found.append(p)
    # a catalog shows what the others made, so it is made after them
    return sorted(found, key=lambda p: read(p).get("make") == "catalog")


def listing() -> str:
    out = []
    for group in GROUPS:
        rows = [(name, mod) for name, mod in all_kinds().items() if mod.GROUP == group]
        if not rows:
            continue
        out.append(f"\n{group}")
        for name, mod in rows:
            out.append(f"  {name:<12} {mod.OUTPUT:<9} {mod.PURPOSE}")
    out.append("\npython -m tools.make --schema KIND   its fields and its example")
    return "\n".join(out).lstrip("\n")


def schema(name: str) -> str:
    mod = kind(name)
    doc = inspect.cleandoc(mod.__doc__ or "")
    ex = example(name)
    tail = f"\n\nExample ({ex.relative_to(EXAMPLES.parent.parent)}):\n\n{ex.read_text(encoding='utf-8')}" if ex.exists() else ""
    return f"{name} -- {mod.PURPOSE}\nwrites {mod.OUTPUT}\n\n{doc}{tail}"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="python -m tools.make", description="Make files from specs.")
    ap.add_argument("specs", nargs="*", type=Path, help="spec files (or folders, with --all or --check)")
    ap.add_argument("--list", action="store_true", help="every kind, by what it is for")
    ap.add_argument("--schema", metavar="KIND", help="a kind's fields, then its example")
    ap.add_argument("--example", metavar="KIND", help="a kind's example spec, alone")
    ap.add_argument("--all", action="store_true", help="make every spec under the folders given")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when an output is not what its spec makes")
    ap.add_argument("--preview", action="store_true", help="also render PNGs of the SVGs and PDFs made, into _preview/")
    ap.add_argument("--strict", action="store_true", help="exit 1 when the check finds anything")
    a = ap.parse_args(argv)
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8")       # type: ignore[union-attr]

    try:
        if a.list:
            print(listing())
            return 0
        if a.schema:
            print(schema(a.schema))
            return 0
        if a.example:
            ex = example(a.example)
            kind(a.example)
            if not ex.exists():
                raise SpecError(f"`{a.example}` has no example yet")
            print(ex.read_text(encoding="utf-8"), end="")
            return 0
        if not a.specs:
            ap.print_usage()
            return 2
        paths: list[Path] = []
        for p in a.specs:
            paths.extend(specs_under(p) if p.is_dir() else [p])
        if not paths:
            raise SpecError("no specs found")
        from ..check import FOUND
        if a.check:
            return check(paths)
        made: list[Path] = []
        for p in paths:
            try:
                written = make(p)
            except SpecError as e:
                print(f"spec: {p}: {e}", file=sys.stderr)
                return 2
            for w in written:
                print(f"made: {w}")
            made.extend(written)
        if a.preview:
            from ..render import png
            looks = [m for m in made if m.suffix in (".svg", ".pdf")]
            for shot in png(looks) if looks else []:
                print(f"preview: {shot}")
            for m in made:
                if m.suffix == ".html":
                    print(f"look: {m} in a browser, at about 1100 and 390 px wide")
        if FOUND:
            print(f"check: {len(FOUND)} finding(s)", file=sys.stderr)
            return 1 if a.strict else 0
        return 0
    except SpecError as e:
        print(f"spec: {e}", file=sys.stderr)
        return 2


def check(paths: list[Path]) -> int:
    stale = 0
    for p in paths:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                written = make(p, Path(tmp))
            except SpecError as e:
                print(f"spec: {p}: {e}", file=sys.stderr)
                return 2
            data = read(p.resolve())
            real = output(p.resolve(), data.get("out")).parent
            for w in written:
                kept = real / w.relative_to(tmp)
                if not kept.exists() or not filecmp.cmp(w, kept, shallow=False):
                    print(f"stale: {kept}")
                    stale += 1
    print(f"{len(paths)} spec(s), {stale} stale output(s)")
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
