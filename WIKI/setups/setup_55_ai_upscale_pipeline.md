---
id: setup_55_ai_upscale_pipeline
lang: ru
category: setups
type: setup
status: full
tags: [pipeline, setup, upscale]
---
# SETUP 55: AI UPSCALE PIPELINE

**ID:** SETUP-55 | **Type:** Upscale | **Difficulty:** ⭐ | **Time:** 15 min
**RU/EN Bilingual**

> Когда применять: когда кадр отрендерен в меньшем разрешении, чем нужно для
> сдачи, — и остался выбор между апскейлом постфактум или повторным рендером.

---

## 🎯 ЦЕЛЬ

Разложить апскейл по полочкам и выбрать правильный инструмент под задачу. Статья
начинается с неприятной правды: **для 3D-рендера AI-апскейл почти всегда хуже,
чем отрендерить в большем разрешении**. Апскейл имеет смысл там, где исходника
больше нет, либо для черновых превью.

Все команды ffmpeg проверены локально на версии 9.0.1.

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 5.x (проверено 5.2.1) | Рендер в большем разрешении — первый и лучший «апскейл» |
| ffmpeg + ffprobe | 7.x+ (проверено 9.0.1) | Честный интерполяционный апскейл, сборка, верификация |
| Real-ESRGAN | см. репозиторий проекта | Нейросетевой апскейл для превью и чужих материалов |
| Cycles denoise | в комплекте Blender | Шум — причина, по которой хотят апскейл |
| Диск | 2× от результата | Мастер не трогаем, работаем на копии |

---

## 🛠️ НАСТРОЙКА

### 1. Сначала — правильная развилка

| Что лежит на входе | Что делать | Почему |
|---|---|---|
| Своя сцена, ещё не отрендерено | Рендерить ×2 по разрешению | Бесплатно, честно, детали настоящие |
| Своя сцена, шумно | Поднять samples + denoise | Шум, а не разрешение, портит картинку |
| Свой рендер, сдавать завтра | Lanczos-апскейл в ffmpeg | Предсказуемо, без галлюцинаций |
| Чужой материал / превью | Real-ESRGAN | Дёшево по времени, качество непредсказуемо |
| Композитинг из 8 слоёв | Апскейлить каждый слой **до** композита | Иначе края разъедутся между слоями |

### 2. Правильный путь: рендер в ×2

```python
# scale_render.py — resolution_percentage вместо ручного пересчёта.
import bpy

sc = bpy.context.scene
sc.render.resolution_percentage = 200      # ровно ×2 к 100%
sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
# → фактический кадр 3840x2160. В панели Render это видно как
#   "Resolution 200%".

# Шум лечится отдельно и почти всегда дешевле, чем лишние пиксели:
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.01
sc.cycles.samples = 256
for vl in sc.view_layers:
    vl.cycles.use_denoising = True        # проверено: реальный флаг во вью-слое
print(sc.render.resolution_x * sc.render.resolution_percentage // 100)
```

> [!NOTE]
> Идентификаторы движка денойзера (`OPENIMAGEDENOISE` / `OPTIX`) в фоне не
> читаются — это динамический enum, и в `blender -b` список приходит пустым
> (проверено на 5.2.1). Выбирайте движок в UI и проверяйте результат, либо
> ставьте флаг `use_denoising = True` и полагайтесь на значение по умолчанию.

### 3. Честный интерполяционный апскейл

```bash
# Lanczos по кадрам. -vf scale с флагом flags=lanczos — это то, чем
# Blender увеличивает текстуру, и не выдумывает детали.
# Проверено на ffmpeg 9.0.1:
ffmpeg -y -framerate 24 -start_number 1 -i render/anim_%04d.png \
  -vf "scale=iw*2:ih*2:flags=lanczos" \
  -c:v libx264 -crf 16 -pix_fmt yuv420p -movflags +faststart \
  delivery/anim_2x.mp4
```

Сначала убедитесь, что вход действительно 1920×1080 — иначе «апскейл ×2» будет
апскейлом с 640×480 и потеря спрячется в этом месте:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=width,height,pix_fmt,r_frame_rate \
  -of default=nw=1 render/anim_0001.png
```

### 4. Нейросетевой апскейл

```bash
# Репозиторий проекта: https://github.com/xinntao/Real-ESRGAN
# Проверьте имена скрипта и ключей в README своей версии:
python inference_realesrgan.py -h

