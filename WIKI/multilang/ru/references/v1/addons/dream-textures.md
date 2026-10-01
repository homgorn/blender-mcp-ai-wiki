---
lang: ru
orig_lang: en
translation: ai
---
# АДДОН DREAM TEXTURES — ПОДРОБНЫЙ РАЗБОР

## Обзор
**Репозиторий:** https://github.com/carson-katri/dream-textures
**Версия:** Latest | **Blender:** 3.3+ | **Лицензия:** GPL-3.0
**Звёзды:** 8.2k | **Discord:** https://discord.gg/EmDJ8CaWZ7

Dream Textures встраивает **Stable Diffusion прямо в Blender** — работает локально через diffusers/PyTorch, внешние сервисы не нужны. Лучше всего подходит для генерации текстур, инпейнтинга, аутпейнтинга и проекции текстур.

---

## Архитектура

```
┌────────────────────────────────────────────────────────────┐
│                    DREAM TEXTURES ADDON                      │
├────────────────────────────────────────────────────────────┤
│  .python_dependencies/    # Bundled PyTorch, diffusers      │
│  builtin_presets/         # Prompt presets                  │
│  community_backends/      # Alternative backends            │
│  engine/                  # Core generation pipeline        │
│  generator_process/       # Subprocess for model inference  │
│  operators/               # Blender operators               │
│  ui/                      # N-panel + node editor           │
│  sd_configs/              # Model configurations            │
│  realtime_viewport.py     # Live preview                    │
│  render_pass.py           # Cycles render pass integration  │
│  prompt_engineering.py    # Prompt enhancement              │
│  image_utils.py           # Image processing                │
└────────────────────────────────────────────────────────────┘
```

---

## Ключевые возможности

### 1. Текст в текстуру
- Генерация наборов PBR-текстур (Base Color, Roughness, Normal, Metallic, Height)
- Опция бесшовного тайлинга
- Пресеты стилей: фотореализм, стилизация, фэнтези, sci-fi

### 2. Проекция текстур (Depth-to-Image)
- Проекция текстур на 3D-модели с помощью карт глубины
- Оператор "Project Dream Texture"
- Работает на целых сценах

### 3. Инпейнтинг / аутпейнтинг
- Исправление швов на текстурах
- Расширение текстур за границы
- Преобразование небесшовных текстур в бесшовные

### 4. Интеграция с render-pass
- Использование рендера Cycles как входа для ControlNet
- Ре-стилизация рендеров через img2img
- Ре-стилизация анимации покадрово

### 5. Апскейл с помощью ИИ
- Увеличение в 4 раза через ESRGAN/RealESRGAN
- Встроено в систему нод

### 6. Система истории
- Повторный вызов, экспорт и импорт генераций
- Сохраняются промпт и параметры

---

## Установка

### Скачать релиз (рекомендуется)
1. Перейти на: https://github.com/carson-katri/dream-textures/releases/latest
2. Скачать `dream_textures-<version>.zip`
3. Blender → Preferences → Add-ons → **Install from ZIP**
4. Включить **Dream Textures**

### Первый запуск
- Аддон скачивает PyTorch + diffusers (~2-4 ГБ) в `.python_dependencies/`
- Требуется **4 ГБ+ VRAM** (CUDA или Apple Silicon)
- На macOS может потребоваться снятие карантина:
  ```bash
  xattr -r -d com.apple.quarantine ~/Library/Application\ Support/Blender/3.3/scripts/addons/dream_textures/.python_dependencies
  ```

### Облачный запасной вариант (DreamStudio)
- Если оборудование не поддерживается: укажите API-ключ DreamStudio в настройках
- Обработка происходит в облаке, а не локально

---

## Требования к оборудованию

| Компонент | Минимум | Рекомендуется |
|-----------|---------|-------------|
| **VRAM** | 4 ГБ | 8-12 ГБ |
| **GPU** | CUDA 11.7+ / Apple Silicon | RTX 3080+ / M2 Max+ |
| **RAM** | 8 ГБ | 16-32 ГБ |
| **Диск** | 10 ГБ свободно | 20 ГБ+ |

---

## Рабочие сценарии

### Базовая генерация текстур
```
1. Выберите объект → N-панель → Dream Textures
2. Откройте вкладку "Generate Texture"
3. Введите промпт: "weathered copper metal, patina, seamless"
4. Включите "Seamless" для тайлинга
5. Нажмите Generate
6. Примените к слотам материала
```

