---
id: setup_15_comfyui_sdxl
lang: ru
category: setups
status: full
---
# SETUP 15: BLENDER + COMFYUI SDXL

**ID:** SETUP-15 | **Type:** AI Texturing | **Difficulty:** ⭐⭐ | **Time:** 25-40 min
**RU/EN Bilingual**

## 🎯 Цель / Goal
RU: ComfyUI как бэкенд генерации PBR. EN: ComfyUI as PBR backend.

## 1. Шаги / Steps
1. ComfyUI локально
2. SDXL base+refiner
3. ControlNet depth/canny
4. Blender texture nodes

## 2. MCP промпт / Prompt
```
RU: "Сгенерируй через ComfyUI SDXL seamless PBR 1k: basecolor+roughness+normal, ControlNet depth из viewport" / EN: "Generate via ComfyUI SDXL seamless PBR 1k: basecolor+roughness+normal, ControlNet depth from viewport"
```

## 3. Проверка / Check
- [ ] Аддон/сервис отвечает
- [ ] Тестовая сцена собирается
- [ ] Экспорт читается целевым софтом

## 4. Типовые ошибки / Pitfalls
- Версии Python/Blender mismatch → пинь 3.11, Blender 4.2 LTS
- Пути с пробелами/кириллицей → только ASCII
- Права на запись → запускать от админа один раз

## 🔗 Связи / Links
Setup 01 blender-mcp, Setup 08 Asset Pipeline, WF-01, INDEX

---

## FULL GUIDE (дополнение до уровня setup_01)

### Архитектура
```
Blender viewport depth → ControlNet depth → SDXL base → SDXL refiner → seamless tile → PBR split
```

### Пошагово
1. ComfyUI: Manager → Install `ComfyUI-ControlNet`, `SeamlessTile`, `UltimateSDUpscale`.
2. Чекпоинты: `sd_xl_base_1.0.safetensors` + `sd_xl_refiner_1.0.safetensors` в `models/checkpoints/`.
3. ControlNet: `control_v11f1p_sd15_depth.pth` (или SDXL-depth) в `models/controlnet/`.
4. Workflow: Load Checkpoint → CLIP Text (positive/negative) → ControlNet Apply (depth image из Blender viewport) → KSampler 30 steps → VAE Decode → Seamless Tile → Save.
5. Blender: depth снимается через viewport render (OpenGL) 1024px, подаётся в ControlNet.
6. Split на карты: basecolor = output; roughness = desaturate+levels; normal = MiDaS→NormalMap node.

### Параметры
| Параметр | Значение |
|----------|----------|
| Steps | 30 (base 20 + refiner 10) |
| CFG | 6.5 |
| Denoise | 0.55 |
| Seamless | X+Y tiling ON |
| Resolution | 1024 (VRAM 8GB) / 512 (VRAM 4GB) |

### MCP промпт
```
"Через ComfyUI SDXL: depth из viewport → ControlNet weight 0.8, 30 steps, seamless XY, split basecolor/rough/normal, примени с repeat 4"
```

### Проверка
- [ ] Нет видимых швов при repeat 4x
- [ ] Depth совпадает с геометрией (проверить overlay 50%)

