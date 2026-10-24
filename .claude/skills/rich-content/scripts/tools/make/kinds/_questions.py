"""
Questions in the Trainings model (ai-workbench-learning, Trainings/QUESTION-STANDARD.md, section 2) --
written in a spec, or read from a Trainings question file -- and how each of the eleven formats is set
on paper (Typst) and on a page (HTML), with its answer.

Shared by the quiz and flashcards kinds. Every question is turned into one plain shape first; the
shuffles a format needs on paper (order, classify, match) are fixed by the question's id, so a quiz
made again is the same quiz.
"""
from __future__ import annotations

import hashlib
import html as H
import json
import random
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .. import Spec, SpecError
from ..document import Typst, inline, ts

FORMATS = ("choice-one", "choice-many", "short-answer", "numeric", "spot", "fill-gaps", "order", "classify",
           "match", "free-response", "case")
MATERIALS = ("none", "code", "text", "list", "dialogue", "table")
LEVELS = ("beginner", "intermediate", "advanced", "expert")
LOADER = Path(__file__).with_name("_trainings.cjs")
LETTERS = "ABCDEFGHIJKL"
GAP = re.compile(r"\{\{(\d+)\}\}")
# a Trainings language name, as Typst's highlighter knows it
TYPST_LANG = {"csharp": "cs", "c#": "cs", "javascript": "js", "typescript": "ts", "python": "py", "text": None,
              "shell": "sh", "bash": "sh", "powershell": "ps1"}


# ----------------------------------------------------------------------------------------------
# Reading
# ----------------------------------------------------------------------------------------------
def load(spec: Spec) -> list[dict[str, Any]]:
    """The questions a spec names: `questions:` written in it, or `from:` a Trainings file, filtered
    by `lessons:`, `levels:` and `ids:`."""
    src = spec.path("from")
    lessons = [str(x) for x in spec.get("lessons", [], list)]
    levels = [str(x) for x in spec.get("levels", [], list)]
    ids = [str(x) for x in spec.get("ids", [], list)]
    for lv in levels:
        if lv not in LEVELS:
            raise SpecError(f"levels: {lv!r} is not one of: {', '.join(LEVELS)}")
    if src is not None:
        if "questions" in spec:
            raise SpecError("`from` and `questions` together: give one")
        qs = [norm(q) for q in from_js(src)]
    else:
        qs = [read_q(q, spec, k) for k, q in enumerate(spec.items("questions"))]
    if lessons:
        qs = [q for q in qs if str(q.get("lesson")) in lessons]
    if levels:
        qs = [q for q in qs if q.get("level") in levels]
    if ids:
        missing = [i for i in ids if i not in {q["id"] for q in qs}]
        if missing:
            raise SpecError(f"ids: no question {', '.join(missing)}")
        qs = [q for q in qs if q["id"] in ids]
    if not qs:
        raise SpecError("no questions: write `questions:`, or name a Trainings file in `from:` (and check the filters)")
    for q in qs:
        prepare(q)
    return qs


def from_js(path: Path) -> list[dict[str, Any]]:
    """A Trainings question file, read by Node: the file's path is passed, its text never built into code."""
    node = shutil.which("node")
    if node is None:
        raise SpecError(f"from: reading {path.name} needs Node (node on the PATH)")
    r = subprocess.run([node, str(LOADER), str(path)], capture_output=True, timeout=120)
    if r.returncode != 0:
        err = r.stderr.decode("utf-8", "replace").strip().splitlines()
        raise SpecError(f"from: Node could not read {path.name}: {err[-1] if err else r.returncode}")
    data = json.loads(r.stdout.decode("utf-8"))
    if not isinstance(data, list):
        raise SpecError(f"from: {path.name} added no questions")
    return data


def _trim(text: str) -> str:
    """A material's text as the Trainings sites number it: the leading newline gone, the end tidied."""
    return text.lstrip("\n").rstrip()


def _material_of(m: dict[str, Any] | None) -> dict[str, Any]:
    m = dict(m or {"kind": "none"})
    if m.get("kind") not in MATERIALS:
        raise SpecError(f"material: kind {m.get('kind')!r} is not one of: {', '.join(MATERIALS)}")
    if "text" in m:
        m["text"] = _trim(str(m["text"]))
    return m


