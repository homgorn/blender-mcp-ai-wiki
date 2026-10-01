#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Close the structural gaps reported by quality_report.py.

78 of 80 files were missing a `## 🔗 СВЯЗИ` section and 67 were missing a
`## 🎯 ЦЕЛЬ` section. Both are required by the templates in WIKI/templates/
and by `validate.py --strict`.

This fills them from data that already exists in the corpus — never invented:

* GOAL  — the article's own `**Type:**` / `**Time:**` metadata line plus the
           first sentence of the description, so it states what the file is.
* LINKS — real cross-references resolved through the database by shared tags
           and neighbouring category, same as the site does. Every link points
           at a file that exists; `validate.py` §9 proves it afterwards.

Idempotent: a file that already has the section is skipped.

Run:  python scripts/complete_sections.py [--dry] [--refresh]
      --refresh  rewrite existing СВЯЗИ sections even if they already contain
                 links (used after the cross-reference graph changes)
"""
import json
import re
import sys
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WIKI = Path(r"C:\BLENDER ai\WIKI")
DRY = "--dry" in sys.argv
REFRESH = "--refresh" in sys.argv
CATS = ["prompts", "setups", "workflows", "cases", "references"]
DB = WIKI / "db" / "wiki_database.json"

TYPE_RU = {
    "prompt": "Промпт", "setup": "Сетап", "workflow": "Воркфлоу",
    "case": "Кейс", "reference": "Референс", "guide": "Гайд",
}
CATEGORY_RU = {
    "prompts": "Промпты", "setups": "Сетапы", "workflows": "Воркфлоу",
    "cases": "Кейсы", "references": "Референсы",
}


def load_entries():
    db = json.loads(DB.read_text(encoding="utf-8"))
    out = []
    for e in db["entries"]:
        m = e["meta"]
        if m.get("is_translation"):
            continue
        out.append({
            "file": e["file_path"].replace("\\", "/"),
            "stem": Path(e["file_path"]).stem,
            "title": m.get("title", ""),
            "type": m.get("type", "reference"),
            "category": m.get("category", ""),
            "difficulty": m.get("difficulty", 0),
            "tags": m.get("tags", []),
        })
    return out


ENTRIES = load_entries()
BY_FILE = {e["file"]: e for e in ENTRIES}
TAGS_BY_CAT = {}
for e in ENTRIES:
    for t in e["tags"]:
        TAGS_BY_CAT.setdefault(t, []).append(e["file"])


def rel_link(from_file: str, to_file: str) -> str:
    """Relative markdown link from one corpus file to another."""
    a = Path(from_file).parent
    b = Path(to_file)
    import posixpath
    rel = posixpath.relpath(b.as_posix(), a.as_posix())
    return f"[{BY_FILE[to_file]['title']}]({rel})"


def related(from_file: str, limit: int = 6):
    """Real neighbours: shared tags, then same category, then same difficulty."""
    me = BY_FILE[from_file]
    score = {}
    for t in me["tags"]:
        for f in TAGS_BY_CAT.get(t, []):
            if f == from_file:
                continue
            score[f] = score.get(f, 0) + 2
    for f, e in BY_FILE.items():
        if f == from_file or f in score:
            continue
        if e["category"] == me["category"]:
            score[f] = score.get(f, 0) + 1
    ranked = sorted(score.items(), key=lambda kv: (-kv[1], BY_FILE[kv[0]]["title"]))
    return [f for f, _ in ranked[:limit]]


def has_section(text: str, marker: str) -> bool:
    return re.search(rf"^##\s+.*\b{marker}\b", text, re.MULTILINE | re.IGNORECASE) is not None


def rewrite_prose_links(text: str, f: str) -> tuple[str, bool]:
    """
    Replace a links section that is plain prose with real markdown links.

    The bulk-authored files say things like "Setup 01 blender-mcp, Setup 08
    Asset Pipeline, WF-01, INDEX" — a human-readable reference that is not
    clickable and that the crawler cannot follow. Since the file already claims
    to have a links section, the gap-filling pass would skip it, so the prose
    form is detected here and rewritten against the real database.

    Some files carry TWO link-ish headings (e.g. `## 🔗 WF-07, Setup 01/08,
    INDEX` alongside a later `## 🔗 СВЯЗИ`). Rendering both is a visible
    duplication, so any other prose link heading is dropped.
    """
    m = re.search(r"^(##\s+[^\n]*(?:СВЯЗИ|Связи|LINKS)[^\n]*)\n(.*?)(?=\n## |\Z)",
                  text, re.MULTILINE | re.DOTALL)
    if not m:
        return text, False
    body = m.group(2)
    already_links = bool(re.search(r"\]\(", body))
    looks_like_prose = bool(re.search(r"Setup\s*\d|Workflow|WF-\d|INDEX", body, re.IGNORECASE))
    if already_links and not REFRESH:
        return text, False
    if not already_links and not looks_like_prose and not REFRESH:
        return text, False

    head, rest = text[:m.start()], text[m.end():]
    # Drop any *other* heading that is only a prose link list.
    rest = re.sub(
        r"\n##\s+[^\n]*🔗[^\n]*\n(?:[^\n]*\n)*?(?=\n## |\Z)",
        "\n", rest, count=1,
    )
    return head + links_section(f) + "\n" + rest.lstrip("\n"), True


def goal_section(f: str, text: str) -> str:
    e = BY_FILE[f]
    kind = TYPE_RU.get(e["type"], "Материал")
    diff = ("⭐" * e["difficulty"]) if e["difficulty"] else "—"
    time_m = re.search(r"\*\*Time:\*\*\s*([^\n]+)", text)
    time_s = time_m.group(1).strip() if time_m else ""
    # First real prose sentence, if the file already has one.
    first = ""
    for para in re.split(r"\n\s*\n", text):
        p = para.strip()
        if not p or p.startswith(("#", "---", "|", "```", "<!--")):
            continue
        p = re.sub(r"\*\*[^*]+:\*\*[^\n]*", "", p).strip()
        if len(p) > 40:
            first = re.split(r"(?<=[.!?])\s", p)[0]
            break
    head = f"## 🎯 ЦЕЛЬ\n\n{kind} категории «{CATEGORY_RU.get(e['category'], e['category'])}»"
    if time_s:
        head += f", {time_s}"
    head += f", сложность {diff}."
    body = f"\n\n{first}\n" if first else "\n"
    return head + body


def links_section(f: str) -> str:
    e = BY_FILE[f]
    my = set(e["tags"])
    # Rank by shared tags first. Alphabetical order would list setup_01..05 for
    # every setup in the folder, which is not navigation, it is noise.
    same = sorted(
        (x for x in ENTRIES if x["category"] == e["category"] and x["file"] != f),
        key=lambda x: (-len(my & set(x["tags"])), x["title"]),
    )[:5]
    lines = ["## 🔗 СВЯЗИ", ""]
    if same:
        lines.append(f"- **Прочие в категории «{CATEGORY_RU.get(e['category'], e['category'])}»:** "
                     + ", ".join(rel_link(f, x["file"]) for x in same))
    # Cross-category neighbours only: repeating the same files under a second
    # heading adds length without adding navigation.
    rel = [x for x in related(f, 8) if x not in {y["file"] for y in same}][:4]
    if rel:
        lines.append("- **По темам:** "
                     + ", ".join(rel_link(f, x) for x in rel))
    if e["tags"]:
        lines.append("- **Теги:** " + ", ".join(f"#{t}" for t in e["tags"][:10]))
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    changed = 0
    goals = links = prose_links = 0
    for cat in CATS:
        d = WIKI / cat
        if not d.exists():
            continue
        # Recursive: 19 articles live in references/v1/** and a flat glob
    # skipped them entirely.
    for path in sorted(d.rglob("*.md")):
            rel = f"{cat}/{path.name}"
            if rel not in BY_FILE:
                continue
            text = path.read_text(encoding="utf-8")

            # A links section written as prose ("Setup 01, WF-01, INDEX") counts as
            # present for the gate but is not navigable. Rewrite it first.
            text, rewritten = rewrite_prose_links(text, rel)
            if rewritten and not DRY:
                path.write_text(text, encoding="utf-8")
                prose_links += 1
                print(f"[ok]  {rel}: prose links -> markdown links")

            need_goal = not has_section(text, r"(ЦЕЛЬ|GOAL)")
            need_links = not has_section(text, r"(СВЯЗИ|LINKS)")
            if not (need_goal or need_links):
                continue
            parts = []
            if need_goal:
                parts.append(goal_section(rel, text))
                goals += 1
            if need_links:
                parts.append(links_section(rel))
                links += 1
            addition = "\n" + "\n---\n\n".join(parts) + "\n"
            if DRY:
                print(f"[dry] {rel}: +{'GOAL ' if need_goal else ''}{'+LINKS' if need_links else ''}")
            else:
                path.write_text(text.rstrip() + "\n" + addition, encoding="utf-8")
                print(f"[ok]  {rel}: +{'GOAL ' if need_goal else ''}{'+LINKS' if need_links else ''}")
            changed += 1
    verb = "would fill" if DRY else "filled"
    print(f"OK {verb} {changed} files (+{goals} GOAL, +{links} LINKS), "
          f"{prose_links} prose link sections rewritten")
    return 0


if __name__ == "__main__":
    sys.exit(main())
