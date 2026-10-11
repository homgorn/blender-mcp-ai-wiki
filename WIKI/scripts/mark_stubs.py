#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mark stub/full status + translation markers in frontmatter.
- setups/workflows/cases: files < 2500 chars without FULL GUIDE/ADDENDUM/PROCESS section => status: stub, else status: full
- multilang/*: human list => translation: human, else translation: template
Idempotent: rewrites frontmatter block only.
"""
import re
import sys
import os
from pathlib import Path
S = Path(__file__).resolve().parent          # WIKI/scripts
WIKI = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
sys.path.insert(0, str(WIKI / "scripts"))
from wiki_const import HUMAN_MIRRORS as HUMAN
FULL_MARKERS = ["FULL GUIDE", "FULL ADDENDUM", "FULL PROCESS"]

def split_fm(text):
    m = re.match(r'^---\n(.*?)\n---\n?', text, re.DOTALL)
    if m:
        return m.group(1), text[m.end():]
    return None, text

def set_key(fm, key, val):
    lines = fm.split('\n')
    out, found = [], False
    for ln in lines:
        if re.match(rf'^{re.escape(key)}\s*:', ln):
            out.append(f"{key}: {val}")
            found = True
        else:
            out.append(ln)
    if not found:
        out.append(f"{key}: {val}")
    return '\n'.join(out)

changed = {"stub": 0, "full": 0, "human": 0, "template": 0}
for cat in ["setups", "workflows", "cases"]:
    # Recursive for robustness: the corpus nests elsewhere (references/v1/**),
    # and a flat glob meant a file added in a subfolder of one of these
    # categories would silently never get its status. `references` is
    # deliberately not in this list — reference docs carry no stub status.
    for f in sorted((WIKI/cat).rglob("*.md")):
        t = f.read_text(encoding="utf-8")
        fm, body = split_fm(t)
        is_full = any(mk in t for mk in FULL_MARKERS) or len(t) >= 2500
        want = "full" if is_full else "stub"
        if fm is None:
            title = f.stem
            fm = f"id: {title}\nlang: ru\ncategory: {cat}"
            body = t
        new_fm = set_key(fm, "status", want)
        f.write_text(f"---\n{new_fm}\n---\n{body.lstrip(chr(10))}", encoding="utf-8")
        changed[want] += 1

for f in sorted((WIKI/"multilang").rglob("*.md")):
    rel = f.relative_to(WIKI).as_posix()
    t = f.read_text(encoding="utf-8")
    fm, body = split_fm(t)
    if fm is None:
        continue
    if re.search(r'^translation\s*:', fm, re.MULTILINE):
        continue  # respect existing marker (human/legacy/template)
    want = "human" if rel in HUMAN else "template"
    new_fm = set_key(fm, "translation", want)
    if new_fm != fm:
        f.write_text(f"---\n{new_fm}\n---\n{body.lstrip(chr(10))}", encoding="utf-8")
    changed[want] += 1

print(f"OK status: stub={changed['stub']} full={changed['full']}; translation: human={changed['human']} template={changed['template']}")
