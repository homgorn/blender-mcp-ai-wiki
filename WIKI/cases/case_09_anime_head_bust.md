---
id: case_09_anime_head_bust
lang: ru
category: cases
type: case
status: full
tags: [case, stylized]
---
# CASE 09: ANIME HEAD BUST

**ID:** CASE-09 | **Type:** Character | **Difficulty:** ⭐⭐⭐
**RU/EN Bilingual**

> Когда применять: когда нужен стилизованный аниме-бюст: крупный план головы с toon-шейдером, контуром и набором shape keys для мимики — для портрета, рекламной иллюстрации или ассета для игры.

## 🎯 ЦЕЛЬ

Бюст головы в аниме-пропорциях, toon-шейдер с двух-трёхступенчатым светом, контур линией и мимикой на shape keys, пригодный для рендера в 3/4 ракурсе.

## 🧭 ИСХОДНАЯ ЗАДАЧА И ОГРАНИЧЕНИЯ

**Задача:** портретный бюст для ключевого визуала, который должен читаться в маленьком размере (иконка профиля) и в большом (постер).

**Ограничения, которые определили решение:**

- Стиль — аниме: укрупнённые глаза, маленький нос и подбородок, 6 голов в полный рост, для бюста — примерно 2.5–3 головы от макушки до плеч.
- Силуэт важнее деталей: бюст должен читаться чёрным пятном на светлом фоне.
- 3–4 выражения лица, не двадцать. Заявка на «20 shape keys» — это перебор: их невозможно поддерживать и они не читаются в движении.
- Никакой внешней модели лица: голова строится из примитивов и кривых, потому что авторский стиль важнее анатомии.

## 📋 ЧТО ПОНАДОБИТЯ

| Компонент | Версия / состояние | Зачем |
|---|---|---|
| Blender с Cycles или EEVEE | любой | toon-шейдер |
| Freestyle | встроенный, рендер-движок Cycles | контур линией |
| Шрифт без участия | — | подписи не нужны |
| Справочник пропорций | 2D-референсы | контроль пропорций |

## 🛠️ НАСТРОЙКА

### Этап 1. Блокаут по пропорциям

```bash
RU: "Бюст: ширина головы = 1.0, высота от макушки до подбородка = 1.15,
     глаза на линии середины головы, зрачки крупные. Собери сферу + челюсть,
     сплющи затылок, сделай скулы"
EN: "Bust: head width = 1.0, chin-to-crown height = 1.15, eyes on the mid-line,
     large irises. Build sphere + jaw, flatten the back of the skull, add cheekbones"
```

Голова — это не сфера. Аниме-голова: широкая сверху, узкая книзу, затылок уплощённый.

```python
import bpy, math

bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=1.0)
head = bpy.context.active_object
head.name = "Head"
for v in head.data.vertices:
    if v.co.z < 0:                       # низ — подбородок: сужаем и вытягиваем
        k = 1.0 - abs(v.co.z) * 0.45
        v.co.x *= k
        v.co.z *= 1.15
    if v.co.y > 0.35:                    # затылок: чуть сплющиваем
        v.co.y *= 0.82
    v.co.x *= 1.02                       # лоб и скулы чуть шире низа

bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
for p in head.data.polygons:
    p.use_smooth = True
```

### Этап 2. Глаза, брови, нос, рот — отдельными объектами

```python
import bpy

def ellipse(name, rx, ry, depth, loc, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0,
                                         location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = (rx, depth, ry)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.data.materials.append(mat)
    return ob

m_skin  = bpy.data.materials.new("M_Skin")
m_eye   = bpy.data.materials.new("M_Eye")
m_iris  = bpy.data.materials.new("M_Iris")
m_hair  = bpy.data.materials.new("M_Hair")

# глаз: белок, радужка, зрачок, блик — 4 слоя, каждый своей геометрией
eye_r = ellipse("Eye_R_White", 0.150, 0.105, 0.030, (-0.22, -0.62, 0.10), m_eye)
iris  = ellipse("Eye_R_Iris",  0.095, 0.100, 0.020, (-0.24, -0.645, 0.10), m_iris)
pup   = ellipse("Eye_R_Pupil", 0.042, 0.052, 0.014, (-0.24, -0.660, 0.10), m_hair)
glint = ellipse("Eye_R_Glint", 0.022, 0.022, 0.010, (-0.28, -0.665, 0.145), m_hair)

# зрачок и радужка смотрят на камеру, а не в -Y: поворачиваем глаз к зрителю
import math
for ob in (iris, pup, glint):
    ob.rotation_euler = (0, math.radians(14), 0)

> [!NOTE]
> Касательно «пропорций аниме-головы»: числа выше (высота головы 1.15 при ширине 1.0, глаза на середине головы) — общее описание стилистики, а не измеренный канон. У конкретных авторов и жанров соотношения отличаются. Если нужен конкретный референс, бери его пропорции, а не эти цифры.

bpy.ops.object.text_add(location=(0, -0.60, -0.30))   # рот-заглушка, дальше кривой
mouth = bpy.context.active_object
mouth.data.body = ""
bpy.data.objects.remove(mouth, do_unlink=True)
```

