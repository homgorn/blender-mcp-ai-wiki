---
id: wf_01_text_to_scene
lang: es
orig_lang: ru
category: workflows
type: workflow
difficulty: 2
translation: human
---
# WF 01: TEXTO-A-ESCENA

**ID:** WF-01 | **Tipo:** Pipeline completo | **Dificultad:** ⭐⭐ | **Tiempo:** 15-30 min

---

## 🎯 OBJETIVO
Pipeline completo: descripción textual → escena 3D (geometría, materiales, luz, cámara, render)

---

## 📋 ARQUITECTURA DEL PIPELINE

```
USER PROMPT
    │
    ▼
┌─────────────────────────────────────┐
│  LLM AGENT (OpenCode/Claude)        │
│  - Analiza la descripción           │
│  - Planifica los pasos              │
│  - Llama herramientas MCP           │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  BLENDER-MCP SERVER (localhost:9876)│
│  - create_object                    │
│  - set_material                     │
│  - download_polyhaven_asset         │
│  - execute_blender_code             │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  BLENDER (ejecución bpy)            │
│  - Creación de geometría            │
│  - Asignación de materiales         │
│  - Configuración de luz             │
│  - Posicionamiento de cámara        │
│  - Ejecución de render              │
└─────────────────────────────────────┘
    │
    ▼
RESULTADO: Imagen renderizada / archivo .blend / exportación GLB
```

---

## 📝 EJEMPLOS DE PROMPTS

### Simple: Habitación
```
"Crea una habitación de 5x5x3m: suelo, 4 paredes, techo.
Añade una ventana de 1.5x1.5m en la pared frontal (boolean).
Materiales: paredes - yeso blanco, suelo - parquet, ventana - cristal.
Luz: HDRI 'studio' 2k de Poly Haven.
Cámara: en la esquina, mirando al centro, 35mm.
Render: Cycles, 128 samples, 1920x1080, guardar en //renders/room.png"
```

### Medio: Localización de juego
```
"Crea una sala de mazmorra de 10x10x5m estilo dark fantasy.
Paredes: mampostería con grietas (PBR).
Suelo: losas de piedra con musgo en las juntas.
Atrezzo: 3 columnas, 2 cofres, altar en el centro.
Iluminación: 3 puntuales (fuego) + HDRI 'dungeon' tenue.
Partículas: polvo en los rayos (volume scatter).
Cámara: contrapicado, DOF en el altar.
Render: 256 samples, denoising ON"
```

### Complejo: Ciudad procedural
```
"Genera un barrio procedural de 200x200m:
- Malla 10x10 edificios, altura aleatoria 10-50m
- Arquitectura: modernismo / neoclásico / futurismo (pesos 40/30/30)
- Calles entre edificios, aceras, farolas cada 20m
- Parques en el 15% en vez de edificios
- HDRI 'city_day' 4k, luz solar
- LOD: edificios cercanos high-poly, lejanos low-poly
- Exportar: GLB con LODs, texturas 2k"
```

---

## 🔧 COMANDOS MCP POR ETAPAS

### Etapa 1: Geometría base
```bash
# Limpiar
"Elimina todos los objetos excepto cámara y luz"

# Suelo
"Crea un plano 'Floor' de 10x10m en (0,0,0)"

# Paredes (4)
"Crea un cubo 'Wall_Front' de 10x0.2x3m en (0, -5, 1.5)"
"Crea un cubo 'Wall_Back' de 10x0.2x3m en (0, 5, 1.5)"
"Crea un cubo 'Wall_Left' de 0.2x10x3m en (-5, 0, 1.5)"
"Crea un cubo 'Wall_Right' de 0.2x10x3m en (5, 0, 1.5)"

# Techo
"Crea un plano 'Ceiling' de 10x10m en (0,0,3)"
```

### Etapa 2: Booleanos (ventanas/puertas)
```bash
# Ventana
"Crea un cubo 'Window_Cut' de 2x0.3x1.5m en (0, -5.1, 1.5)
Resta Window_Cut de Wall_Front (DIFFERENCE)"

# Puerta
"Crea un cubo 'Door_Cut' de 1x0.3x2.2m en (-2, -5.1, 1.1)
Resta Door_Cut de Wall_Front (DIFFERENCE)"
```

### Etapa 3: Materiales
```bash
# Suelo - parquet
"Crea material 'Mat_Parquet': BaseColor #8B7355, Roughness 0.6, Metallic 0
Asígnaselo a Floor"

# Paredes - yeso
"Crea material 'Mat_Plaster': BaseColor #F5F0E8, Roughness 0.85
Asígnaselo a Wall_Front, Wall_Back, Wall_Left, Wall_Right, Ceiling"

# Cristal
"Crea material 'Mat_Glass': Transmission 1.0, IOR 1.45, Roughness 0
Asígnaselo a las ventanas"
```

### Etapa 4: Assets de Poly Haven
```bash
# HDRI
"Busca en Poly Haven el HDRI 'studio' categoría 'indoor' 2k
Descárgalo y ponlo como World Environment"

# Modelos (opcional)
"Busca en Poly Haven el modelo 'chair' categoría 'furniture' 1k
Descarga y coloca 3 sillas alrededor de la mesa"
```

### Etapa 5: Cámara y render
```bash
# Cámara
"Crea una cámara 'Cam_Main' en (7, -7, 4) mirando al centro, 35mm
Hazla activa: bpy.context.scene.camera = bpy.data.objects['Cam_Main']
DOF en el objeto central"

# Render
"Configura Cycles: 128 samples, denoising ON, 1920x1080
Renderiza y guarda en //renders/scene_01.png"
```

---

## 🎯 PARÁMETROS DE CALIDAD

| Nivel | Samples | Denoising | Resolución | Tiempo (RTX 3080) |
|-------|---------|-----------|------------|-------------------|
| **Borrador** | 32 | ON | 1280x720 | ~15 seg |
| **Vista previa** | 64 | ON | 1920x1080 | ~30 seg |
| **Final** | 128 | ON | 1920x1080 | ~1 min |
| **Producción** | 256 | ON + OptiX | 3840x2160 | ~5 min |

---

## 🔗 ENLACES

- **Prompts:** [P01-P05](../prompts/), [P09-P15](../materials/), [P16-P21](../lighting/)
- **Casos:** [Case 01: ArchViz](../cases/case_01_archviz_interior.md), [Case 02: Game Props](../cases/case_02_game_props.md)
- **Setup:** [Setup 01: blender-mcp](../setups/setup_01_blender_mcp_basic.md)
- **Siguiente:** [WF 02: Image-to-3D](../workflows/wf_02_image_to_3d.md)
