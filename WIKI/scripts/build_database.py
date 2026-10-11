#!/usr/bin/env python3
"""
BLENDER AI WIKI - DATABASE BUILDER
Scans all markdown files and creates a searchable JSON database
with full-text search capabilities for future site/service integration.
"""

import os
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    import yaml
except ImportError:          # ADR 0004: the pipeline must run on a bare Python
    yaml = None

S = Path(__file__).resolve().parent          # WIKI/scripts
WIKI_ROOT = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
DB_PATH = WIKI_ROOT / "db" / "wiki_database.json"
INDEX_PATH = WIKI_ROOT / "db" / "search_index.json"
EXPORT_PATH = WIKI_ROOT / "db" / "wiki_export.json"

# Категории для классификации
CATEGORIES = {
    "prompts": {"path": "prompts", "prefix": "P", "type": "prompt"},
    "cases": {"path": "cases", "prefix": "CASE", "type": "case"},
    "setups": {"path": "setups", "prefix": "SETUP", "type": "setup"},
    "workflows": {"path": "workflows", "prefix": "WF", "type": "workflow"},
    "mcp": {"path": "mcp", "prefix": "MCP", "type": "reference"},
    "mcp_advanced": {"path": "mcp_advanced", "prefix": "MCP_ADV", "type": "reference"},
    "api": {"path": "api", "prefix": "API", "type": "reference"},
    "guides": {"path": "guides", "prefix": "GUIDE", "type": "guide"},
    "references": {"path": "references", "prefix": "REF", "type": "reference"},
    "integrations": {"path": "integrations", "prefix": "INT", "type": "reference"},
    "simulation": {"path": "simulation", "prefix": "SIM", "type": "reference"},
    "realtime": {"path": "realtime", "prefix": "RT", "type": "reference"},
    "usd": {"path": "usd", "prefix": "USD", "type": "reference"},
    "pipeline": {"path": "pipeline", "prefix": "PIPE", "type": "reference"},
    "version_control": {"path": "version_control", "prefix": "VC", "type": "reference"},
    "color": {"path": "color", "prefix": "COLOR", "type": "reference"},
    "performance": {"path": "performance", "prefix": "PERF", "type": "reference"},
    "testing": {"path": "testing", "prefix": "TEST", "type": "reference"},
    "security": {"path": "security", "prefix": "SEC", "type": "reference"},
    "ml_ai": {"path": "ml_ai", "prefix": "ML", "type": "reference"},
    "accessibility": {"path": "accessibility", "prefix": "ACC", "type": "reference"},
    "collaboration": {"path": "collaboration", "prefix": "COLLAB", "type": "reference"},
    "visuals": {"path": "visuals", "prefix": "VIS", "type": "reference"},
}

# Теги для автоматического извлечения
# `#([\w-]+)`, not `#(\w+)`: \w excludes the hyphen, so `#true-displacement`
# yielded both "true-displacement" and the fragment "true". That shipped 44
# junk tags across 456 (entry, tag) pairs — and tag overlap drives related()
# scoring, the tag facet and the search index, so junk is not cosmetic.
TAG_PATTERNS = [
    r'#([\w-]+)',  # #tag or #multi-word-tag
    r'Теги:\s*([^\n]+)',  # Теги: tag1, tag2
    r'Tags:\s*([^\n]+)',  # Tags: tag1, tag2
    r'теги:\s*([^\n]+)',
    r'tags:\s*([^\n]+)',
]

DIFFICULTY_PATTERNS = [
    r'Сложность:\s*⭐+',
    r'Difficulty:\s*⭐+',
    r'сложность:\s*⭐+',
    r'difficulty:\s*⭐+',
]

LANG_PATTERNS = {
    'ru': [r'[а-яё]', r'Сложность', r'Теги', r'ЦЕЛЬ', r'ПРОМПТ'],
    'en': [r'Difficulty', r'Tags', r'GOAL', r'PROMPT'],
}

_CYRILLIC = re.compile(r'[Ѐ-ӿ]')
_LATIN = re.compile(r'[A-Za-z]')
_CJK = re.compile(r'[぀-ヿ㐀-䶿一-鿿豈-﫿]')

