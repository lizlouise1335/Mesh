#!/usr/bin/env python3
"""Create labels, milestones and the 38 issues from docs/PLAN.md via the `gh` CLI.

Usage:
  python3 scripts/bootstrap_github.py --dry-run   # parse and print, touch nothing
  python3 scripts/bootstrap_github.py             # create on GitHub (needs `gh auth login`)

The plan number goes in the title as "[N] Title" (GitHub assigns its own numbers).
Re-running skips issues whose title already exists.
Estimate and Sprint are not labels; they are written into the issue body so they
can be copied into GitHub Project fields.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "lizlouise1335/Mesh"
DRY = "--dry-run" in sys.argv

MILESTONE_BY_HEADING = {
    "Milestone 1": "Oct Foundations",
    "Milestone 2": "Nov Distributed",
    "Milestone 3": "Dec Agents",
    "Milestone 4": "Jan Production",
}
TYPES = {"Feature", "Infrastructure", "Data", "Test", "Documentation"}


def parse_plan():
    issues, milestone, sprint = [], None, None
    cur = None
    for line in (ROOT / "docs/PLAN.md").read_text().splitlines():
        m = re.match(r"# (Milestone \d)", line)
        if m:
            milestone = MILESTONE_BY_HEADING[m.group(1)]
        m = re.match(r"### (\w{3} W\d)", line)
        if m:
            sprint = m.group(1)
        m = re.match(r"#### #(\d+) (.+)", line)
        if m:
            cur = {"n": int(m.group(1)), "title": m.group(2), "milestone": milestone,
                   "sprint": sprint, "body": []}
            issues.append(cur)
            continue
        if line.startswith("## ") or line.startswith("# "):
            cur = None
        if cur is not None:
            cur["body"].append(line)
    for i in issues:
        meta = re.match(r"\*\*(P\d) · (\w+) · (\d)\*\*", next(l for l in i["body"] if l.strip()))
        i["priority"], i["type"], i["estimate"] = meta.group(1), meta.group(2), meta.group(3)
        rest = [l for l in i["body"] if l.strip() and not l.startswith("**P")]
        i["text"] = "\n\n".join(rest).strip()
    return issues


# Area per issue (the plan gives Type inline; Area is its own project field).
AREAS = {
    1: "infra", 2: "infra", 3: "data", 4: "data", 5: "data", 6: "backend", 7: "backend",
    8: "matching", 9: "matching", 10: "matching", 11: "data", 12: "infra", 13: "frontend",
    14: "security", 15: "distributed", 16: "infra", 17: "distributed", 18: "distributed",
    19: "infra", 20: "distributed", 21: "distributed", 22: "distributed", 23: "mcp",
    24: "security", 25: "agents", 26: "agents", 27: "agents", 28: "agents", 29: "agents",
    30: "security", 31: "security", 32: "observability", 33: "distributed", 34: "distributed",
    35: "distributed", 36: "infra", 37: "distributed", 38: "backend",
}


def gh(*args, stdin=None):
    cmd = ["gh", *args]
    if DRY:
        print("DRY:", " ".join(cmd[:6]), "...")
        return ""
    return subprocess.run(cmd, input=stdin, text=True, check=True, capture_output=True).stdout


def main():
    issues = parse_plan()
    assert len(issues) == 38, f"expected 38 issues, parsed {len(issues)}"
    for l in json.loads((ROOT / ".github/labels.json").read_text()):
        if not DRY:
            subprocess.run(["gh", "label", "create", l["name"], "--color", l["color"],
                            "--repo", REPO, "--force"], check=True, capture_output=True)
    for m in json.loads((ROOT / ".github/milestones.json").read_text()):
        if not DRY:
            r = subprocess.run(["gh", "api", f"repos/{REPO}/milestones", "-f", f"title={m['title']}",
                                "-f", f"due_on={m['due_on']}", "-f", f"description={m['description']}"],
                               capture_output=True, text=True)
            if r.returncode and "already_exists" not in r.stdout + r.stderr:
                sys.exit(r.stderr)
    existing = set()
    if not DRY:
        out = gh("issue", "list", "--repo", REPO, "--state", "all", "--limit", "200",
                 "--json", "title")
        existing = {i["title"] for i in json.loads(out)}
    for i in issues:
        title = f"[{i['n']}] {i['title']}"
        area = AREAS[i["n"]]
        body = (f"{i['text']}\n\n---\nSprint: {i['sprint']} · Estimate: {i['estimate']} · "
                f"Area: {area}\n")
        # The plan's middle field is a Type when it is one, else an Area (=> Feature).
        typ = i["type"] if i["type"] in TYPES else "Feature"
        labels = f"{i['priority']},type:{typ.lower()},area:{area}"
        if DRY:
            print(f"{title} | {i['milestone']} | {labels} | {i['sprint']} | est {i['estimate']}")
            continue
        if title in existing:
            print("skip", title)
            continue
        gh("issue", "create", "--repo", REPO, "--title", title, "--body", body,
           "--milestone", i["milestone"], "--label", labels)
        print("created", title)


if __name__ == "__main__":
    main()
