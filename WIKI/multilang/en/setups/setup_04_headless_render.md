---
id: setup_04_headless_render
lang: en
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# SETUP 04: HEADLESS RENDER (CLI / CI/CD)

> Goal: ## 🌍 MULTILANG

**ID:** setup_04_headless_render | **Lang:** en | **Orig:** ru | **Category:** setups | **Tags:** 

---

# SETUP 04: HEADLESS RENDER (CLI / CI/CD)

**ID:** SETUP-04 | **Type:** Automated Rendering | **Difficulty:** ⭐⭐ | **Time:** 15-30 min

---

## 🎯 ЦЕЛЬ
Настроить рендеринг без GUI для CI/CD, серверов, батч-обработки

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

| Компонент | Linux | Windows (WSL2) | macOS |
|-----------|-------|----------------|-------|
| **Blender** | 4.0+ | 4.0+ | 4.0+ |
| **GPU** | NVIDIA + CUDA | NVIDIA + CUDA | Apple Silicon / AMD |
| **Display** | Virtual (Xvfb) | Virtual (Xvfb) | Native |
| **Python** | 3.10+ | 3.10+ | 3.10+ |

---

## 🐧 LINUX УСТАНОВКА

### 1. Установка зависимостей
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y \
    blender \
    xvfb \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxcb1 \
    libx11-6 \
    libglu1-mesa \
    libegl1 \
    libgles2

# Для NVIDIA GPU:
sudo apt install -y nvidia-driver-535 nvidia-cuda-toolkit
```

### 2. Проверка Blender
```bash
# GUI режим
blender --version

# Headless (background) режим
blender -b --version

# С GPU поддержкой
blender -b -E CYCLES --cycles-device CUDA --version
```

---

## 🪟 WINDOWS (WSL2)

### 1. Включить WSL2
```powershell
wsl --install
wsl --set-default-version 2
```

### 2. В WSL2 (Ubuntu)
```bash
# Тот же процесс что и Linux
# GPU passthrough работает автоматически в WSL2 с драйверами Windows
```

---

## 🍎 MACOS

### 1. Установка
```bash
# Homebrew
brew install --cask blender

# Или скачать с blender.org
```

### 2. Headless работает нативно
```bash
/Applications/Blender.app/Contents/MacOS/Blender -b --version
```

---

## 🎬 БАЗОВЫЕ КОМАНДЫ РЕНДЕРА

### Одиночный кадр
```bash
blender -b scene.blend \
    -E CYCLES \
    -o //renders/frame_#### \
    -f 1
```

### Анимация (диапазон кадров)
```bash
blender -b scene.blend \
    -E CYCLES \
    -o //renders/anim_#### \
    -s 1 -e 250 -j 1 \
    -a
```

### С кастомными настройками
```bash
blender -b scene.blend \
    -E CYCLES \
    -o //renders/ \
    -f 1 \
    -P render_settings.py
```

---

## ⚙️ PYTHON СКРИПТЫ ДЛЯ НАСТРОЕК (`-P script.py`)

### render_settings.py
```python
import bpy

scene = bpy.context.scene

# Engine
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'

# Resolution
scene.render.resolution_x = 3840
scene.render.resolution_y = 2160
scene.render.resolution_percentage = 100

# Output
scene.render.filepath = "//renders/render_"
scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '32'
scene.render.image_settings.exr_codec = 'ZIP'
scene.render.image_settings.use_preview = True

# Color Management
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'

# Performance
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.01
scene.cycles.adaptive_min_samples = 32

# Save
bpy.ops.wm.save_mainfile(filepath="scene_render_ready.blend")
```

### Запуск с настройками
```bash
blender -b scene.blend -P render_settings.py -o //renders/ -f 1
```

---

## 🎞️ БАТЧ РЕНДЕР (МНОГО ФАЙЛОВ)

### batch_render.py
```python
import bpy
import sys
import os

