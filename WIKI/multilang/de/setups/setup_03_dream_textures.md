---
id: setup_03_dream_textures
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: template
---
# СЕТАП 03: DREAM TEXTURS (STABLE DIFFUSION IN BLENDER)

> Ziel: 

**ID:** setup_03_dream_textures | **Lang:** de | **Orig:** ru | **Category:** setups | **Tags:** **

## Verwendung
Dies ist die deutsche Version von 'setup_03_dream_textures'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
setup_03_dream_textures / setups / **
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: setup_03_dream_textures
lang: ru
orig_lang: ru
category: setups
type: setup
difficulty: 2
---

# СЕТАП 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)

> Цель: ## 🌍 MULTILANG

**ID:** setup_03_dream_textures | **Lang:** ru | **Orig:** ru | **Category:** setups | **Tags:** 

---

# SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)

**ID:** SETUP-03 | **Type:** Local AI Texturing | **Difficulty:** ⭐⭐ | **Time:** 20-40 min (зависит от загрузки моделей)

---

## 🎯 ЦЕЛЬ
Установить и настроить Dream Textures для генерации PBR текстур, инпейнтинга, аутпейнтинга и проекции текстур прямо в Blender

---

## 📋 ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ

| Компонент | Минимум | Рекомендуется |
|-----------|---------|---------------|
| **Blender** | 3.3+ | 4.0+ |
| **GPU** | 4GB VRAM | 8-12GB VRAM |
| **RAM** | 8GB | 16-32GB |
| **Диск** | 10GB | 20GB+ |
| **CUDA** | 11.7+ | 12.1+ |
| **Python** | 3.10+ | 3.10+ (встроен в Blender) |

---

## 🪟 УСТАНОВКА

### 1. Скачать релиз
```bash
# Последний релиз:
# https://github.com/carson-katri/dream-textures/releases/latest

# Скачать: dream_textures-<version>.zip
# НЕ распаковывать! Устанавливать как ZIP.
```

### 2. Установка в Blender
```
Edit → Preferences → Add-ons → Install from ZIP
Выбрать: dream_textures-<version>.zip
☑ Dream Textures
```

### 3. Первая загрузка (автоматическая)
```
N-Panel → Dream Textures вкладка
→ Preferences → Download Models
```

**Скачиваются автоматически (~2-4 GB):**
- PyTorch + TorchVision
- Diffusers + Transformers
- Safetensors + Accelerate

---

## 🤖 ВЫБОР МОДЕЛЕЙ (Preferences → Models)

### ОБЯЗАТЕЛЬНЫЕ (базовые)
| Модель | Назначение | Размер |
|--------|------------|--------|
| `stabilityai/stable-diffusion-2-1-base` | Основная генерация 512x512 | ~2.1 GB |
| `stabilityai/stable-diffusion-2-inpainting` | Инпейтинг/аутпейтинг | ~2.1 GB |

### РЕКОМЕНДУЕМЫЕ (дополнительные)
| Модель | Назначение | Размер |
|--------|------------|--------|
| `stabilityai/stable-diffusion-2-depth` | Texture Projection, Depth-to-Image | ~2.1 GB |
| `stabilityai/stable-diffusion-x4-upscaler` | AI Upscaling 4x | ~0.5 GB |
| `stabilityai/stable-diffusion-2-1` | Генерация 768x768 | ~2.1 GB |

### ПРОДВИНУТЫЕ (опционально)
| Модель | Назначение |
|--------|------------|
| `stabilityai/sdxl-base-1.0` | SDXL качество (требует 8GB+ VRAM) |
| `runwayml/stable-diffusion-v1-5` | SD 1.5 стиль |
| Custom `.ckpt` / `.safetensors` | Любые файн-тюны (Import Checkpoint) |

---

## ⚙️ НАСТРОЙКИ ПРЕФЕРЕНСЕС

