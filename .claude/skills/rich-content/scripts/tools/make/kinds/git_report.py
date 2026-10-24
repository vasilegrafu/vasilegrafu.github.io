"""
A page on a repository's history, read from git: how much changed, week by week, where, and the latest
commits. Merges are left out; a commit's date is its author's.

  repo:     the repository, relative to the spec (the checkout the spec is in by default)
  since:    the first day counted, YYYY-MM-DD (from the first commit by default)
  until:    the last day counted, YYYY-MM-DD (today by default -- set it, or the page moves with every
            commit and --check calls it stale)
  paths:    only commits touching these paths, and only these paths counted: [src, docs/x.md]
  folders:  how many levels of a path name its folder in "where": 1 (the default) counts docs, src; 3
            counts .claude/skills/rich-content
  files:    how many of the most-changed files to list (12);  latest: how many recent commits (15)
  title, eyebrow, lead, footer, format (html | pdf | [html, pdf]): as for the doc kind; the title is
            "<repository>: its history" when not given
"""
from __future__ import annotations

import math
import re
import subprocess
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from .. import Spec, SpecError
from ..document import Doc, common

PURPOSE = "a page on a repository's history from git: activity by week, where it went, the latest commits"
GROUP = "from the repository"
OUTPUT = "html|pdf"

DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SpecError(f"git {' '.join(args[:2])}: {r.stderr.strip()[:300]}")
    return r.stdout


def md_escape(s: str) -> str:
    """Text as Markdown shows it as written: every character Markdown would read as markup escaped."""
    return re.sub(r"([\\`*_\[\]<>#!|~])", r"\\\1", s)


def renamed(path: str) -> str:
    """git's numstat names a moved file "{old => new}/x" or "old => new": the path it has now."""
    path = re.sub(r"\{[^{}]*? => ([^{}]*?)\}", r"\1", path)
    if " => " in path:
        path = path.split(" => ", 1)[1]
    return path.replace("//", "/")