### Проекция текстур
```
1. Настройте камеру/вид для проекции
2. Выберите целевой объект(ы)
3. Выберите "Project Dream Texture"
4. Введите промпт: "ancient stone temple walls, moss, cracks"
5. Отрегулируйте влияние глубины
6. Project → создаёт текстуры с UV-развёрткой
```

### Инпейнтинг (исправление швов)
```
1. Выберите текстуру в Image Editor
2. Замаскируйте проблемный участок
3. Dream Textures → Inpaint
4. Промпт: "seamless continuation of stone texture"
5. Смешайте результат
```

### Ре-стилизация рендера
```
1. Настройте сцену с Cycles
2. Render pass → нода Dream Textures
3. Промпт: "cyberpunk neon aesthetic, volumetric lighting"
4. Перерендерите → ИИ трансформирует результат
```

---

## Система нод (продвинутый уровень)

Dream Textures добавляет собственные ноды в Shader Editor:
- **Dream Texture Node** — генерация текстур прямо в графе нод
- **ControlNet Node** — управление через Depth/Canny/Normal
- **Upscale Node** — апскейл средствами ИИ внутри конвейера

Позволяет строить сложные процедурные сценарии.

---

## Бэкенды моделей

| Бэкенд | Модели | Примечания |
|---------|--------|-------|
| **diffusers** (по умолчанию) | SD 1.5, SDXL, SD 2.1, ControlNet | Локально, бесплатно |
| **DreamStudio** | SDXL, SD 3 | Облако, платно |
| **Community** | Flux, SD3, пользовательские | Экспериментально |

---

## Конфигурация

### Настройки (Edit → Preferences → Add-ons → Dream Textures)
- **Device:** CUDA / MPS / CPU
- **Precision:** fp16 (по умолчанию) / fp32 / bf16
- **Model Cache:** пользовательский путь к весам моделей
- **DreamStudio API Key:** для облачной обработки
- **Telemetry:** включение/отключение

### Пресеты
Встроенные пресеты в `builtin_presets/`:
- PBR-материалы (металл, ткань, дерево, камень)
- Окружения (небо, земля, листва)
- Стили (аниме, фотореализм, пиксель-арт)

---

## Решение проблем

| Проблема | Решение |
|-------|-----|
| **Не хватает VRAM** | Снизьте разрешение; используйте fp16; закройте другие приложения |
| **Модель не скачивается** | Проверьте интернет; задайте HF_TOKEN для моделей с ограниченным доступом |
| **Карантин macOS** | Выполните команду xattr, приведённую выше |
| **Медленная генерация** | Используйте меньше шагов (20-30); меньшее разрешение |
| **Видны швы** | Включите "Seamless"; исправьте инпейнтингом |

---

## Интеграция с GenesisCore / blender-mcp

Dream Textures работает **независимо** — интеграции с MCP нет. Варианты использования:
1. **Вручную** — через N-панель в Blender
2. **Python API** — вызов операторов из `execute_blender_code`:
   ```python
   bpy.ops.dream_texture.generate(
       prompt="brick wall, seamless",
       seamless=True,
       width=1024,
       height=1024
   )
   ```
3. **Комбинирование сценариев:**
   - GenesisCore для геометрии/сцены
   - Dream Textures для материалов

---

## Расположение файлов

| Файл | Путь |
|------|------|
| Аддон | `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\dream_textures\` |
| Модели | `%APPDATA%\Blender Foundation\Blender\4.2\scripts\addons\dream_textures\.python_dependencies\` |
| Пресеты | `builtin_presets/` внутри аддона |
| Вывод | Временная папка Blender / папка проекта |

---

## Связанные страницы вики
- [Сценарий генерации текстур](../workflows/texture-generation.md)
- [Связка GenesisCore + Dream Textures](../workflows/scene-building.md)
- [API материалов Blender](../api/materials.md)

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [BLENDER-MCP ADDON - DEEP DIVE](blender-mcp.md), [DREAM TEXTURES - FULL WIKI DOCUMENTATION](dream-textures-full.md), [GENESISCORE ADDON - DEEP DIVE](genesiscore.md), [TROUBLESHOOTING GUIDE](../guides/troubleshooting.md)
- **По темам:** [ANIMATION WORKFLOWS](../workflows/animation.md), [BLENDER MATERIALS API REFERENCE](../api/materials.md), [BLENDER MESH OPERATIONS API REFERENCE](../api/mesh-operations.md)
- **Теги:** #addon, #reference, #stable-diffusion

