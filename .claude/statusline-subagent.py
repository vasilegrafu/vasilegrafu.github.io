#!/usr/bin/env python3
"""Claude Code subagent rows for this checkout.

Claude Code runs this once per refresh tick with every visible subagent in
one JSON object on stdin -- a `tasks` array and `columns`, the usable row
width -- and replaces the body of each row in the agent panel with whatever
this prints for its id. One JSON line per row:

  {"id": "<task id>", "content": "Sonnet 5 (200K context) | high | ctx: 17%/200K (83%) | general-purpose . fix the login"}

A row this script prints nothing for keeps Claude Code's default rendering,
so a task it cannot format is left out rather than shown wrong.

The payload names the model by resolved id only, so the display name is
derived from it; the context percentage is tokenCount over contextWindowSize,
which is how the docs say to render one. Shares its formatting with
statusline.py beside it.

Standard library only.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from statusline import effort_label, pct, size_label, utf8_stdio  # noqa: E402


def model_label(model_id: str) -> str:
    """`Fable 5.1` from `claude-fable-5-1`, `Haiku 4.5` from
    `claude-haiku-4-5-20251001`: the family word, then the version digits
    before any date stamp."""
    if not model_id:
        return "?"
    m = re.match(r"(?:claude-)?([a-z]+)-(\d+)(?:-(\d+))?(?=-\d{8}|\[|$)", model_id)
    if not m:
        return model_id
    family = m.group(1).capitalize()
    version = m.group(2) + (f".{m.group(3)}" if m.group(3) else "")
    return f"{family} {version}"


def effort(task: dict) -> str:
    level = task.get("effort")
    if isinstance(level, (int, float)):
        return f"{int(level) // 1000}k" if level >= 1000 else str(int(level))
    if level:
        return str(level)
    return effort_label({})  # the user's default, as the main line does


def context(task: dict, size) -> str:
    tokens = task.get("tokenCount")
    label = size_label(size)
    if tokens is None or not size:
        return f"ctx: --/{label} (--)"
    used = min(100.0, 100.0 * tokens / size)
    return f"ctx: {pct(used)}/{label} ({pct(100.0 - used)})"


def doing(task: dict) -> str:
    name = task.get("name") or task.get("type") or "agent"
    what = task.get("description") or task.get("label") or ""
    text = f"{name} . {what}" if what else name
    status = task.get("status")
    if status and status not in ("running", "in_progress", "active"):
        text += f" ({status})"
    return text


def fit(text: str, columns) -> str:
    if not columns or len(text) <= columns:
        return text
    return text[: max(1, columns - 3)] + "..."


def row(task: dict, columns) -> str:
    size = task.get("contextWindowSize")
    parts = [
        f"{model_label(task.get('model') or '')} ({size_label(size)} context)",
        effort(task),
        context(task, size),
        doing(task),
    ]
    return fit(" | ".join(parts), columns)


def main() -> None:
    raw = utf8_stdio()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return
    columns = data.get("columns")
    for task in data.get("tasks") or []:
        task_id = task.get("id") if isinstance(task, dict) else None
        if not task_id:
            continue
        try:
            content = row(task, columns)
        except Exception:  # a row this cannot format keeps the default
            continue
        print(json.dumps({"id": task_id, "content": content}))


if __name__ == "__main__":
    main()
