---
id: setup_59_web_viewer_export
lang: ru
category: setups
type: setup
status: full
tags: [pipeline, setup, web]
---
# SETUP 59: WEB VIEWER EXPORT

**ID:** SETUP-59 | **Type:** Web 3D | **Difficulty:** ⭐⭐ | **Time:** 20 min
**RU/EN Bilingual**

> Когда применять: когда модель из Blender нужно показать на сайте — в
> презентации, в портфолио, в документации.

---

## 🎯 ЦЕЛЬ

Собрать минимальный веб-вьювер: GLB с компрессией Draco, локальный сервер для
проверки, статическая публикация на GitHub Pages.

Важное уточнение, проверенное на Blender 5.2.1: **встроенный glTF-экспортёр не
умеет KTX2**. Перечисление `export_image_format` там ровно
`AUTO, JPEG, WEBP, NONE`. KTX2 — это отдельный пост-проход.

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Blender | 5.x (проверено 5.2.1) | glTF-экспорт с Draco и WebP |
| three.js | актуальный релиз | Лоадер и рендер в браузере |
| Локальный HTTP-сервер | любой (`python -m http.server`) | Проверка до публикации |
| glTF-Transform | по необходимости | Пост-оптимизация и KTX2 |
| GitHub Pages | бесплатный тариф | Хостинг статики |

---

## 🛠️ НАСТРОЙКА

### 1. Подготовить сцену

```python
# prepare_viewer.py — перед экспортом: без applied-модификаторов и мусора.
import bpy

sc = bpy.context.scene
sc.unit_settings.system = 'METRIC'
sc.unit_settings.scale_length = 1.0        # glTF ждёт метры

# Ограничить то, что поедет на сайт: свет внутри glTF — отдельная история,
# лучше оставить свет на стороне viewer'а.
for ob in sc.objects:
    if ob.type not in {'MESH', 'EMPTY', 'ARMATURE', 'CAMERA'}:
        ob.hide_viewport = True
```

### 2. Экспортировать GLB

```python
# export_viewer.py — все параметры проверены вызовом в Blender 5.2.1.
import bpy

bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.context.scene.objects:
    if ob.type in {'MESH', 'EMPTY'}:
        ob.select_set(True)
bpy.context.view_layer.objects.active = bpy.context.view_layer.objects.active

bpy.ops.export_scene.gltf(
    filepath="//web/viewer.glb",
    export_format='GLB',                       # встроенный .glb, не .gltf + буфер
    use_selection=True,
    export_apply=True,                         # применить модификаторы в экспорт
    export_yup=True,                           # glTF: +Y вверх, Blender: +Z
    export_materials='EXPORT',                 # EXPORT / PLACEHOLDER / VIEWPORT / NONE
    export_image_format='WEBP',                # AUTO / JPEG / WEBP / NONE — KTX2 тут нет
    export_image_quality=80,
    export_draco_mesh_compression_enable=True,
    export_draco_mesh_compression_level=6,     # целое 0..10, 6 — разумный компромисс
    export_texture_dir="//web/textures",       # текстуры рядом, а не внутри GLB
)
```

Проверить, что файл действительно стал меньше и что текстуры на месте:

```bash
ls -lh web/viewer.glb web/textures/
python -c "import json,sys;print(open('web/viewer.glb','rb').read(4))"   # должно быть 'glTF'
```

`glTF` в первых четырёх байтах — самая дешёвая проверка, что это не HTML
страницы ошибки, скачанная под именем `.glb`.

### 3. Альтернатива Draco — Meshopt

```python
# meshopt сжимает лучше Draco, но требует декодера на стороне браузера.
bpy.ops.export_scene.gltf(
    filepath="//web/viewer_meshopt.glb",
    export_format='GLB',
    export_apply=True,
    export_meshopt_compression_enable=True,     # проверенный параметр в 5.2
    export_image_format='WEBP',
)
```

### 4. KTX2 как пост-проход

```bash
# KTX2 делается после экспорта Blender'ом — в самом экспортёре такой опции нет.
# Инструменты: KTX-Software (toktx) либо glTF-Transform.
# Точные ключи проверяйте в --help своих версий.
npx @gltf-transform/cli optimize web/viewer.glb web/viewer.opt.glb --texture-compress webp
```

> [!NOTE]
> Имена подкоманд и флагов glTF-Transform менялись между мажорными версиями
> (команда `optimize` и параметры текстур особенно). Сверяйтесь с
> `npx @gltf-transform/cli --help` и не принимайте эту строку за
> гарантированно рабочую. KTX2-энкодер (KTX-Software) ставится отдельно:
> https://github.com/KhronosGroup/KTX-Software

### 5. Страница вьювера

