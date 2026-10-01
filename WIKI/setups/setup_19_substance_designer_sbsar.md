---
id: setup_19_substance_designer_sbsar
lang: ru
category: setups
type: setup
status: full
tags: [setup, shading, substance]
---
# SETUP 19: SUBSTANCE DESIGNER SBSAR

**ID:** SETUP-19 | **Type:** Procedural | **Difficulty:** ⭐⭐ | **Time:** 40-70 min
**RU/EN Bilingual**

> Когда применять: когда материал должен быть параметрическим — один граф даёт десятки вариантов (разная ширина шва, разный износ, разная толщина), и править его руками в текстуре дороже, чем двигать ручку. Классика: кирпич, бетон, ткань, металл с паттерном ржавчины.

## 🎯 ЦЕЛЬ
Собрать из графа Substance 3D Designer переиспользуемый материал и подключить его к Blender так, чтобы в сцене появились ноды, которыми можно крутить параметры. Основной путь — готовые аддоны-конвертеры `.sbsar` в нодовый граф Blender; запасной, работающий всегда — запечь текстуры через `sbscooker`/`sbsrender` и собрать Principled BSDF вручную.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|-----------|--------|-------|
| Substance 3D Designer | 12.x / 13.x (ранее Substance Designer) | авторство графа и экспорт `.sbsar` |
| Substance 3D Player | та же мажорная версия | бесплатный просмотр `.sbsar`, проверка до Blender |
| Blender | 4.2 LTS+ | приём материала |
| Аддон-конвертер `.sbsar` → ноды Blender | см. примечание | превращает граф в ShaderNode-дерево |
| `sbscooker` (входит в поставку Designer) | — | запекание текстур из `.sbsar` без GUI |
| Готовый `.sbsar` | любой из Substance Share или свой | входные данные |

> [!NOTE]
> Официального аддона от Adobe для Blender нет: конвертеры `.sbsar` — сторонние проекты с разной степенью поддержки версий Blender. Перед тем как строить на них пайплайн, открой README конкретного аддона и проверь две вещи: на какую версию Blender он рассчитан и умеет ли он переносить exposed-параметры как отдельные ноды с дефолтами. Если не умеет — переходи на запекание через `sbscooker`, оно верно во всех версиях.

## 🛠️ НАСТРОЙКА

### 1. Экспорт `.sbsar` из Designer

`.sbsar` — это уже готовый, параметрический пакет: граф плюс список входов, которые он объявил как «exposed». Именно эта функция и делает файл ценным.

```text
Substance 3D Designer:
  1. Открой свой граф (или собери: Uniform Color → Bitmap/Scan → Blend → Output)
  2. Выходной нод (Output) должен вести в группу с включённым Output
  3. File → Export → Export SBSAR  →  my_material.sbsar

Проверка без Blender:
  Substance 3D Player → File → Open → my_material.sbsar
  В панели Parameters справа должны появиться exposed-ручки.
  Их нет → параметры не были экспонированы, и конвертер их не подхватит.
```

Что должно быть на выходе графа (это то, что потом увидит Blender):

```text
Output-узел со следующими каналами:
  baseColor (rgb)   → Base Color
  metallic  (scalar)→ Metallic
  roughness (scalar)→ Roughness
  normal    (normal)→ Normal
  height    (scalar)→ Height      (опционально, нужен для бампа)
  ambient   (rgb)   → AO          (опционально)
  opacity   (scalar)→ Alpha       (опционально)
  emissive  (rgb)   → Emission    (опционально)
```

### 2. Запекание через `sbscooker` — путь, который работает всегда

`sbscooker` берёт `.sbsar` и список входов в `.sbsxml` и раскладывает текстуры в папку. Это ровно то, что делает аддон-конвертер, но без конвертации в ноды.

```bash
# Структура запуска (путь зависит от установки Designer, см. ниже)
"C:\Program Files\Adobe\Adobe Substance 3D Designer\...\sbscooker.exe" \
    C:\mat\brick.sbsar C:\mat\brick_out \
    --inputs C:\mat\brick_inputs.sbsxml

# Список доступных флагов — сам надёжный источник правды:
sbscooker.exe --help
```

Входы описываются в `.sbsxml` — это обычный XML с идентификаторами параметров из графа:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- Идентификаторы (mortar_width и т.п.) — это UUID или label'ы,
     которые видны в Designer: правый клик на вход → Copy Parameter ID.
     Смотри также "Output" в Substance 3D Player: там готовые имена. -->