def detect_language(text: str) -> str:
    """
    Script-ratio detection.

    The previous version counted marker words (ЦЕЛЬ/GOAL/Теги/Tags). That is
    unreliable: a Russian article whose headings are the English "GOAL"/"LINKS"
    dialect scored as English, and those files were then published under /en/
    with Russian text. Counting characters per script is stable for this corpus
    and cannot be flipped by a single heading.
    """
    sample = text[:6000]
    if _CJK.search(sample):
        return 'zh'
    cyr = len(_CYRILLIC.findall(sample))
    lat = len(_LATIN.findall(sample))
    if cyr == 0 and lat == 0:
        return 'en'
    return 'ru' if cyr * 2 >= lat else 'en'

def _coerce(v: str):
    """Scalar coercion for the fallback frontmatter parser."""
    v = v.strip()
    if not v:
        return ""
    if v[0] in "\"'" and v[-1] == v[0] and len(v) > 1:
        return v[1:-1]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_coerce(x) for x in inner.split(",")] if inner else []
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d*\.\d+", v):
        return float(v)
    return v


def parse_frontmatter_min(block: str) -> Dict:
    """
    Minimal YAML subset parser for frontmatter: `key: value`, inline lists
    `[a, b]` and block lists (`- item`). Covers every field the wiki actually
    uses. Used only when PyYAML is unavailable — keeps the pipeline stdlib-only.
    """
    out: Dict[str, Any] = {}
    key = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.lstrip().startswith("- ") and key is not None:
            out.setdefault(key, [])
            if not isinstance(out[key], list):
                out[key] = []
            out[key].append(_coerce(raw.lstrip()[2:]))
            continue
        m = re.match(r"^([A-Za-z0-9_\-]+)\s*:\s*(.*)$", raw)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        out[key] = _coerce(val) if val.strip() else []
    return out


FM_ERRORS: List[str] = []


def extract_frontmatter(content: str, filepath: str = "?") -> Dict:
    """Извлечь YAML frontmatter если есть.

    A YAML error must never be swallowed: losing frontmatter means losing
    id/lang/translation for a whole file, silently. PyYAML is tried first, the
    minimal parser second, and a total failure is recorded for the report.
    """
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    block = match.group(1)
    if yaml is not None:
        try:
            data = yaml.safe_load(block)
            return data if isinstance(data, dict) else {}
        except Exception as ex:
            FM_ERRORS.append(f"{filepath}: yaml ({str(ex).splitlines()[0][:60]})")
    try:
        return parse_frontmatter_min(block)
    except Exception as ex:
        FM_ERRORS.append(f"{filepath}: fallback ({ex})")
        return {}

