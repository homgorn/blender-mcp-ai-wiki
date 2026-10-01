---
id: setup_07_ci_cd
lang: es
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 07: CI/CD INTEGRATION

> Objetivo: 

**ID:** setup_07_ci_cd | **Lang:** es | **Orig:** ru | **Category:** setups | **Tags:** **, blender

## Cómo usar
Esta es la versión en español de 'setup_07_ci_cd'. Los bloques de código son independientes del idioma. Sigue los pasos en orden y verifica.

## Prompt MCP (copiar-pegar)
```
setup_07_ci_cd / setups / **, blender
```

> Nota: el código/rutas quedan en inglés por compatibilidad con Blender/Python.

---

---
id: setup_07_ci_cd
lang: ru
orig_lang: ru
category: setups
type: setup
difficulty: 2
---

# СЕТАП 07: CI/CD INTEGRATION

> Цель: ## 🌍 MULTILANG

**ID:** setup_07_ci_cd | **Lang:** ru | **Orig:** ru | **Category:** setups | **Tags:** blender

---

# SETUP 07: CI/CD INTEGRATION

**ID:** SETUP-07 | **Type:** Automated Pipeline | **Difficulty:** ⭐⭐ | **Time:** 20-40 min

---

## 🎯 ЦЕЛЬ
Интеграция Blender в CI/CD пайплайны: автотесты, рендер, экспорт, деплой

---

## 📋 CI/CD СЦЕНАРИИ

| Сценарий | Триггер | Действия |
|----------|---------|----------|
| **PR Validation** | Pull Request | Линт, тесты, быстрый рендер превью |
| **Nightly Build** | Schedule (cron) | Полный рендер, регрессионные тесты |
| **Release** | Tag push | Финальный рендер, экспорт ассетов, деплой |
| **Asset Update** | Asset changed | Пересборка зависимых сцен |

---

## 🔧 GITHUB ACTIONS

### .github/workflows/blender.yml
```yaml
name: Blender CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'scenes/**/*.blend'
      - 'assets/**/*'
      - 'scripts/**/*.py'
      - '.github/workflows/blender.yml'
  pull_request:
    branches: [main]
    paths:
      - 'scenes/**/*.blend'
      - 'assets/**/*'
      - 'scripts/**/*.py'
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM
  workflow_dispatch:  # Manual trigger

env:
  BLENDER_VERSION: "4.2"
  BLENDER_DOWNLOAD_URL: "https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz"

jobs:
  # ===== LINT & TESTS =====
  lint-and-test:
    name: Lint & Unit Tests
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      
      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
          pip install flake8 black isort pytest pytest-cov
      
      - name: Lint (flake8)
        run: flake8 scripts/ --max-line-length=120 --ignore=E501,W503
      
      - name: Format check (black)
        run: black --check scripts/
      
      - name: Import sort check (isort)
        run: isort --check-only scripts/
      
      - name: Run unit tests
        run: pytest tests/ -v --cov=scripts --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml

  # ===== QUICK RENDER PREVIEW (PR) =====
  render-preview:
    name: Render Preview (PR)
    needs: lint-and-test
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Blender
        uses: ./.github/actions/setup-blender
      
      - name: Render Preview (Frame 1, Low Samples)
        run: |
          xvfb-run -a blender -b scenes/main.blend \
            -E CYCLES \
            -o //preview/preview_ \
            -F PNG \
            -f 1 \
            -P scripts/render_preview.py
      
      - name: Upload Preview
        uses: actions/upload-artifact@v4
        with:
          name: render-preview
          path: preview/
          retention-days: 7

  # ===== FULL RENDER (MAIN/RELEASE) =====
  render-full:
    name: Full Render
    needs: lint-and-test
    if: github.event_name == 'push' || github.event_name == 'schedule' || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    timeout-minutes: 120
    
    strategy:
      matrix:
        resolution: ["1080p", "4k"]
        samples: [128, 256]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Blender
        uses: ./.github/actions/setup-blender
      
      - name: Render Full Quality
        run: |
          xvfb-run -a blender -b scenes/main.blend \
            -E CYCLES \
            -o //renders/${{ matrix.resolution }}_${{ matrix.samples }}s/frame_#### \
            -E CYCLES \
            -P scripts/render_full.py \
            -- \
            --resolution ${{ matrix.resolution }} \
            --samples ${{ matrix.samples }} \
            --output //renders/${{ matrix.resolution }}_${{ matrix.samples }}s/
      
      - name: Create Video (MP4)
        run: |
          ffmpeg -framerate 30 -i renders/${{ matrix.resolution }}_${{ matrix.samples }}s/frame_%04d.png \
            -c:v libx264 -pix_fmt yuv420p -crf 18 \
            renders/main_${{ matrix.resolution }}_${{ matrix.samples }}s.mp4
      
      - name: Upload Renders
        uses: actions/upload-artifact@v4
        with:
          name: renders-${{ matrix.resolution }}-${{ matrix.samples }}s
          path: renders/
          retention-days: 30

  # ===== EXPORT ASSETS =====
  export-assets:
    name: Export Game Assets
    needs: render-full
    runs-on: ubuntu-latest
    timeout-minutes: 60
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Blender
        uses: ./.github/actions/setup-blender
      
      - name: Export Game Assets (GLTF/FBX/USD)
        run: |
          xvfb-run -a blender -b scenes/main.blend \
            -P scripts/export_assets.py \
            -- \
            --output-dir exports/ \
            --formats GLTF,FBX,USDZ \
            --formats GLTF,FBX,USDZ
      
      - name: Validate Exports
        run: |
          python scripts/validate_exports.py exports/
      
      - name: Upload Exports
        uses: actions/upload-artifact@v4
        with:
          name: game-assets
          path: exports/
          retention-days: 30

  # ===== DEPLOY =====
  deploy:
    name: Deploy to CDN
    needs: [export-assets, render-full]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: game-assets
          path: exports/
      
      - name: Deploy to CDN
        run: |
          # AWS S3 / Cloudflare R2 / Netlify / Vercel
          aws s3 sync exports/ s3://my-game-assets/latest/ --delete
          aws cloudfront create-invalidation --distribution-id $CF_DIST_ID --paths "/*"
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          CF_DIST_ID: ${{ secrets.CF_DIST_ID }}

  # ===== NOTIFICATIONS =====
  notify:
    name: Notify
    needs: [lint-and-test, render-preview, render-full, export-assets, deploy]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - name: Send Discord/Slack notification
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#blender-ci'
          text: "Blender CI/CD: ${{ job.status }}"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 🎬 RENDER SCRIPTS

### scripts/render_preview.py
```python
import bpy
import sys

