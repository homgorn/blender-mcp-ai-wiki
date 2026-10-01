#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turns the template-conformance findings into a tracked, actionable artifact:
WIKI/quality_report.md. Non-fatal by design — this is a backlog, not a gate.

    python scripts/quality_report.py
"""
import sys
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

WIKI = Path(r"C:\BLENDER ai\WIKI")

# Accepted markers per required section. Two things matter here and both were
# got wrong before:
#   1. Case-insensitivity. The bulk-authored files use `## 🎯 Цель / Goal` and
#      `## 🔗 Связи / Links`, so a case-sensitive compare against ЦЕЛЬ/СВЯЗИ
#      reported 67 goals and 47 links as missing while they were present.
#      A gate that cries wolf gets ignored.
#   2. MULTILANG is NOT a substitute. It is a language-navigation table, not the
#      cross-reference section; counting it hid 49 files that had no links.
# Keep this table identical to validate.py and complete_sections.py.
REQUIRED = {
    "prompts":   {"goal": ["ЦЕЛЬ", "GOAL"], "prompt": ["ПРОМПТ", "PROMPT"],
                  "mcp": ["MCP", "КОМАНДЫ", "COMMANDS"], "links": ["СВЯЗИ", "LINKS"]},
    "setups":    {"goal": ["ЦЕЛЬ", "GOAL", "ЗАДАЧА"], "links": ["СВЯЗИ", "LINKS"]},
    "workflows": {"goal": ["ЦЕЛЬ", "GOAL"], "links": ["СВЯЗИ", "LINKS"]},
    "cases":     {"goal": ["ЦЕЛЬ", "GOAL", "ЗАДАЧА", "BRIEF"], "links": ["СВЯЗИ", "LINKS"]},
}


def missing_sections(text, groups):
    upper = text.upper()
    return [name for name, marks in groups.items()
            if not any(mk.upper() in upper for mk in marks)]
RU_EN = {"goal": "ЦЕЛЬ/GOAL", "prompt": "ПРОМПТ/PROMPT", "mcp": "MCP", "links": "СВЯЗИ/LINKS"}


def scan():
    rows = []
    for cat, groups in REQUIRED.items():
        # Recursive: references/v1/** was invisible to a flat glob.
        for f in sorted((WIKI / cat).rglob("*.md")):
            t = f.read_text(encoding="utf-8")
            miss = missing_sections(t, groups)
            if miss:
                status = "stub" if "status: stub" in t else ("full" if "status: full" in t else "—")
                rows.append((cat, f.name, status, miss))
    return rows


def main():
    rows = scan()
    out = [f"# QUALITY REPORT", "",
           "Автогенерация: `python scripts/quality_report.py`. Не гейт — это бэклог.", "",
           "Проверяется **наличие секций**, а не язык заголовка: в корпусе два диалекта",
           "(`ЦЕЛЬ/ПРОМПТ/СВЯЗИ` и `GOAL/PROMPT/LINKS`). Эталон структуры: `WIKI/templates/`.",
           "", f"**Файлов с пробелами: {len(rows)}**", ""]
    by_cat = {}
    for cat, name, status, miss in rows:
        by_cat.setdefault(cat, []).append((name, status, miss))
    out += ["| Категория | Файлов |", "|-----------|--------|"]
    for cat in REQUIRED:
        out.append(f"| {cat} | {len(by_cat.get(cat, []))} |")
    out += ["", "## По файлам", "", "| Файл | Статус | Не хватает |", "|------|--------|-----------|"]
    for cat in REQUIRED:
        for name, status, miss in sorted(by_cat.get(cat, [])):
            out.append(f"| `{cat}/{name}` | {status} | {', '.join(miss)} |")
    out += ["", "## Как закрыть", "",
            "1. Открыть файл, добавить недостающие секции по образцу `WIKI/templates/`.",
            "2. Прогнать `python scripts/run_all.py`.",
            "3. Проверить: `python scripts/quality_report.py` — число должно уменьшиться.",
            "",
            "Когда счётчик станет 0, включайте гейт: `validate.py --strict`.", ""]
    p = WIKI / "quality_report.md"
    p.write_text("\n".join(out), encoding="utf-8")
    print(f"OK quality_report: {len(rows)} files with gaps -> {p.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
