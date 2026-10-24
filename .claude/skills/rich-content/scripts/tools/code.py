"""
code — source code highlighted in the theme's colours, the same in an HTML page (Pygments) and in a
PDF (a TextMate theme Typst reads), so a code block looks alike in both.

    from tools.code import highlight
    html = highlight('print("hi")', "python")       # <pre class="code">…</pre>; Page.code() calls it

The colours are the theme's kind colours, which every theme holds to text contrast: keywords in the
compute colour, strings in the data colour, numbers in the async colour, function and class names in
the edge colour, built-ins in the cache colour, comments in muted italic, the rest in ink.
"""
from __future__ import annotations

from html import escape
from typing import Any

from .theme import Theme, current


def roles(th: Theme) -> dict[str, str]:
    k = th.kinds
    return {"keyword": k["compute"]["stroke"], "string": k["data"]["stroke"], "number": k["async"]["stroke"],
            "name": k["edge"]["stroke"], "builtin": k["cache"]["stroke"], "comment": th.colour["muted"],
            "text": th.colour["ink"], "error": th.signal["bad"]}


def _style(th: Theme) -> Any:
    from pygments.style import Style
    from pygments.token import (Comment, Error, Keyword, Name, Number, Operator, Punctuation, String, Text,
                                Token)
    r = roles(th)
    styles = {
        Token: r["text"], Text: r["text"], Punctuation: r["text"], Operator: r["text"],
        Keyword: f"bold {r['keyword']}", Keyword.Constant: f"bold {r['keyword']}",
        Name.Builtin: r["builtin"], Name.Attribute: r["builtin"], Name.Tag: r["keyword"],
        Name.Function: r["name"], Name.Class: f"bold {r['name']}", Name.Decorator: r["name"],
        String: r["string"], Number: r["number"], Comment: f"italic {r['comment']}",
        Error: r["error"],
    }
    return type("ThemeStyle", (Style,), {"styles": styles, "background_color": th.colour["paper"]})


def css(th: Theme | None = None, scope: str = ".code") -> str:
    """The CSS for highlighted code inside `scope`, in the theme's colours."""
    from pygments.formatters import HtmlFormatter
    th = th or current()
    return HtmlFormatter(style=_style(th)).get_style_defs(scope)


def highlight(src: str, language: str | None = None) -> str:
    """Code as an HTML block, highlighted when Pygments knows the language, plain when not."""
    from pygments import highlight as pyg
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_by_name
    from pygments.util import ClassNotFound
    try:
        lexer = get_lexer_by_name(language) if language else None
    except ClassNotFound:
        lexer = None
    body = pyg(src, lexer, HtmlFormatter(nowrap=True)) if lexer else escape(src)
    return f'<pre class="code"><code>{body.rstrip()}</code></pre>'


def tm_theme(th: Theme | None = None) -> str:
    """A TextMate theme with the same colours, for Typst's `raw` (render.pdf passes it in)."""
    th = th or current()
    r = roles(th)

    def rule(scope: str, colour: str, style: str = "") -> str:
        extra = f"<key>fontStyle</key><string>{style}</string>" if style else ""
        return (f"<dict><key>scope</key><string>{scope}</string><key>settings</key><dict>"
                f"<key>foreground</key><string>{colour}</string>{extra}</dict></dict>")
    rules = [
        rule("keyword, storage, keyword.control, constant.language", r["keyword"], "bold"),
        rule("string, string.quoted", r["string"]),
        rule("constant.numeric, constant.character", r["number"]),
        rule("entity.name.function, entity.name.class, entity.name.type, meta.decorator", r["name"]),
        rule("support.function, support.type, support.class, entity.other.attribute-name, variable.language",
             r["builtin"]),
        rule("comment, punctuation.definition.comment", r["comment"], "italic"),
        rule("invalid", r["error"]),
    ]
    return ('<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict>'
            f"<key>name</key><string>{th.name}</string><key>settings</key><array>"
            f"<dict><key>settings</key><dict><key>foreground</key><string>{r['text']}</string></dict></dict>"
            + "".join(rules) + "</array></dict></plist>")


__all__ = ["highlight", "css", "tm_theme", "roles"]
