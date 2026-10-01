---
id: wf_01_text_to_scene
lang: de
orig_lang: ru
category: workflows
type: workflow
difficulty: 2
translation: human
---
# WF 01: TEXT-ZU-SZENE

**ID:** WF-01 | **Typ:** End-to-End-Pipeline | **Schwierigkeit:** ⭐⭐ | **Zeit:** 15-30 Min

---

## 🎯 ZIEL
Komplette Pipeline: Textbeschreibung → 3D-Szene (Geometrie, Materialien, Licht, Kamera, Render)

---

## 📋 PIPELINE-ARCHITEKTUR

```
USER PROMPT
    │
    ▼
┌─────────────────────────────────────┐
│  LLM AGENT (OpenCode/Claude)        │
│  - Beschreibung parsen              │
│  - Schritte planen                  │
│  - MCP-Tools aufrufen               │
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
│  BLENDER (bpy-Ausführung)           │
│  - Geometrie erstellen              │
│  - Materialien zuweisen             │
│  - Licht einrichten                 │
│  - Kamera positionieren             │
│  - Rendern                          │
└─────────────────────────────────────┘
    │
    ▼
ERGEBNIS: Gerendertes Bild / .blend-Datei / GLB-Export
```

---

## 📝 PROMPT-BEISPIELE

### Einfach: Zimmer
```
"Erstelle ein Zimmer 5x5x3m: Boden, 4 Wände, Decke.
Füge ein Fenster 1.5x1.5m in die Vorderwand ein (Boolean).
Materialien: Wände - weißer Putz, Boden - Parkett, Fenster - Glas.
Licht: HDRI 'studio' 2k von Poly Haven.
Kamera: in der Ecke, zur Mitte, 35mm.
Render: Cycles, 128 Samples, 1920x1080, speichern unter //renders/room.png"
```

### Mittel: Dungeon-Raum
```
"Erstelle einen Dungeon-Raum 10x10x5m im Dark-Fantasy-Stil.
Wände: Steinmauerwerk mit Rissen (PBR).
Boden: Steinplatten mit Moos in den Fugen.
Requisiten: 3 Säulen, 2 Truhen, Altar in der Mitte.
Licht: 3 Punktlichter (Feuer) + schwaches HDRI 'dungeon'.
Kamera: Untersicht, DOF auf den Altar.
Render: 256 Samples, Denoising ON"
```

---

## 🔧 MCP-BEFEHLE NACH ETAPPEN

### Etappe 1: Basisgeometrie
```bash
"Erstelle eine Ebene 'Floor' 10x10m bei (0,0,0)"
"Erstelle einen Würfel 'Wall_Front' 10x0.2x3m bei (0, -5, 1.5)"
```

### Etappe 2: Boolean (Fenster/Tür)
```bash
"Erstelle einen Würfel 'Window_Cut' 2x0.3x1.5m bei (0, -5.1, 1.5)
Subtrahiere Window_Cut von Wall_Front (DIFFERENCE)"
```

### Etappe 3: Materialien
```bash
"Erstelle Material 'Mat_Parquet': BaseColor #8B7355, Roughness 0.6
Weise es Floor zu"
```

### Etappe 4: Poly Haven
```bash
"Suche auf Poly Haven das HDRI 'studio' Kategorie 'indoor' 2k
Lade es und setze es als World"
```

### Etappe 5: Kamera und Render
```bash
"Erstelle Kamera 'Cam_Main' bei (7, -7, 4) zur Mitte, 35mm
Mache sie aktiv, DOF auf das Zentrum"
"Stelle Cycles ein: 128 Samples, Denoising ON, 1920x1080
Rendere nach //renders/scene_01.png"
```

---

## 🔗 LINKS

- **Setups:** [Setup 01: blender-mcp](../setups/setup_01_blender_mcp_basic.md)
- **Nächster:** [WF 02: Image-to-3D](../workflows/wf_02_image_to_3d.md)