# Типичный вызов для одиночного кадра 2x:
python inference_realesrgan.py -n realesrgan-x4plus -i plate.png -o plate_2x.png -s 2
```

> [!NOTE]
> Точные имена весов (`realesrgan-x4plus`, `-s`, `-i`, `-o`) и требуемая версия
> PyTorch/Torchvision менялись между релизами Real-ESRGAN. Проверяйте
> `inference_realesrgan.py -h` и README — приведённая строка это форма команды,
> а не гарантия, что конкретная версия её примет без правок.

Для последовательности — только батч, по кадру за вызов:

```bash
# Один процесс на кадр. Тяжёлая модель в памяти не держится дольше вызова,
# поэтому параллелизм упирается в RAM, а не в GPU.
for f in render/anim_*.png; do
  python inference_realesrgan.py -n realesrgan-x4plus -i "$f" -o "upscale2x/$(basename "$f")" -s 2
done
```

### 5. Денойз → шарпен → сборка

```bash
# Шарпен умножением, без пересвета: unsharp с amount ниже 1.0
ffmpeg -y -framerate 24 -start_number 1 -i upscale2x/anim_%04d.png \
  -vf "unsharp=5:5:0.4:5:5:0.0" \
  -c:v libx264 -crf 16 -pix_fmt yuv420p -movflags +faststart \
  delivery/anim_final.mp4

# ffprobe — обязательная финальная проверка перед сдачей:
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,pix_fmt \
  -of csv=p=0 delivery/anim_final.mp4
```

### 6. Не тронуть EXR-мастер

```bash
# Последний рубеж: мастер должен остаться нетронутым.
# Проверяем, что апскейлер писал только в delivery/:
ls -la delivery/ master/exr/ | head -20
# и сверяем размеры: мастер не мог измениться
git status --porcelain -- master/     # в git-репозитории
```

Мастер — линейный EXR. Прогоняя его через нейросеть или 8-битный H.264, вы
теряете и HDR-диапазон, и возможность пере-грейдить позже. Апскейл — операция
**на копии под сдачу**, и её результат никогда не поднимается в мастер.

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр | Значение | Когда менять |
|---|---|---|
| `resolution_percentage` | `200` | Вместо увеличения `resolution_x/y` — не расходится с UI |
| `adaptive_threshold` | `0.01` | Шумно — снижать до `0.005`; медленно — поднимать до `0.02` |
| `flags=lanczos` | обязательно | `bilinear` мыльнее, `neighbor` — лестница |
| `-crf` | `16` для сдачи, `23` для превью | Ниже 14 размер растёт неоправданно |
| `-pix_fmt yuv420p` | обязательно | Иначе часть плееров покажет чёрный экран |
| `unsharp` amount | `0.4` | Выше `1.0` появляются ореолы на контрастных краях |
| Мастер EXR | не трогать | Апскейл делается на копии под конкретный формат сдачи |

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Кадры «мягкие» в 2K, хотя рендер был 4K | Вход оказался 960×540 | `ffprobe` на первом кадре **до** апскейла |
| Нейросеть дорисовала лишнее: изменились надписи, узоры | AI-апскейл не выдумывает — он галлюцинирует | Для финальной сдачи — Lanczos, не ESRGAN |
| Ореолы вокруг контрастных краёв | `unsharp` amount > 1.0 | Снизить до `0.3–0.5` или убрать совсем |
| Композитинг развалился: слои разного размера | Апскейлили готовый кадр, а не слои | Апскейлить каждый слой до композита (см. P15) |
| Не открывается в плеере / на площадке | Не задан `-pix_fmt yuv420p` | Добавить флаг, перезалить |
| Ресайз в Batch-рендере проигнорирован | Меняли `resolution_x` после включения пресета | Проверять итог: `resolution_x * resolution_percentage` |
| Шум «уехал» после апскейла | Шум масштабируется вместе с картинкой | Денойз в рендере, а не после увеличения |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 08: ASSET PIPELINE](setup_08_asset_pipeline.md), [SETUP 14: BLENDER + GODOT PIPELINE](setup_14_godot_pipeline.md), [SETUP 38: FAB.COM (EPIC) PIPELINE](setup_38_fab_epic.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 49: FFMPEG + VSE PIPELINE](setup_49_ffmpeg_vse_pipeline.md)
- **По темам:** [SETUP 59: WEB VIEWER EXPORT](setup_59_web_viewer_export.md), [CASE 02: GAME PROPS PIPELINE](../cases/case_02_game_props.md), [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md)
- **Теги:** #pipeline, #setup, #upscale
