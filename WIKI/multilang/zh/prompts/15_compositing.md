---
id: 15_compositing
lang: zh
orig_lang: ru
category: prompts
type: prompt
difficulty: 3
translation: template
---
# P15: COMPOSITING

> 目标: 

**ID:** 15_compositing | **Lang:** zh | **Orig:** ru | **Category:** prompts | **Tags:** **, color, color-grading, compositing, cryptomatte, nodes, passes, post, post-processing

## 使用方法
这是 '15_compositing' 的中文版。代码块与语言无关。请按顺序执行步骤并检查。

## MCP 提示词（复制粘贴）
```
15_compositing / prompts / **, color, color-grading, compositing, cryptomatte, nodes, passes, post
```

> 注意：代码/路径保留英文以兼容 Blender/Python。

---

---
id: 15_compositing
lang: ru
orig_lang: en
category: prompts
type: prompt
difficulty: 3
---

# P15: COMPOSITING

> Цель: ## 🌍 MULTILANG

**ID:** 15_compositing | **Lang:** ru | **Orig:** en | **Category:** prompts | **Tags:** **, color, color-grading, compositing, cryptomatte, nodes, passes, post, post-processing

---

# P15: COMPOSITING

**ID:** P15 | **Cluster:** Rendering/Post | **Difficulty:** ⭐⭐⭐ | **Tags:** #compositing #nodes #post-processing #color-grading #passes #cryptomatte

---

## 🎯 GOAL
Professional compositing workflow using Blender's Node Compositor with render passes, color grading, and effects

---

## 📝 PROMPT (RUS)

```
Настрой композитинг для сцены "[SCENE_NAME]":
Passes: COMBINED, VIEW_LAYER, CRYPTOMATTE, MIST, AO, NORMAL, DEPTH, EMMISSION
Операции: Color Balance, Hue/Sat, Gamma, Glare, Lens Distortion, Vignette, Film Grain
Output: EXR MultiLayer / PNG Sequence / MP4
```

---

## 📝 PROMPT (ENG)

```
Setup compositing for scene "[SCENE_NAME]":
Passes: COMBINED, VIEW_LAYER, CRYPTOMATTE, MIST, AO, NORMAL, DEPTH, EMMISSION
Operations: Color Balance, Hue/Sat, Gamma, Glare, Lens Distortion, Vignette, Film Grain
Output: EXR MultiLayer / PNG Sequence / MP4
```

---

## 🔧 MCP: `execute_blender_code`

### ENABLE RENDER PASSES
```python
import bpy

scene = bpy.context.scene
view_layer = scene.view_layers[0]

# Основные проходы
view_layer.use_pass_combined = True
view_layer.use_pass_z = True              # Depth
view_layer.use_pass_normal = True         # Normal
view_layer.use_pass_mist = True           # Mist
view_layer.use_pass_ambient_occlusion = True  # AO
view_layer.use_pass_emission = True       # Emission
view_layer.use_pass_shadow = True         # Shadow
view_layer.use_pass_diffuse_color = True  # DiffCol
view_layer.use_pass_glossy_color = True   # GlossCol

# Cryptomatte (для масок объектов/материалов)
view_layer.use_pass_cryptomatte = True
view_layer.cryptomatte_use_object = True
view_layer.cryptomatte_use_material = True
view_layer.cryptomatte_use_asset = True

# Freestyle (контурные линии)
scene.render.use_freestyle = True
view_layer.use_freestyle = True

# Настройки Mist
scene.world.mist_settings.start = 1.0
scene.world.mist_settings.depth = 50.0
scene.world.mist_settings.falloff = 'QUADRATIC'

# Настройки Cycles для качества
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.cycles.denoiser = 'OPTIX'  # 'OPENIMAGEDENOISE' / 'OPTIX'
scene.cycles.denoising_prefilter = 'ACCURATE'
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.01
scene.cycles.adaptive_min_samples = 32

print("Render passes enabled!")
```

