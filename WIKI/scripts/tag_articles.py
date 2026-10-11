#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Give every original article at least one real tag.

127 of 182 originals had none. That is not cosmetic: an empty tag list means
- `/api/tags` and the search index know nothing about the article,
- the site's "по темам" cross-references have no signal to rank on,
- the topic is invisible to anyone browsing by subject.

Tags are NOT invented here. They are taken from three sources that already
exist in the corpus:

1. The article's own title and headings (the tools and concepts it names).
2. Its category and type, which are facts about the file.
3. A controlled vocabulary file (`wiki_taxonomy.py`) mapping real keywords to
   real tags, so `#cycles` means the same thing everywhere.

Existing explicit tags are never overwritten.

Idempotent.

Run:  python scripts/tag_articles.py [--dry]
"""
import re
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

S = Path(__file__).resolve().parent          # WIKI/scripts
WIKI = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
DRY = "--dry" in sys.argv

# Directory -> baseline tag. Facts about the file, not guesses about content.
# Every article is guaranteed at least one tag this way, so a file can never be
# untaggable no matter how obscure its title is.
CATEGORY_TAG = {
    "prompts": "prompt", "setups": "setup", "workflows": "workflow",
    "cases": "case", "references": "reference",
    "mcp": "mcp", "mcp_advanced": "mcp", "integrations": "integration",
    "simulation": "simulation", "realtime": "realtime", "usd": "usd",
    "pipeline": "pipeline", "version_control": "version-control",
    "color": "color", "performance": "performance", "testing": "testing",
    "security": "security", "ml_ai": "ml", "accessibility": "accessibility",
    "collaboration": "collaboration", "visuals": "visuals",
    "blender_api": "api",
}

# keyword -> tag. Only terms that actually appear in this corpus.
VOCAB = {
    # tools and software
    "mcp": "mcp", "blender-mcp": "mcp", "genesiscore": "mcp",
    "ollama": "llm", "llama": "llm", "llm": "llm",
    "automatic1111": "stable-diffusion", "a1111": "stable-diffusion",
    "comfyui": "stable-diffusion", "comfy": "stable-diffusion",
    "sdxl": "stable-diffusion", "dream textures": "stable-diffusion",
    "stable diffusion": "stable-diffusion",
    "krita": "2d-ai", "krita ai": "2d-ai",
    "substance painter": "substance", "substance designer": "substance",
    "zbrush": "sculpt", "sculpt": "sculpt", "sculpting": "sculpt",
    "zgoz": "sculpt", "goz": "sculpt",
    "marvelous": "clothing", "clo3d": "clothing", "cloth": "clothing",
    "rizomuv": "topology", "rizom": "topology", "topogun": "topology",
    "metashape": "photogrammetry", "realitycapture": "photogrammetry",
    "polycam": "photogrammetry", "luma": "photogrammetry",
    "mixamo": "rigging", "autorignpro": "rigging", "accrig": "rigging",
    "rigify": "rigging", "mocap": "mocap", "rokoko": "mocap",
    "arkit": "mocap", "makehuman": "character", "daz": "character",
    "cc4": "character", "metahuman": "character",
    "readyplayer.me": "character", "readyplayerme": "character",
    "vroid": "character",
    "blenderkit": "assets", "fab": "assets", "quixel": "assets",
    "ambientcg": "assets", "poly haven": "assets", "polyhaven": "assets",
    "tripo": "ai-3d", "meshy": "ai-3d", "rodin": "ai-3d",
    "hunyuan": "ai-3d", "zero123": "ai-3d", "instantmesh": "ai-3d",
    "shap-e": "ai-3d",
    "gaussian splatting": "ai-3d", "ply": "ai-3d",
    # rendering
    "cycles": "cycles", "eevee": "eevee", "blender_eevee": "eevee",
    "render": "render", "рендер": "render",
    "hdri": "lighting", "lighting": "lighting", "освещение": "lighting",
    "light": "lighting", "portal": "lighting",
    "compositing": "compositing", "compositor": "compositing",
    "vse": "video", "ffmpeg": "video", "davinci": "video",
    "flamenco": "render-farm", "render farm": "render-farm",
    "aws": "cloud", "cloud": "cloud", "batch": "automation",
    "automation": "automation", "ci/cd": "ci", "ci": "ci",
    # pipeline and data
    "pipeline": "pipeline", "пайплайн": "pipeline",
    "usd": "usd", "openusd": "usd", "materialx": "usd",
    "openpype": "pipeline", "ayon": "pipeline",
    "shotgrid": "production", "ftrack": "production",
    "notion": "docs", "obsidian": "docs", "lfs": "version-control",
    "git": "version-control",
    # realtime / platform
    "touchdesigner": "realtime", "spout": "realtime", "ndi": "realtime",
    "osc": "realtime", "unreal": "unreal", "unity": "unity",
    "godot": "godot", "usdz": "web", "web viewer": "web",
    "glb": "web", "gltf": "web", "webxr": "web", "vr": "vr",
    "vision pro": "vr", "arkit": "vr",
    # modelling / shading
    "boolean": "modeling", "моделирование": "modeling",
    "uv": "uv", "unwrap": "uv", "sbsar": "shading", "shader": "shading",
    "principled": "shading", "ocio": "color", "aces": "color",
    "colormanagement": "color",
    "retopology": "retopology", "remesh": "retopology",
    "quad remesher": "retopology", "geometry nodes": "geometry-nodes",
    "gn": "geometry-nodes",
    # security / infra
    "safe mode": "security", "security": "security",
    "upscale": "upscale", "real-esrgan": "upscale",
    "profiling": "performance", "performance": "performance",
    "ocio_aces": "color",
    "accesibility": "accessibility", "accessibility": "accessibility",
    "localization": "localization", "dub": "localization",
    "sound": "audio", "crowd": "simulation", "cloth sim": "simulation",
    "destruction": "simulation", "fluid": "simulation",
    "motion graphics": "motion", "titles": "motion",
    "dataviz": "dataviz", "isometric": "stylized", "npr": "stylized",
    "anime": "stylized", "anime bust": "stylized", "voxel": "stylized",
    "kitbash": "stylized", "greeble": "stylized",
    "product viz": "product", "turntable": "product",
    "lookdev": "lookdev", "photorealistic": "render",
    "archviz": "archviz", "interior": "archviz",
    "game props": "game-assets", "dungeon": "game-assets",
    "vegetation": "vegetation", "forest": "vegetation",
    "sneaker": "product", "car studio": "product",
    "food": "product", "diorama": "stylized",
    "environment": "environment", "shot": "production",
    "loop": "animation", "animation": "animation", "stop motion": "animation",
    "fashion": "animation", "melee": "animation",
    "concept": "ai-3d", "final": "ai-3d",
    "meta": "ai-3d", "human": "ai-3d",
    # core modelling / texturing vocabulary
    "geometry": "modeling", "bmesh": "modeling", "mesh": "modeling",
    "vertex": "modeling", "edge loop": "modeling", "polycount": "performance",
    "texture": "texturing", "texturing": "texturing", "uv map": "uv",
    "material": "shading", "materials": "shading",
    "blender": "blender", "add-on": "addon", "addon": "addon",
    "operator": "api", "api": "api", "bpy": "api",
    "node": "shading", "compositor": "compositing",
    "uv": "uv", "ao": "lighting", "ssao": "lighting", "gi": "lighting",
    "shadow": "lighting", "specular": "shading", "roughness": "shading",
    "keyframe": "animation", "rig": "rigging", "armature": "rigging",
    "shape key": "animation", "shape keys": "animation",
    "export": "pipeline", "import": "pipeline", "interchange": "pipeline",
    "batch render": "render", "headless": "automation", "ffmpeg": "video",
}

FM_TAG = re.compile(r"^tags\s*:\s*\[(.*?)\]", re.MULTILINE)


def extract_existing(text: str) -> list[str]:
    m = FM_TAG.search(text)
    if not m:
        return []
    return [t.strip().strip("\"'").lower() for t in m.group(1).split(",") if t.strip()]


def add_frontmatter_tag(path: Path, tag: str) -> None:
    text = path.read_text(encoding="utf-8")
    m = FM_TAG.search(text)
    if m:
        current = [t.strip() for t in m.group(1).split(",") if t.strip()]
        if tag in current:
            return
        merged = sorted(set(current + [tag]))
        text = text[:m.start()] + "tags: [" + ", ".join(merged) + "]" + text[m.end():]
    else:
        # Insert after the last frontmatter key, keeping the block valid.
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not fm:
            return
        block = fm.group(1).rstrip()
        text = text[:fm.end(1)] + f"\ntags: [{tag}]" + text[fm.end(1):]
    path.write_text(text, encoding="utf-8")


def compile_vocab() -> list[tuple[re.Pattern, str, str]]:
    """
    (pattern, tag, keyword) triples, word-bounded.

    Plain substring matching produced nonsense: "ci" hit "instanCI NG" and
    "princiCLED", and "animation" hit "composItION". Short keywords need
    boundaries or the tag set becomes noise wearing metadata's clothes.
    """
    out = []
    for kw, tag in VOCAB.items():
        parts = [re.escape(p) for p in kw.split()]
        out.append((re.compile(r"(?<!\w)" + r"\s+".join(parts) + r"(?!\w)"), tag, kw))
    return out


RULES = compile_vocab()


def tags_in(text: str, min_kw_len: int = 0) -> set[str]:
    low = text.lower()
    return {tag for rx, tag, kw in RULES
            if len(kw) >= min_kw_len and rx.search(low)}


def set_frontmatter_tags(path: Path, tags: list[str], cat: str) -> bool:
    """
    Write the tag list in one edit. Returns whether the file was changed.

    Returning a bool is the point: the first version printed `[ok]` after an
    early `return` for files with no frontmatter block, so it reported work it
    had not done. A tagger that claims success while writing nothing is worse
    than no tagger, because the backlog then looks closed.
    """
    text = path.read_text(encoding="utf-8")
    line = "tags: [" + ", ".join(tags) + "]"
    m = FM_TAG.search(text)
    if m:
        new = text[:m.start()] + line + text[m.end():]
    else:
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if fm:
            new = text[:fm.end(1)] + "\n" + line + text[fm.end(1):]
        else:
            # No frontmatter at all: create a minimal, valid block. Without
            # this the file silently kept no tags while the log said otherwise.
            new = f"---\nid: {path.stem}\ncategory: {cat}\ntags: [{', '.join(tags)}]\n---\n" + text
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    # Read back: a write that did not land is not a success.
    return FM_TAG.search(path.read_text(encoding="utf-8")) is not None


def main() -> int:
    cats = ["prompts", "setups", "workflows", "cases", "references",
            "mcp", "mcp_advanced", "integrations", "simulation", "realtime",
            "usd", "pipeline", "version_control", "color", "performance",
            "testing", "security", "ml_ai", "accessibility", "collaboration",
            "visuals", "blender_api"]
    touched = 0
    no_tag = 0
    failed = 0
    for cat in cats:
        d = WIKI / cat
        if not d.exists():
            continue
        # Recursive: references/v1/** was invisible to a flat glob.
        for f in sorted(d.rglob("*.md")):
            text = f.read_text(encoding="utf-8")
            if FM_TAG.search(text):
                continue                       # already declares tags
            # Match against the TITLE only. Matching the body matched the
            # boilerplate — every prompt has an "MCP" heading and a "СВЯЗИ"
            # section, so every file came out tagged mcp/ci/ai-3d.
            m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
            title = m.group(1) if m else ""
            found = tags_in(f"{f.stem} {title}")
            if not found:
                # Second chance: the opening prose with code stripped, and only
                # keywords long enough that a coincidental hit is unlikely.
                prose = re.sub(r"```[\s\S]*?```", " ", text)
                found = tags_in(prose[:900], min_kw_len=5)
            base = CATEGORY_TAG.get(cat)
            if base:
                found.add(base)
            if not found:
                no_tag += 1
                print(f"[skip] {cat}/{f.name}: no vocabulary match")
                continue
            tag_list = sorted(found)[:8]
            if DRY:
                print(f"[dry]  {cat}/{f.name}: {tag_list}")
            else:
                if set_frontmatter_tags(f, tag_list, cat):
                    print(f"[ok]   {cat}/{f.name}: {tag_list}")
                else:
                    failed += 1
                    print(f"[FAIL] {cat}/{f.name}: could not write tags")
                    continue
            touched += 1
    if failed:
        print(f"FAIL: {failed} file(s) could not be tagged")
        return 1
    verb = "would tag" if DRY else "tagged"
    print(f"OK {verb} {touched} files, {no_tag} had no vocabulary match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
