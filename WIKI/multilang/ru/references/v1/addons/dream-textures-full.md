---
lang: ru
orig_lang: en
translation: ai
---
# DREAM TEXTURES — ПОЛНАЯ ДОКУМЕНТАЦИЯ

## Обзор
**Репозиторий:** https://github.com/carson-katri/dream-textures
**Wiki:** https://github.com/carson-katri/dream-textures/wiki
**Версия:** Latest | **Blender:** 3.3+ | **Лицензия:** GPL-3.0

---

## Руководство по настройке (из Wiki)

### Установка
1. Скачать из [последнего релиза](https://github.com/carson-katri/dream-textures/releases/latest)
2. Windows: распаковать архив 7-Zip → получить `.zip` → установить в Blender Preferences → Add-ons
3. Включить **Dream Textures** в аддонах
4. **НЕ** устанавливать зависимости вручную — использовать только готовую сборку

### Скачивание моделей
В настройках аддона найти и скачать:
- `stabilityai/stable-diffusion-2-1-base` — основная модель 512x512
- `stabilityai/stable-diffusion-2-inpainting` — для инпейнтинга/аутпейнтинга
- `stabilityai/stable-diffusion-2-depth` — для проекции текстур, depth-to-image
- `stabilityai/stable-diffusion-x4-upscaler` — для 4-кратного апскейла средствами ИИ
- `stabilityai/stable-diffusion-2-1` — дообучена под 768x768

### Приватные модели
- Сгенерировать токен Hugging Face на https://huggingface.co/settings/tokens
- Вставить его в поле "Token" в настройках

### Импорт чекпойнтов (.ckpt)
- Нажать "Import Checkpoint File" в настройках
- Выбрать файл → указать Model Config:
  - `v1` — оригинальные модели CompVis (SD 1.x)
  - `v2 (512, epsilon)` — модели 512x512 с prediction_type="epsilon"
  - `v2 (768, v_prediction)` — модели 768x768 с prediction_type="v_prediction"

### DreamStudio (облако)
- Ввести API-ключ с https://beta.dreamstudio.ai/membership?tab=apiKeys
- Обработка в облаке, если локального железа не хватает

---

## Генерация изображений (из Wiki)

### Доступ
- Открыть Image Editor или Shader Editor
- Нажать `N` для боковой панели → панель **Dream**

### Параметры

| Параметр | Описание |
|--------|-------------|
| **Pipeline** | Stable Diffusion (локально) или DreamStudio (облако) |
| **Model** | Выбор установленной модели (части функций требуют конкретных моделей) |
| **Prompt** | Текстовый промпт. Доступны пресеты (например, "Texture" добавляет суффикс "texture") |
| **Seamless** | Циклическая свёртка для идеального тайлинга. Можно указать оси |
| **Negative** | Чего избегать (например, "building", чтобы убрать здания) |
| **Size** | Целевые размеры (кратны 64). Лучше всего 512x512 |
| **Source Image** | Файл или Open Image для img2img |

#### Режимы исходного изображения
1. **Color** — смешивание изображения с шумом
2. **Color + Generated Depth** — глубина MiDaS + цвет (требуется модель глубины)
3. **Color + Depth Map** — пользовательское изображение-карта глубины
3. **Depth** — трактовать изображение только как карту глубины

#### Продвинутые параметры
| Параметр | Описание |
|-----------|-------------|
| **Random Seed** | Автогенерация или ручной сид |
| **Steps** | Шаги сэмплера (больше — лучше сходимость) |
| **CFG Scale** | Сила следования промпту |
| **Scheduler** | Разные скорости сходимости |
| **Step Preview** | "Fast" (превью латента) или "Accurate" (декодирование VAE на каждом шаге) |
| **Speed Optimizations** | Рекомендуется Half Precision |
| **Memory Optimizations** | Рекомендуется Attention Slicing (Auto) |

---

## Проекция текстур (из Wiki)

### Рабочий процесс
1. Выбрать объекты в 3D Viewport
2. Войти в Edit Mode → выбрать целевые полигоны
3. Local View (`/`) чтобы ограничить карту глубины выделением
4. **Совет:** если проекция искажается, разбейте большие полигоны

### Настройки
- Выбрать **модель глубины** (например, `stable-diffusion-2-depth`)
- Ввести промпт
- **Источник данных:** "Depth" (по умолчанию) или "Depth and Color" (использует затенение вьюпорта)
- Подобрать размер изображения под соотношение сторон вьюпорта

### Выполнение
- Нажать **Project Dream Texture**
- Создаётся новый материал с именем-сидом
- UV обновляются под угол проекции
- Живое превью в режиме Viewport Shading

---

## Инпейнт и аутпейнт (из Wiki)

### Инпейнтинг
- Замаскировать участок в Image Editor
- Требуется модель `stable-diffusion-2-inpainting`
- Промпт: "seamless continuation of [texture]"
- **Как сделать текстуры бесшовными:** инпейнтить края, чтобы смешать их

### Аутпейнтинг
- Расширить изображение за границы
- Выбрать точку отсчёта (центр, углы, края)
- Генерирует новое содержимое в том же стиле

---

## Render-движок / система нод (из Wiki)

### Добавленные ноды
- **Dream Texture Node** — генерация текстур в графе шейдеров
- **ControlNet Node** — управление через Depth/Canny/Normal
- **Upscale Node** — апскейл средствами ИИ внутри конвейера

### Интеграция с render-pass
- Использовать рендер Cycles как вход для ControlNet
- Ре-стилизация через img2img
- Анимация: ре-стилизация покадрово

#### Управляющие параметры
| Параметр | Эффект |
|-----------|--------|
| **Depth** | Использовать depth-pass для структуры |
| **Noise Strength** | Отклонение от рендера (0-1) |
| **Seed** | Воспроизводимость |

---

## Апскейл средствами ИИ (из Wiki)
- Увеличение в 4 раза через ESRGAN/RealESRGAN
- Опция **Tile Size** для больших изображений

---

## История (из Wiki)
- Повторный вызов, экспорт и импорт генераций
- **Export:** сохранить промпт + параметры + сид
- **Import:** восстановить настройки предыдущей генерации

---

## Настройка для разработки (из Wiki)
```bash
git clone https://github.com/carson-katri/dream-textures
cd dream-textures
# Установить в Blender
# Установить зависимости: pip install -r requirements.txt
```

---

## Требования к оборудованию
| Компонент | Минимум | Рекомендуется |
|-----------|---------|-------------|
| **VRAM** | 4 ГБ | 8-12 ГБ |
| **GPU** | CUDA 11.7+ / Apple Silicon | RTX 3080+ / M2 Max+ |
| **RAM** | 8 ГБ | 16-32 ГБ |
| **Диск** | 10 ГБ | 20 ГБ+ |

---

## Решение проблем
| Проблема | Решение |
|-------|-----|
| OOM / CUDA OOM | Снизьте разрешение; fp16; закройте приложения |
| Модель не скачивается | Проверьте интернет; HF_TOKEN для моделей с ограниченным доступом |
| Карантин macOS | `xattr -r -d com.apple.quarantine <addon_path>/.python_dependencies` |
| Медленная генерация | Меньше шагов (20-30); меньшее разрешение |
| Видны швы | Включите Seamless; инпейнтить края |

---

## Интеграция с MCP
Dream Textures — **самостоятельный** аддон, интеграции с MCP нет.
Варианты использования:
1. Вручную через N-панель
2. Python API через `execute_blender_code`:
```python
bpy.ops.dream_texture.generate(
    prompt="brick wall, seamless",
    seamless=True,
    width=1024,
    height=1024
)
```
3. Комбинированный сценарий: GenesisCore для геометрии → Dream Textures для материалов

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [DREAM TEXTURES ADDON - DEEP DIVE](dream-textures.md), [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [ANIMATION WORKFLOWS](../workflows/animation.md), [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md)
- **По темам:** [BLENDER PYTHON API REFERENCE (4.x)](../api/blender-api.md), [BLENDER SCRIPTING PATTERNS - SAFE & EFFECTIVE](../api/scripting-patterns.md), [BLENDER-MCP - FULL DOCUMENTATION](blender-mcp-full.md)
- **Теги:** #reference, #stable-diffusion