def extract_metadata(content: str, filepath: Path) -> Dict:
    """Извлечь метаданные из markdown"""
    meta = {
        "id": None,
        "title": "",
        "category": "",
        "type": "",
        "difficulty": 0,
        "tags": [],
        "language": "en",
        "description": "",
        "mcp_tools": [],
        "links": [],
        "code_blocks": 0,
        "word_count": 0,
        "updated": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
    }
    
    # Из frontmatter
    fm = extract_frontmatter(content, str(filepath))
    if fm:
        meta.update(fm)
    
    # created: prefer frontmatter value, else fall back to file mtime (reproducible)
    if "created" not in meta:
        meta["created"] = datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
    
    # ID из имени файла (для multilang — уникальный суффикс языка)
    stem = filepath.stem
    try:
        _rp0 = filepath.relative_to(WIKI_ROOT).parts
        if len(_rp0) > 2 and _rp0[0] == "multilang":
            meta["orig_id"] = stem
            meta["id"] = f"{stem}__{_rp0[1]}"
        else:
            meta["id"] = stem
    except Exception:
        meta["id"] = stem
    
    # Категория/язык из пути (multilang/{lang}/{cat}/...)
    rel_path = filepath.relative_to(WIKI_ROOT)
    parts = rel_path.parts
    is_ml = len(parts) > 2 and parts[0] == "multilang"
    if is_ml:
        ml_lang, ml_cat = parts[1], parts[2]
        meta["language"] = ml_lang
        if ml_cat in CATEGORIES:
            meta["category"] = ml_cat
            meta["type"] = CATEGORIES[ml_cat]["type"]
    elif len(parts) > 1:
        cat = parts[0]
        if cat in CATEGORIES:
            meta["category"] = cat
            meta["type"] = CATEGORIES[cat]["type"]
    
    # Заголовок (первый заголовок #)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        meta["title"] = title_match.group(1).strip()
    else:
        meta["title"] = stem.replace('_', ' ').title()
    
    # Сложность
    diff_match = re.search(r'⭐+', content)
    if diff_match:
        meta["difficulty"] = len(diff_match.group(0))
    
    # Теги (с фильтрацией мусора: hex-цвета, bold-маркеры, цифры)
    #
    # Fenced code is removed first. Tags live in prose and in frontmatter, never
    # in a snippet, and scanning code produced tags straight out of Python:
    # `tags: List[str] = None` yielded "list" and "none". Those tags then reached
    # the search index, the tag facet and related-article scoring.
    scannable = re.sub(r"```[\s\S]*?```", "\n", content)
    scannable = re.sub(r"~~~[\s\S]*?~~~", "\n", scannable)
    tags = set()
    for pattern in TAG_PATTERNS:
        matches = re.findall(pattern, scannable, re.IGNORECASE)
        for match in matches:
            if isinstance(match, str):
                for raw in re.split(r'[,\s]+', match.rstrip('.,;:)')):
                    # Strip list punctuation as well as emphasis: frontmatter
                    # written as `tags: [a, b]` was yielding tags like
                    # "setup]" and "prompt]" because only *_`# were removed.
                    tag = raw.strip().lower().strip('*_`[]').lstrip('#')
                    if not tag or len(tag) < 2 or len(tag) > 30:
                        continue
                    # Brackets anywhere, not just at the ends: a type hint like
                    # `list[str]` leaves "list[str" after the end-strip and
                    # becomes a search tag nobody would ever query.
                    if '[' in tag or ']' in tag:
                        continue
                    # Colour-space placeholders. `Base Color: [R, G, B] или hex
                    # #RRGGBB` is how shader inputs are documented throughout
                    # this corpus, and the 3/6/8-digit hex filter does not catch
                    # it because R, G and B are not hex digits. Named explicitly
                    # rather than filtered by shape, because a generic rule would
                    # also drop real tags.
                    if tag in ('rgb', 'rgba', 'rrggbb', 'rrggbbaa'):
                        continue
                    if not re.match(r'[^\W\d_]', tag, re.UNICODE):
                        continue  # должен начинаться с буквы
                    if re.fullmatch(r'[0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8}', tag):
                        continue  # hex-цвета (#8b7355 и т.п.)
                    if re.fullmatch(r'\d+', tag):
                        continue
                    tags.add(tag)
    meta["tags"] = sorted(list(tags))
    
    # Language precedence:
    #   1. multilang/{lang}/ path   (structural, always correct)
    #   2. `lang:` in frontmatter  (declared by the author / mark_stubs.py)
    #   3. script-ratio detection  (last resort)
    # The previous code always overwrote (2) with (3). That published Russian
    # articles under /en/ and made Russian mirrors look like duplicates of
    # English originals. An explicit declaration must beat a heuristic.
    _is_ml_path = False
    try:
        _rp = filepath.relative_to(WIKI_ROOT).parts
        _is_ml_path = len(_rp) > 2 and _rp[0] == "multilang"
    except Exception:
        pass
    _declared = str((fm or {}).get("lang") or "").strip().lower()
    if not _is_ml_path:
        if _declared in ("ru", "en", "es", "de", "zh"):
            meta["language"] = _declared
        else:
            meta["language"] = detect_language(content[:6000])
    
    # MCP инструменты
    mcp_tools = re.findall(r'`(?:create_object|set_material|execute_blender_code|download_polyhaven_asset|search_polyhaven_assets|get_scene_info|get_object_info|get_viewport_screenshot|search_polypizza_models|download_polypizza_model|search_sketchfab_models|download_sketchfab_model|create_rodin_job|poll_rodin_job_status|import_generated_asset|create_hunyuan_job|poll_hunyuan_job_status|import_generated_asset_hunyuan|get_polyhaven_categories|get_polyhaven_status|get_hyper3d_status|get_sketchfab_status|get_polypizza_status|get_hunyuan3d_status|get_addon_info|get_telemetry_consent|set_telemetry_consent|drain_human_activity)`', content)
    meta["mcp_tools"] = sorted(list(set(mcp_tools)))
    
    # Ссылки на другие файлы
    links = re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', content)
    meta["links"] = [{"text": t, "url": u} for t, u in links]
    
    # Код блоки
    meta["code_blocks"] = len(re.findall(r'```[\s\S]*?```', content))
    
    # Word count
    meta["word_count"] = len(content.split())
    
    # Description (первый абзац после заголовка)
    desc_match = re.search(r'^#\s+.+\n\n(.+?)(?:\n\n|\n#)', content, re.DOTALL)
    if desc_match:
        meta["description"] = desc_match.group(1).strip()[:500]
    
    return meta