# Парсинг аргументов после --
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32  # Быстрый превью
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.filepath = "//preview/preview_"
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'

# Быстрый рендер кадра 1
bpy.ops.render.render(write_still=True)
print("Preview rendered!")
```

### scripts/render_full.py
```python
import bpy
import sys
import argparse

# Парсинг аргументов
argv = sys.argv[sys.argv.index("--") + 1:]
parser = argparse.ArgumentParser()
parser.add_argument("--resolution", choices=["1080p", "4k"], default="1080p")
parser.add_argument("--samples", type=int, default=256)
parser.add_argument("--output", default="//renders/")
args = parser.parse_args(argv)

scene = bpy.context.scene

# Resolution
res_map = {"1080p": (1920, 1080), "4k": (3840, 2160)}
scene.render.resolution_x, scene.render.resolution_y = res_map[args.resolution]
scene.render.resolution_percentage = 100

# Cycles Settings
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
scene.cycles.samples = args.samples
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'
scene.cycles.denoising_prefilter = 'ACCURATE'
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.01
scene.cycles.adaptive_min_samples = 32

# Output
scene.render.filepath = args.output
scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '32'
scene.render.image_settings.exr_codec = 'ZIP'
scene.render.image_settings.use_preview = True

# Color Management
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'

# Animation range
scene.frame_start = 1
scene.frame_end = 250

# Render Animation
bpy.ops.render.render(animation=True, write_still=False)
print(f"Full render complete: {args.resolution} @ {args.samples} samples")
```

### scripts/export_assets.py
```python
import bpy
import os
import sys
import argparse

argv = sys.argv[sys.argv.index("--") + 1:]
parser = argparse.ArgumentParser()
parser.add_argument("--output-dir", default="exports/")
parser.add_argument("--formats", nargs="+", default=["GLTF", "FBX", "USDZ"])
args = parser.parse_args(argv)

os.makedirs(args.output_dir, exist_ok=True)

# Найти все объекты для экспорта
export_objects = [obj for obj in bpy.data.objects if obj.get("export", True)]