### BASIC COMPOSITOR SETUP
```python
def setup_compositor():
    scene = bpy.context.scene
    scene.use_nodes = True
    tree = scene.node_tree
    nodes = tree.nodes
    links = tree.links
    nodes.clear()
    
    # === INPUT NODES ===
    # Render Layers
    rl = nodes.new('CompositorNodeRLayers')
    rl.location = (-400, 0)
    rl.layer = "ViewLayer"
    
    # === COLOR CORRECTION ===
    # Color Balance (Lift/Gamma/Gain)
    color_bal = nodes.new('CompositorNodeColorBalance')
    color_bal.location = (0, 200)
    color_bal.correction_method = 'LIFT_GAMMA_GAIN'
    # Lift (теня) - тёплые
    color_bal.lift = (1.02, 1.0, 0.98)
    # Gamma (полутона) - нейтральные
    color_bal.gamma = (1.0, 1.0, 1.0)
    # Gain (светлые) - холодные
    color_bal.gain = (0.98, 1.0, 1.02)
    
    # Hue/Saturation/Value
    hsv = nodes.new('CompositorNodeHueSat')
    hsv.location = (200, 200)
    hsv.color_saturation = 1.1
    hsv.color_value = 1.0
    hsv.color_hue = 0.0
    
    # Gamma
    gamma = nodes.new('CompositorNodeGamma')
    gamma.location = (400, 200)
    gamma.inputs['Gamma'].default_value = 1.1
    
    # Exposure/Contrast
    exp = nodes.new('CompositorNodeExposure')
    exp.location = (600, 200)
    exp.inputs['Exposure'].default_value = 0.1
    exp.inputs['Contrast'].default_value = 1.05
    
    # === EFFECTS ===
    
    # Glare (Bloom)
    glare = nodes.new('CompositorNodeGlare')
    glare.location = (0, -200)
    glare.glare_type = 'FOG_GLOW'
    glare.quality = 'HIGH'
    glare.iterations = 5
    glare.mix = 0.3
    glare.threshold = 0.8
    glare.size = 7
    
    # Lens Distortion
    lens = nodes.new('CompositorNodeLensdist')
    lens.location = (200, -200)
    lens.distort = 0.02
    lens.dispersion = 0.01
    
    # Vignette
    vignette = nodes.new('CompositorNodeVignette')
    vignette.location = (400, -200)
    vignette.intensity = 0.3
    vignette.size = 0.8
    
    # Film Grain
    noise = nodes.new('CompositorNodeNoise')
    noise.location = (600, -200)
    noise.noise_type = 'GAUSSIAN'
    noise.inputs['Scale'].default_value = 300
    noise.inputs['Distortion'].default_value = 0.1
    
    mix_grain = nodes.new('CompositorNodeMixRGB')
    mix_grain.location = (800, -200)
    mix_grain.blend_type = 'OVERLAY'
    mix_grain.inputs[0].default_value = 0.03
    
    # === COLOR GRADING (Film Look) ===
    # Color Matrix (LUT-like)
    cm = nodes.new('CompositorNodeColorMatrix')
    cm.location = (800, 200)
    # Teal & Orange lookup
    cm.matrix = [
        1.1, -0.1, -0.1, 0,
        -0.1, 1.0, -0.1, 0,
        -0.1, -0.1, 1.1, 0,
        0, 0, 0, 1
    ]
    
    # === OUTPUT ===
    comp = nodes.new('CompositorNodeComposite')
    comp.location = (1000, 0)
    
    viewer = nodes.new('CompositorNodeViewer')
    viewer.location = (1000, -200)
    viewer.use_alpha = False
    
    # === LINKS ===
    links.new(rl.outputs['Image'], color_bal.inputs['Image'])
    links.new(color_bal.outputs['Image'], hsv.inputs['Image'])
    links.new(hsv.outputs['Image'], gamma.inputs['Image'])
    links.new(gamma.outputs['Image'], exp.inputs['Image'])
    links.new(exp.outputs['Image'], glare.inputs['Image'])
    links.new(glare.outputs['Image'], lens.inputs['Image'])
    links.new(lens.outputs['Image'], vignette.inputs['Image'])
    links.new(vignette.outputs['Image'], mix_grain.inputs[1])
    links.new(noise.outputs['Image'], mix_grain.inputs[2])
    links.new(mix_grain.outputs['Image'], cm.inputs['Image'])
    links.new(cm.outputs['Image'], comp.inputs['Image'])
    links.new(cm.outputs['Image'], viewer.inputs['Image'])
    
    # === PASSES OUTPUT (для EXR) ===
    # File Output для слоёв
    file_out = nodes.new('CompositorNodeOutputFile')
    file_out.location = (1000, -400)
    file_out.format.file_format = 'OPEN_EXR_MULTILAYER'
    file_out.format.color_mode = 'RGBA'
    file_out.format.color_depth = '32'
    file_out.base_path = "//renders/exr/"
    
    # Подключить проходы
    passes = ['Image', 'Depth', 'Normal', 'Mist', 'AO', 'Emission', 'Shadow', 'Cryptomatte00', 'Cryptomatte10']
    for i, pass_name in enumerate(passes):
        if pass_name in rl.outputs:
            file_out.layer_slots.new(pass_name)
            links.new(rl.outputs[pass_name], file_out.inputs[pass_name])
    
    print("Compositor setup complete!")

setup_compositor()
```

