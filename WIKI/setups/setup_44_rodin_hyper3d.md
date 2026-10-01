---
id: setup_44_rodin_hyper3d
lang: ru
category: setups
type: setup
status: full
tags: [ai-3d, setup]
---
# SETUP 44: RODIN / HYPER3D GEN

**ID:** SETUP-44 | **Type:** Image-to-3D | **Difficulty:** ⭐⭐ | **Time:** 25-30 min

> Когда применять: когда нужна быстрая облачная генерация меша по текстовому описанию с последующей чисткой в Blender — и когда хочется делать это прямо из MCP-сессии, а не отдельным HTTP-клиентом.

## 🎯 ЦЕЛЬ

Rodin от Hyper3D — облачный генератор: ключ API, кредиты, очередь заданий. Настраиваем полный цикл через встроенные MCP-инструменты: проверить, что провайдер включён; отправить промпт с необязательным ограничением габаритов; опросить статус; импортировать результат в сцену. Дальше — обязательная чистка: облако возвращает плотный меш с непредсказуемой топологией, и без декаimation, авто-UV и запекания он не годится ни для рендера, ни для игры.

> [!NOTE]
> Имена MCP-тулов, как они выглядят сейчас: `get_hyper3d_status`, `generate_hyper3d_model_via_text`, `poll_rodin_job_status`, `import_generated_asset`. В справочниках проекта встречаются и другие (`create_rodin_job`, `generate_rodin_model`) — это версии постарше. Ориентируйся на свой каталог тулов, а не на архивные страницы.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Аккаунт Hyper3D | — | кредиты и подписка |
| Ключ API | — | авторизация |
| Переменная `BLENDERMCP_HYPER3D_API_KEY` | — | аддон читает её при старте |
| Blender | 4.x LTS | импорт и чистка |
| blender-mcp с Hyper3D-инструментами | текущий | весь цикл |
| Спрайт нормалей | — | запечь после ремеша |

## 🛠️ НАСТРОЙКА

### 1. Ключ в окружении аддона

```python
import os
# Аддон читает ключ из окружения при старте Blender. Проверяем, что он есть —
# иначе get_hyper3d_status вернёт «disabled».
print("BLENDERMCP_HYPER3D_API_KEY:", "set" if os.environ.get("BLENDERMCP_HYPER3D_API_KEY") else "missing")
```

> [!NOTE]
> `BLENDERMCP_HYPER3D_API_KEY` — имя из документации проекта. Если MCP-сервер запускается не из того окружения, где ты её задал, аддон её не увидит. Ключ можно занести и в настройки аддона в UI — проверь оба пути.

### 2. Проверка провайдера

```python
# Вызов в MCP-сессии:
# get_hyper3d_status()
# Возвращает, включён ли провайдер и есть ли ключ. Пока здесь disabled —
# все шаги дальше вернут ошибку авторизации.
```

### 3. Отправляем промпт

```python
# generate_hyper3d_model_via_text(text_prompt="...", bbox_condition=[...])
# 1) Минимальный вызов:
#    generate_hyper3d_model_via_text(text_prompt="weathered stone garden gnome holding a lantern")
# 2) С ограничением габаритов — чтобы объект не вылез за пропорции:
#    generate_hyper3d_model_via_text(text_prompt="low poly wooden crate",
#                                    bbox_condition=[-0.5, -0.5, 0.0, 0.5, 0.5, 1.0])
```

> [!NOTE]
> `bbox_condition` — массив из шести чисел, и это **единственное**, что я не могу описать точно: непонятно, это ли центр+размер или минимум+максимум, и в каких единицах. Проверь в документации Hyper3D, прежде чем полагаться на масштаб. Как ограничение габаритов он очевидно полезен: без него модель приходит в произвольном масштабе.

### 4. Опрос статуса

```python
# poll_rodin_job_status(request_id="...")
# Поля: subscription_key (опционально), request_id.
# Возвращает статус и прогресс; пока не терминальное состояние — жди и опрашивай снова.
```

```text
Ожидаемые состояния по ходу жизни задания (смысл, не точные строки):
  queued / running   -> задание в работе, ждём
  succeeded         -> готово, можно импортировать
  failed            -> смотрим текст ошибки в ответе
```

> [!NOTE]
> Точные строковые значения статусов не привожу: набор различается между сборками. Смотри на поле `status` в фактическом ответе `poll_rodin_job_status` и сравнивай с тем, что вернул предыдущий опрос.

### 5. Импорт результата

```python
# import_generated_asset(name="RodinGnome", request_id="...")
# Дополнительно доступен параметр task_uuid — заполняй его, если он есть в ответе:
# import_generated_asset(name="RodinGnome", request_id="...", task_uuid="...")
```