def norm(q: dict[str, Any]) -> dict[str, Any]:
    """A question read from a Trainings file, in the one shape (fields kept as the standard names them)."""
    q = dict(q)
    if q.get("format") not in FORMATS:
        raise SpecError(f"question {q.get('id')}: format {q.get('format')!r} is not one of: {', '.join(FORMATS)}")
    q["id"] = str(q.get("id", ""))
    q["material"] = _material_of(q.get("material"))
    if q["format"] == "case":
        q["steps"] = [norm({**s, "id": f"{q['id']}.{k + 1}"}) for k, s in enumerate(q.get("steps", []))]
    if q["format"] == "spot":
        q["notes"] = {int(k): v for k, v in (q.get("notes") or {}).items()}
    if "options" in q:                                     # a Trainings file writes `ok` only where it is true
        q["options"] = [{"t": str(o.get("t", "")), "ok": bool(o.get("ok")), "why": str(o.get("why", ""))}
                        for o in q["options"]]
    return q


def read_q(v: Any, spec: Spec, k: int, step: bool = False) -> dict[str, Any]:
    """A question written in a spec, read key by key so that a typo is named."""
    if not isinstance(v, Spec):
        raise SpecError(f"questions[{k}]: a question is a mapping: {{format, q, …}}")
    s = v
    q: dict[str, Any] = {}
    if not step:
        q["id"] = str(s.get("id", str(k + 1)))
        q["lesson"] = s.get("lesson")
        q["level"] = s.get("level", None, str, LEVELS)
        q["type"] = s.get("type", kind=str)
        q["since"] = s.get("since")
        q["chapter"] = s.get("chapter")
        s.get("check")                                     # a Trainings check: not shown on paper
    fmt = s.need("format", str, FORMATS[:-1] if step else FORMATS)
    q["format"] = fmt
    m = s.sub("material")
    q["material"] = _read_material(m) if m else {"kind": "none"}
    q["q"] = str(s.need("q"))
    q["why"] = s.get("why", kind=str)
    q["takeaway"] = s.get("takeaway", kind=str)
    if fmt in ("choice-one", "choice-many"):
        opts = []
        for j, o in enumerate(s.items("options")):
            if not isinstance(o, Spec):
                raise SpecError(f"{s.where}.options[{j}]: {{t, ok, why}}")
            opts.append({"t": str(o.need("t")), "ok": bool(o.get("ok", False, bool)), "why": o.get("why", "", str)})
        if len(opts) < 2:
            raise SpecError(f"{s.where}.options: at least two")
        right = sum(o["ok"] for o in opts)
        if fmt == "choice-one" and right != 1:
            raise SpecError(f"{s.where}.options: a choice-one has exactly one `ok: true`, this has {right}")
        if fmt == "choice-many" and right < 1:
            raise SpecError(f"{s.where}.options: a choice-many has at least one `ok: true`")
        q["options"] = opts
    elif fmt == "short-answer":
        q["accept"] = [str(a) for a in s.need("accept", list)]
        q["compare"] = s.get("compare", "exact", str, ("exact", "ignore-case-and-spaces"))
        q["traps"] = []
        for j, tr in enumerate(s.items("traps")):
            if not isinstance(tr, Spec):
                raise SpecError(f"{s.where}.traps[{j}]: {{text, why}}")
            q["traps"].append({"text": str(tr.need("text")), "why": str(tr.get("why", ""))})
    elif fmt == "numeric":
        q["answer"] = s.need("answer", (int, float))
        q["unit"] = str(s.get("unit", ""))
        tol = s.sub("tolerance")
        q["tolerance"] = ({"kind": tol.get("kind", "absolute", str, ("absolute", "relative")),
                           "value": tol.get("value", 0, (int, float))} if tol else {"kind": "absolute", "value": 0})
    elif fmt == "spot":
        q["faulty"] = [int(x) for x in s.need("faulty", list)]
        q["notes"] = {int(a): str(b) for a, b in s.get("notes", {}, dict).items()}
        if q["material"]["kind"] not in ("code", "list", "dialogue", "table"):
            raise SpecError(f"{s.where}: a spot question's material is code, a list, a dialogue or a table")
    elif fmt == "fill-gaps":
        gaps = []
        for j, g in enumerate(s.items("gaps")):
            if not isinstance(g, Spec):
                raise SpecError(f"{s.where}.gaps[{j}]: {{choices, answer, why}}")
            gaps.append({"choices": [str(c) for c in g.need("choices", list)], "answer": str(g.need("answer")),
                         "why": str(g.get("why", ""))})
        q["gaps"] = gaps
        found = GAP.findall(q["material"].get("text", ""))
        if len(found) != len(gaps):
            raise SpecError(f"{s.where}: the material has {len(found)} gaps ({{{{1}}}}, …) for {len(gaps)} `gaps`")
    elif fmt == "order":
        q["items"] = [str(x) for x in s.need("items", list)]
        q["orderBy"] = str(s.get("orderBy", "first to last"))
    elif fmt == "classify":
        groups = []
        for j, g in enumerate(s.items("groups")):
            if not isinstance(g, Spec):
                raise SpecError(f"{s.where}.groups[{j}]: {{name, items}}")
            groups.append({"name": str(g.need("name")), "items": [str(x) for x in g.need("items", list)]})
        q["groups"] = groups
    elif fmt == "match":
        pairs = s.need("pairs", list)
        if not all(isinstance(p, list) and len(p) == 2 for p in pairs):
            raise SpecError(f"{s.where}.pairs: [left, right] pairs")
        q["pairs"] = [[str(a), str(b)] for a, b in pairs]
    elif fmt == "free-response":
        q["model"] = str(s.need("model"))
        q["points"] = [str(x) for x in s.get("points", [], list)]
    elif fmt == "case":
        q["scenario"] = str(s.need("scenario"))
        q["steps"] = []
        for j, st in enumerate(s.items("steps")):
            step_q = read_q(st, s, j, step=True)
            step_q["id"] = f"{q['id']}.{j + 1}"
            q["steps"].append(step_q)
        if not q["steps"]:
            raise SpecError(f"{s.where}.steps: a case has steps")
    return q