### CRYPTOMATTE MASKING
```python
def setup_cryptomatte_mask(material_name, output_node):
    """Создать маску по Cryptomatte для материала"""
    tree = bpy.context.scene.node_tree
    nodes = tree.nodes
    links = tree.links
    
    rl = nodes.get('Render Layers')
    if not rl:
        return
    
    # Cryptomatte нода
    crypto = nodes.new('CompositorNodeCryptomatte')
    crypto.location = (200, -400)
    crypto.matte_id = material_name  # или ID объекта
    crypto.use_matte_output = True
    
    links.new(rl.outputs['Cryptomatte00'], crypto.inputs['Image'])
    links.new(crypto.outputs['Matte'], output_node.inputs['Fac'])
```

### DEPTH OF FIELD (POST)
```python
def setup_dof_post(z_input, focus_distance=5.0, fstop=2.8, max_blur=20):
    """DOF в пост-продакшене через Z-pass"""
    tree = bpy.context.scene.node_tree
    nodes = tree.nodes
    links = tree.links
    
    # Defocus нода
    defocus = nodes.new('CompositorNodeDefocus')
    defocus.location = (400, 0)
    defocus.use_zbuffer = True
    defocus.fStop = fstop
    defocus.maxblur = max_blur
    defocus.bokeh_type = 'POLYGON'
    defocus.blade_count = 8
    defocus.rotation = 0
    
    links.new(nodes['Render Layers'].outputs['Image'], defocus.inputs['Image'])
    links.new(nodes['Render Layers'].outputs['Depth'], defocus.inputs['Z'])
    
    return defocus
```

### EXPORT SETTINGS
```python
def setup_render_output(format='PNG', color_mode='RGBA', depth='16', filepath="//renders/"):
    scene = bpy.context.scene
    scene.render.filepath = filepath
    scene.render.image_settings.file_format = format
    scene.render.image_settings.color_mode = color_mode
    scene.render.image_settings.color_depth = depth
    scene.render.image_settings.compression = 90
    
    if format == 'OPEN_EXR':
        scene.render.image_settings.exr_codec = 'ZIP'
        scene.render.image_settings.use_preview = True
    
    # Для анимации
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.ffmpeg.audio_codec = 'AAC'
    scene.render.ffmpeg.audio_bitrate = 192

# EXR MultiLayer для Nuke/After Effects
setup_render_output('OPEN_EXR', 'RGBA', '32', "//renders/exr/")
# PNG для быстрого превью
setup_render_output('PNG', 'RGBA', '16', "//renders/png/")
```