def extract_content_sections(content: str) -> List[Dict]:
    """Разбить контент на секции для поиска"""
    sections = []
    
    # Разбить по заголовкам ##
    pattern = r'^(##\s+.+?)$\n(.*?)(?=\n## |\n# |\Z)'
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
    
    for i, (heading, body) in enumerate(matches):
        section = {
            "index": i,
            "heading": heading.strip('# ').strip(),
            "content": body.strip()[:2000],
            "word_count": len(body.split()),
            "has_code": '```' in body,
        }
        sections.append(section)
    
    return sections

def build_database():
    """Построить полную базу данных"""
    print("[SCAN] Scanning WIKI directory...")
    
    all_entries = []
    file_count = 0
    
    for category, info in CATEGORIES.items():
        cat_path = WIKI_ROOT / info["path"]
        if not cat_path.exists():
            continue
            
        # Deterministic order: sort files by relative path
        md_files = sorted(
            (f for f in cat_path.rglob("*.md") if not f.name.startswith('.')),
            key=lambda f: f.relative_to(WIKI_ROOT).as_posix()
        )
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                meta = extract_metadata(content, md_file)
                sections = extract_content_sections(content)
                
                entry = {
                    "meta": meta,
                    "sections": sections,
                    "full_content": content,
                    "file_path": str(md_file.relative_to(WIKI_ROOT)),
                    "content_hash": hashlib.md5(content.encode()).hexdigest()[:16],
                }
                
                all_entries.append(entry)
                file_count += 1
                
            except Exception as e:
                print(f"  ⚠️ Error processing {md_file}: {e}")
    
    # Добавить multilang файлы (все 5 языков) — deterministic order
    for lang in ['en', 'ru', 'es', 'de', 'zh']:
        lang_path = WIKI_ROOT / "multilang" / lang
        if lang_path.exists():
            md_files = sorted(
                lang_path.rglob("*.md"),
                key=lambda f: f.relative_to(WIKI_ROOT).as_posix()
            )
            for md_file in md_files:
                try:
                    content = md_file.read_text(encoding='utf-8')
                    meta = extract_metadata(content, md_file)
                    meta["language"] = lang
                    meta["is_translation"] = True
                    
                    entry = {
                        "meta": meta,
                        "sections": extract_content_sections(content),
                        "full_content": content,
                        "file_path": str(md_file.relative_to(WIKI_ROOT)),
                        "content_hash": hashlib.md5(content.encode()).hexdigest()[:16],
                    }
                    all_entries.append(entry)
                    file_count += 1
                except Exception as e:
                    print(f"  ⚠️ Error processing {md_file}: {e}")
    
    print(f"[OK] Processed {file_count} files")
    if FM_ERRORS:
        print(f"[WARN] frontmatter unparsable: {len(FM_ERRORS)} (see below)")
        for e in FM_ERRORS[:10]:
            print(f"   - {e}")
    else:
        print("[OK] frontmatter parsed for every file")
    
    # Построить поисковый индекс
    search_index = build_search_index(all_entries)
    
    # Статистика
    stats = build_statistics(all_entries)
    
    # Сохранить базу данных
    database = {
        "version": "1.0",
        "created": datetime.now().isoformat(),
        "total_entries": len(all_entries),
        "statistics": stats,
        "entries": all_entries,
    }
    
    # Сохранить основную БД
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(database, f, ensure_ascii=False, indent=2)
    print(f"[DB] Database saved: {DB_PATH}")
    
    # Сохранить поисковый индекс
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False, indent=2)
    print(f"[INDEX] Search index saved: {INDEX_PATH}")
    
    # Экспорт для сайта (упрощенный)
    export_data = build_export(all_entries)
    with open(EXPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    print(f"[EXPORT] Export saved: {EXPORT_PATH}")
    
    return database

def build_search_index(entries: List[Dict]) -> Dict:
    """Построить обратный индекс для полнотекстового поиска"""
    index = {
        "terms": {},           # term -> [entry_ids]
        "tags": {},            # tag -> [entry_ids]
        "tools": {},           # mcp_tool -> [entry_ids]
        "categories": {},      # category -> [entry_ids]
        "languages": {},       # lang -> [entry_ids]
        "difficulties": {},    # difficulty -> [entry_ids]
        "entry_lookup": {},    # id -> entry index
    }
    
    stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an', 'в', 'и', 'или', 'но', 'на', 'в', 'для', 'с', 'по', 'к', 'от', 'из', 'у', 'о', 'а', 'это', 'тот', 'эта', 'эти', 'как', 'так', 'же', 'भी'}
    
    for idx, entry in enumerate(entries):
        meta = entry["meta"]
        entry_id = meta["id"]
        index["entry_lookup"][entry_id] = idx
        
        # Категории
        cat = meta.get("category", "unknown")
        index["categories"].setdefault(cat, []).append(entry_id)
        
        # Языки
        lang = meta.get("language", "en")
        index["languages"].setdefault(lang, []).append(entry_id)
        
        # Сложность
        diff = meta.get("difficulty", 0)
        index["difficulties"].setdefault(str(diff), []).append(entry_id)
        
        # Теги
        for tag in meta.get("tags", []):
            index["tags"].setdefault(tag, []).append(entry_id)
        
        # MCP инструменты
        for tool in meta.get("mcp_tools", []):
            index["tools"].setdefault(tool, []).append(entry_id)
        
        # Полнотекстовый индекс (только заголовки, теги, описание)
        text_parts = [
            meta.get("title", ""),
            meta.get("description", ""),
            " ".join(meta.get("tags", [])),
            " ".join(meta.get("mcp_tools", [])),
        ]
        
        full_text = " ".join(text_parts).lower()
        words = re.findall(r'\b\w{3,}\b', full_text)
        unique_words = set(w for w in words if w not in stop_words and len(w) > 2)
        
        for word in unique_words:
            index["terms"].setdefault(word, []).append(entry_id)
    
    # Дедупликация списков — deterministic sort for reproducibility
    for key in index:
        if isinstance(index[key], dict):
            for subkey in index[key]:
                val = index[key][subkey]
                if isinstance(val, list):
                    index[key][subkey] = sorted(set(val))
    
    print("[INDEX] Search index: {} terms, {} tags, {} tools".format(len(index['terms']), len(index['tags']), len(index['tools'])))
    return index

def build_statistics(entries: List[Dict]) -> Dict:
    """Построить статистику по базе"""
    stats = {
        "total_entries": len(entries),
        "by_category": {},
        "by_type": {},
        "by_language": {},
        "by_difficulty": {},
        "top_tags": {},
        "top_tools": {},
        "total_words": 0,
        "total_code_blocks": 0,
        "entries_with_code": 0,
    }
    
    tag_counts = {}
    tool_counts = {}
    
    for entry in entries:
        meta = entry["meta"]
        
        # Категории
        cat = meta.get("category", "unknown")
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        
        # Типы
        typ = meta.get("type", "unknown")
        stats["by_type"][typ] = stats["by_type"].get(typ, 0) + 1
        
        # Языки
        lang = meta.get("language", "en")
        stats["by_language"][lang] = stats["by_language"].get(lang, 0) + 1
        
        # Сложность
        diff = meta.get("difficulty", 0)
        stats["by_difficulty"][str(diff)] = stats["by_difficulty"].get(str(diff), 0) + 1
        
        # Теги
        for tag in meta.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Инструменты
        for tool in meta.get("mcp_tools", []):
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        # Статистика контента
        stats["total_words"] += meta.get("word_count", 0)
        stats["total_code_blocks"] += meta.get("code_blocks", 0)
        if meta.get("code_blocks", 0) > 0:
            stats["entries_with_code"] += 1
    
    # Топ теги и инструменты
    stats["top_tags"] = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:30])
    stats["top_tools"] = dict(sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:20])
    
    return stats