```html
<!-- web/index.html -->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Viewer</title>
  <style>html,body{margin:0;height:100%}canvas{display:block}</style>
</head>
<body>
<script type="importmap">
{
  "imports": {
    "three": "https://unpkg.com/three/build/three.module.js",
    "three/addons/": "https://unpkg.com/three/examples/jsm/"
  }
}
</script>
<script type="module">
import * as THREE from 'three';
import { GLTFLoader }    from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader }   from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);

const scene  = new THREE.Scene();
scene.background = new THREE.Color(0x111317);
const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.1, 100);
camera.position.set(1.6, 1.4, 2.4);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

scene.add(new THREE.HemisphereLight(0xffffff, 0x20242a, 2.0));
const key = new THREE.DirectionalLight(0xffffff, 2.0);
key.position.set(3, 5, 4);
scene.add(key);

const draco = new DRACOLoader();
draco.setDecoderPath('vendor/draco/');   // файлы декодера — С ТОГО ЖЕ origin
const loader = new GLTFLoader();
loader.setDRACOLoader(draco);

loader.load('viewer.glb',
  (gltf) => {
    const box = new THREE.Box3().setFromObject(gltf.scene);
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());
    gltf.scene.position.sub(center);
    camera.position.set(size.x * 1.6, size.y * 1.4, size.z * 2.0);
    scene.add(gltf.scene);
    console.log('size', size.toArray().map(n => n.toFixed(3)));
  },
  (e) => console.log('progress', e.loaded / e.total),
  (err) => console.error('load failed', err));

renderer.setAnimationLoop(() => {
  controls.update();
  renderer.render(scene, camera);
});
</script>
</body>
</html>
```

### 6. Проверить локально и поставить бюджет размера

Открывать `index.html` двойным кликом нельзя: браузер запрещает загрузку модулей и
fetch с `file://`. Нужен сервер — это не формальность, а причина «пустого экрана».

```bash
cd web
python -m http.server 8000
# затем http://localhost:8000/ и вкладка Network в devtools
```

| Модель | Размер | Способ | Примечание |
|---|---|---|---|
| 1–3 тыс. треугольников | 200–600 КБ | без сжатия | Достаточно лоу-поли, ничего не нужно |
| 5–20 тыс. | 1–4 МБ | Draco | Бюджет: под 5 МБ на модель |
| 20–100 тыс. | 4–15 МБ | Draco + WebP + KTX2 | KTX2 заметно жмёт текстуры |
| > 100 тыс. | > 15 МБ | не грузить в браузер | Ссылка на демо-рендер или онлайн-просмотрщик |

### 7. Опубликовать

```yaml
# .github/workflows/pages.yml
name: Deploy viewer to Pages
on:
  push:
    paths: ['web/**', '.github/workflows/pages.yml']
permissions:
  contents: read
  pages: write
  id-token: write
concurrency:
  group: pages
  cancel-in-progress: true
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: web
      - id: deploy
        uses: actions/deploy-pages@v4
```

> [!NOTE]
> Версии actions (`@v4`, `@v5`, `@v3`) меняются; сверьтесь с текущими
> релизами в документации GitHub Actions. Альтернатива без экшенов —
> ветка `gh-pages` и `git push --force origin gh-pages`.

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Проверка, что GLB — валидный, а не HTML-страница ошибки
python - <<'PY'
from pathlib import Path
p = Path("web/viewer.glb")
head = p.read_bytes()[:4]
print("magic:", head, "OK" if head == b"glTF" else "НЕ GLB", p.stat().st_size // 1024, "KB")
PY
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `export_image_format` | `WEBP` | `AUTO` — если часть текстур с альфой ломается |
| `export_draco_mesh_compression_level` | `6` | Больше — меньше файл, дольше распаковка на клиенте |
| `export_apply` | `True` | Модификаторы применятся только к экспорту, сцена останется живой |
| `export_texture_dir` | отдельная папка | Для кеширования текстур отдельно от модели |
| `unit_settings.scale_length` | `1.0` | Иначе модель приедет в сантиметрах и станет «игрушечной» |
| Draco decoder path | тот же origin | Иначе CORS-ошибка и пустой экран без внятного сообщения |

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Чёрный экран, в консоли ошибка импорта | Открыт `file://`, а не http | Поднять `python -m http.server` |
| `RuntimeError: Failed to fetch` на декодере | Декодер Draco лежит на другом домене | Положить `draco/` рядом со страницей и задать `setDecoderPath` |
| Модель в 100 раз меньше ожидаемого | Сцена в сантиметрах при экспорте в метры | `unit_settings.scale_length = 1.0`, объекты в метрах |
| Текстуры чёрные | Нет света во вьювере либо слишком яркий WebP | Добавить свет в сцену three.js; проверить альфу |
| KTX2 не появился | Встроенный экспортёр его не поддерживает | Пост-проход через KTX-Software / glTF-Transform |
| Модель «мигает» | `use_selection=True`, а выбор менялся | Экспортировать из чистой копии сцены |
| Анимация не играет | `export_animations` выключен | Включить `export_animations=True` и проверить `export_animation_mode` |
| Страница не обновилась после правки | Кеш CDN | Версия файла в имени или `?v=<дата>` |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 08: ASSET PIPELINE](setup_08_asset_pipeline.md), [SETUP 14: BLENDER + GODOT PIPELINE](setup_14_godot_pipeline.md), [SETUP 38: FAB.COM (EPIC) PIPELINE](setup_38_fab_epic.md), [SETUP 45: HUNYUAN3D 2.1 LOCAL](setup_45_hunyuan3d_21.md), [SETUP 49: FFMPEG + VSE PIPELINE](setup_49_ffmpeg_vse_pipeline.md)
- **По темам:** [P39: EXPORT PRESETS (GLB/FBX/USD)](../prompts/39_export_presets.md), [SETUP 55: AI UPSCALE PIPELINE](setup_55_ai_upscale_pipeline.md), [CASE 02: GAME PROPS PIPELINE](../cases/case_02_game_props.md)
- **Теги:** #pipeline, #setup, #web
