#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bulk multilang generator: 5 langs (en,ru,es,de,zh) in chunks. Usage: python bulk_multilang.py --lang es --chunk 0 --chunks 4 --only setups"""
import argparse, json, re, os
from pathlib import Path
S = Path(__file__).resolve().parent          # WIKI/scripts
WIKI = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
DB = WIKI/"db"/"wiki_database.json"

LANGS = ["en","ru","es","de","zh"]
UI = {
 "en":{"goal":"Goal","steps":"Steps / Prompts","check":"Check","pitfalls":"Pitfalls","links":"Links"},
 "ru":{"goal":"Цель","steps":"Шаги / Промпты","check":"Проверка","pitfalls":"Ошибки","links":"Связи"},
 "es":{"goal":"Objetivo","steps":"Pasos / Prompts","check":"Verificación","pitfalls":"Errores","links":"Enlaces"},
 "de":{"goal":"Ziel","steps":"Schritte / Prompts","check":"Prüfung","pitfalls":"Fehler","links":"Links"},
 "zh":{"goal":"目标","steps":"步骤 / 提示词","check":"检查","pitfalls":"常见错误","links":"相关链接"},
}
SEC_HEAD = {
 "es":[("GOAL","OBJETIVO"),("PROMPT","PROMPT"),("STEPS","PASOS"),("CHECK","VERIFICACIÓN"),("LINKS","ENLACES"),("PARAMETERS","PARÁMETROS"),("EXAMPLES","EJEMPLOS"),("ERRORS","ERRORES"),("WORKFLOW","FLUJO DE TRABAJO"),("INSTALLATION","INSTALACIÓN"),("USAGE","USO"),("TROUBLESHOOTING","SOLUCIÓN DE PROBLEMAS")],
 "de":[("GOAL","ZIEL"),("PROMPT","PROMPT"),("STEPS","SCHRITTE"),("CHECK","PRÜFUNG"),("LINKS","LINKS"),("PARAMETERS","PARAMETER"),("EXAMPLES","BEISPIELE"),("ERRORS","FEHLER"),("WORKFLOW","ARBEITSABLAUF"),("INSTALLATION","INSTALLATION"),("USAGE","VERWENDUNG"),("TROUBLESHOOTING","FEHLERBEHEBUNG")],
 "zh":[("GOAL","目标"),("PROMPT","提示词"),("STEPS","步骤"),("CHECK","检查"),("LINKS","相关链接"),("PARAMETERS","参数"),("EXAMPLES","示例"),("ERRORS","错误"),("WORKFLOW","工作流"),("INSTALLATION","安装"),("USAGE","用法"),("TROUBLESHOOTING","故障排除")],
 "ru":[("GOAL","ЦЕЛЬ"),("PROMPT","ПРОМПТ"),("STEPS","ШАГИ"),("CHECK","ПРОВЕРКА"),("LINKS","СВЯЗИ"),("PARAMETERS","ПАРАМЕТРЫ"),("EXAMPLES","ПРИМЕРЫ"),("ERRORS","ОШИБКИ")],
}
def translate_sections(body, lang):
    if lang in ("en",) or lang not in SEC_HEAD: return body
    out = body
    for en, tr in SEC_HEAD[lang]:
        out = re.sub(rf"^(#+\s*){en}\b", rf"\1{tr}", out, flags=re.MULTILINE|re.IGNORECASE)
    return out
TITLE_MAP = {
 "es":{"SETUP":"CONFIGURACIÓN","WORKFLOW":"FLUJO","CASE":"CASO","PROMPT":"PROMPT","BLENDER":"BLENDER","MCP":"MCP","TEXTURE":"TEXTURA","LIGHTING":"ILUMINACIÓN","CAMERA":"CÁMARA","CHARACTER":"PERSONAJE","GAME":"JUEGO","RENDER":"RENDER","PIPELINE":"PIPELINE"},
 "de":{"SETUP":"SETUP","WORKFLOW":"WORKFLOW","CASE":"FALL","PROMPT":"PROMPT","BLENDER":"BLENDER","MCP":"MCP","TEXTURE":"TEXTUR","LIGHTING":"BELEUCHTUNG","CAMERA":"KAMERA","CHARACTER":"CHARAKTER","GAME":"SPIEL","RENDER":"RENDER","PIPELINE":"PIPELINE"},
 "zh":{"SETUP":"配置","WORKFLOW":"工作流","CASE":"案例","PROMPT":"提示词","BLENDER":"Blender","MCP":"MCP","TEXTURE":"纹理","LIGHTING":"灯光","CAMERA":"相机","CHARACTER":"角色","GAME":"游戏","RENDER":"渲染","PIPELINE":"管线"},
 "ru":{"SETUP":"СЕТАП","WORKFLOW":"ВОРКФЛОУ","CASE":"КЕЙС"},
 "en":{},
}
def translate_title(title, lang):
    if lang in ("en",): return title
    m = TITLE_MAP.get(lang,{})
    out = title
    for k,v in m.items():
        out = re.sub(k, v, out, flags=re.IGNORECASE)
    return out