def _read_material(m: Spec) -> dict[str, Any]:
    kind = m.need("kind", str, MATERIALS)
    out: dict[str, Any] = {"kind": kind}
    if kind == "code":
        out["lang"] = str(m.get("lang", "text"))
        out["text"] = _trim(str(m.need("text")))
    elif kind == "text":
        out["text"] = _trim(str(m.need("text")))
    elif kind == "list":
        out["items"] = [str(x) for x in m.need("items", list)]
    elif kind == "dialogue":
        turns = []
        for j, t in enumerate(m.items("turns")):
            if not isinstance(t, Spec):
                raise SpecError(f"{m.where}.turns[{j}]: {{who, says}}")
            turns.append({"who": str(t.need("who")), "says": str(t.need("says"))})
        out["turns"] = turns
    elif kind == "table":
        out["columns"] = [str(x) for x in m.need("columns", list)]
        out["rows"] = [[str(c) for c in r] for r in m.need("rows", list)]
    return out


def prepare(q: dict[str, Any]) -> None:
    """The shuffles a format needs on paper, fixed by the question's id."""
    rng = random.Random(int(hashlib.md5(q["id"].encode("utf-8")).hexdigest()[:8], 16))

    def shuffled(n: int) -> list[int]:
        idx = list(range(n))
        if n > 1:
            while idx == list(range(n)):
                rng.shuffle(idx)
        return idx

    if q["format"] == "order":
        q["_shown"] = shuffled(len(q["items"]))               # shown position -> item index
    elif q["format"] == "classify":
        flat = [(item, gi) for gi, g in enumerate(q["groups"]) for item in g["items"]]
        q["_items"] = [flat[i] for i in shuffled(len(flat))]
    elif q["format"] == "match":
        q["_rights"] = shuffled(len(q["pairs"]))              # letter position -> pair index
    elif q["format"] == "case":
        for st in q["steps"]:
            prepare(st)


def info(q: dict[str, Any]) -> str:
    """The small line beside a question's number: its id, lesson and level."""
    parts = [q.get("id") or ""]
    if q.get("lesson"):
        parts.append(f"lesson {q['lesson']}")
    if q.get("level"):
        parts.append(str(q["level"]))
    return " · ".join(p for p in parts if p)


def _gapped(text: str, md: bool) -> str:
    """A fill-gaps material with its gaps drawn as numbered blanks."""
    return GAP.sub(lambda m: (f"**({m.group(1)})** \\_\\_\\_\\_\\_\\_\\_\\_" if md else f"__({m.group(1)})__"), text)