# Аргументы после --
argv = sys.argv[sys.argv.index("--") + 1:]
input_dir = argv[0]
output_dir = argv[1]

# Найти все .blend файлы
blend_files = [f for f in os.listdir(input_dir) if f.endswith('.blend')]

for blend_file in blend_files:
    filepath = os.path.join(input_dir, blend_file)
    name = os.path.splitext(blend_file)[0]
    
    # Открыть
    bpy.ops.wm.open_mainfile(filepath=filepath)
    
    # Настроить вывод
    scene = bpy.context.scene
    scene.render.filepath = os.path.join(output_dir, f"{name}_####")
    
    # Рендер анимации
    bpy.ops.render.render(animation=True, write_still=False)
    
    print(f"Rendered: {name}")

# Выход
bpy.ops.wm.quit_blender()
```

### Запуск батча
```bash
blender -b -P batch_render.py -- /path/to/scenes /path/to/output
```

---

## 🐳 DOCKER (ПОЛНАЯ ИЗОЛЯЦИЯ)

### Dockerfile
```dockerfile
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    blender \
    xvfb \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Python deps
RUN pip3 install bpy-sdk

# Working dir
WORKDIR /workspace

# Entry point
ENTRYPOINT ["xvfb-run", "-a", "blender", "-b"]
CMD ["--help"]
```

### Сборка и запуск
```bash
docker build -t blender-render .
docker run --gpus all -v $(pwd)/scenes:/workspace -v $(pwd)/output:/output blender-render -b /workspace/scene.blend -o /output/render_ -f 1
```

---

## 🔄 CI/CD ИНТЕГРАЦИЯ

### GitHub Actions (.github/workflows/render.yml)
```yaml
name: Render Animation

on:
  push:
    paths: ['scenes/**/*.blend']

jobs:
  render:
    runs-on: ubuntu-latest
    container:
      image: nvidia/cuda:12.1-devel-ubuntu22.04
      options: --gpus all
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Blender
        run: |
          apt-get update && apt-get install -y blender xvfb
      
      - name: Render
        run: |
          xvfb-run -a blender -b scenes/animation.blend \
            -E CYCLES -o //renders/anim_#### -a
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: rendered-frames
          path: renders/
          retention-days: 7
```

### GitLab CI (.gitlab-ci.yml)
```yaml
render:
  image: nvidia/cuda:12.1-devel-ubuntu22.04
  services:
    - name: xvfb
  variables:
    NVIDIA_VISIBLE_DEVICES: all
  script:
    - apt-get update && apt-get install -y blender
    - xvfb-run -a blender -b $SCENE_FILE -E CYCLES -o //renders/ -a
  artifacts:
    paths:
      - renders/
    expire_in: 1 week
```

---

## 📊 МОНИТОРИНГ И ЛОГИ

### Прогресс рендера
```bash
# В логах ищите:
# "Fra: 0042 Time: 00:15.23"

# Python callback для прогресса
import bpy

def render_progress(scene):
    frame = scene.frame_current
    total = scene.frame_end - scene.frame_start + 1
    percent = (frame / total) * 100
    print(f"PROGRESS: {percent:.1f}% ({frame}/{total})")

bpy.app.handlers.render_post.append(render_progress)
```

### Таймауты и ретраи
```bash
# Таймаут на кадр (секунды)
timeout 300 blender -b scene.blend -f 1

# Ретраи при ошибке
for i in {1..3}; do
  blender -b scene.blend -f $FRAME && break || sleep 10
done
```

---

## 🔗 LINKS

- **Blender CLI Docs:** https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html
- **Blender Python API:** https://docs.blender.org/api/current/
- **Setup 05:** [Render Farm (Flamenco)](../setups/setup_05_render_farm.md)
- **Next:** [Setup 05: Render Farm (Flamenco)](../setups/setup_05_render_farm.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/setups/setup_04_headless_render.md` |
| Russian | `multilang/ru/setups/setup_04_headless_render.md` |