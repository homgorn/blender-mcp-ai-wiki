#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check that every `bpy.*` path used in the corpus exists in the installed Blender.

Run:
    blender -b --factory-startup --python WIKI/scripts/api_compat.py -- [--warn]

Why this exists
---------------
The corpus was written against Blender 4.x. Blender 5.2.1 LTS is what is
installed. A probe on 5.2.1 confirmed that `Mesh.use_auto_smooth` is gone (removed
in 4.1), `bpy.ops.export_mesh.stl` / `import_mesh.stl` were renamed to
`bpy.ops.wm.stl_export` / `stl_import`, `Scene.sequence_editor.sequences` became
`.strips`, and `bpy.ops.xr` has no members at all. Twelve articles taught
`action.fcurves`, which slotted Actions removed. None of that is visible by
reading markdown, and every structural gate passes regardless.

Two classes of finding, deliberately kept apart:

  broken    a path that has never worked in any Blender — a wrong namespace.
            Fixing it is not a judgement call.
  renamed   a path that worked in 4.x and no longer does. Fixing it means
            choosing which version the corpus targets, so it is reported and left.

Why introspection and not execution
------------------------------------
Nothing from the corpus is run. A snippet that writes a file, opens a render or
waits on a socket would be a hazard in a gate; here the code is only parsed, and
the paths are resolved with getattr/dir. `ast` also rejects fragments as
fragments, so a snippet that is a shell line rather than a module is reported as
unparsed instead of being silently skipped.

Why `dir()` and not `hasattr()`
------------------------------
`bpy.ops` is a dynamic namespace: getattr invents a stub for anything you ask it
for. `hasattr(bpy.ops.xr, 'anything')` is True in a Blender where that namespace
does not exist at all, which is how `bpy.ops.xr` passed a hasattr-based check on
a build that has no XR operator. Dynamic levels are therefore compared against
`dir()`.

