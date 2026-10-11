#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Upgrade next top-15 stub files to full level (append FULL GUIDE sections). Idempotent."""
import os
from pathlib import Path
S = Path(__file__).resolve().parent          # WIKI/scripts
W = Path(os.environ.get("BLENDER_WIKI_ROOT") or S.parent)   # WIKI
UP = {
 "setups/setup_09_blenderbot_ai.md": """\n---\n\n## FULL GUIDE\n\n### Архитектура\n```\nBlender N-panel → HTTP localhost → LLM API → code → Text Editor → Run\n```\n\n### Шаги\n1. API-ключ провайдера (OpenRouter/DeepSeek) в настройках аддона.\n2. Промпт с контекстом сцены: `get_scene_info` → вставить в запрос.\n3. Сгенерированный код ВСЕГДА проверять: dry-run на копии сцены.\n4. Частые задачи: примитивы+модификаторы, расстановка, рендер-пресеты.\n\n### MCP промпт\n```\n"Сгенерируй bpy-скрипт: [задача]. Контекст сцены: [get_scene_info]. Только безопасные ops, без os/sys."\n```\n\n### Проверка\n- [ ] Скрипт выполняется без ошибок на пустой сцене\n- [ ] Нет `os.system`, `subprocess`, записи вне `//`\n""",
 "setups/setup_11_touchdesigner.md": """\n---\n\n## FULL GUIDE\n\n### Протоколы\n| Протокол | Задержка | Назначение |\n|----------|----------|------------|\n| OSC | 1–5ms | Параметры, триггеры |\n| NDI | 1–2 кадра | Видео поток |\n| Spout | 0–1 кадр | GPU-текстуры (Windows) |\n| Shared Memory | ~0 | Текстуры/геометрия |\n\n### Шаги\n1. Blender: OSC-аддон, порт 7000, отправка трансформов выбранных объектов.\n2. TouchDesigner: OSC In CHOP → связать с параметрами COMP.\n3. Видео: NDI Out (Blender) → NDI In (TD) или Spout пара.\n4. Синхронизация кадров: frame counter + drift correction (порог 2 кадра).\n\n### Проверка\n- [ ] Параметры двигаются без залипаний\n- [ ] Видео без тиринга, задержка измерена\n""",
 "setups/setup_12_unreal_livelink.md": """\n---\n\n## FULL GUIDE\n\n### Методы\n| Метод | Кейс |\n|-------|------|\n| Live Link | Камеры, мокап в реальном времени |\n| Datasmith | Статика/архитектура |\n| USD | Пайплайн, варианты, LOD |\n| Alembic | Анимация/кэш |\n| FBX | Быстрый обмен |\n\n### FBX-пресет под Unreal\n- Apply Unit Scale, FBX Scale All, bake transform OFF для Unreal (cm через unit scale).\n- Forward Y, Up X. Leaf bones OFF. NLA strips baked.\n\n### Проверка\n- [ ] Масштаб персонажа 180cm в Unreal\n- [ ] Анимации играют, root motion отдельно\n""",
 "setups/setup_13_unity_roundtrip.md": """\n---\n\n## FULL GUIDE\n\n### FBX-пресет под Unity\n- Apply Unit Scale, bake space transform ON, Forward Y.\n- NLA strips baked, deform bones only.\n\n### Материалы URP/HDRP\n| Blender | Unity |\n|---------|-------|\n| BaseColor (sRGB) | Base Map |\n| Metallic/Roughness | Mask Map + Smoothness remap |\n| Normal OpenGL | Normal Map (flip Y) |\n\n### Проверка\n- [ ] Префаб собирается, LOD-суффиксы распознаны\n- [ ] Нормали без инверсии (flip Y при артефактах)\n""",
 "setups/setup_14_godot_pipeline.md": """\n---\n\n## FULL GUIDE\n\n### glTF как нативный мост\n- Export: apply transforms, Y-up, tangents, animations, skins, morphs.\n- Draco OFF (Godot плохо читает), текстуры KTX2/Basis.\n\n### Риг\n- Имена костей без пробелов, root в origin. AnimationPlayer + AnimationTree из GLB.\n\n### Проверка\n- [ ] GLB открывается в Godot без ошибок\n- [ ] Анимации в списке, LOD-суффиксы на месте\n""",
 "setups/setup_18_substance_painter_live.md": """\n---\n\n## FULL GUIDE\n\n### Roundtrip\n1. Blender → FBX с UDIM в Substance Painter.\n2. Bake: ID, curvature, AO, thickness, position.\n3. Smart materials + слои wear/dirt/damage.\n4. Export 4k PBR → Blender Principled (BaseColor sRGB, остальные Non-Color).\n\n### Проверка\n- [ ] UDIM-тайлы совпадают\n- [ ] Curvature-маски дают чистый edge wear\n""",
 "setups/setup_23_realitycapture_scan.md": """\n---\n\n## FULL GUIDE\n\n### Пайплайн\n1. RC: align → dense → mesh 5M → simplify preview.\n2. Export OBJ + 8k textures.\n3. Blender: Quad Remesher 20k → Smart UV → bake normal/AO/curvature с high.\n4. LOD: 20k/8k/2k + billboard.\n\n### Проверка\n- [ ] Масштаб реальный (scale bar)\n- [ ] Normal map без швов на стыках чанков\n""",
 "setups/setup_30_rigify_advanced.md": """\n---\n\n## FULL GUIDE\n\n### Rigify + лицо\n1. Meta-rig human + face rig (52 кости: jaw/eyes/brows/lips).\n2. Generate → weights auto → чистка: плечи/таз градиенты, пальцы по фалангам.\n3. Correctives: колени/локти (см. P34).\n4. Game export: bake deform, remove drivers.\n\n### Проверка\n- [ ] Экстремальные позы без разрывов\n- [ ] Лицо: 6 базовых эмоций читаются\n""",
 "setups/setup_44_rodin_hyper3d.md": """\n---\n\n## FULL GUIDE\n\n### Генерация\n1. Front+side фото → Rodin job → poll до DONE.\n2. Скачай GLB + PBR.\n3. Cleanup: decimate 15k, Smart UV, bake normal.\n4. Scale to meters, origin to base.\n\n### Проверка\n- [ ] Пропорции совпадают с референсом\n- [ ] Текстуры 2k, без растяжек на лице/руках\n""",
 "setups/setup_56_mocap_rokoko.md": """\n---\n\n## FULL GUIDE\n\n### Пайплайн\n1. Rokoko Studio → export FBX (60fps).\n2. Blender: import → retarget на Rigify (см. P44).\n3. Foot lock на контактных кадрах, despike, bake.\n4. Loop: первый = последний+1.\n\n### Проверка\n- [ ] Стопы не скользят\n- [ ] Нет спайков в Graph Editor\n""",
 "workflows/wf_04_character_animation.md": """\n---\n\n## FULL ADDENDUM: engine gates\n\n### Unity gate\n- [ ] FBX + bake transform, NLA baked, scale applied\n### Unreal gate\n- [ ] FBX + smoothing + tangents, LOD suffixes\n### Godot gate\n- [ ] GLB без Draco, animations separate\n""",
 "workflows/wf_05_procedural_assets.md": """\n---\n\n## FULL ADDENDUM: performance gates\n\n- Collection Instancing: 1 draw call на тип.\n- Distance culling + decimate LOD.\n- Billboard impostors > 500м.\n- Seed = frame для детерминированного трафика.\n""",
 "workflows/wf_06_archviz_workflow.md": """\n---\n\n## FULL ADDENDUM: portals + delivery\n\n- Порталы на окнах: 3–5x меньше шума в интерьере.\n- Delivery: 4K EXR + PNG + MP4 H.264; HDR — ProRes/HEVC с метадатой.\n""",
 "workflows/wf_08_batch_processing.md": """\n---\n\n## FULL ADDENDUM: logging\n\n- Structured logging каждого батча (JSON): operation/target/duration.\n- Ретрай только упавших чанков, таймаут на кадр.\n""",
 "cases/case_08_sci_fi_corridor.md": """\n---\n\n## FULL PROCESS\n\n1. Модульная сетка 2м: пол/стена/потолок/угол/дверь.\n2. Trim sheets: одна текстура на все модули (UV строго в полосах).\n3. Greeble-кит: 10 деталей, инстансинг.\n4. LOD: full + decimate 0.3.\n5. Export: FBX grid snap 2м, нейминг `mod_{part}_{var}`.\n""",
}
n = 0
for rel, add in UP.items():
    p = W/rel
    if not p.exists():
        print("MISSING", rel); continue
    t = p.read_text(encoding="utf-8")
    if "FULL GUIDE" in t or "FULL ADDENDUM" in t or "FULL PROCESS" in t:
        print("skip", rel); continue
    p.write_text(t.rstrip() + "\n" + add + "\n", encoding="utf-8")
    n += 1
    print("upgraded", rel)
print(f"OK upgraded={n}")
