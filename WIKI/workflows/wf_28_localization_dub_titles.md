---
id: wf_28_localization_dub_titles
lang: ru
category: workflows
type: workflow
status: full
tags: [localization, motion, workflow]
---
# WF 28: LOCALIZATION TITLES

**ID:** WF-28 | **Type:** Publish | **Difficulty:** ⭐
**RU/EN Bilingual**

> Когда применять: когда ролик с титрами надо отдать на пять языков или в четыре вертикальных формата, и перерисовывать каждое слово вручную — не вариант.

## 🎯 ЦЕЛЬ

Из одного исходного SRT или списка реплик получаются титры на N языков, автоматически расставленные по таймкодам, проверенные по **safe area** под конкретный формат кадра, и экспортированные отдельными файлами.

Два свойства, которые делают такую систему пригодной к повторному использованию: титры живут **как данные** (текст + таймкод в таблице), а не как нарисованные объекты в сцене; и проверка safe area — это код, а не «посмотрел глазами».

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с VSE | встроенный | полосы-титры и таймкоды |
| Файл SRT или CSV | UTF-8 | источник текста и таймкодов |
| Шрифт с нужными наборами символов | `.ttf`/`.otf`, Latin + CJK + Cyrillic | иначе будут «квадратики» |
| Таблица safe area | считается в коде | проверка попадания под обрезку площадок |

> [!NOTE]
> Импорт субтитров как готовых полос в VSE появился в Blender 4.x (`Text Import` в меню VSE → Add, оператор вроде `bpy.ops.sequencer.text_import`). В более старых версиях этого нет. Код ниже **не зависит** от него: он создаёт полосы-текст сам, поэтому работает везде, где есть `new_effect(type='TEXT')`.

## 🛠️ НАСТРОЙКА

### Этап 1. Разбор SRT

```bash
RU: "Локализация титров: исходный //subs/ru.srt, языки en, de, es, zh.
     Создай полосы-текст по таймкодам исходника, проверь safe area под 16:9 и 9:16,
     экспортируй рендеры //subs/out/<lang>_<format>"
EN: "Subtitle localization: source //subs/ru.srt, languages en, de, es, zh.
     Create text strips on the source timings, check safe area for 16:9 and 9:16,
     export renders to //subs/out/<lang>_<format>"
```

```python
import re

TS = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")

def parse_srt(path):
    def ms(h, m, s, f):
        return ((int(h) * 60 + int(m)) * 60 + int(s)) * 1000 + int(f)
    cues, idx, t0, t1, buf = [], 0, None, None, []
    with open(path, encoding="utf-8-sig") as fh:
        for raw in fh.read().splitlines() + [""]:
            line = raw.strip()
            if not line:
                if t0 is not None:
                    cues.append((t0, t1, "\n".join(buf)))
                t0, t1, buf = None, None, []
                continue
            m = TS.match(line)
            if m:
                g = m.groups()
                t0, t1 = ms(*g[:4]), ms(*g[4:])
            elif t0 is not None and not line.isdigit():
                buf.append(line)
    return cues

cues = parse_srt(r"<путь-к-проекту>\subs\ru.srt")
print(f"реплик: {len(cues)}")
for (a, b, txt) in cues[:3]:
    print(f"{a:>7} .. {b:<7} | {txt[:40]!r}")
```

### Этап 2. Перевод как данные, не как сцена

Пока перевода нет, таймкоды живут отдельно от текста. Это позволяет генерировать языки в любом порядке и не трогать сцену.

```python
import json, os

# translations.json: { "en": [[start_ms, end_ms, "text"], ...], ... }
# Ключ времени — не индекс: сдвиг на одну строку в переводе не должен ломать синхронизацию.
path = r"<путь-к-проекту>\subs\translations.json"
if os.path.exists(path):
    with open(path, encoding="utf-8") as fh:
        TRANSLATIONS = json.load(fh)
else:
    TRANSLATIONS = {"en": [[a, b, "[перевод]"] for a, b, _ in cues]}

for lang, rows in TRANSLATIONS.items():
    bad = [i for i, (a, b, _) in enumerate(rows) if b <= a]
    print(f"{lang}: {len(rows)} реплик, некорректных таймкодов {len(bad)}")
```

> [!NOTE]
> Реальной автоматической трансляции в Blender нет. Переводы приходят из внешней TMS, из таблицы или из GPT-подсказок, которую человек ревьюит. Всё, что делает Blender, — раскладка уже готового текста по таймкодам. Не выдавай перевод за автоматический, если это не так.

### Этап 3. Полосы-текст в VSE