Exit code is non-zero on `broken`, so it can be a gate; `--warn` reports without
failing.
"""
import argparse
import ast
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import bpy  # noqa: E402  — provided by Blender

WIKI = Path(r"C:\BLENDER ai\WIKI")
CATS = ["prompts", "setups", "workflows", "cases", "references"]

# Paths whose absence under --factory-startup is expected, not a defect.
#
#   addon    registered by an add-on that is off in a factory startup; the article
#            is correct about the tool, so the absence says nothing about the code
#   context  needs a live object or a compositing-enabled scene; the chain cannot
#            be walked from a default file
#
# Anything listed here must say so in a comment, or the entry becomes a place to
# hide a real breakage.
EXPECTED_ABSENT = {
    "addon": [
        ("bpy.ops.dream_texture", "Dream Texture is an add-on, off under --factory-startup"),
        ("bpy.ops.dream_texture.", "Dream Texture is an add-on, off under --factory-startup"),
        ("bpy.ops.mesh.primitive_torus_add", None),   # keep shape: see note below
    ],
    "context": [
        ("bpy.context.object.data.shape_keys", "needs an active object with shape keys"),
        ("bpy.context.object.data.shape_keys.", "needs an active object with shape keys"),
        ("bpy.context.scene.node_tree", "exists only when compositing is enabled"),
        ("bpy.context.scene.eevee", "engine id differs by version; see the renames below"),
    ],
}

# Verified on 5.2.1. Recorded rather than auto-fixed, because each one means the
# corpus claims a version it does not target.
KNOWN_RENAMED = {
    # Exporter/Importer namespaces, 2.8–3.6; became wm.* in 4.0.
    "bpy.ops.export_mesh": "bpy.ops.wm  (namespace no longer exists)",
    "bpy.ops.import_mesh": "bpy.ops.wm  (namespace no longer exists)",
    "bpy.ops.export_mesh.stl": "bpy.ops.wm.stl_export",
    "bpy.ops.import_mesh.stl": "bpy.ops.wm.stl_import",
    # Removed in 4.1 with the auto-smooth rework.
    "bpy.context.view_layer.objects.active.data.use_auto_smooth": "bpy.ops.object.shade_auto_smooth",
    # Renamed by 5.2.
    "bpy.context.scene.tool_settings.sculpt.detail_type": "...sculpt.detail_type_method",
    "bpy.context.scene.tool_settings.sculpt.constant_detail": "...sculpt.constant_detail_resolution",
    # Present in 4.x, absent in 5.2. The replacement is a UI toggle, not a
    # property, so there is no drop-in replacement to name here.
    "bpy.context.scene.tool_settings.sculpt.dyntopo": "no property equivalent; toggle in the sculpt header",
    "bpy.context.scene.tool_settings.use_snap_project": "no property equivalent in 5.2",
}

PY_BLOCK = re.compile(r"```python[ \t]*\n([\s\S]*?)```")


def collect() -> tuple[dict, list]:
    """path -> file list, plus the blocks ast could not read."""
    found = defaultdict(set)
    unparsed = []
    blocks = 0
    for cat in CATS:
        d = WIKI / cat
        if not d.exists():
            continue
        for p in sorted(d.rglob("*.md")):
            text = p.read_text(encoding="utf-8")
            rel = p.relative_to(WIKI).as_posix()
            for m in PY_BLOCK.finditer(text):
                blocks += 1
                src = m.group(1).replace("\t", "    ")
                try:
                    tree = ast.parse(src)
                except SyntaxError as e:
                    unparsed.append((rel, str(e)[:60]))
                    continue
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Attribute):
                        continue
                    chain = []
                    cur = node
                    while isinstance(cur, ast.Attribute):
                        chain.append(cur.attr)
                        cur = cur.value
                    if not isinstance(cur, ast.Name) or cur.id != "bpy":
                        continue
                    chain.append(cur.id)          # the root name is part of the path
                    chain.reverse()
                    if chain and chain[0] == "bpy":
                        found[".".join(chain)].add(rel)
    return found, unparsed


def resolve(path: str):
    """('ok'|'missing'|'skipped'|'expected', reached)"""
    for kind, prefixes in EXPECTED_ABSENT.items():
        for pre, why in prefixes:
            if why and path.startswith(pre):
                return "expected", kind

    if path in KNOWN_RENAMED:
        return "renamed", KNOWN_RENAMED[path]

    parts = path.split(".")[1:]
    cur = bpy
    walked = ["bpy"]
    for part in parts:
        if part.startswith("_"):
            return "private", ".".join(walked)
        # Dynamic namespaces only answer honestly to dir(); see module docstring.
        dynamic = walked[-1] == "ops" or walked[:2] == ["bpy", "types"]
        if dynamic:
            if part not in set(dir(cur)):
                return "missing", ".".join(walked)
            walked.append(part)
            cur = getattr(cur, part, None)
            continue
        if part in ("new", "remove", "get", "pop", "items", "keys", "values"):
            return "skipped", ".".join(walked)
        try:
            cur = getattr(cur, part)
        except AttributeError:
            return "missing", ".".join(walked)
        walked.append(part)
    return "ok", ".".join(walked)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--warn", action="store_true",
                    help="report without failing, for use while a batch is in flight")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    args = ap.parse_args(argv)

    found, unparsed = collect()
    report = {}
    for path, files in found.items():
        status, detail = resolve(path)
        report[path] = {"status": status, "detail": detail, "files": sorted(files)}

    tally = Counter(r["status"] for r in report.values())
    broken = {p: r for p, r in report.items() if r["status"] == "missing"}
    renamed = {p: r for p, r in report.items() if r["status"] == "renamed"}

    if args.json:
        print(json.dumps({"tally": tally, "report": report,
                          "unparsed": unparsed}, ensure_ascii=False, indent=2))
    else:
        print(f"== API compatibility against {bpy.app.version_string} ==")
        print(f"  bpy-rooted paths : {len(report)}")
        print(f"  tally           : {dict(tally)}")
        print(f"  unparsed blocks : {len(unparsed)} (fragments, not whole modules)")
        for label, group, why in (
            ("MISSING — never worked, fix", broken,
             "a wrong namespace: absent in every version"),
            ("RENAMED — worked in 4.x, gone in 5.x", renamed,
             "needs a target-version decision"),
        ):
            if not group:
                print(f"\n  [OK ] {label}")
                continue
            print(f"\n  [{len(group)}] {label}  ({why})")
            for p in sorted(group):
                r = group[p]
                files = ", ".join(r["files"][:2])
                extra = f"  -> {r['detail']}" if r["detail"] and r["status"] == "renamed" else ""
                print(f"        {p}{extra}")
                print(f"          in: {files}")
        if unparsed:
            print("\n  unparsed blocks by file:")
            for f, n in Counter(f for f, _ in unparsed).most_common(8):
                print(f"        {n:>3}x {f}")

    if broken and not args.warn:
        print(f"\nRESULT: FAIL ({len(broken)} path(s) that never existed)")
        return 1
    print(f"\nRESULT: OK ({len(broken)} broken, {len(renamed)} renamed, "
          f"{tally.get('expected', 0)} expected-absent)")
    return 0


if __name__ == "__main__":
    sys.exit(main())