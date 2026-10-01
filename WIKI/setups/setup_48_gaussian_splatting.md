---
id: setup_48_gaussian_splatting
lang: ru
category: setups
type: setup
status: full
tags: [ai-3d, blender, setup]
---
# SETUP 48: GAUSSIAN SPLATTING → BLENDER

**ID:** SETUP-48 | **Type:** 3DGS | **Difficulty:** ⭐⭐⭐ | **Time:** 1.5-2 h

> Когда применять: когда есть 3DGS-сцена (.ply на миллион сплатов) и нужно либо посмотреть её, либо частично перенести в Blender. Главное предупреждение сразу: **штатный Blender не рендерит 3DGS**, и миллион гауссианов в сцену не засунуть — дальше решается, что тебе на самом деле нужно.

## 🎯 ЦЕЛЬ

3D Gaussian Splatting хранит сцену как набор анизотропных эллипсоидов с цветом, прозрачностью и ковариациями. Blender про это понятия не имеет: у него полигоны. Поэтому статья разбирает три честных пути: (1) смотреть сплаты во внешнем просмотрщике и композить результат, (2) привести сплаты к мешу специализированным инструментом, (3) построить в Blender инстансированный меш из подмножества сплатов — для отсева фона, кадрирования и анализа, не для финального рендера.

> [!NOTE]
> Про конвертацию в `.mesh` через SuGaR и про веса `.ply` от нейросетевых реконструкций я говорю обобщённо: репозиторий SuGaR (Anttwo) действительно оптимизирует сплаты в меш с нормалями, но конкретные имена его скриптов и флагов я не привожу — сверяй README. Формат самого `.ply` для 3DGS стандартен, и ниже он разобран явно.

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| `numpy` | 1.24+ | разбор `.ply` |
| Blender | 4.x LTS | инстансы и композитинг |
| Просмотрщик сплатов | — | посмотреть сцену целиком (см. шаг 1) |
| 8+ ГБ VRAM | — | если рендеришь через GPU-бэкенд |
| SuGaR (опционально) | — | честная конвертация сплатов в меш |

## 🛠️ НАСТРОЙКА

### 1. Сначала посмотри, не трогая Blender

Прежде чем конвертировать, убедись, что сцена вообще стоит того:

```bash
# Просмотрщик в браузере (PlayCanvas SuperSplat) или десктопный — на твой выбор.
# Суть: открыть .ply и посмотреть ракурсы.
# Суперсплат нужен для инспекции, а не для продакшн-рендера.
echo "scene: C:/assets/gs/scene/point_cloud/iteration_30000/point_cloud.ply"
```

> [!NOTE]
> Не подставляй сюда конкретные URL приложений: набор просмотрщиков меняется, и часть из них живёт как веб-приложения без стабильного API. Практический путь: найди актуальный просмотрщик 3DGS (их несколько, включая браузерные), открой им `.ply`. Ссылку на инструмент бери из репозитория, из которого ты получил `.ply`.

### 2. Читаем `.ply` 3DGS напрямую

Формат — бинарный little-endian PLY, где каждая вершина несёт SH-коэффициенты, логитмасштаб, сигмоид прозрачности и кватернион. Читаем без посредников:

```python
import numpy as np
from pathlib import Path

PLY = Path(r"C:/assets/gs/scene/point_cloud/iteration_30000/point_cloud.ply")

def read_gsplat_ply(path: Path):
    with open(path, "rb") as f:
        header = []
        while True:
            line = f.readline()
            if not line:
                raise ValueError("PLY header not terminated")
            s = line.decode("ascii").strip()
            header.append(s)
            if s == "end_header":
                break
        n, props, in_vertex = 0, [], False
        for s in header[1:]:
            t = s.split()
            if not t:
                continue
            if t[0] == "element":
                in_vertex = t[1] == "vertex"
                if in_vertex:
                    n = int(t[2])
            elif t[0] == "property" and in_vertex:
                props.append(t[-1])
        dtype = np.dtype([(name, "<f4") for name in props])
        return np.fromfile(f, dtype=dtype, count=n)

data = read_gsplat_ply(PLY)
print("сплатов:", len(data), "| полей:", data.dtype.names[:8], "...")
```

