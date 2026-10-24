#!/usr/bin/env python3
"""Claude Code status line for this checkout.

Claude Code runs this with one JSON payload on stdin and shows whatever it
prints. One line, in this shape:

  Fable 5.1 (1M context) | high | ctx: 42%/1M (58%) | 5h: 23% (2h14m) | 7d: 41% (3d06h)

Every segment survives its field being absent -- rate limits arrive only for
Pro/Max subscribers and only after the first response; context percentages
are null before the first call and right after /compact -- because a status
line script that raises shows nothing and says nothing.

The two rate-limit windows are the whole of what Claude Code sends: a
per-model budget is not in the payload, so it is not shown.

Standard library only.
"""
import json
import re
import sys
import time
from pathlib import Path



def utf8_stdio() -> str:
    """The payload on stdin as text, and stdout set to UTF-8. Claude Code
    writes and reads UTF-8, but on Windows a piped stream is the locale's
    code page (cp1252 here): read that way, a dash in a description comes
    out as three letters of mojibake, and a character the code page lacks
    cannot be printed at all. `replace` keeps a stray byte from taking the
    payload down."""
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    return sys.stdin.buffer.read().decode("utf-8", errors="replace")


def model_label(model: dict) -> str:
    """`Fable 5.1` from display_name `Fable` and id `claude-fable-5-1[1m]`."""
    name = model.get("display_name") or model.get("id") or "?"
    if re.search(r"\d", name):
        return name
    m = re.search(r"-(\d+)-(\d+)", model.get("id") or "")
    return f"{name} {m.group(1)}.{m.group(2)}" if m else name


def effort_label(data: dict) -> str:
    """The live effort level; the user settings' `effortLevel` when the
    payload carries none, which happens for a model without the parameter."""
    level = (data.get("effort") or {}).get("level")
    if level:
        return level
    try:
        settings = json.loads(Path.home().joinpath(".claude", "settings.json")
                              .read_text(encoding="utf-8"))
        return settings.get("effortLevel") or "--"
    except (OSError, ValueError):
        return "--"


def num(value):
    """Coerce a payload field that may arrive as a number or a numeric
    string; None when it cannot be read as one."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def size_label(size) -> str:
    size = num(size)
    if not size:
        return "?"
    if size >= 1_000_000:
        return f"{size / 1_000_000:g}M"
    return f"{int(size) // 1000}K"


def pct(value) -> str:
    value = num(value)
    return "--" if value is None else f"{value:.0f}%"


def until(epoch) -> str:
    """Time left until a Unix-seconds instant: 37m, 2h14m, 3d06h."""
    epoch = num(epoch)
    if not epoch:
        return "--"
    left = int(epoch - time.time())
    if left <= 0:
        return "now"
    d, rem = divmod(left, 86400)
    h, rem = divmod(rem, 3600)
    m = rem // 60
    if d:
        return f"{d}d{h:02d}h"
    if h:
        return f"{h}h{m:02d}m"
    return f"{m}m"


def window(rate: dict, key: str) -> str:
    w = rate.get(key) or {}
    if not w:
        return "--"
    return f"{pct(w.get('used_percentage'))} ({until(w.get('resets_at'))})"


def main(data: dict) -> None:
    model = data.get("model") or {}
    ctx = data.get("context_window") or {}
    rate = data.get("rate_limits") or {}

    size = size_label(ctx.get("context_window_size"))
    parts = [
        f"{model_label(model)} ({size} context)",
        effort_label(data),
        f"ctx: {pct(ctx.get('used_percentage'))}/{size} ({pct(ctx.get('remaining_percentage'))})",
        f"5h: {window(rate, 'five_hour')}",
        f"7d: {window(rate, 'seven_day')}",
    ]
    print(" | ".join(parts))


if __name__ == "__main__":
    raw = utf8_stdio()
    try:
        data = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        data = {}
    try:
        main(data)
    except Exception:  # a status line that raises shows nothing; print something instead
        try:
            fallback = model_label(data.get("model") or {})
        except Exception:
            fallback = None
        print(fallback or "status unavailable")
    sys.exit(0)