def build_export(entries: List[Dict]) -> Dict:
    """Построить экспорт для сайта (упрощенный)"""
    export = {
        "version": "1.0",
        "exported": datetime.now().isoformat(),
        "categories": {},
    }
    
    for entry in entries:
        meta = entry["meta"]
        cat = meta.get("category", "other")
        
        if cat not in export["categories"]:
            export["categories"][cat] = []
        
        export["categories"][cat].append({
            "id": meta["id"],
            "title": meta["title"],
            "type": meta.get("type", ""),
            "difficulty": meta.get("difficulty", 0),
            "tags": meta.get("tags", []),
            "language": meta.get("language", "en"),
            "description": meta.get("description", ""),
            "mcp_tools": meta.get("mcp_tools", []),
            "file_path": entry["file_path"],
        })
    
    return export

def search(query: str, index: Dict, entries: List[Dict], limit: int = 10) -> List[Dict]:
    """Поиск по индексу"""
    query = query.lower().strip()
    if not query:
        return []
    
    # Разбить запрос на слова
    words = re.findall(r'\b\w{3,}\b', query)
    words = [w for w in words if w not in {'the', 'and', 'for', 'with', 'from', 'в', 'и', 'для', 'на', 'с', 'по', 'к', 'от', 'из'}]
    
    if not words:
        return []
    
    # Найти пересечение entry_ids для всех слов
    candidate_ids = None
    for word in words:
        # Точное совпадение
        ids = set(index["terms"].get(word, []))
        
        # Частичное совпадение
        for term, term_ids in index["terms"].items():
            if word in term or term in word:
                ids.update(term_ids)
        
        if candidate_ids is None:
            candidate_ids = ids
        else:
            candidate_ids &= ids
    
    if not candidate_ids:
        return []
    
    # Ранжировать результаты
    results = []
    for entry_id in candidate_ids:
        idx = index["entry_lookup"].get(entry_id)
        if idx is not None:
            entry = entries[idx]
            meta = entry["meta"]
            
            # Простой скор
            score = 0
            title = meta.get("title", "").lower()
            desc = meta.get("description", "").lower()
            tags = " ".join(meta.get("tags", [])).lower()
            
            for word in words:
                if word in title: score += 10
                if word in desc: score += 5
                if word in tags: score += 3
                if word in entry_id.lower(): score += 2
            
            results.append({
                "score": score,
                "id": entry_id,
                "title": meta.get("title", ""),
                "category": meta.get("category", ""),
                "type": meta.get("type", ""),
                "difficulty": meta.get("difficulty", 0),
                "tags": meta.get("tags", []),
                "language": meta.get("language", "en"),
                "file_path": entry["file_path"],
            })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]