Волосы — отдельный объём: в toon-рендере они читаются силуэтом, а не деталями.

```python
import bpy, math
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.06,
                                     location=(0, 0.10, 0.06))
hair = bpy.context.active_object
hair.name = "Hair_Shell"
for v in hair.data.vertices:
    if v.co.z < 0.05:                                  # срез низа: убираем то, что внутри головы
        v.co.z = max(v.co.z, -0.02)
        v.co.x *= 1.05
        v.co.y *= 1.05
hair.data.materials.append(m_hair)
bpy.ops.object.modifier_add(type='SOLIDIFY')
hair.modifiers["Solidify"].thickness = 0.06
```

### Этап 3. Toon-шейдер: диффузия → цветовая шкала → эмиссия

Классический cel-шейдер: диффузия не показывается напрямую, её яркость проходит через `ColorRamp` с интерполяцией `Constant` — получаются 2–3 дискретных тона. Второй слой от `Layer Weight` даёт обводку по контуру ракурса.

```python
import bpy

def toon_material(name, base, steps=3, rim=(1, 1, 1), rim_power=2.5, rim_strength=0.6):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")

    diff = nt.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs['Color'].default_value = (1, 1, 1, 1)

    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = 'CONSTANT'
    dark = tuple(c * 0.55 for c in base)
    light = tuple(min(1.0, c * 1.08) for c in base)
    cr.elements[0].position = 0.0
    cr.elements[0].color = (*dark, 1)
    cr.elements[1].position = 0.42 if steps > 2 else 0.5
    cr.elements[1].color = (*base, 1)
    if steps > 2:
        for pos, col in ((0.72, light), (0.92, light)):
            cr.elements.new(pos).color = (*col, 1)

    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs['Strength'].default_value = 1.0

    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs['Blend'].default_value = 0.35
    rim_ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr2 = rim_ramp.color_ramp
    cr2.elements[0].position = 0.0
    cr2.elements[0].color = (0, 0, 0, 1)
    cr2.elements[1].position = 1.0 - (1.0 - rim_power / 10.0)
    cr2.elements[1].color = (*rim, 1)
    rim_em = nt.nodes.new("ShaderNodeEmission")
    rim_em.inputs['Strength'].default_value = rim_strength

    mix = nt.nodes.new("ShaderNodeMixShader")
    add = nt.nodes.new("ShaderNodeAddShader")

    nt.links.new(diff.outputs['BSDF'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], em.inputs['Color'])
    nt.links.new(lw.outputs['Fresnel'], rim_ramp.inputs['Fac'])
    nt.links.new(rim_ramp.outputs['Color'], rim_em.inputs['Color'])
    nt.links.new(em.outputs['Emission'], mix.inputs[1])
    nt.links.new(rim_em.outputs['Emission'], mix.inputs[2])
    nt.links.new(mix.outputs['Shader'], add.inputs[0])
    nt.links.new(add.outputs['Shader'], out.inputs['Surface'])
    return mat

> [!NOTE]
> Набор выходов ноды `Layer Weight` стабилен (`Fresnel`, `Facing`), но конкретное поведение `Facing` как маски зависит от настроек ноды и версии. Если контурный свет ложится не туда — крути `Blend` и смотри результат, а не догадывайся о формуле. Имена сокетов Principled BSDF не используются в toon-цепочке намеренно: у неё нет ни одного Principled, поэтому расхождения версий её не касаются.

bpy.data.materials["M_Skin"] = toon_material("M_Skin", (1.0, 0.86, 0.78), steps=3,
                                             rim=(1, 0.85, 0.85), rim_strength=0.5)
bpy.data.materials["M_Hair"] = toon_material("M_Hair", (0.22, 0.16, 0.28), steps=2,
                                             rim=(0.7, 0.8, 1.0), rim_strength=1.1)
bpy.data.materials["M_Eye"]  = toon_material("M_Eye",  (0.98, 0.98, 1.0), steps=2, rim_strength=0.2)
```