def answer_text(q: dict[str, Any]) -> str:
    """The right answer in a line of Markdown, for a flashcard's back."""
    f = q["format"]
    if f in ("choice-one", "choice-many"):
        return "\n\n".join(f"**✓** {o['t']}" for o in q["options"] if o["ok"])
    if f == "short-answer":
        return " or ".join(f"`{a}`" for a in q["accept"])
    if f == "numeric":
        unit = f" {q['unit']}" if q.get("unit") else ""
        return f"**{_num(q['answer'])}{unit}**"
    if f == "spot":
        return "Faulty: " + ", ".join(str(x) for x in q["faulty"]) + "".join(
            f"\n\n{n}. {q['notes'][n]}" for n in q["faulty"] if n in q.get("notes", {}))
    if f == "fill-gaps":
        return "\n\n".join(f"({k + 1}) **{g['answer']}**" for k, g in enumerate(q["gaps"]))
    if f == "order":
        return "\n".join(f"{k + 1}. {it}" for k, it in enumerate(q["items"]))
    if f == "classify":
        return "\n\n".join(f"**{g['name']}**: " + "; ".join(g["items"]) for g in q["groups"])
    if f == "match":
        return "\n\n".join(f"{a} → {b}" for a, b in q["pairs"])
    if f == "free-response":
        return "\n".join(f"- {p}" for p in q["points"]) if q.get("points") else q["model"]
    if f == "case":
        return "\n\n".join(f"**({LETTERS[k].lower()})** {answer_text(st)}" for k, st in enumerate(q["steps"]))
    return ""


def _num(v: Any) -> str:
    """A number as a reader writes it: thousands grouped only from ten thousand, so 1350 stays 1350."""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return f"{v:,}" if isinstance(v, int) and abs(v) >= 10000 else str(v)


# ----------------------------------------------------------------------------------------------
# Typst
# ----------------------------------------------------------------------------------------------
TYPST_HELPERS = """
#let mark-one = box(baseline: 0.15em, circle(radius: 0.42em, stroke: 0.7pt + colour("muted")))
#let mark-many = box(baseline: 0.15em, rect(width: 0.85em, height: 0.85em, radius: 1pt, stroke: 0.7pt + colour("muted")))
#let write-box = box(baseline: 0.3em, rect(width: 1.8em, height: 1.3em, radius: 1.5pt, stroke: 0.7pt + colour("muted")))
#let blank(w) = box(width: w, baseline: 0.1em, line(length: 100%, stroke: 0.5pt + colour("muted")))
#let ruled(n) = for i in range(n) { block(width: 100%, height: 2em, above: 0pt, below: 0pt,
  stroke: (bottom: 0.4pt + colour("rule"))) }
#let tag(body) = text(font: sans, weight: "semibold", body)
#let meta(body) = text(font: sans, size: 0.78em, fill: colour("muted"), body)
#let hint(body) = block(above: 0.7em, below: 0.5em, text(font: sans, size: 0.82em, style: "italic",
  fill: colour("muted"), body))
#let qhead(n, about) = block(above: 1.7em, below: 0.7em, sticky: true, text(font: sans, size: 10.5pt,
  weight: "bold", fill: colour("heading"), [Question #n]) + h(8pt) + text(font: sans, size: 8pt, fill: colour("muted"), about))
#let khead(n) = block(above: 1.3em, below: 0.5em, sticky: true, text(font: sans, size: 10pt, weight: "bold",
  fill: colour("heading"), [Question #n]))
#let step-head(label) = block(above: 1.1em, below: 0.5em, sticky: true, text(font: sans, size: 0.92em,
  weight: "semibold", fill: colour("heading"), label))
#let numbered-code(lang, src) = {
  show raw.line: it => box(width: 2em, text(fill: colour("muted"), str(it.number))) + it
  raw(block: true, lang: lang, src)
}
#let right-mark = text(font: sans, weight: "bold", fill: signal("good"), "✓")
#let wrong-mark = text(font: sans, fill: colour("muted"), "✗")
#let takeaway(body) = block(above: 0.8em, below: 0.4em, inset: (left: 0.9em, y: 0.3em),
  stroke: (left: 1.5pt + signal("good")), text(size: 0.95em, body))
"""