### Device & Precision
```
Preferences → Dream Textures:
Device: CUDA (или MPS для Apple Silicon)
Precision: fp16 (Half) - рекомендуется
Speed Optimizations: Half Precision ✓
Memory Optimizations: Attention Slicing (Auto) ✓
```

### Model Cache
```
Model Cache Directory: (можно изменить на другой диск)
# По умолчанию: %APPDATA%\Blender Foundation\Blender\4.x\scripts\addons\dream_textures\.python_dependencies
```

### DreamStudio (облачный фоллбэк)
```
API Key: (опционально, если GPU слабый)
# https://beta.dreamstudio.ai/membership?tab=apiKeys
```

---

## 🎨 БЫСТРЫЙ СТАРТ (3 ШАГА)

### 1. Генерация текстуры
```
1. Выбери объект → N-Panel → Dream Textures → Generate
2. Prompt: "weathered brick wall, moss in cracks, seamless, 8k"
3. ✓ Seamless
4. Model: stable-diffusion-2-1-base
5. Size: 512x512 (или 1024x1024 если 8GB+ VRAM)
6. Generate → Apply to Material
```

### 2. Texture Projection (на модель)
```
1. Tab → Edit Mode → Select faces → Numpad / (Local View)
2. Dream Textures → Project Dream Texture
3. Model: stable-diffusion-2-depth (ОБЯЗАТЕЛЬНО!)
4. Prompt: "ancient stone wall, moss, cracks, torch light"
5. Project → Авто UV + Материал
```

### 3. Inpainting (исправление швов)
```
1. Image Editor → Открыть текстуру
2. Mask проблемную область (RMB drag)
5. Dream → Inpaint
6. Prompt: "seamless continuation of stone texture"
7. Generate
```

---

## ⚙️ ОПТИМИЗАЦИЯ VRAM

| Настройка | 4GB VRAM | 8GB VRAM | 12GB+ VRAM |
|-----------|----------|----------|------------|
| **Resolution** | 512x512 | 512-768 | 768-1024 |
| **Precision** | fp16 | fp16 | fp16/bf16 |
| **Attention Slicing** | Auto | Auto | Auto |
| **Model Offloading** | Sequential | Auto | None |
| **Steps** | 20-25 | 25-30 | 30-50 |

### При нехватке памяти:
```python
# В Blender Python Console:
import torch
torch.cuda.empty_cache()
# Или перезапустить Blender
```

---

## 🌐 MACOS СПЕЦИФИКА
```bash
# Если ошибка "quarantine":
xattr -r -d com.apple.quarantine ~/Library/Application\ Support/Blender/4.x/scripts/addons/dream_textures/.python_dependencies

# Запуск Blender для логов:
/Applications/Blender.app/Contents/MacOS/Blender
```

---

## 🔧 УСТРАНЕНИЕ НЕИСПРАВНОСТЕЙ

| Ошибка | Решение |
|--------|---------|
| `CUDA out of memory` | Уменьшить Resolution, Steps; закрыть другие приложения |
| `Model download failed` | Проверить интернет; HF_TOKEN для гейтнутых моделей |
| `ModuleNotFoundError: torch` | Переустановить аддон; проверить `.python_dependencies` |
| `macOS quarantine` | Команда `xattr` выше |
| `Slow generation` | fp16, Attention Slicing, меньше steps |

---

## 🔗 LINKS

- **Repo:** https://github.com/carson-katri/dream-textures
- **Wiki:** https://github.com/carson-katri/dream-textures/wiki
- **Discord:** https://discord.gg/EmDJ8CaWZ7
- **Releases:** https://github.com/carson-katri/dream-textures/releases
- **Setup 02:** [GenesisCore Local](../setups/setup_02_genesiscore_local.md)
- **Next:** [Setup 04: Headless Render](../setups/setup_04_headless_render.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/setups/setup_03_dream_textures.md` |
| Russian | `multilang/ru/setups/setup_03_dream_textures.md` |