SUMMARY_T = {
 "en":"This page is the {lang} version of '{id}'. Code blocks are language-agnostic. Follow steps in order, verify with Check section.",
 "ru":"Это русская версия '{id}'. Кодовые блоки языконезависимы. Выполняйте шаги по порядку, проверяйте разделом Проверка.",
 "es":"Esta es la versión en español de '{id}'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.",
 "de":"Dies ist die deutsche Version von '{id}'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.",
 "zh":"这是 '{id}' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。",
}
SEC_T = {
 "en":{"prompt":"MCP Prompt (copy-paste)","how":"How to use","note":"Note: code/paths stay in English for Blender/Python compatibility."},
 "ru":{"prompt":"MCP-промпт (копипаст)","how":"Как пользоваться","note":"Замечание: код/пути оставлены на английском для совместимости Blender/Python."},
 "es":{"prompt":"Prompt MCP (copiar-pegar)","how":"Cómo usar","note":"Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python."},
 "de":{"prompt":"MCP-Prompt (kopieren)","how":"Verwendung","note":"Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität)."},
 "zh":{"prompt":"MCP 提示词（复制粘贴）","how":"使用方法","note":"注意：代码/路径保留英文以兼容 Blender/Python。"},
}
def build_file(entry, lang):
    meta = entry["meta"]; body = entry.get("full_content","")
    ui = UI[lang]; sec = SEC_T[lang]
    title = translate_title(meta.get("title",meta["id"]), lang)
    summary = SUMMARY_T[lang].format(lang=lang, id=meta['id'])
    header = f"""---
id: {meta['id']}
lang: {lang}
orig_lang: {meta.get('language','en')}
category: {meta.get('category','')}
type: {meta.get('type','')}
difficulty: {meta.get('difficulty',0)}
tags: {', '.join(meta.get('tags',[])[:15])}
---

# {title}

> {ui['goal']}: {meta.get('description','')[:400]}

**ID:** {meta['id']} | **Lang:** {lang} | **Orig:** {meta.get('language','en')} | **Category:** {meta.get('category','')} | **Tags:** {', '.join(meta.get('tags',[])[:12])}

## {sec['how']}
{summary}

## {sec['prompt']}
```
{meta['id']} / {meta.get('category','')} / {', '.join(meta.get('tags',[])[:8])}
```

> {sec['note']}

---
"""
    return header + "\n" + translate_sections(body, lang)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="es", choices=LANGS)
    ap.add_argument("--chunk", type=int, default=0)
    ap.add_argument("--chunks", type=int, default=4)
    ap.add_argument("--only", default="", help="comma: setups,workflows,cases,prompts")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--force", action="store_true", help="overwrite existing files")
    a = ap.parse_args()
    db = json.loads(DB.read_text(encoding="utf-8"))
    entries = db["entries"]
    only = set([x.strip() for x in a.only.split(",") if x.strip()])
    if only:
        entries = [e for e in entries if e["meta"].get("category") in only]
    # deterministic chunk split
    entries = sorted(entries, key=lambda e: e["meta"]["id"])
    n = len(entries)
    size = (n + a.chunks - 1)//a.chunks
    part = entries[a.chunk*size:(a.chunk+1)*size]
    if a.limit: part = part[:a.limit]
    made = 0
    for e in part:
        meta = e["meta"]
        cat = meta.get("category") or "misc"
        # map original filename
        orig = Path(e["file_path"]).name
        out = WIKI/"multilang"/a.lang/cat/orig
        out.parent.mkdir(parents=True, exist_ok=True)
        if (not a.force) and out.exists() and out.stat().st_size > 500:
            continue
        out.write_text(build_file(e, a.lang), encoding="utf-8")
        made += 1
    print(f"OK lang={a.lang} chunk={a.chunk}/{a.chunks} made={made} total_in_chunk={len(part)}")

if __name__ == "__main__":
    main()