class Paper:
    """A question and its answer as Typst markup."""

    def __init__(self, t: Typst):
        self.t = t

    def md(self, s: str) -> str:
        return "#" + self.t.md(s)

    def plain(self, s: str) -> str:
        return f"#{ts(s)}"

    def code(self, lang: str | None, src: str, numbered: bool = False) -> str:
        lang_ = TYPST_LANG.get((lang or "text").lower(), lang)
        lang_arg = ts(lang_) if lang_ else "none"
        if numbered:
            return f"#numbered-code({lang_arg}, {ts(src)})"
        return f"#raw(block: true, lang: {lang_arg}, {ts(src)})"

    def material(self, m: dict[str, Any], spot: bool = False, gaps: bool = False) -> str:
        k = m["kind"]
        if k == "none":
            return ""
        if k == "code":
            src = _gapped(m["text"], False) if gaps else m["text"]
            return self.code(m.get("lang"), src, numbered=spot)
        if k == "text":
            return self.md(_gapped(m["text"], True) if gaps else m["text"])
        if k == "list":
            return "#enum(" + ", ".join(f"[{self.md(i)}]" for i in m["items"]) + ")"
        if k == "dialogue":
            cells = []
            for n, t in enumerate(m["turns"], 1):
                if spot:
                    cells.append(f"[#meta({ts(str(n))})]")
                cells += [f"[#text(font: sans, weight: \"semibold\", {ts(t['who'])})]", f"[{self.md(t['says'])}]"]
            cols = "(auto, auto, 1fr)" if spot else "(auto, 1fr)"
            return f"#grid(columns: {cols}, column-gutter: 1em, row-gutter: 0.8em, {', '.join(cells)})"
        if k == "table":
            head = [ts(c) for c in m["columns"]]
            rows = [[f"[{self.md(c)}]" for c in r] for r in m["rows"]]
            if spot:
                head = [ts("#")] + head
                rows = [[f"[#meta({ts(str(n))})]"] + r for n, r in enumerate(rows, 1)]
            h = "(" + ", ".join(f"[#{x}]" for x in head) + ",)"
            b = "(" + ", ".join("(" + ", ".join(r) + ",)" for r in rows) + ",)"
            return f"#data-table({h}, {b})"
        return ""

    def body(self, q: dict[str, Any], card: bool = False) -> str:
        """The question as asked: its material, its words, and where to answer -- on a card, only what
        the question cannot be answered without (its options, its items, its pairs), no lines to write on."""
        f = q["format"]
        out = []
        if f == "case":
            out.append(self.md(q["scenario"]))
            out.append(self.md(q["q"]))
            for k, st in enumerate(q["steps"]):
                out.append(f"#step-head({ts('(' + LETTERS[k].lower() + ')')})")
                out.append(self.body(st, card))
            return "\n\n".join(x for x in out if x)
        mat = self.material(q["material"], spot=f == "spot", gaps=f == "fill-gaps")
        if mat:
            out.append(mat)
        out.append(self.md(q["q"]))
        if not card or f in ("choice-one", "choice-many", "order", "classify", "match", "fill-gaps"):
            out.append(self.area(q))
        return "\n\n".join(x for x in out if x)

    def area(self, q: dict[str, Any]) -> str:
        f = q["format"]
        if f in ("choice-one", "choice-many"):
            mark = "mark-one" if f == "choice-one" else "mark-many"
            cells = []
            for i, o in enumerate(q["options"]):
                cells += [f"[#{mark}]", f"[#tag({ts(LETTERS[i])})]",
                          f"[{self.md(o['t'])}]"]
            hint = "Tick one." if f == "choice-one" else "Tick every one that applies."
            return (f"#hint({ts(hint)})\n#grid(columns: (auto, auto, 1fr), column-gutter: 0.8em, row-gutter: 0.9em, "
                    + ", ".join(cells) + ")")
        if f == "short-answer":
            return "#block(above: 1em)[Answer: #blank(55%)]"
        if f == "numeric":
            unit = f" {self.plain(q['unit'])}" if q.get("unit") else ""
            return f"#block(above: 1em)[Answer: #blank(28%){unit}]"
        if f == "spot":
            return "#hint(\"Write the number of every faulty part.\")\n#block(above: 0.4em)[Faulty: #blank(40%)]"
        if f == "fill-gaps":
            rows = []
            for k, g in enumerate(q["gaps"]):
                rows += [f"[#tag({ts('(' + str(k + 1) + ')')})]", "[#blank(100%)]",
                         f"[#meta({ts(' · '.join(g['choices']))})]"]
            return ("#block(above: 1em)[#grid(columns: (auto, 34%, 1fr), column-gutter: 1em, row-gutter: 1.4em, "
                    "align: bottom, " + ", ".join(rows) + ")]")
        if f == "order":
            cells = []
            for pos, i in enumerate(q["_shown"]):
                cells += ["[#write-box]", f"[#tag({ts(LETTERS[pos])})]",
                          f"[{self.md(q['items'][i])}]"]
            return (f"#hint({ts('Number them, ' + q['orderBy'] + '.')})\n#grid(columns: (auto, auto, 1fr), "
                    "column-gutter: 0.8em, row-gutter: 0.9em, align: horizon, " + ", ".join(cells) + ")")
        if f == "classify":
            groups = ", ".join(f"#tag({ts(str(n + 1))}) #{ts(g['name'])}" for n, g in enumerate(q["groups"]))
            cells = []
            for item, _ in q["_items"]:
                cells += ["[#write-box]", f"[{self.md(item)}]"]
            return (f"#hint([Write each one's group: {groups}.])\n#grid(columns: (auto, 1fr), column-gutter: 0.8em, "
                    "row-gutter: 0.9em, align: horizon, " + ", ".join(cells) + ")")
        if f == "match":
            cells = []
            n = len(q["pairs"])
            for k in range(n):
                left = q["pairs"][k][0]
                right = q["pairs"][q["_rights"][k]][1]
                cells += ["[#write-box]", f"[#tag({ts(str(k + 1))}) #h(4pt) {self.md(left)}]",
                          f"[#tag({ts(LETTERS[k])}) #h(4pt) {self.md(right)}]"]
            return ("#hint(\"Write beside each number the letter it goes with.\")\n#grid(columns: (auto, 1fr, 1fr), "
                    "column-gutter: 1em, row-gutter: 0.9em, align: horizon, " + ", ".join(cells) + ")")
        if f == "free-response":
            return "#v(0.4em)\n#ruled(8)"
        return ""

    def key(self, q: dict[str, Any]) -> str:
        """The answer, with why it is right and what to remember."""
        f = q["format"]
        out = []
        if f in ("choice-one", "choice-many"):
            cells = []
            for i, o in enumerate(q["options"]):
                mark = "#right-mark" if o["ok"] else "#wrong-mark"
                cells += [f"[{mark} #tag({ts(LETTERS[i])})]",
                          f"[{self.md(o['why'] or o['t'])}]"]
            out.append("#grid(columns: (auto, 1fr), column-gutter: 0.8em, row-gutter: 0.7em, " + ", ".join(cells) + ")")
        elif f == "short-answer":
            acc = ", ".join(f"#raw({ts(a)})" for a in q["accept"])
            out.append(f"#right-mark {acc}")
            if q.get("traps"):
                cells = []
                for tr in q["traps"]:
                    cells += [f"[#wrong-mark #raw({ts(tr['text'])})]", f"[{self.md(tr['why'])}]"]
                out.append("#grid(columns: (auto, 1fr), column-gutter: 0.8em, row-gutter: 0.7em, " + ", ".join(cells) + ")")
        elif f == "numeric":
            unit = f" {q['unit']}" if q.get("unit") else ""
            tol = q.get("tolerance") or {}
            within = ""
            if tol.get("value"):
                within = f" (within {tol['value']}{' %' if tol.get('kind') == 'relative' else unit})"
            out.append(f"#right-mark #text(weight: \"bold\", {ts(_num(q['answer']) + unit)}){self.plain(within)}")
        elif f == "spot":
            out.append(f"#right-mark Faulty: #tag({ts(', '.join(str(x) for x in q['faulty']))})")
            notes = q.get("notes") or {}
            if notes:
                cells = []
                for n in sorted(notes):
                    mark = "#right-mark" if n in q["faulty"] else "#wrong-mark"
                    cells += [f"[{mark} #tag({ts(str(n))})]", f"[{self.md(str(notes[n]))}]"]
                out.append("#grid(columns: (auto, 1fr), column-gutter: 0.8em, row-gutter: 0.7em, " + ", ".join(cells) + ")")
        elif f == "fill-gaps":
            cells = []
            for k, g in enumerate(q["gaps"]):
                cells += [f"[#tag({ts('(' + str(k + 1) + ')')}) #raw({ts(g['answer'])})]", f"[{self.md(g['why'])}]"]
            out.append("#grid(columns: (auto, 1fr), column-gutter: 1em, row-gutter: 0.7em, " + ", ".join(cells) + ")")
        elif f == "order":
            shown_at = {i: pos for pos, i in enumerate(q["_shown"])}
            seq = " → ".join(LETTERS[shown_at[i]] for i in range(len(q["items"])))
            out.append(f"#right-mark #tag({ts(seq)})")
            out.append("#enum(" + ", ".join(f"[{self.md(it)}]" for it in q["items"]) + ")")
        elif f == "classify":
            cells = []
            for n, g in enumerate(q["groups"]):
                cells += [f"[#tag({ts(str(n + 1) + ' ' + g['name'])})]",
                          "[" + " #h(3pt)·#h(3pt) ".join(self.md(i) for i in g["items"]) + "]"]
            out.append("#grid(columns: (auto, 1fr), column-gutter: 1em, row-gutter: 0.7em, " + ", ".join(cells) + ")")
        elif f == "match":
            letter_of = {pair: LETTERS[pos] for pos, pair in enumerate(q["_rights"])}
            out.append("#right-mark #tag(" + ts(", ".join(f"{k + 1} → {letter_of[k]}" for k in range(len(q["pairs"]))))
                       + ")")
        elif f == "free-response":
            out.append(self.md(q["model"]))
            if q.get("points"):
                out.append("#hint(\"A strong answer covers:\")")
                out.append("#list(" + ", ".join(f"[{self.md(p)}]" for p in q["points"]) + ")")
        elif f == "case":
            for k, st in enumerate(q["steps"]):
                out.append(f"#step-head({ts('(' + LETTERS[k].lower() + ')')})")
                out.append(self.key(st))
        if q.get("why") and f not in ("case",):
            out.append(self.md(q["why"]))
        if q.get("takeaway"):
            out.append(f"#takeaway[{self.md(q['takeaway'])}]")
        return "\n\n".join(x for x in out if x)