### 6. Чистка меша: декаimация

```python
import bpy

obj = bpy.data.objects.get("RodinGnome") or bpy.data.collections["AI3D"].objects[0]
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj)

print("до:", len(obj.data.polygons), "полигонов")

dec = obj.modifiers.new("Decimate", "DECIMATE")
# ratio считается от текущей плотности, а не задаёт целевое число
current = len(obj.data.polygons)
target = 15000
dec.ratio = max(0.0, min(1.0, target / current))

# Subdivision обратно сглаживает то, что декаimation сломала
sub = obj.modifiers.new("Subdiv", "SUBSURF")
sub.levels, sub.render_levels = 1, 2
print("ratio:", dec.ratio, "| целевой бюджет:", target)
```

### 7. Авто-UV и запекание нормалей

```python
import bpy

bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.uv.smart_project(angle_limit=1.15192, island_margin=0.02)   # ~66 градусов
bpy.ops.object.mode_set(mode="OBJECT")
print("UV islands:", len(obj.data.uv_layers))

# Запекаем нормали, чтобы они не ездили после изменения топологии
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.context.view_layer.objects.active.data.use_auto_smooth = True   # если есть в версии
bpy.ops.object.bake(type="NORMAL", margin=8, use_clear=True)
print("bake done")
```

> [!NOTE]
> Поле `use_auto_smooth` на меш-данных удаляли в 4.1 вместе с переездом на шейдерные углы. Перед вызовом проверь: `hasattr(obj.data, "use_auto_smooth")`, иначе пропусти строку и полагайся на `shade_smooth_by_angle` / `bpy.ops.object.modifier_add(type="NODES")` с модификатором Smooth by Angle.

### 8. Масштаб и посадка на сцену

```python
import bpy
from mathutils import Vector

bpy.context.view_layer.update()
if obj.dimensions.z > 0:
    s = 0.6 / obj.dimensions.z
    obj.scale = (s, s, s)
bpy.context.view_layer.update()
ground_z = min((obj.matrix_world @ Vector(c)).z for c in obj.bound_box)
obj.location.z -= ground_z
print("посажено на Z=0, итог:", tuple(round(v, 3) for v in obj.dimensions))
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Проверить, что аддон видит ключ, до того как ждать ошибку от облака
echo $env:BLENDERMCP_HYPER3D_API_KEY | cut -c1-6
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `text_prompt` | конкретный объект + материал + стиль | «красивый проп» не работает, детализация важнее |
| `bbox_condition` | 6 чисел | ограничить габарит; точный формат уточнить в документации |
| `name` в `import_generated_asset` | `Rodin<Что>` | имя попадёт в сцену и в Outliner |
| `task_uuid` | из ответа задания | заполняй, если поле есть — иначе импорт может не найти результат |
| `dec.ratio` | `target / current` | пересчитывай после каждой новой генерации |
| `smart_project angle_limit` | `1.15192` рад (~66°) | меньше — больше швов на сгибах |
| `bake margin` | `8` px | увеличивай, если по краям UV видны артефакты |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| `get_hyper3d_status` = disabled | ключ не виден аддону | проверь `BLENDERMCP_HYPER3D_API_KEY` в окружении сервера, перезапусти Blender |
| Ошибка авторизации при отправке | ключ неверный или истёк | перевыпусти на hyper3d.ai |
| `poll` возвращает 404 по id | перепутан `request_id` и `task_uuid` | сверь поля в ответе на отправку |
| Задание `failed` без текста | в ответе ошибка в другом поле | напечатай полный ответ, а не только `status` |
| Модель в 100 раз больше сцены | не сработал `bbox_condition` / нет нормализации | прогони шаг 8 |
| После декаимации кашица | слишком агрессивный `ratio` | подними ratio до 0.6-0.8, добавь Subdivision |
| Нормали «плывут» после правки | не запечены | `bpy.ops.object.bake(type="NORMAL")` |
| `use_auto_smooth` не существует | версия 4.1+ | проверь `hasattr` и используй Smooth by Angle |
| Текстуры не на месте | GLB без встроенных карт | импортируй карты отдельными файлами |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 42: TRIPO AI API](setup_42_tripo_ai_api.md), [SETUP 43: MESHY API V4](setup_43_meshy_api_v4.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 46: SHAP-E / POINT-E LOCAL](setup_46_shap_e_local.md), [SETUP 47: ZERO123 / INSTANTMESH](setup_47_zero123_instantmesh.md)
- **По темам:** [SETUP 48: GAUSSIAN SPLATTING → BLENDER](setup_48_gaussian_splatting.md), [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md)
- **Теги:** #ai-3d, #setup