if __name__ == "__main__":
    print("=" * 60)
    print("BLENDER AI WIKI - DATABASE BUILDER")
    print("=" * 60)
    
    db = build_database()
    
    print("\n" + "=" * 60)
    print("STATISTICS")
    print("=" * 60)
    stats = db["statistics"]
    print("[STATS] Total entries: {}".format(stats['total_entries']))
    print("[STATS] Total words: {:,}".format(stats['total_words']))
    print("[STATS] Code blocks: {}".format(stats['total_code_blocks']))
    print("[STATS] Entries with code: {}".format(stats['entries_with_code']))
    print("\nBy category: {}".format(stats['by_category']))
    print("By language: {}".format(stats['by_language']))
    print("By difficulty: {}".format(stats['by_difficulty']))
    print("\nTop tags: {}".format(list(stats['top_tags'].items())[:10]))
    print("Top tools: {}".format(list(stats['top_tools'].items())[:10]))
    
    # Тест поиска
    print("\n" + "=" * 60)
    print("SEARCH TEST")
    print("=" * 60)
    
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        search_index = json.load(f)
    
    test_queries = [
        "primitive cube",
        "boolean difference",
        "principled bsdf",
        "uv unwrapping",
        "poly haven",
        "geometry nodes",
        "retopology",
    ]
    
    for query in test_queries:
        results = search(query, search_index, db["entries"], limit=3)
        print("\n[SEARCH] '{}':".format(query))
        for r in results:
            t = r['title'].encode('ascii', 'replace').decode('ascii')
            print("  {} - {} ({}/{}) [{}]".format(r['score'], t, r['category'], r['type'], r['language']))