### Этап 4. Контур линией: Freestyle

```python
import bpy
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.render.use_freestyle = True
vl = sc.view_layers[0]
vl.use_freestyle = True
fs = vl.freestyle_settings
lines = fs.linesets[0] if len(fs.linesets) else fs.linesets.new("Main")
lines.select_silhouette = True
lines.select_border = True
lines.select_crease = False           # crease-контур на глазах превращается в кашу
ls = lines.linestyle
ls.color = (0.06, 0.05, 0.08)
ls.thickness = 1.8
if hasattr(fs, "crease_angle"):
    fs.crease_angle = math.radians(134)
```

> [!NOTE]
> Freestyle — отдельный проход рендера, он есть только в Cycles и только при финальном рендере: ни в EEVEE, ни во вьюпорте его не видно. Поэтому toon-сцену с Freestyle приходится считать заметно дольше. На этапе подбора формы контур лучше рисовать кривыми вручную, а Freestyle включать на финальных прогонах.
>
> Точное имя свойства порога угла на линиях (`crease_angle`) и его расположение менялись между версиями — код выше проверяет наличие поля через `hasattr` вместо того, чтобы гадать. Если поля нет, порог задаётся в самом наборе линий, а не в настройках Freestyle.

### Этап 5. Мимика: 4 shape keys, а не 20

```python
import bpy, math

head = bpy.data.objects["Head"]
basis = head.shape_key_add(name="Basis", from_mix=False)

def make_key(obj, name, deform):
    k = obj.shape_key_add(name=name, from_mix=False)
    deform(k)
    k.value = 0.0
    k.slider_min, k.slider_max = 0.0, 1.0
    return k

def z_of(k, limit):
    zs = [p.co.z for p in k.data if p.co.z < limit]
    return sum(zs) / max(len(zs), 1)

def blink(k):
    zmax = max(p.co.z for p in k.data)
    for p in k.data:
        if p.co.z > zmax - 0.12:           # веки: верхняя треть глаза
            p.co.z -= (p.co.z - (zmax - 0.12)) * 0.9
            p.co.y -= 0.015

def smile(k):
    for p in k.data:
        if p.co.y < -0.5 and -0.30 < p.co.z < -0.18:   # область рта
            p.co.z += 0.02
            p.co.x *= 1.05

def wide_eyes(k):
    for p in k.data:
        if -0.25 < p.co.z < 0.25 and p.co.y < -0.5:
            p.co.y -= 0.02
            p.co.z *= 1.08

def squint(k):
    for p in k.data:
        if -0.25 < p.co.z < 0.25 and p.co.y < -0.5:
            p.co.z *= 0.88
            p.co.y += 0.012

for fn in (blink, smile, wide_eyes, squint):
    make_key(head, fn.__name__, fn)

keys = bpy.data.objects["Head"].data.shape_keys.key_blocks
print("shape keys:", [k.name for k in keys])
```

Проверка: каждая форма должна читаться **силуэтом**, иначе в аниме это не работает.

```python
import bpy
sc = bpy.context.scene
for i, name in enumerate(("Basis", "blink", "smile", "wide_eyes", "squint")):
    kb = bpy.data.objects["Head"].data.shape_keys.key_blocks[name]
    kb.value = 1.0 if name != "Basis" else 0.0
    sc.frame_set(sc.frame_start + i)
    sc.render.filepath = f"//renders/face_{name}.png"
    sc.render.resolution_x = sc.render.resolution_y = 800
    bpy.ops.render.render(write_still=True)
    kb.value = 0.0
```

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `ColorRamp.interpolation` | `'CONSTANT'` | ровно это даёт дискретные тона; `LINEAR` — градиент, а не cel-шейдер |
| `Layer Weight.Blend` | 0.3–0.4 | толщина контурного света |
| `rim_emission.Strength` | 0.4–1.2 | слишком сильный rim «обжигает» силуэт |
| `linestyle.thickness` | 1.5–2.5 px | зависит от разрешения кадра |
| `select_crease` | `False` | crease-контур на сферических глазах даёт сетку линий |
| `crease_angle` | ~134° | порог, выше которого ребро считается «сгибом» |

## ⚠️ ЧТО ПОШЛО НЕ ТАК

**1. Глаза из сфер выглядели стеклянными пуговицами.** Первая версия — четыре эллипсоида на глаз — в рендере читалась как наклеенные шарики: specular от toon-шейдера давал отдельный блик на каждом слое, и радужка «плавала» над белком. Помогло два изменения: убрать Specular у toon-материала вообще (для cel-шейдера он не нужен и всегда мешает) и посадить радужку глубже — `y` на 0.02 ближе к лицу, а не на 0.03 наружу. После этого глаз стал плоским и читался правильно.

