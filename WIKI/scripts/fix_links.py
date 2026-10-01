#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix known broken links + missing frontmatter. Idempotent. Excludes generated dirs."""
from pathlib import Path
WIKI = Path(r"C:\BLENDER ai\WIKI")
SKIP = {"db", "site", "export_obsidian", "export_notion"}

def files():
    for f in WIKI.rglob("*.md"):
        rel = f.relative_to(WIKI).parts
        if rel[0] in SKIP:
            continue
        yield f

# (scope_substr_or_None, old, new) — scope matches file's relative posix path
RULES = [
    ("cases/case_02_game_props.md", "./01_geometry_basics.md", "../prompts/01_geometry_basics.md"),
    ("cases/case_02_game_props.md", "./02_boolean_operations.md", "../prompts/02_boolean_operations.md"),
    ("cases/case_02_game_props.md", "./03_modifiers_stack.md", "../prompts/03_modifiers_stack.md"),
    ("cases/case_02_game_props.md", "./05_uv_unwrapping.md", "../prompts/05_uv_unwrapping.md"),
    ("cases/case_02_game_props.md", "../materials/09_principled_bsdf.md", "../prompts/09_principled_bsdf.md"),
    ("cases/case_02_game_props.md", "[P13](../materials/13_material_library.md)", "[P10](../prompts/10_node_groups.md)"),
    (None, "../mcp/mcp_tools_reference.md", "../references/v1/mcp/server-api.md"),
    (None, "- **Setup 04:** [Character Rig](../setups/setup_04_character_rig.md)",
     "- **Setup 30:** [Rigify Advanced](../setups/setup_30_rigify_advanced.md)"),
    (None, "./29_procedural_building.md", "./25_procedural_building.md"),
    (None, "../materials/10_node_groups.md", "./10_node_groups.md"),
    ("references/v1/", "../guides/workflows.md", "../workflows/scene-building.md"),
]

FM_LEGACY = {
    # path suffix -> (id, lang, category, translation)
    "multilang/en/prompts/01_primitive_creation.md": ("01_primitive_creation", "en", "prompts", "legacy"),
    "multilang/ru/prompts/01_primitive_creation.md": ("01_primitive_creation", "ru", "prompts", "legacy"),
    "multilang/en/prompts/12_texture_painting.md": ("12_texture_painting", "en", "prompts", "legacy"),
    "multilang/en/prompts/13_lighting_hdri.md": ("13_lighting_hdri", "en", "prompts", "legacy"),
    "multilang/en/prompts/14_camera_composition.md": ("14_camera_composition", "en", "prompts", "legacy"),
    "multilang/en/prompts/15_compositing.md": ("15_compositing", "en", "prompts", "legacy"),
}

fixed_links = 0
fixed_fm = 0
# NOTE: rules with scope "cases/case_02_game_props.md" also match mirrors
# (multilang/*/cases/case_02_game_props.md) since we match on suffix.
for f in files():
    rel = f.relative_to(WIKI).as_posix()
    try:
        t = f.read_text(encoding="utf-8")
    except Exception as e:
        print("READ-ERR", rel, e)
        continue
    orig = t
    for scope, old, new in RULES:
        if scope and scope not in rel:
            continue
        if old in t:
            t = t.replace(old, new)
    if t != orig:
        f.write_text(t, encoding="utf-8")
        fixed_links += 1

for suffix, (fid, lang, cat, tr) in FM_LEGACY.items():
    f = WIKI / suffix
    if not f.exists():
        print("MISSING", suffix)
        continue
    t = f.read_text(encoding="utf-8")
    if t.startswith("---"):
        continue
    fm = f"---\nid: {fid}\nlang: {lang}\ncategory: {cat}\ntype: prompt\ndifficulty: 2\ntranslation: {tr}\n---\n\n"
    f.write_text(fm + t, encoding="utf-8")
    fixed_fm += 1

print(f"OK links fixed in {fixed_links} files; frontmatter added to {fixed_fm} files")
