"""What the impact and spec-graph kinds read of a product-specs folder: its model as the skill's own spec.py
wrote it -- model/index.json (each ID's kind and name), model/edges.tsv (every edge), reviewed.json (what each
page was last reviewed against) -- and, for what a change reaches, spec.py --impact itself. Nothing here works
out what the skill already says."""
from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from ...svgkit import text_width
from ...theme import SKILL
from .. import Spec, SpecError

SPEC_PY = SKILL.parent / "product-specs" / "scripts" / "spec.py"

# each kind of page as a kind of box: its colours, its icon
LOOK: dict[str, tuple[str, str]] = {
    "requirement": ("compute", "file-text"), "criterion": ("compute", "file-text"),
    "rule": ("data", "shield"), "entity": ("data", "database"), "state": ("data", "database"),
    "role": ("external", "users"), "goal": ("external", "zap"),
    "screen": ("client", "monitor"), "element": ("client", "monitor"),
    "flow": ("async", "send"), "component": ("edge", "code"), "part": ("edge", "code"),
    "endpoint": ("edge", "globe"), "api": ("edge", "network"),
    "question": ("cache", "pencil"), "decision": ("cache", "hammer"), "risk": ("cache", "octagon-x"),
    "constraint": ("cache", "landmark"), "quality": ("compute", "cog"), "term": ("data", "book-open"),
    "finding": ("external", "book-open"), "source": ("external", "files"), "contradiction": ("external", "octagon-x"),
    "foundation": ("compute", "cog"), "document": ("compute", "file-text"),
}


@dataclass
class Model:
    folder: Path
    kind: dict[str, str]
    name: dict[str, str]
    edges: list[tuple[str, str, str]]
    against: dict[str, dict[str, str]]                 # page -> what it was last reviewed against

    def page(self, ref: str) -> str:
        """The page an element, a part or a criterion belongs to: SC3.13 -> SC3."""
        head = ref.split(".", 1)[0]
        return head if head in self.kind else ref

    def kind_of(self, ref: str) -> str:
        return self.kind.get(ref) or self.kind.get(self.page(ref), "document")


def load(spec: Spec, key: str = "specs") -> Model:
    folder = spec.path(key)
    if folder is None:
        raise SpecError(f"`{key}` is required: a product-specs folder (the one holding model/ and site/)")
    index_file = folder / "model" / "index.json"
    if not index_file.exists():
        raise SpecError(f"{key}: {folder} holds no model/index.json -- is it a product-specs folder, written by spec.py --write?")
    index = json.loads(index_file.read_text(encoding="utf-8"))
    kind = {n["id"]: n.get("kind", "") for n in index["nodes"]}
    name = {n["id"]: n.get("name", "") for n in index["nodes"]}
    lines = (folder / "model" / "edges.tsv").read_text(encoding="utf-8").splitlines()[1:]
    edges = [tuple(line.split("\t")) for line in lines if line.count("\t") == 2]
    reviewed = folder / "reviewed.json"
    against = {}
    if reviewed.exists():
        against = {p: v.get("against", {}) for p, v in
                   json.loads(reviewed.read_text(encoding="utf-8")).get("pages", {}).items()}
    return Model(folder, kind, name, edges, against)  # type: ignore[arg-type]


def natural(ref: str) -> list[tuple[int, int | str]]:
    """R2 before R10, SC3 before SC3.13: letters and numbers in the order a reader expects."""
    import re
    return [(0, int(x)) if x.isdigit() else (1, x) for x in re.findall(r"\d+|\D+", ref)]


def known(model: Model, ref: str, where: str) -> str:
    if ref not in model.kind:
        import difflib
        near = difflib.get_close_matches(ref, list(model.kind), n=3)
        raise SpecError(f"{where}: no ID `{ref}` in {model.folder}" + (f" -- did you mean {', '.join(near)}?" if near else ""))
    return ref


def impact_text(model: Model, ref: str) -> str:
    """What spec.py --impact says of `ref`, as it says it."""
    r = subprocess.run([sys.executable, str(SPEC_PY), str(model.folder), "--impact", ref], capture_output=True,
                       text=True, encoding="utf-8")
    out = r.stdout
    if not out.startswith("# Impact of"):
        raise SpecError(f"spec.py --impact {ref} said: {(out + r.stderr).strip()[:300]}")
    return out


def section(text: str, heading: str) -> list[str]:
    """The bullet lines of a `## heading` of spec.py's Markdown."""
    body = text.split(f"## {heading}\n", 1)
    if len(body) < 2:
        return []
    out = []
    for line in body[1].splitlines():
        if line.startswith("## "):
            break
        if line.startswith("- "):
            out.append(line[2:])
    return out


def fit(s: str, width: float, size: float = 13, weight: int = 600) -> str:
    """s cut with an ellipsis to fit `width` px."""
    if text_width(s, size, weight) <= width:
        return s
    s = s.rstrip("…").rstrip()
    while s and text_width(s + "…", size, weight) > width:
        s = s[:-1]
    return s.rstrip(" ,;:-·") + "…"


def node(model: Model, ref: str, width: float, state: str = "normal", sub: str | None = None,
         at: list[float] | None = None) -> dict:
    """A box for `ref`, as kinds/flow.py draws one: "ID · name", coloured and drawn by its kind."""
    k = model.kind_of(ref)
    look, icon = LOOK.get(k, ("compute", "file-text"))
    label = fit(f"{ref} · {model.name.get(ref, '')}".rstrip(" ·"), width - 30 - 24)
    return {"id": ref, "label": label, "sub": fit(sub if sub is not None else k, width - 30 - 24, 10.5, 400),
            "kind": look, "icon": icon, "shape": "box", "state": state, "count": None, "tag": None, "at": at}


def edge(a: str, b: str, label: str | None, dash: bool = False, color: str | None = None) -> dict:
    return {"from": a, "to": b, "label": label, "dash": dash, "both": False, "head": True, "color": color,
            "mono": False, "step": None}