# ----------------------------------------------------------------------------------------------
# HTML
# ----------------------------------------------------------------------------------------------
def md_html(text: str) -> str:
    from markdown_it import MarkdownIt
    from ...code import highlight
    md = MarkdownIt("commonmark", {"html": False})
    md.options["highlight"] = lambda src, lang, attrs: highlight(src.rstrip("\n"), lang or None)
    return md.render(text or "")


class Web:
    """A question and its answer as HTML (the text escaped; code highlighted in the theme's colours)."""

    def material(self, m: dict[str, Any], spot: bool = False, gaps: bool = False) -> str:
        from ...code import highlight
        k = m["kind"]
        if k == "code":
            src = _gapped(m["text"], False) if gaps else m["text"]
            if spot:
                width = len(str(src.count("\n") + 1))
                src = "\n".join(f"{n:>{width}}  {line}" for n, line in enumerate(src.split("\n"), 1))
            return highlight(src, None if (m.get("lang") or "text") == "text" else m.get("lang"))
        if k == "text":
            return md_html(_gapped(m["text"], True) if gaps else m["text"])
        if k == "list":
            return "<ol>" + "".join(f"<li>{inline(i)}</li>" for i in m["items"]) + "</ol>"
        if k == "dialogue":
            rows = "".join(f"<p>{(str(n) + '. ') if spot else ''}<strong>{H.escape(t['who'])}:</strong> "
                           f"{inline(t['says'])}</p>" for n, t in enumerate(m["turns"], 1))
            return f"<blockquote>{rows}</blockquote>"
        if k == "table":
            cols = (["#"] if spot else []) + m["columns"]
            head = "".join(f"<th>{H.escape(c)}</th>" for c in cols)
            body = "".join("<tr>" + (f"<td>{n}</td>" if spot else "") + "".join(f"<td>{inline(c)}</td>" for c in r)
                           + "</tr>" for n, r in enumerate(m["rows"], 1))
            return f'<div class="table card"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
        return ""

    def body(self, q: dict[str, Any]) -> str:
        f = q["format"]
        if f == "case":
            parts = [md_html(q["scenario"]), md_html(q["q"])]
            for k, st in enumerate(q["steps"]):
                parts.append(f"<h3>({LETTERS[k].lower()})</h3>" + self.body(st))
            return "".join(parts)
        return (self.material(q["material"], spot=f == "spot", gaps=f == "fill-gaps") + md_html(q["q"])
                + self.area(q))

    def area(self, q: dict[str, Any]) -> str:
        f = q["format"]
        if f in ("choice-one", "choice-many"):
            items = "".join(f"<li>{inline(o['t'])}</li>" for o in q["options"])
            hint = "Tick one." if f == "choice-one" else "Tick every one that applies."
            return f'<p class="caption"><em>{hint}</em></p><ol type="A">{items}</ol>'
        if f == "fill-gaps":
            items = "".join(f"<li>{H.escape(' · '.join(g['choices']))}</li>" for g in q["gaps"])
            return f"<p><em>Choose a word for each gap:</em></p><ol>{items}</ol>"
        if f == "order":
            items = "".join(f"<li>{inline(q['items'][i])}</li>" for i in q["_shown"])
            return f"<p><em>Put them in order, {H.escape(q['orderBy'])}.</em></p><ol type=\"A\">{items}</ol>"
        if f == "classify":
            groups = ", ".join(f"<strong>{n + 1}</strong> {H.escape(g['name'])}" for n, g in enumerate(q["groups"]))
            items = "".join(f"<li>{inline(item)}</li>" for item, _ in q["_items"])
            return f"<p><em>Sort each into its group: {groups}.</em></p><ul>{items}</ul>"
        if f == "match":
            n = len(q["pairs"])
            rows = "".join(f"<tr><td><strong>{k + 1}</strong> {inline(q['pairs'][k][0])}</td>"
                           f"<td><strong>{LETTERS[k]}</strong> {inline(q['pairs'][q['_rights'][k]][1])}</td></tr>"
                           for k in range(n))
            return f'<div class="table card"><table><tbody>{rows}</tbody></table></div>'
        if f == "spot":
            return "<p><em>Which parts are faulty? Note their numbers.</em></p>"
        return ""

    def key(self, q: dict[str, Any]) -> str:
        f = q["format"]
        out = []
        if f in ("choice-one", "choice-many"):
            out.append("<ul>" + "".join(
                f"<li>{'✓' if o['ok'] else '✗'} <strong>{LETTERS[i]}</strong> {inline(o['why'] or o['t'])}</li>"
                for i, o in enumerate(q["options"])) + "</ul>")
        elif f == "short-answer":
            out.append("<p>✓ " + ", ".join(f"<code>{H.escape(a)}</code>" for a in q["accept"]) + "</p>")
            if q.get("traps"):
                out.append("<ul>" + "".join(f"<li>✗ <code>{H.escape(t['text'])}</code>: {inline(t['why'])}</li>"
                                            for t in q["traps"]) + "</ul>")
        elif f == "case":
            for k, st in enumerate(q["steps"]):
                out.append(f"<h3>({LETTERS[k].lower()})</h3>" + self.key(st))
        elif f == "free-response":
            out.append(md_html(q["model"]))
            if q.get("points"):
                out.append("<p><em>A strong answer covers:</em></p><ul>"
                           + "".join(f"<li>{inline(p)}</li>" for p in q["points"]) + "</ul>")
        elif f == "order":
            shown_at = {i: pos for pos, i in enumerate(q["_shown"])}
            out.append("<p>✓ <strong>" + " → ".join(LETTERS[shown_at[i]] for i in range(len(q["items"])))
                       + "</strong></p>")
            out.append("<ol>" + "".join(f"<li>{inline(it)}</li>" for it in q["items"]) + "</ol>")
        elif f == "match":
            letter_of = {pair: LETTERS[pos] for pos, pair in enumerate(q["_rights"])}
            out.append("<p>✓ " + ", ".join(f"<strong>{k + 1}</strong> → <strong>{letter_of[k]}</strong>"
                                           for k in range(len(q["pairs"]))) + "</p>")
        elif f == "spot":
            out.append(f"<p>✓ Faulty: <strong>{', '.join(str(x) for x in q['faulty'])}</strong></p>")
            notes = q.get("notes") or {}
            if notes:
                out.append("<ul>" + "".join(f"<li>{'✓' if n in q['faulty'] else '✗'} <strong>{n}</strong> "
                                            f"{inline(str(notes[n]))}</li>" for n in sorted(notes)) + "</ul>")
        elif f == "fill-gaps":
            out.append("<ul>" + "".join(f"<li><strong>({k + 1}) {H.escape(g['answer'])}</strong>: {inline(g['why'])}</li>"
                                        for k, g in enumerate(q["gaps"])) + "</ul>")
        elif f == "classify":
            out.append("<ul>" + "".join(f"<li><strong>{H.escape(g['name'])}</strong>: "
                                        + "; ".join(inline(i) for i in g["items"]) + "</li>" for g in q["groups"]) + "</ul>")
        else:
            out.append(md_html(answer_text(q)))
        if q.get("why") and f != "case":
            out.append(md_html(q["why"]))
        if q.get("takeaway"):
            out.append(f"<p><strong>Takeaway:</strong> {inline(q['takeaway'])}</p>")
        return "".join(out)