```python
import bpy

sc = bpy.context.scene
sc.render.fps = 24
sc.frame_start, sc.frame_end = 0, int(200 * 24)
se = sc.sequence_editor or sc.sequence_editor_create()

def strips_container(se):
    for attr in ("strips", "sequences"):
        c = getattr(se, attr, None)
        if c is not None:
            return c
    raise AttributeError("не найдено ни strips, ни sequences в sequence_editor")

strips = strips_container(se)

def add_subtitle(text, start_ms, end_ms, channel=2):
    f0 = int(start_ms / 1000 * sc.render.fps)
    f1 = max(f0 + 1, int(end_ms / 1000 * sc.render.fps))
    st = strips.new_effect(name=f"sub_{f0:05d}", type='TEXT', channel=channel, frame_start=f0)
    st.frame_final_end = f1
    for prop, val in (("text", text), ("font_size", 0.052), ("align_x", 'CENTER'),
                      ("align_y", 'BOTTOM'), ("use_shadow", True),
                      ("box_color", (0.0, 0.0, 0.0, 0.55)), ("use_box", True)):
        try:
            setattr(st, prop, val)
        except (AttributeError, TypeError):
            pass        # свойства текстовых полос различаются между версиями — не молчим, а продолжаем
    return st

lang = "en"
made = 0
for start_ms, end_ms, text in TRANSLATIONS[lang]:
    add_subtitle(text, start_ms, end_ms)
    made += 1
print(f"полос-титров: {made}, всего полос в VSE: {len(strips)}")
```

> [!NOTE]
> Свойства текстовых полос (`text`, `font_size`, `align_x`, `align_y`, `use_box`, `box_color`, `use_shadow`, `shadow_color`) и их точные имена менялись. Код выше ставит их через `setattr` в `try/except` — если имя не подошло, полоса создастся без этого свойства, и это будет видно визуально. Список актуальных имён смотри так: `[p.identifier for p in bpy.types.TextSequence.bl_rna.properties]` (или `bpy.types.TextEffect`, если так называется тип в твоей версии).

### Этап 4. Safe area: считаем, а не смотрим

Зоны: для 16:9 обычно 90% по действию и 80% для названий; вертикальные форматы площадок режут по бокам гораздо сильнее. Считать надо в пикселях финального кадра.

```python
def safe_area(res_x, res_y, action=0.90, title=0.80):
    """Прямоугольники в пикселях, внутри которых текст обязателен."""
    def rect(f):
        w = res_x * f
        h = res_y * f
        x0, y0 = (res_x - w) / 2, (res_y - h) / 2
        return (x0, y0, x0 + w, y0 + h)
    return {"action": rect(action), "title": rect(title)}

for name, (rx, ry) in (("16:9", (1920, 1080)), ("9:16", (1080, 1920)), ("1:1", (1080, 1080))):
    sa = safe_area(rx, ry)
    a, t = sa["action"], sa["title"]
    print(f"{name:<5} action={tuple(round(v) for v in a)}  title={tuple(round(v) for v in t)}")

def text_fits(n_chars, font_px, box_w_px):
    """Грубая оценка: средняя ширина глифа ≈ 0.5em. Точнее не сделать без шрифта."""
    return n_chars * font_px * 0.5 <= box_w_px

box = safe_area(1920, 1080)["action"]
for line in ("TRANSFORMERS ARE WATCHING", " transformers are watching "):
    ok = text_fits(len(line), 34, box[2] - box[0])
    print(f"{line.strip():<28} влезает в action-safe 16:9: {ok}")
```

### Этап 5. Вертикальный формат

Тот же монтаж, другая геометрия кадра. Перекомпоновка — это не «обрезать по бокам», а сдвинуть смысловой центр в новый центр.

```python
import bpy, math
sc = bpy.context.scene

def set_format(name, rx, ry):
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    sc.render.resolution_percentage = 100
    cam = sc.camera
    if cam is None:
        return
    cam.data.sensor_fit = 'VERTICAL'          # иначе FoV считается по другой оси
    base_fov = cam.data.lens
    # для вертикального кадра угол по ширине должен вырасти
    if name == "9:16":
        cam.data.lens = base_fov * (9 / 16) * (16 / 9)
        cam.location = (cam.location.x, cam.location.y * 1.15, cam.location.z)
        cam.keyframe_insert("location", frame=sc.frame_start)

set_format("9:16", 1080, 1920)
print(sc.render.resolution_x, sc.render.resolution_y,
      sc.camera.data.sensor_fit if sc.camera else "камеры нет")
```