> [!NOTE]
> Парсер выше рассчитан на бинарный little-endian PLY, где все вершинные свойства — `float32`. Если попался ASCII-PLY или счётчик граней (`element face`), он не сработает — сначала напечатай первые строки заголовка `print(header)` и адаптируй. Конвертеры, которые пишут сплаты, почти всегда делают бинарный вариант.

### 3. Раскладываем данные в понятные поля

```python
# Константа SH нулевого порядка: 0.5 * sqrt(1/pi)
SH_C0 = 0.28209479177387814

xyz   = np.stack([data["x"], data["y"], data["z"]], axis=1)
rgb   = 0.5 + SH_C0 * np.stack([data["f_dc_0"], data["f_dc_1"], data["f_dc_2"]], axis=1)
alpha = 1.0 / (1.0 + np.exp(-data["opacity"]))          # сигмоид
scale = np.exp(np.stack([data["scale_0"], data["scale_1"], data["scale_2"]], axis=1))
quat  = np.stack([data["rot_0"], data["rot_1"], data["rot_2"], data["rot_3"]], axis=1)

print("bounds:", xyz.min(axis=0).round(2), xyz.max(axis=0).round(2))
print("alpha mean:", float(alpha.mean()), "| scale median:", float(np.median(scale)))
print("прозрачных (a<0.05):", int((alpha < 0.05).sum()))
```

### 4. Отсекаем фон — это главный практический шаг

```python
keep = alpha > 0.05
xyz, rgb, scale, quat = xyz[keep], rgb[keep], scale[keep], quat[keep]
print("после отсева:", len(xyz))

# Дополнительно: отсечь по расстоянию от камеры/центра
center = xyz.mean(axis=0)
radius = np.linalg.norm(xyz - center, axis=1)
keep2 = radius < np.percentile(radius, 98)
xyz, rgb, scale, quat = xyz[keep2], rgb[keep2], scale[keep2], quat[keep2]
print("после отсева по радиусу:", len(xyz), "| центр:", center.round(2))
```

### 5. Строим инстансы в Blender

Один икосфер, миллион связанных копий — Blender не потянет. Работаем с подмножеством в десятки тысяч и режем дальше:

```python
import bpy
from mathutils import Vector, Quaternion

MAX_SPLATS = 30000                     # потолок: выше Blender встанет
sel = np.linspace(0, len(xyz) - 1, min(MAX_SPLATS, len(xyz)), dtype=int)
xyz, rgb, scale, quat = xyz[sel], rgb[sel], scale[sel], quat[sel]

bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0)
proto = bpy.context.object
proto.name = "SplatProto"
proto.data.name = "SplatProtoMesh"

mat = bpy.data.materials.new("SplatColor")
mat.use_nodes = True
nt = mat.node_tree
info = nt.nodes.new("ShaderNodeObjectInfo")     # читает object.color
emiss = nt.nodes.new("ShaderNodeEmission")
out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(info.outputs["Color"], emiss.inputs["Color"])
nt.links.new(emiss.outputs["Emission"], out.inputs["Surface"])
proto.data.materials.append(mat)

print("прототип готов, сплатов к инстансированию:", len(xyz))
```

### 6. Раскладываем инстансы

```python
coll = bpy.data.collections.get("GSPLATS") or bpy.data.collections.new("GSPLATS")
scene_coll = bpy.context.scene.collection
if coll.name not in scene_coll.children:
    scene_coll.children.link(coll)

for i in range(len(xyz)):
    dup = bpy.data.objects.new(f"s_{i:06d}", proto.data)   # shared mesh = дёшево по памяти
    coll.objects.link(dup)
    p = xyz[i]
    dup.location = (float(p[0]), float(p[1]), float(p[2]))
    dup.rotation_mode = "QUATERNION"
    # в .ply порядок кватерниона (w, x, y, z)
    dup.rotation_quaternion = Quaternion((float(quat[i][0]), float(quat[i][1]),
                                          float(quat[i][2]), float(quat[i][3])))
    s = scale[i]
    dup.scale = (float(s[0]), float(s[1]), float(s[2]))
    c = np.clip(rgb[i], 0.0, 1.0)
    dup.color = (float(c[0]), float(c[1]), float(c[2]), 1.0)

print("инстансов:", len(coll.objects))
```

