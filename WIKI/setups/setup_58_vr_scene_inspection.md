---
id: setup_58_vr_scene_inspection
lang: ru
category: setups
type: setup
status: full
tags: [setup, vr]
---
# SETUP 58: VR SCENE INSPECTION

**ID:** SETUP-58 | **Type:** VR/XR | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

> Когда применять: когда масштаб сцены, высоты и перекрытия невозможно оценить
> на мониторе — а проверить их надо до рендера.

---

## 🎯 ЦЕЛЬ

Провести сцену в VR-сессии Blender, зафиксировать реальный масштаб и наложить
аннотации, которые переживут сессию.

Отдельно и важно: **API XR в Blender 5.x поменялся**. Проверено на 5.2.1 — оператора
`bpy.ops.xr.start_session` и свойства `scene.xr` больше нет, есть
`bpy.ops.wm.xr_session_toggle` и `wm.xr_session_settings`. Старые рецепты из
интернета на этой версии не сработают.

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 5.x (проверено 5.2.1) | XR-сессия, навигация, аннотации |
| Сборка с OpenXR | `bpy.app.build_options.xr_openxr == True` | Иначе сессия не запустится |
| HMD и рантайм | OpenXR-совместимый (Quest Link / SteamVR / Meta XR) | Вывод картинки в шлем |
| Комната с реальным масштабом | 2–3 м в длину | Сверять ощущения с метрами |

---

## 🛠️ НАСТРОЙКА

### 1. Проверить, что XR вообще собран

```python
# Проверка до того, как надели шлем. В фоне не запускается — только читается.
import bpy

bo = bpy.app.build_options
print("openxr:", bo.xr_openxr)
print("gpu cycles:", bo.cycles, "| compositor:", bo.compositor_cpu)
```

Если `xr_openxr` — `False`, сессия не поднимется ни при каких настройках: нужен
другой дистрибутив Blender.

### 2. Настроить масштаб и отсечение до входа в сессию

```python
# xr_preflight.py — запускать в UI-сессии перед стартом XR.
import bpy

wm = bpy.context.window_manager
xr = wm.xr_session_settings        # проверенный тип: XrSessionSettings

xr.use_absolute_tracking = True     # world-scale: 1 юнит = 1 метр
xr.use_positional_tracking = False  # без room-scale, чтобы «пол» не прыгал
xr.base_scale = 1.0                 # базовая позиция пользователя относительно мира
xr.view_scale = 1.0                 # масштаб просмотра (не гейт)
xr.clip_start = 0.01                # проверенное значение по умолчанию
xr.clip_end = 1000.0                # проверенное значение по умолчанию
xr.show_floor = True
xr.show_controllers = True
# проверенные значения enum в 5.2: DARK, LIGHT, DARK_RAY, LIGHT_RAY
xr.controller_draw_style = 'DARK'
xr.fly_speed = 2.0

print("scale ok:", xr.base_scale, xr.view_scale, xr.clip_start, xr.clip_end)
```

`clip_start = 0.01` обязателен: при стандартном «внутри» ближняя геометрия
пропадает, и кажется, что в стене дыра.

### 3. Знать актуальные операторы навигации

В 5.2.1 в `bpy.ops.wm` есть ровно это (проверено перечислением):

| Оператор | Что делает |
|---|---|
| `wm.xr_session_toggle` | Войти/выйти из XR-сессии |
| `wm.xr_navigation_teleport` | Телепорт по указателю; есть `range`, `selectable_only`, `force` |
| `wm.xr_navigation_fly` | Полёт; есть `mode`, `fly_speed_factor`, `turn_speed_factor`, `snap_turn_threshold` |
| `wm.xr_navigation_grab` | Сдвиг/поворот/масштаб мира; есть `lock_location`, `lock_rotation`, `lock_scale` |
| `wm.xr_navigation_reset` | Сброс навигации; принимает `location`, `rotation`, `scale` |
| `wm.xr_navigation_swap_hands` | Поменять руки местами |

```python
# Включить сессию из скрипта/UI-кнопки:
bpy.ops.wm.xr_session_toggle()
# ...и выключить тем же вызовом.

# Телепорт на расстояние до 10 м только по selectable-объектам:
bpy.ops.wm.xr_navigation_teleport(range=10.0, selectable_only=True)
```

> [!NOTE]
> На более старых версиях Blender (до 5.x) вход в сессию выглядел как
> `bpy.ops.xr.start_session()`, а настройки жили в `scene.xr`. Если вы работаете
> на такой версии — сверяйтесь со своей: точный набор операторов
> перечисляется через `dir(bpy.ops.wm)`.

### 4. Поставить в сцену объекты известного размера

Это единственный надёжный способ проверить масштаб: не «на глаз», а сравнением с
эталоном.

```python
# scale_reference.py — эталонные объекты в сцене.
import bpy

def make_reference(name, size, color=(1, 0, 0, 1)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (size, size, size)
    ob.location = (0, 0, size / 2)          # стоит на полу
    ob.hide_render = True                    # в рендер не идёт
    mat = bpy.data.materials.new(f"{name}_mat")
    mat.diffuse_color = color
    ob.data.materials.append(mat)
    return ob

make_reference("REF_door", 2.05)        # дверной проём
make_reference("REF_eye", 1.70)         # рост человека
make_reference("REF_step", 0.18)        # ступенька

def audit_scale(objects, tolerance=0.01):
    """Напечатать габариты, чтобы сравнить с замыслом."""
    for ob in objects:
        dims = ob.dimensions
        flag = "OK" if abs(dims.z - 0.0) < tolerance else ""
        print(f"{ob.name}: {dims.x:.2f} x {dims.y:.2f} x {dims.z:.2f} {flag}")

audit_scale([bpy.data.objects[n] for n in ("REF_door", "REF_eye", "REF_step")])
```

