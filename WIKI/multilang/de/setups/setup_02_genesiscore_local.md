---
id: setup_02_genesiscore_local
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: human
---
# SETUP 02: GENESISCORE LOKAL (OLLAMA)

**ID:** SETUP-02 | **Typ:** Lokale LLM-Integration | **Schwierigkeit:** ⭐⭐ | **Zeit:** 15-30 Min

---

## 🎯 ZIEL
GenesisCore für lokale LLMs via Ollama einrichten (Privatsphäre, kostenlos, offline)

---

## 📋 VORAUSSETZUNGEN

| Komponente | Version | Status |
|-----------|--------|--------|
| **Blender** | 4.0+ | ✅ Erforderlich |
| **Ollama** | latest | ✅ Erforderlich |
| **RAM** | 16GB+ | 🟡 Empfohlen |
| **VRAM** | 8GB+ | 🟡 Für 7B+ Modelle |

---

## 🪟 WINDOWS-INSTALLATION

### 1. Ollama installieren
```powershell
# Herunterladen und installieren
winget install Ollama.Ollama

# Oder von der offiziellen Website
# https://ollama.com/download/windows

# Prüfen
ollama --version
ollama list
```

### 2. Modelle für Coding/Blender laden
```powershell
# Beste Modelle für Blender Python (nach Priorität)
ollama pull codellama:13b        # Bestes für Code, 7.3GB
ollama pull deepseek-coder:6.7b  # Exzellent für Python, 3.8GB
ollama pull qwen2.5-coder:7b     # Neu, schnell, 4.7GB
ollama pull llama3.2:3b          # Leicht, schnell, 2.0GB

# Prüfen
ollama list
```

### 3. Ollama-Server starten
```powershell
# Sollte im Hintergrund laufen (Autostart bei Installation)
# Prüfen:
curl http://localhost:11434/api/tags

# Falls nicht:
ollama serve
```

---

## 🔧 GENESISCORE-EINRICHTUNG

### 1. Addon installieren (falls noch nicht)
```bash
# In Blender: Edit → Preferences → Add-ons → Install from ZIP
# Wählen: GenesisCore-main.zip
# Aktivieren: GenesisCore
```

### 2. Provider einrichten
```
N-Panel → Reiter GenesisCore:
1. Provider: ▼ Ollama
2. Base URL: http://localhost:11434/v1  (wichtig: /v1 am Ende!)
3. API Key: (leer lassen für Ollama)
4. "Fetch Models" klicken
4. Modell wählen: codellama:13b / deepseek-coder:6.7b / qwen2.5-coder:7b
5. Tool Modules: alle aktivieren (Shift+Click)
6. Save Config
7. Connect
```

### 3. Modell-Einstellungen (empfohlen)
```json
{
  "provider": "Ollama",
  "base_url": "http://localhost:11434/v1",
  "model": "codellama:13b",
  "temperature": 0.1,
  "top_p": 0.9,
  "max_tokens": 4096,
  "use_history": true
}
```

---

## 🔧 LEISTUNGSOPTIMIERUNG

### GPU Offloading (NVIDIA)
```powershell
# Ollama nutzt die GPU automatisch bei CUDA
# Prüfen:
ollama run codellama:13b "test"
# Sollte zeigen: "using GPU" in den Logs

# GPU-Layer erzwingen:
# In Umgebungsvariablen:
OLLAMA_NUM_GPU=999
OLLAMA_GPU_LAYERS=999
```

### Speicheroptimierung
```yaml
# In GenesisCore-Einstellungen:
use_history: false          # Verlauf deaktivieren um Tokens zu sparen
max_tokens: 2048            # Antwortlänge begrenzen
temperature: 0.1            # Deterministische Antworten
```

### Quantisierung (bei wenig VRAM)
```powershell
# Quantisierte Versionen nutzen:
ollama pull codellama:13b-q4_K_M   # 4-bit, 7.3GB → 4.7GB
ollama pull deepseek-coder:6.7b-q4_K_M  # 3.8GB → 2.5GB
```

---

## 🧪 TESTS

### Schnelltest im GenesisCore-Chat
```
"Erstelle einen Würfel 'TestCube' an Position (1, 2, 3) mit rotem Material"
```

### Erwartetes Ergebnis
1. Der Agent analysiert die Anfrage
2. Ruft `create_object` + `set_material` auf
3. In Blender erscheint ein Würfel bei (1, 2, 3) mit rotem Material

---

## 🔧 FEHLERBEHEBUNG

| Problem | Lösung |
|----------|---------|
| `Connection refused` | Ollama läuft nicht → `ollama serve` |
| `Model not found` | `ollama pull <model_name>` |
| `Out of memory` | Kleineres Modell nutzen (3b/7b) oder q4-Quantisierung |
| `Slow response` | GPU-Offloading aktivieren, `max_tokens` senken |
| `Base URL error` | Prüfen: `http://localhost:11434/v1` (mit /v1!) |

---

## 🔗 LINKS

- **Ollama-Modelle:** https://ollama.com/library
- **GenesisCore-Repo:** https://github.com/AIGODLIKE/GenesisCore
- **Setup 01:** [blender-mcp Basic](../setups/setup_01_blender_mcp_basic.md)
- **Nächster:** [Setup 03: Dream Textures](../setups/setup_03_dream_textures.md)