def document(spec: Spec) -> Doc:
    where = spec.path("repo")
    start = where or spec.base
    try:
        top = Path(git(start, "rev-parse", "--show-toplevel").strip())
    except SpecError:
        raise SpecError(f"repo: {start} is not in a git repository") from None
    # YAML reads 2026-10-23 as a date; quoted, it is text: either is a day
    since = spec.get("since", kind=(str, date))
    until = spec.get("until", kind=(str, date))
    since, until = (v.isoformat() if isinstance(v, date) else v for v in (since, until))
    for key, v in (("since", since), ("until", until)):
        if v is not None and not DAY.match(v):
            raise SpecError(f"{key}: a day, YYYY-MM-DD")
    paths = [str(p) for p in spec.get("paths", [], list)]
    depth = spec.get("folders", 1, int)
    n_files = spec.get("files", 12, int)
    n_latest = spec.get("latest", 15, int)
    spec.data.setdefault("title", f"{top.name}: its history")

    args = ["log", "--no-merges", "--numstat", "--date=short", "--format=%x1e%h%x1f%ad%x1f%an%x1f%s"]
    if since:
        args.append(f"--since={since} 00:00:00")
    if until:
        args.append(f"--until={until} 23:59:59")
    args += ["--", *paths] if paths else []
    commits = []
    for rec in git(top, *args).split("\x1e")[1:]:
        head, _, body = rec.partition("\n")
        h, day, author, subject = head.split("\x1f", 3)
        files = []
        for line in body.splitlines():
            parts = line.split("\t")
            if len(parts) == 3:
                add = int(parts[0]) if parts[0].isdigit() else 0
                rem = int(parts[1]) if parts[1].isdigit() else 0
                files.append((renamed(parts[2]), add, rem))
        commits.append({"hash": h, "day": date.fromisoformat(day), "author": author, "subject": subject,
                        "files": files})
    if not commits:
        raise SpecError("no commits in that range" + (" touching those paths" if paths else ""))

    first, last = min(c["day"] for c in commits), max(c["day"] for c in commits)
    added = sum(a for c in commits for _, a, _ in c["files"])
    removed = sum(r for c in commits for _, _, r in c["files"])
    touched = {p for c in commits for p, _, _ in c["files"]}
    days = {c["day"] for c in commits}
    authors = Counter(c["author"] for c in commits)

    # week by week, Mondays, the empty weeks too
    monday = first - timedelta(days=first.weekday())
    weeks = []
    while monday <= last:
        weeks.append(monday)
        monday += timedelta(days=7)
    per_week = Counter(c["day"] - timedelta(days=c["day"].weekday()) for c in commits)
    every = max(1, math.ceil(len(weeks) / 7))          # a label every few weeks, so none runs into the next
    week_labels = [f"{w.day} {w:%b}" if k % every == 0 else "" for k, w in enumerate(weeks)]

    def folder(p: str) -> str:
        parts = p.split("/")[:-1]
        return "/".join(parts[:depth]) if parts else "(top)"

    by_folder: Counter = Counter()
    for c in commits:
        for f in {folder(p) for p, _, _ in c["files"]}:
            by_folder[f] += 1
    top_folders = by_folder.most_common(8)
    by_file: dict[str, list[int]] = {}
    for c in commits:
        for p, a, r in c["files"]:
            row = by_file.setdefault(p, [0, 0, 0])
            row[0] += 1
            row[1] += a
            row[2] += r
    most = sorted(by_file.items(), key=lambda kv: (-kv[1][0], -(kv[1][1] + kv[1][2]), kv[0]))[:n_files]

    doc = common(spec)
    if doc.lead is None:
        span = f"{first.day} {first:%B %Y}" + (f" to {last.day} {last:%B %Y}" if last != first else "")
        doc.lead = (f"{len(commits)} commits from {span}"
                    + (f", touching {', '.join('`' + p + '`' for p in paths)}" if paths else "")
                    + f", by {len(authors)} author{'s' if len(authors) != 1 else ''}. Merges are left out.")
    if doc.eyebrow is None:
        doc.eyebrow = "History, from git"
    doc.blocks = [
        {"kpis": [["Commits", f"{len(commits):,}", f"on {len(days)} days", "neutral"],
                  ["Files touched", f"{len(touched):,}", f"in {len(by_folder)} folders", "neutral"],
                  ["Lines added", f"+{added:,}", f"{added / max(len(commits), 1):,.0f} a commit", "good"],
                  ["Lines removed", f"−{removed:,}", f"{removed / max(len(commits), 1):,.0f} a commit", "neutral"]]},
        {"h2": "Week by week"},
        {"figure": {"make": "chart", "type": "bar", "title": f"Commits a week, the busiest {max(per_week.values())}",
                    "x": week_labels, "series": {"commits": [per_week.get(w, 0) for w in weeks]},
                    "size": [6.4, 2.4], "colors": ["blue"]},
         "caption": f"Each bar is a week from its Monday; {len(weeks)} week{'s' if len(weeks) != 1 else ''}, "
                    f"{len([w for w in weeks if per_week.get(w)])} with commits."},
        {"h2": "Where the work went"},
        {"figure": {"make": "chart", "type": "hbar", "title": "Commits that touched each folder",
                    "x": [f for f, _ in top_folders], "series": {"commits": [n for _, n in top_folders]},
                    "values": True, "size": [6.4, max(1.4, 0.32 * len(top_folders) + 0.6)], "colors": ["teal"]},
         "caption": "A commit counts once for each folder it touched, so the bars add up to more than the commits."
                    + (f" The {len(by_folder) - len(top_folders)} other folders are left out." if len(by_folder) > len(top_folders) else "")},
        {"table": {"header": ["File", "Commits", "Added", "Removed"],
                   "rows": [[f"`{p}`" if "`" not in p else md_escape(p), str(n), f"+{a:,}", f"−{r:,}"]
                            for p, (n, a, r) in most],
                   "numeric": [1, 2, 3]},
         "caption": f"The {len(most)} files changed in the most commits."},
        {"h2": "The latest commits"},
        {"table": {"header": ["Day", "Commit", "Subject"],
                   "rows": [[f"{c['day'].day} {c['day']:%b %Y}", f"`{c['hash']}`", md_escape(c["subject"])]
                            for c in commits[:n_latest]]},
         "caption": f"The {min(n_latest, len(commits))} most recent, newest first."},
    ]
    return doc