for fmt in args.formats:
    fmt_dir = os.path.join(args.output_dir, fmt.lower())
    os.makedirs(fmt_dir, exist_ok=True)
    
    for obj in export_objects:
        name = obj.name.replace(" ", "_")
        filepath = os.path.join(fmt_dir, f"{name}.{fmt.lower()}")
        
        # Select only this object
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        if fmt == "GLTF":
            bpy.ops.export_scene.gltf(
                filepath=filepath,
                export_format='GLB',
                use_selection=True,
                export_apply=True,
                export_tangents=True,
                export_materials='EXPORT',
            )
        elif fmt == "FBX":
            bpy.ops.export_scene.fbx(
                filepath=filepath,
                use_selection=True,
                apply_unit_scale=True,
                apply_scale_options='FBX_SCALE_ALL',
                bake_space_transform=True,
                object_types={'ARMATURE', 'MESH'},
                add_leaf_bones=False,
            )
        elif fmt == "USDZ":
            bpy.ops.wm.usd_export(
                filepath=filepath,
                export_selected=True,
            )

print(f"Exported {len(export_objects)} objects to {args.output_dir}")
```

---

## 🔧 CUSTOM GITHUB ACTION

### .github/actions/setup-blender/action.yml
```yaml
name: "Setup Blender"
description: "Install and configure Blender for CI"
inputs:
  version:
    description: "Blender version"
    required: false
    default: "4.2"
  cuda:
    description: "Enable CUDA"
    required: false
    default: "true"

runs:
  using: "composite"
  steps:
    - name: Download Blender
      run: |
        VERSION="${{ inputs.version }}"
        URL="https://download.blender.org/release/Blender${VERSION%.*}/blender-${VERSION}-linux-x64.tar.xz"
        wget -q "$URL" -O blender.tar.xz
        tar -xf blender.tar.xz
        echo "$(pwd)/blender-${VERSION}-linux-x64/blender" >> $GITHUB_PATH
      shell: bash

    - name: Install xvfb
      run: sudo apt-get update && sudo apt-get install -y xvfb
      shell: bash

    - name: Verify Blender
      run: |
        blender --version
        blender -b --version
      shell: bash
```

---

## 🔧 GITLAB CI

### .gitlab-ci.yml
```yaml
stages:
  - test
  - render
  - export
  - deploy

variables:
  BLENDER_VERSION: "4.2"

before_script:
  - apt-get update -qq && apt-get install -y -qq blender xvfb ffmpeg
  - blender --version

lint:
  stage: test
  script:
    - pip install flake8 black isort pytest
    - flake8 scripts/
    - black --check scripts/
    - pytest tests/

render_preview:
  stage: render
  script:
    - xvfb-run -a blender -b $SCENE_FILE -E CYCLES -o //preview/ -f 1 -P scripts/render_preview.py
  artifacts:
    paths:
      - preview/
    expire_in: 1 week

render_full:
  stage: render
  script:
    - xvfb-run -a blender -b $SCENE_FILE -E CYCLES -o //renders/ -a -P scripts/render_full.py
  artifacts:
    paths:
      - renders/
    expire_in: 1 month

export_assets:
  stage: export
  script:
    - blender -b $SCENE_FILE -P scripts/export_assets.py -- --output-dir exports/
  artifacts:
    paths:
      - exports/
    expire_in: 1 month

deploy:
  stage: deploy
  script:
    - aws s3 sync exports/ s3://my-bucket/latest/ --delete
  only:
    - main
  when: manual
```

---

## 📊 МОНИТОРИНГ И МЕТРИКИ

### Prometheus Metrics (Python)
```python
# scripts/metrics.py
from prometheus_client import Counter, Histogram, Gauge, push_to_gateway

RENDER_DURATION = Histogram('blender_render_duration_seconds', 'Render time', ['scene', 'resolution'])
RENDER_FRAMES = Counter('blender_render_frames_total', 'Frames rendered', ['scene', 'status'])
VRAM_USAGE = Gauge('blender_vram_usage_bytes', 'VRAM usage', ['device'])

def record_render(scene, resolution, duration, frames, status):
    RENDER_DURATION.labels(scene=scene, resolution=resolution).observe(duration)
    RENDER_FRAMES.labels(scene=scene, status=status).inc(frames)
    push_to_gateway('pushgateway:9091', job='blender_render', registry=registry)
```

---

## 🔗 LINKS

- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **GitLab CI Docs:** https://docs.gitlab.com/ee/ci/
- **Blender CLI:** https://docs.blender.org/manual/en/latest/advanced/command_line/
- **Setup 06:** [Custom MCP Tools](../setups/setup_06_custom_mcp_tools.md)
- **Next:** [Setup 08: Asset Pipeline](../setups/setup_08_asset_pipeline.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/setups/setup_07_ci_cd.md` |
| Russian | `multilang/ru/setups/setup_07_ci_cd.md` |