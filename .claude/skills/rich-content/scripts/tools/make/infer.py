"""What a box is when a spec names it only: its kind, icon and shape, guessed from its words, and the
short forms specs write -- a box as "Label", an edge as "a -> b: label"."""
from __future__ import annotations

import re
from typing import Any

from . import Spec, SpecError

KINDS = ("client", "edge", "compute", "cache", "data", "async", "external")
STATES = ("normal", "dim", "focus", "fail", "warn", "good")

# (words, kind, icon, shape): the first whose word is in the box's id or label wins
RULES: list[tuple[tuple[str, ...], str, str, str]] = [
    (("cache", "redis", "memcached", "cdn cache"), "cache", "zap", "box"),
    (("queue", "kafka", "rabbitmq", "rabbit", "sqs", "topic", "stream", "bus", "pubsub", "kinesis", "events",
      "outbox", "inbox"), "async", "send", "queue"),
    (("db", "database", "postgres", "postgresql", "mysql", "sql", "sqlite", "mongo", "mongodb", "dynamo",
      "dynamodb", "cassandra", "warehouse", "replica", "primary", "ledger"), "data", "database", "cylinder"),
    (("s3", "bucket", "blob", "storage", "disk", "files", "volume"), "data", "hard-drive", "box"),
    (("mobile", "phone", "ios", "android"), "client", "smartphone", "box"),
    (("user", "users", "customer", "customers", "person", "people", "admin", "staff"), "client", "users", "box"),
    (("browser", "client", "web", "frontend", "spa", "ui", "desktop"), "client", "monitor", "box"),
    (("cdn", "dns"), "edge", "globe", "box"),
    (("firewall", "waf"), "edge", "shield", "box"),
    (("gateway", "lb", "balancer", "proxy", "nginx", "ingress", "router", "edge", "envoy"), "edge", "network", "box"),
    (("stripe", "payment", "payments", "paypal", "bank", "card"), "external", "credit-card", "box"),
    (("email", "mail", "smtp", "sendgrid", "ses", "mailer"), "external", "mail", "box"),
    (("external", "third-party", "partner", "saas", "vendor", "provider"), "external", "cloud", "box"),
    (("auth", "identity", "login", "oauth", "sso", "iam"), "compute", "shield", "box"),
    (("llm", "ai", "model", "agent", "bot", "claude"), "compute", "bot", "box"),
    (("worker", "job", "jobs", "cron", "scheduler", "batch", "consumer"), "compute", "cog", "box"),
    (("function", "lambda", "serverless"), "compute", "code", "box"),
    (("search", "elastic", "index", "opensearch"), "data", "files", "box"),
    (("ci", "build", "pipeline", "deploy"), "compute", "hammer", "box"),
    (("cli", "terminal", "shell", "console"), "client", "terminal", "box"),
]


def words(*texts: str) -> list[str]:
    return [w for t in texts for w in re.split(r"[^a-z0-9]+", t.lower().replace("-", " ")) if w]


def guess(ident: str, label: str) -> tuple[str, str, str]:
    """kind, icon, shape for a box called `ident`, labelled `label`."""
    ws = words(ident, label)
    joined = " ".join(ws)
    for keys, k, icon, shape in RULES:
        for key in keys:
            if (" " in key and key in joined) or key in ws:
                return k, icon, shape
    return "compute", "server", "box"


def box(ident: str, value: Any, parent: Spec, where: str, extra: tuple[str, ...] = ()) -> dict[str, Any]:
    """A box from a spec: "Label", or a mapping of label, sub, kind, icon, shape, state, count, tag
    and `extra` keys; what is not given is guessed from its words."""
    if value is None:
        value = ident
    if isinstance(value, (str, int, float)):
        label = str(value)
        k, icon, shape = guess(ident, label)
        return {"id": ident, "label": label, "sub": None, "kind": k, "icon": icon, "shape": shape,
                "state": "normal", "count": None, "tag": None}
    s = value if isinstance(value, Spec) else parent.wrap(value, where)
    label = str(s.get("label", ident))
    k, icon, shape = guess(ident, label)
    out = {
        "id": ident, "label": label, "sub": s.get("sub", kind=str),
        "kind": s.get("kind", k, str, KINDS),
        "state": s.get("state", "normal", str, STATES),
        "count": s.get("count", None, int), "tag": s.get("tag", None, str),
    }
    given_kind = "kind" in s.data
    out["icon"] = s.get("icon", None if given_kind and out["kind"] != k else icon)
    if out["icon"] is False:
        out["icon"] = None
    out["shape"] = s.get("shape", shape if not given_kind or out["kind"] == k else
                         ("cylinder" if out["kind"] == "data" else "queue" if out["kind"] == "async" else "box"),
                         str, ("box", "cylinder", "queue"))
    for key in extra:
        out[key] = s.get(key)
    return out


EDGE = re.compile(r"^\s*([^\s:<>-][^\s:<>]*?)\s*(<-->|<->|-->|->|<--|<-|--|—)\s*([^\s:<>-][^\s:<>]*?)\s*(?::\s*(.*?))?\s*$")


def edge(value: Any, parent: Spec, where: str, known: set[str] | None = None,
         extra: tuple[str, ...] = ()) -> dict[str, Any]:
    """An edge from a spec: "a -> b: label" (--> dashed, <-> both ways, -- no head), or a mapping of
    from, to, label, dash, both, head, color and `extra` keys."""
    if isinstance(value, str):
        m = EDGE.match(value)
        if not m:
            raise SpecError(f"{parent.where}{where}: {value!r} is not an edge (\"a -> b: label\")")
        a, arrow, b, label = m.groups()
        if arrow in ("<-", "<--"):
            a, b = b, a
        e = {"from": a, "to": b, "label": label or None, "dash": arrow in ("-->", "<--", "<-->"),
             "both": arrow.startswith("<") and arrow.endswith(">"), "head": arrow not in ("--", "—"),
             "color": None, "mono": False}
        for key in extra:
            e[key] = None
    else:
        s = value if isinstance(value, Spec) else parent.wrap(value, where)
        e = {"from": str(s.need("from")), "to": str(s.need("to")), "label": s.get("label"),
             "dash": bool(s.get("dash", False, bool)), "both": bool(s.get("both", False, bool)),
             "head": bool(s.get("head", True, bool)),
             "color": s.get("color", None, str, ("good", "bad", "warn", "info", "accent", "muted", "ink")),
             "mono": bool(s.get("mono", False, bool))}
        for key in extra:
            e[key] = s.get(key)
    if e["label"] is not None:
        e["label"] = str(e["label"])
        if e["label"].startswith("`") and e["label"].endswith("`") and len(e["label"]) > 1:
            e["label"], e["mono"] = e["label"][1:-1], True
    if known is not None:
        for end in (e["from"], e["to"]):
            if end not in known:
                raise SpecError(f"{parent.where}{where}: no box `{end}`; there are: {', '.join(sorted(known))}")
    return e


def colour(c: Any, name: str | None, default: str) -> str:
    """A colour named in a spec -- a signal, accent, muted, ink -- on canvas `c`."""
    if name is None:
        return default
    if name in ("good", "bad", "warn", "info"):
        return c.th.signal[name]
    return c.col(name)