> [!NOTE]
> Это **визуализация**, а не рендер сплатов: у эллипсоидов нет анизотропного сплаттинга и альфа-смешивания, поэтому картинка будет грубой. Зато видно форму, отсеивается фон и можно работать с камерой. Для финального изображения нужен нормальный просмотрщик сплатов.

### 7. Экспорт подмножества в обычный меш

```python
# Из инстансов можно получить обычный меш: объединяем и применяем модификаторы
bpy.ops.object.select_all(action="DESELECT")
for o in bpy.data.collections["GSPLATS"].objects:
    o.select_set(True)
bpy.context.view_layer.objects.active = proto
bpy.ops.object.join()
merged = bpy.context.object
merged.name = "GSplatMesh"
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Разумный полигон-бюджет: 30k сплатов по ~80 граней — это уже миллионы
dec = merged.modifiers.new("Decimate", "DECIMATE")
dec.ratio = 0.01
bpy.ops.object.modifier_apply(modifier=dec.name)
print("после объединения:", len(merged.data.polygons), "полигонов")
```

### 8. Честная конвертация через SuGaR

```bash
# Репозиторий SuGaR оптимизирует сплаты в меш с нормалями — это настоящая конвертация,
# а не инстансинг. Клонируй, ставь по README, имя скрипта и флаги смотри там.
git clone https://github.com/Anttwo/SuGaR.git
```

> [!NOTE]
> Внутренние имена скриптов SuGaR и набор флагов я не привожу: они менялись, а выдуманная команда хуже отсутствующей. Открой README репозитория и следуй описанному там запуску. Главное, что стоит запомнить: результат SuGaR — обычный меш, пригодный для рендера в Blender.

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Сколько сплатов в сцене — печатаем, а не гадаем
python -c "import numpy as np;from pathlib import Path;p=Path(r'C:/assets/gs/point_cloud.ply');d=p.read_bytes();print('size MB:', round(len(d)/2**20,1))"
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `MAX_SPLATS` | `30000` | выше — Blender начнёт тормозить и падать |
| порог `alpha` | `0.05` | выше — чище фон, теряются полупрозрачные детали |
| отсев по радиусу | `98` перцентиль | обрезает «хвосты» на краях сцены |
| `SH_C0` | `0.28209479177387814` | константа, не параметр |
| `subdivisions` прототипа | `1` | `2` — глаже, но втрое больше граней |
| `dec.ratio` при join | `0.01` | подбирай под бюджет полигонов |
| пропорции сплата | прямо из `exp(scale_*)` | не подгоняй вручную — иначе потеряется форма |

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| PLY не читается, 0 вершин | ASCII-PLY или не тот формат | напечатай `print(header)`, проверь `format binary_little_endian` |
| Цвета «кислотные» | не применил формулу SH→RGB | `rgb = 0.5 + SH_C0 * f_dc`, а не сырое `f_dc` |
| Всё прозрачное | забыт сигмоид на прозрачности | `alpha = sigmoid(opacity)` |
| Blender зависает при скрипте | слишком много объектов | срежь `MAX_SPLATS` до 10-20k |
| Один сплат = гигантский эллипсоид | не применил `exp()` к scale | хранится логитм, в сцену идёт экспонента |
| Повёрнутые сплаты «не туда» | порядок кватерниона | в 3DGS `rot_*` = (w, x, y, z) |
| Текстуры на месте, объект не видно | меши связаны, но материал не задан | `ShaderNodeObjectInfo → Color` в Emission |
| `.ply` весит 4 ГБ, RAM не хватает | читаешь всё в память | читай подмножество: сдвиг в заголовке + `np.fromfile(offset=...)` |
| Хочу финальный рендер из Blender | сплаты не рендерятся нативно | SuGaR-конвертация или рендер во внешнем просмотрщике |

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md), [SETUP 09: BLENDERBOT / AI CODING AGENT](setup_09_blenderbot_ai.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 10: BLENDER + COMPOSITING (NUKE/AFTER EFFECTS ROUNDTRIP)](setup_10_compositing_roundtrip.md), [SETUP 11: BLENDER + TOUCHDESIGNER REALTIME VISUALS](setup_11_touchdesigner.md)
- **Теги:** #ai-3d, #blender, #setup
