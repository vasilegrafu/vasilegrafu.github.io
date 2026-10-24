"""
setup — put what the rich-content skill needs into the venv that runs this script, and say what
is there. Run it with that venv's python, from anywhere:

    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\scripts\\setup.py           # install what is missing
    .venv\\Scripts\\python.exe .claude\\skills\\rich-content\\scripts\\setup.py --check   # only say

It installs, each only when missing:
  packages  typst (PDFs), matplotlib (charts; brings fontTools and Pillow), pypdfium2 (PDF previews
            and the PDF check), seaborn (statistical charts), pandas and openpyxl (CSV and Excel
            in), Pygments (code highlighting), markdown-it-py (Markdown to HTML) and segno (QR
            codes), at the versions the skill was proven with, by pip;
  typst     the Typst packages the house style uses -- cmarker, which sets Markdown -- into
            <venv>/share/typst/packages/, so nothing is fetched while a PDF compiles;
  fonts     every family themes/fonts.json lists, static cuts, into <venv>/share/fonts/;
  .pth      rich-content.pth in site-packages, naming this skill's scripts/ folder, so that
            `import tools` and `python -m tools.render` work from any folder.
Everything not from pip is downloaded from its project's release page, pinned in fonts.json and
below, into a fresh temporary folder, and only the named files are taken out of each archive.

Everything is free to use, commercially too: typst Apache-2.0, matplotlib its PSF-style licence,
pypdfium2 Apache-2.0/BSD-3 (PDFium BSD-3), fontTools MIT, Pillow MIT-CMU, seaborn BSD-3, pandas
BSD-3, openpyxl MIT, Pygments BSD-2, markdown-it-py MIT, segno BSD-3, cmarker MIT; every font SIL OFL
1.1, none with a reserved name or a trademark. Nothing copyleft, weak copyleft included: Graphviz
(EPL, its Windows build LGPL libraries) laid diagrams out once and is gone; diagrams are placed by
hand. --check lists each font family's licence, and refuses any other. The icons are the skill's
own drawings (icons/), so nothing is downloaded for them.

This is the skill's one exception to the workbench rule that a skill needs nothing but the
standard library: what it makes cannot be made without these. Everything else in the skill
checks for them first and points here when something is missing.
"""
from __future__ import annotations

import argparse
import importlib.metadata as md
import json
import re
import shutil
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
FONTS_JSON = SCRIPTS.parent / "themes" / "fonts.json"

PACKAGES = {"typst": "0.15.0", "matplotlib": "3.11.2", "pypdfium2": "5.13.0", "seaborn": "0.13.2",
            "pandas": "3.0.5", "openpyxl": "3.1.5", "pygments": "2.21.0", "markdown-it-py": "4.2.0",
            "segno": "1.6.6", "pyyaml": "6.0.3"}

# namespace, name, version, archive
TYPST_PACKAGES = [("preview", "cmarker", "0.1.10", "https://packages.typst.org/preview/cmarker-0.1.10.tar.gz")]
FREE_FONT_LICENCES = {"OFL-1.1"}


def _version(name: str) -> str | None:
    try:
        return md.version(name)
    except md.PackageNotFoundError:
        return None


def _download(url: str, into: Path) -> Path:
    dest = into / url.rsplit("/", 1)[1]
    print(f"  downloading {url}")
    with urllib.request.urlopen(url, timeout=120) as r, open(dest, "wb") as f:
        shutil.copyfileobj(r, f)
    return dest


def _take(archive: Path, pattern: re.Pattern[str], dest: Path) -> int:
    """Copy the archive's members whose file name matches into dest, flat; nothing else is
    extracted, and no member's path is used beyond its last part."""
    dest.mkdir(parents=True, exist_ok=True)
    taken = set()
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            name = info.filename.rsplit("/", 1)[-1]
            if info.is_dir() or not pattern.match(name) or name in taken:
                continue
            with z.open(info) as src, open(dest / name, "wb") as out:
                shutil.copyfileobj(src, out)
            taken.add(name)
    return len(taken)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="setup.py", description=(__doc__ or "").split("\n\n")[0])
    ap.add_argument("--check", action="store_true", help="only say what is there and what is missing")
    ap.add_argument("--prefix", type=Path, help="put fonts and tools under this folder instead of the venv "
                                                 "(to try the downloads without touching the venv)")
    args = ap.parse_args(argv)
    prefix = (args.prefix or Path(sys.prefix)).resolve()
    fonts = prefix / "share" / "fonts"
    missing = 0

    if sys.prefix == sys.base_prefix and not args.prefix:
        print(f"note: {sys.executable} is not a venv's python; packages would go into the system Python")

    print("packages")
    for name, want in PACKAGES.items():
        have = _version(name)
        if have:
            print(f"  {name} {have}" + ("" if have == want else f"  (the skill was proven with {want})"))
            continue
        missing += 1
        if args.check:
            print(f"  {name}: missing")
        else:
            print(f"  {name}: installing {want}")
            subprocess.run([sys.executable, "-m", "pip", "install", f"{name}=={want}"], check=True)

    typst_pkgs = prefix / "share" / "typst" / "packages"
    print(f"typst packages in {typst_pkgs}")
    for ns, name, version, url in TYPST_PACKAGES:
        home = typst_pkgs / ns / name / version
        if (home / "typst.toml").exists():
            print(f"  @{ns}/{name}:{version}")
            continue
        missing += 1
        if args.check:
            print(f"  @{ns}/{name}:{version}: missing")
            continue
        home.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp, tarfile.open(_download(url, Path(tmp))) as tar:
            tar.extractall(home, filter="data")
        print(f"  @{ns}/{name}:{version}: installed")

    print(f"fonts in {fonts}")
    registry = {k: v for k, v in json.loads(FONTS_JSON.read_text(encoding="utf-8")).items() if not k.startswith("_")}
    for family, fam in registry.items():
        folder, licence = fam["folder"], fam["licence"]
        if licence not in FREE_FONT_LICENCES:
            print(f"  {family}: licence {licence} is not one the skill takes ({', '.join(FREE_FONT_LICENCES)})")
            missing += 1
            continue
        absent = [f for f in fam["files"].values() if not (fonts / folder / f).exists()]
        if not absent:
            print(f"  {family}: {len(fam['files'])} faces, {licence}")
            continue
        missing += 1
        if args.check:
            print(f"  {family}: missing {', '.join(absent)}")
            continue
        if "raw" in fam:                              # each file from a pinned folder of the repository
            (fonts / folder).mkdir(parents=True, exist_ok=True)
            for f in absent:
                _download(fam["raw"] + f, fonts / folder)
            n = len(absent)
        else:
            with tempfile.TemporaryDirectory() as tmp:
                n = _take(_download(fam["url"], Path(tmp)), re.compile(fam["take"]), fonts / folder)
        print(f"  {family}: {n} files, {licence}")

    pth = Path(sysconfig.get_paths()["purelib"]) / "rich-content.pth"
    print(f"path file {pth}")
    if pth.exists() and pth.read_text(encoding="utf-8").strip() == str(SCRIPTS):
        print(f"  names {SCRIPTS}")
    else:
        missing += 1
        if args.check:
            print("  missing" if not pth.exists() else f"  names {pth.read_text(encoding='utf-8').strip()}, not {SCRIPTS}")
        else:
            pth.write_text(str(SCRIPTS) + "\n", encoding="utf-8")
            print(f"  written: names {SCRIPTS}")

    if args.check:
        print("ready" if not missing else f"{missing} thing(s) missing: run setup.py without --check")
        return 1 if missing else 0
    print("ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