Результат, который нужно увидеть в VR: дверь 2.05 м ощущается дверью, а не
щелью; уровень глаз камеры — около 1.6–1.7 м; если объекты «плывут» при ходьбе,
виноват не рендер, а `use_absolute_tracking` и единицы сцены.

### 5. Записывать находки, а не держать их в голове

```python
# annotate.py — аннотация = текстовый блок в .blend + маркер на таймлайне.
import bpy, datetime

def annotate(text, frame=None, kind='note'):
    name = f"XR_{kind}_{datetime.datetime.now():%H%M%S}"
    txt = bpy.data.texts.get(name) or bpy.data.texts.new(name)
    txt.clear()
    txt.write(text)
    if frame is not None:
        bpy.context.scene.timeline_markers.new(name, frame=frame)
    return txt.name

print(annotate("коридор: потолок ниже 2.4 m — опустить на 0.15", frame=120))
print(annotate("лестница: ступень 0.18 m, ок", kind='ok'))

# Объектные заметки — чтобы подписать проблемный объект прямо в сцене:
obj = bpy.data.objects.get("Corridor_Ceiling")
if obj:
    obj["xr_review"] = "too low, -0.15"
    obj["xr_review_frame"] = 120
```

Текстовый блок переживает перезагрузку файла и попадает в `.blend`, маркер — в
таймлайн, а `custom property` висит на самом объекте: три разных носителя под
три разных вопроса (что решено, где в таймлайне, какой объект виноват).

### 6. Забрать позицию пользователя программно

```python
# Если нужно понять, где стоял оператор в момент находки:
state = bpy.context.window_manager.xr_session_state   # XrSessionState
print("viewer:", state.viewer_pose_location)
print("navigation:", state.navigation_location, state.navigation_rotation)
print("scale:", state.navigation_scale)
print("actionmaps:", [m.name for m in state.actionmaps])
```

Полезно, чтобы приложить к отчёту «с этого ракурса» координату наблюдателя:
иначе через неделю никто не вспомнит, о какой именно двери речь.

### 7. Снять стерео-кадр для архива

```python
# Вариант для рендера, а не для OpenGL-захвата с экрана.
# views_format — обычный enum; stereo_views — коллекция имён видов,
# по умолчанию содержит 'left' и 'right' (проверено на 5.2.1).
sc = bpy.context.scene
sc.render.use_multiview = True
sc.render.views_format = 'STEREO_3D'
print("views:", [getattr(v, "name", v) for v in sc.render.stereo_views])
sc.render.filepath = "//xr_check/frame_"
bpy.ops.render.render(write_still=True)
```

> [!NOTE]
> `bpy.ops.render.opengl()` (захват вьюпорта) требует графического контекста и
> в `blender -b` не работает — для headless-сценария используйте обычный
> `bpy.ops.render.render()`. Порядок видов (`left`/`right`) и их имена
> зависят от того, как настроен мульти-view в вашей сцене, поэтому печатайте
> их, а не задавайте строкой.

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Проверка сборки без GUI:
blender -b --python-expr "import bpy;print('openxr', bpy.app.build_options.xr_openxr)"
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `use_absolute_tracking` | `True` | `False` — если нужно world-scale 1:100 для миниатюр |
| `clip_start` | `0.01` | Ниже — z-fighting; выше `0.02` — исчезает геометрия у лица |
| `clip_end` | `1000.0` | Для интерьеров хватит `100` — экономит глубину |
| `base_scale` / `view_scale` | `1.0` | `view_scale` не трогать, если не собираете gizmo-режим |
| `wm.xr_navigation_teleport(range=)` | `10.0` | Радиус телепорта: меньше — не упасть в пролёт |
| `wm.xr_navigation_grab(lock_scale=)` | `True` | Запрет масштабирования мира при осмотре |
| Габариты сцены | метры | Сцена в сантиметрах + XR = «всё в 100 раз меньше» |

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Кнопка XR в UI серая | Сборка без OpenXR | Проверить `bpy.app.build_options.xr_openxr`, поставить подходящий дистрибутив |
| `bpy.ops.xr.start_session` → AttributeError | Старый рецепт для версии до 5.x | `bpy.ops.wm.xr_session_toggle()` |
| Геометрия пропадает у лица и под ногами | `clip_start` слишком большой | `clip_start = 0.01` |
| Сцена «микроскопическая» | Сцена в сантиметрах, а XR ждёт метры | Масштабировать сцену в 0.01 либо задать `use_absolute_tracking = False` |
| Пол прыгает при ходьбе | Включён room-scale / позиционное отслеживание | `use_positional_tracking = False` |
| Телепорт не срабатывает | Некуда телепортироваться: пустота | `selectable_only=False`, увеличить `range` |
| Шлем не видит HMD | Рантайм не подхватил трекер | Проверить, что рантайм запущен и видит HMD **до** входа в сессию |
| `render.opengl` падает в headless | Нужен графический контекст | Использовать `bpy.ops.render.render()` |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 57: FACE MOCAP ARKIT](setup_57_face_mocap_arkit.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md)
- **Теги:** #setup, #vr