### Этап 6. Экспорт по языкам

```python
import bpy, os, shutil
sc = bpy.context.scene
se = sc.sequence_editor
strips = strips_container(se)

os.makedirs(bpy.path.abspath("//subs/out"), exist_ok=True)
all_subs = [s for s in strips if s.type == 'TEXT']

def only_language(lang, rows, channel=2):
    """Оставляем только полосы одного языка на своём канале."""
    wanted = {int(a / 1000 * sc.render.fps) for a, _, _ in rows}
    for s in all_subs:
        s.channel = channel if s.frame_start in wanted else 1
    sc.render.use_sequencer = True

for lang, rows in TRANSLATIONS.items():
    only_language(lang, rows)
    sc.render.filepath = bpy.path.abspath(f"//subs/out/{lang}_")
    sc.render.image_settings.file_format = 'PNG'
    bpy.ops.render.render(animation=True)

shutil.copy(bpy.path.abspath("//subs/translations.json"),
            bpy.path.abspath("//subs/out/translations.json"))
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `render.fps` | совпадает с исходным таймкодом | смена fps ломает тайминги субтитров |
| `font_size` | 3.5–5.5% высоты кадра | для 9:16 обычно крупнее по проценту ширины |
| safe area action | 90% | большинство площадок |
| safe area title | 80% | названия и логотипы |
| `align_y` | `'BOTTOM'` | нижние трети по умолчанию |
| `use_box` | `True` при тёмном фоне | без подложки текст пропадает на светлом |
| канал полосы | отдельный на язык | позволяет держать все языки в одной сцене |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| `AttributeError` на `sequences` | переименование API в 4.4 | резолвер `strips_container` выше |
| Текст выводится, но не с тем шрифтом/размером | часть свойств не применилась (типы полос разные) | вызвать `setattr` в `try/except` и проверить визуально; список имён — из `bl_rna` |
| Субтитры «уехали» на полсекунды | fps сцены не совпал с исходником | таймкоды пересчитываются как `ms/1000*fps` при каждом изменении fps |
| Текст обрезан площадкой | не попал в safe area | прогнать `safe_area` и подвинуть `align_y`/кегль |
| «Квадратики» в CJK | в шрифте нет нужных глифов | подключить шрифт с полным набором в `Preferences → File Paths → Fonts` |
| Длинная реплика не влезает | не включён перенос по словам | включить перенос строк и/или уменьшить `font_size` для длинных реплик |
| Все языки наложились друг на друга | полосы на одном канале | развести по каналам, включать нужный при экспорте |

## ✅ РЕЗУЛЬТАТ

На выходе: один `.blend` со всеми языками на разных каналах, файл `//subs/out/translations.json` с таймкодами и текстами, и набор отрендеренных прогонов — по одному на язык и формат (например 4 языка × 2 формата = 8 прогонов).

Характеристики — **оценка по порядку величины, а не измеренный результат**: 3-минутный ролик на 24 fps — около 4300 кадров на прогон. VSE-рендер (пересборка готовых клипов с наложением текста, без 3D) — секунды на кадр, то есть единицы минут на прогон; 8 прогонов — десятки минут. Полоса текста в VSE рендерится композитором видеоредактора и почти не стоит ничего по ресурсам. Кадр 1920×1080 PNG — 1–4 МБ.

**Это оценка.** Если под титрами идёт 3D-сцена, а не готовые клипы, время определяется рендером 3D, а не VSE. Замеряй у себя.

Базовые сетапы: [SETUP 01: BLENDER MCP BASIC](../setups/setup_01_blender_mcp_basic.md) — транспорт команд в Blender, [SETUP 08: ASSET PIPELINE](../setups/setup_08_asset_pipeline.md) — общая схема работы с ассетами.

## 🔗 СВЯЗИ

- **Прочие в категории «Воркфлоу»:** [WF 21: MOTION GRAPHICS TITLES](wf_21_motion_graphics_titles.md), [WF 01: TEXT-TO-SCENE](wf_01_text_to_scene.md), [WF 02: IMAGE-TO-3D](wf_02_image_to_3d.md), [WF 03: TEXTURE PIPELINE](wf_03_texture_pipeline.md), [WF 04: CHARACTER ANIMATION](wf_04_character_animation.md)
- **По темам:** [WF 05: PROCEDURAL ASSETS](wf_05_procedural_assets.md), [WF 06: ARCHVIZ WORKFLOW](wf_06_archviz_workflow.md), [WF 07: GAME ASSET PIPELINE](wf_07_game_asset_pipeline.md)
- **Теги:** #localization, #motion, #workflow