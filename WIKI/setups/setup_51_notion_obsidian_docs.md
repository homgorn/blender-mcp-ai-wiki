---
id: setup_51_notion_obsidian_docs
lang: ru
category: setups
status: stub
---
# SETUP 51: NOTION/OBSIDIAN DOCS SYNC

**ID:** SETUP-51 | **Type:** Docs | **Difficulty:** ⭐ | **Time:** 10 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: Документация из вики. EN: Docs from wiki.

## 1. Шаги / Steps
1. Markdown export
2. Asset registry
3. Changelog
4. Search index

## 2. MCP промпт / Prompt
```
RU: "Экспорт WIKI db/*.json → Notion/Obsidian, теги, обратные ссылки" / EN: "Export WIKI db JSON → Notion/Obsidian with tags/backlinks"
```

## 3. Проверка / Check
- [ ] Аддон/сервис отвечает
- [ ] Тестовая сцена собирается
- [ ] Экспорт читается целевым софтом

## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

## 🔗 Связи / Links
Setup 01 blender-mcp, Setup 08 Asset Pipeline, WF-01, INDEX