**2. Тонирование кожи уходило в «серый пластик».** Раньше в toon-материале оставался Principled BSDF как база, и свет от реальных ламп смешивался с эмиссией из ColorRamp. Результат: в тенях кожа была серой, потому что тень от лампы перемножилась на цвет из шкалы. Пришлось убрать Principled целиком и оставить чистую цепочку Diffuse → ColorRamp → Emission. После этого тон стабилен при любом освещении.

**3. Заявленные 20 shape keys упёрлись в поддержку.** Первые 12 выражений делались «на глаз», и после правки сетки четыре из них ломались: при подвижке вершин деформация в районе рта съезжала на щеку. Пришлось ограничиться 4 базовыми формами и ограничить зону деформации по Z. Оставшиеся «выражения» собираются как комбинация этих четырёх — этого хватает для мигания и смены эмоции.

## 📊 ЧТО ПОЛУЧИЛОСЬ

Ниже — **оценка по порядку величины, а не измеренный рендер**. Число полигонов посчитано арифметикой от известной сложности примитивов (UV-сфера 48×24 — около 2.3 тыс. квадов, `subdivisions=3` — около 1280 треугольников, Solidify удваивает), а не измерением: добавление bevel или смена разрешения сферы меняют результат в разы. Проверяется это единственным способом — пересчётом через `evaluated_depsgraph_get()`, см. WF 19.

- Объектов: 8 (голова, 4 слоя глаза × 2 = 8, волосы, брови) — порядка 12–16 объектов.
- Полигоны: голова ~4.6 тыс. (сфера 48×24), глаз ~1 тыс. на слой, волосы с Solidify — итого **15–30 тыс. треугольников**.
- Материалов: 4 (кожа, волосы, глаз, зрачок), текстур **ноль** — всё наtoon-процедурное.
- Shape keys: 4 (Basis + blink/smile/wide_eyes/squint).
- Рендер 800×800 в Cycles, 64 сэмпла, Freestyle: **секунды**. Эта оценка верна именно для 20 тыс. полигонов: Freestyle — отдельный проход, и его время растёт с числом рёбер быстрее всего остального. На модели в сотню тысяч полигонов тот же контур уже не считается секундами, поэтому для итераций лучше EEVEE без контура.

> [!NOTE]
> Время рендера везде в этой секции — оценка по порядку величины для средней дискретной видеокарты, а не замер. Freestyle добавляет отдельный проход, время которого зависит от числа рёбер сильнее, чем всё остальное вместе взятое, поэтому цифра «секунды» верна только для этой сцены.

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Тона «полосатые» | `ColorRamp` с `LINEAR` вместо `CONSTANT` | интерполяция `CONSTANT` |
| Силуэт не читается | волосы того же тона, что и кожа | hair-шейдер темнее кожи минимум на 40% |
| Контур лезет на глаз | `select_crease` включён | выключить, оставить только silhouette и border |
| Rim «съедает» лицо | слишком сильный `rim_emission` и узкий Layer Weight | снизить strength до ~0.5, поднять Blend |
| Свет затеняет форму | в сцене стоят обычные лампы | для toon рендерить при постоянном `Light Path` / плоском свете |

## ✅ РЕЗУЛЬТАТ

На выходе: `.blend` с бюстом, 4 toon-материала, 4 shape keys, Freestyle-настройка и 5 превью 800×800 (`face_Basis.png` … `face_squint.png`) — базовый ассет, пригодный как для рендера, так и для анимации лица.

## 🔗 WF-07, Setup 01/08, INDEX

---

## 🔗 СВЯЗИ

- **Прочие в категории «Кейсы»:** [CASE 08: SCI-FI CORRIDOR MODULAR](case_08_sci_fi_corridor.md), [CASE 11: COZY ROOM DIORAMA](case_11_cozy_room_diorama.md), [CASE 01: ARCHVIZ INTERIOR](case_01_archviz_interior.md), [CASE 02: GAME PROPS PIPELINE](case_02_game_props.md), [CASE 03: PRODUCT VISUALIZATION](case_03_product_viz.md)
- **По темам:** [CASE 04: CHARACTER RIG & ANIMATION](case_04_character_rig.md), [CASE 05: PROCEDURAL CITY](case_05_procedural_city.md), [CASE 06: ANIMATION LOOP](case_06_animation_loop.md)
- **Теги:** #case, #stylized