### ADVANCED: COLOR GRADING NODES
```python
def create_film_look_nodes(tree):
    """Создать ноды для киноподобного образа"""
    nodes = tree.nodes
    links = tree.links
    
    # 1. Log -> Linear (если исходник в Log)
    # log2lin = nodes.new('CompositorNodeColorSpace')
    # log2lin.location = (0, 400)
    # log2lin.color_space = 'LOG_TO_LINEAR'
    
    # 2. Contrast Curve
    rgb_curves = nodes.new('CompositorNodeRGBCurve')
    rgb_curves.location = (0, 400)
    # S-кривая
    for curve in rgb_curves.mapping.curves:
        curve.points[0].location = (0, 0)
        curve.points[1].location = (0.25, 0.2)
        curve.points[2].location = (0.5, 0.5)
        curve.points[3].location = (0.75, 0.8)
        curve.points[4].location = (1, 1)
    
    # 3. Lift/Gamma/Gain (Color Balance)
    cdl = nodes.new('CompositorNodeColorBalance')
    cdl.location = (200, 400)
    cdl.correction_method = 'LIFT_GAMMA_GAIN'
    cdl.lift = (1.02, 1.01, 1.0)      # Shadows -> warm
    cdl.gamma = (1.0, 1.0, 1.0)       # Midtones -> neutral
    cdl.gain = (0.98, 1.0, 1.02)      # Highlights -> cool
    
    # 4. Saturation
    sat = nodes.new('CompositorNodeHueSat')
    sat.location = (400, 400)
    sat.color_saturation = 1.15
    
    # 5. Vignette
    vign = nodes.new('CompositorNodeVignette')
    vign.location = (600, 400)
    vign.intensity = 0.25
    
    # 5. Grain
    grain = nodes.new('CompositorNodeNoise')
    grain.location = (800, 400)
    grain.noise_type = 'GAUSSIAN'
    grain.inputs['Scale'].default_value = 400
    
    mix_grain = nodes.new('CompositorNodeMixRGB')
    mix_grain.location = (1000, 400)
    mix_grain.blend_type = 'OVERLAY'
    mix_grain.inputs[0].default_value = 0.02
    
    return {
        'curves': rgb_curves,
        'cdl': cdl,
        'sat': sat,
        'vignette': vign,
        'grain': grain,
        'mix_grain': mix_grain,
    }
```

---

## 📊 COMPOSITOR NODES REFERENCE

| Категория | Ноды | Назначение |
|-----------|------|------------|
| **Input** | Render Layers, Image, Movie Clip, Texture | Источники |
| **Color** | Color Balance, Hue/Sat, Gamma, Exposure, RGB Curves, Color Matrix | Коррекция цвета |
| **Filter** | Blur, Defocus, Glare, Kuwahara, Bilateral, Despeckle | Размытие/резкость |
| **Distort** | Lens Dist, Displace, Transform, Crop, Flip | Геометрия |
| **Matte** | Cryptomatte, ID Mask, Chroma Key, Difference | Маски |
| **Convert** | Color Space, Premult, Alpha Over, Set Alpha | Альфа/премальт |
| **Output** | Composite, Viewer, File Output, Map Viewer | Результат |

---

## 💡 PRO TIPS

| Tip | Why |
|-----|-----|
| Работай в EXR 32-bit | Максимальный 다이내мик, без бандинга |
| Используй Viewer Node | Мгновенный предпросмотр |
| Группируй ноды (Ctrl+G) | Читаемость сложных деревьев |
| Сохраняй пресеты нод (Node Groups) | Переиспользование |
| Denoise в рендере + Glare в компе | Меньше артефактов |
| Cryptomatte для селекций | Никакого ручного маскирования |

---

## 🔗 LINKS

- **Prompts:** [P13 Lighting](./13_lighting_hdri.md), [P14 Camera](./14_camera_composition.md)
- **Workflows:** [WF 01: Text-to-Scene](../workflows/wf_01_text_to_scene.md), [WF 08: Batch Processing](../workflows/wf_08_batch_processing.md)
- **Cases:** [Case 01: ArchViz](../cases/case_01_archviz_interior.md), [Case 03: Product Viz](../cases/case_03_product_viz.md)
- **MCP Tools:** `execute_blender_code`, `get_viewport_screenshot`

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/prompts/15_compositing.md` |
| Russian | `multilang/ru/prompts/15_compositing.md` |