<properties>
    <property name="mortar_width" type="float">
        <value>0.012</value>
    </property>
    <property name="color_variation" type="float">
        <value>0.35</value>
    </property>
    <property name="tile_scale" type="float">
        <value>4.0</value>
    </property>
</properties>
```

> [!NOTE]
> Набор флагов `sbscooker` менялся между версиями Designer (в частности, формат входных параметров). Не переноси команды из интернета один в один: запусти `sbscooker.exe --help` из своей установки и сверь имена. Точный путь к бинарнику смотри в директории установки Designer, там же лежит `sbsrender.exe` — она делает то же самое, но в PNG-превью.

### 3. Blender: сборка Principled BSDF из запечённых карт

```python
# sbsar_to_material.py — Blender: Text Editor → Run Script
import bpy, os, glob

MAT_DIR = r"C:\mat\brick_out"      # куда положил sbscooker
MAT_NAME = "M_Brick_SBSAR"

def _find(pattern):
    hits = glob.glob(os.path.join(MAT_DIR, pattern))
    return hits[0] if hits else None

def build(mat_name=MAT_NAME):
    mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    nodes, links = tree.nodes, tree.links

    out = nodes.new("ShaderNodeOutputMaterial"); out.location = (800, 0)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled"); bsdf.location = (500, 0)

    def tex(label, srgb=False, y=0):
        path = _find(f"*{label}*")
        if not path:
            print("нет карты:", label); return None
        n = nodes.new("ShaderNodeTexImage")
        n.location = (0, y)
        n.image = bpy.data.images.load(path, check_existing=False)
        n.image.colorspace_settings.name = 'sRGB' if srgb else 'Non-Color'
        return n

    t = tex("basecolor", srgb=True, y=400)
    if t: links.new(t.outputs["Color"], bsdf.inputs["Base Color"])

    t = tex("roughness", y=200)
    if t: links.new(t.outputs["Color"], bsdf.inputs["Roughness"])

    t = tex("metallic", y=0)
    if t: links.new(t.outputs["Color"], bsdf.inputs["Metallic"])

    t = tex("normal", y=-200)
    if t:
        nm = nodes.new("ShaderNodeNormalMap"); nm.location = (250, -200)
        nm.inputs["Strength"].default_value = 1.0
        links.new(t.outputs["Color"], nm.inputs["Color"])
        links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])

    # Height в Bump, а не в Displace: displacement требует достаточной
    # плотности меша и ломается на тайлах UDIM
    t = tex("height", y=-400)
    if t:
        bump = nodes.new("ShaderNodeBump"); bump.location = (250, -400)
        bump.inputs["Strength"].default_value = 0.2
        bump.inputs["Distance"].default_value = 0.02
        links.new(t.outputs["Color"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    # Мировые масштабы: узор SBSAR рассчитан на свои единицы, в Blender он
    # почти всегда «поедет» — задавай явно
    mapping = nodes.new("ShaderNodeMapping"); mapping.location = (-250, 400)
    mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    coord = nodes.new("ShaderNodeTexCoord"); coord.location = (-450, 400)
    links.new(coord.outputs["Object"], mapping.inputs["Vector"])

    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat

m = build()
m.use_fake_user = True
print("материал:", m.name, "| нод:", len(m.node_tree.nodes))
```

### 4. Путь «живых параметров»: аддон-конвертер

```text
1. Установить аддон через Edit → Preferences → Add-ons → Install…
   (проверь совместимость версий по README до установки)
2. Открыть панель аддона (обычно в Properties → Material или отдельный панель)
3. Выбрать .sbsar → аддон конвертирует граф в ноды
4. Exposed-параметры появляются как отдельные ноды Value/RGB с дефолтами
5. Изменить параметр → пересчитать (Recompile / Refresh) → текстура обновится
```

Что важно понимать про этот путь:

| Свойство | Значение |
|----------|----------|
| Что становится нодой | Одна нода на input графа, значение в `default_value` |
| Что НЕ становится нодой | Внутренняя логика графа — она «запекается» в текстуру |
| Скорость пересчёта | Секунды для 1K, десятки секунд для 4K — это рендер, не live-обновление |
| Разрешение | Задаётся в настройках аддона или в Output-группе графа |
| Зависимость от Adobe | Нет: `.sbsar` — самостоятельный файл со встроенным движком |

### 5. Сравнение подходов

| | Конвертер в ноды | `sbscooker` + ручная сборка |
|---|---|---|
| Параметры | крутятся прямо в Blender | только перезапуск `sbscooker` с новым `.sbsxml` |
| Зависимость от аддона | да | нет, только бинарник Designer |
| Автоматизация/CI | плохо (нужен интерактивный UI) | отлично (скрипт + аргументы) |
| Что выбрать | интерактивная работа, один материал | пайплайн, много вариантов, рендер-ферма |

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Пакетная генерация N вариантов одного материала: меняем только .sbsxml
for w in 0.006 0.012 0.024; do
  sed "s|<value>0.012</value>|<value>$w</value>|" inputs.sbsxml > in_$w.sbsxml
  sbscooker.exe brick.sbsar out_$w --inputs in_$w.sbsxml
done
```

```python
# Blender: прогнать все варианты в сцене как отдельные объекты — быстрый A/B
import bpy, glob, os
for d in sorted(glob.glob(r"C:\mat\out_*")):
    mat = bpy.data.materials.get(os.path.basename(d))
    if not mat:
        print("пропущен (нет материала):", d); continue
    ob = bpy.data.objects.new(os.path.basename(d), bpy.data.meshes.new(os.path.basename(d)))
    ob.data.materials.append(mat)
    bpy.context.collection.objects.link(ob)
    ob.location = (len(bpy.context.collection.objects) * 1.5, 0, 0)
```

| Параметр | Значение | Когда менять |
|----------|----------|--------------|
| Exposure (Output-группа) | `default`, `parent`, `0-1` | `default` — гамма 2.2, sRGB-текстуры; `0-1` — линейные данные |
| Разрешение выхода | 1K / 2K / 4K / 8K | 8K — это ~800 МБ на канал, для Cycles и GPU не всегда полезно |
| `tile_scale` (через mapping) | 1.0 | узор из SBSAR масштабируется в мировых единицах Blender, а не в UV |
| Bump `Distance` | 0.01–0.05 | слишком большое значение даёт «жестянку» на мелких деталях |
| Bump `Strength` | 0.1–0.4 | выше 0.5 высоты перестают читаться как рельеф |
| Входные параметры графа | float / color / integer | тип влияет на формат XML в `.sbsxml` |

### Про лицензию и зависимости

`sbsar` — открытый формат, но рендер идёт через движок, который **поставляется вместе с Substance 3D Designer или Player**. Player бесплатный и умеет открывать `.sbsar`, поэтому чаще всего достаточно его. Аддон-конвертер, который работает внутри Blender, зависит от того, что аддон сам умеет считать граф — проверяй в его README, нужна ли ему установленная Adobe.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|--------|---------|---------|
| В Player нет ручек Parameters | Параметры не экспонированы в графе | В Designer отметь нужные входы как exposed перед экспортом |
| Аддон не находит граф | Несовместимость версий аддона и Blender | Проверь README аддона; запасной путь — `sbscooker` |
| `sbscooker` не запускается | Путь к бинарнику отличается от ожидаемого | Найди `sbscooker.exe` в директории установки Designer и вызови по полному пути |
| Материал чёрный | Exposure Output-группы не тот, либо карта не нашлась | Проверь путь/имена файлов в `MAT_DIR`, сверь exposure в Player |
| Текстура мылится вдали | Нет мирового масштаба: узор считался в UV | Добавь Mapping + TexCoord Object и подбери `Scale` |
| Тайлы UDIM из SBSAR не подхватаются | Blender не собрал тайлы в один датаблок | Открой все файлы `1001.png…` разом через Image Editor → Open |
| Рельеф выглядит как «жесть» | Displace вместо Bump, либо слишком большой Distance | Используй Bump ноду; Distancе держи в пределах 0.01–0.05 |
| Нормали инвертированы | Каналы перепутаны или.flip по Y | Сравни с любой готовой картой normal того же формата; в Substance — «direct» против «OpenGL» |
| Пересчёт параметра занимает минуты | Рендер графа на высоком разрешении | Опусти разрешение на этапе подбора параметров, подними на финальном |
| Материал пропал после перезагрузки файла | У датаблока не стоял пользователь | `mat.use_fake_user = True` |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 18: SUBSTANCE PAINTER LIVE-LINK](setup_18_substance_painter_live.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [P09: PRINCIPLED BSDF SETUP](../prompts/09_principled_bsdf.md), [P10: NODE GROUP CREATION](../prompts/10_node_groups.md), [P11: PROCEDURAL TEXTURES](../prompts/11_procedural_textures.md)
- **Теги:** #setup, #shading, #substance