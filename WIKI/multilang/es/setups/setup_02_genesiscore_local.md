---
id: setup_02_genesiscore_local
lang: es
orig_lang: ru
category: setups
type: setup
difficulty: 2
translation: human
---
# CONFIGURACIÓN 02: GENESISCORE LOCAL (OLLAMA)

**ID:** SETUP-02 | **Tipo:** Integración LLM local | **Dificultad:** ⭐⭐ | **Tiempo:** 15-30 min

---

## 🎯 OBJETIVO
Configurar GenesisCore para trabajar con LLM locales vía Ollama (privacidad, gratis, sin conexión)

---

## 📋 REQUISITOS PREVIOS

| Componente | Versión | Estado |
|-----------|--------|--------|
| **Blender** | 4.0+ | ✅ Obligatorio |
| **Ollama** | latest | ✅ Obligatorio |
| **RAM** | 16GB+ | 🟡 Recomendado |
| **VRAM** | 8GB+ | 🟡 Para modelos 7B+ |

---

## 🪟 INSTALACIÓN EN WINDOWS

### 1. Instalar Ollama
```powershell
# Descargar e instalar
winget install Ollama.Ollama

# O desde el sitio oficial
# https://ollama.com/download/windows

# Comprobar
ollama --version
ollama list
```

### 2. Descargar modelos para coding/Blender
```powershell
# Mejores modelos para Blender Python (por prioridad)
ollama pull codellama:13b        # El mejor para código, 7.3GB
ollama pull deepseek-coder:6.7b  # Excelente para Python, 3.8GB
ollama pull qwen2.5-coder:7b     # Nuevo, rápido, 4.7GB
ollama pull llama3.2:3b          # Ligero, rápido, 2.0GB

# Comprobar
ollama list
```

### 3. Iniciar el servidor Ollama
```powershell
# Debe ejecutarse en segundo plano (autostart al instalar)
# Comprobar:
curl http://localhost:11434/api/tags

# Si no funciona:
ollama serve
```

---

## 🔧 CONFIGURACIÓN DE GENESISCORE

### 1. Instalar el addon (si aún no)
```bash
# En Blender: Edit → Preferences → Add-ons → Install from ZIP
# Elegir: GenesisCore-main.zip
# Activar: GenesisCore
```

### 2. Configurar el proveedor
```
N-Panel → pestaña GenesisCore:
1. Provider: ▼ Ollama
2. Base URL: http://localhost:11434/v1  (¡importante: /v1 al final!)
3. API Key: (dejar vacío para Ollama)
4. Pulsar "Fetch Models"
4. Elegir modelo: codellama:13b / deepseek-coder:6.7b / qwen2.5-coder:7b
5. Tool Modules: activar todos (Shift+Click)
6. Save Config
7. Connect
```

### 3. Ajustes del modelo (recomendados)
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

## 🔧 OPTIMIZACIÓN DEL RENDIMIENTO

### GPU Offloading (NVIDIA)
```powershell
# Ollama usa la GPU automáticamente si hay CUDA
# Comprobar:
ollama run codellama:13b "test"
# Debe mostrar: "using GPU" en los logs

# Forzar GPU layers:
# En variables de entorno:
OLLAMA_NUM_GPU=999
OLLAMA_GPU_LAYERS=999
```

### Optimización de memoria
```yaml
# En ajustes de GenesisCore:
use_history: false          # Desactivar historial para ahorrar tokens
max_tokens: 2048            # Limitar la longitud de respuesta
temperature: 0.1            # Respuestas deterministas
```

### Cuantización (si hay poca VRAM)
```powershell
# Usar versiones cuantizadas:
ollama pull codellama:13b-q4_K_M   # 4-bit, 7.3GB → 4.7GB
ollama pull deepseek-coder:6.7b-q4_K_M  # 3.8GB → 2.5GB
```

---

## 🧪 PRUEBAS

### Prueba rápida en el chat de GenesisCore
```
"Crea un cubo 'TestCube' en la posición (1, 2, 3) con material rojo"
```

### Resultado esperado
1. El agente analiza la petición
2. Llama a `create_object` + `set_material`
3. En Blender aparece un cubo en (1, 2, 3) con material rojo

---

## 🔧 SOLUCIÓN DE PROBLEMAS

| Problema | Solución |
|----------|---------|
| `Connection refused` | Ollama no está en marcha → `ollama serve` |
| `Model not found` | `ollama pull <model_name>` |
| `Out of memory` | Usar un modelo menor (3b/7b) o cuantización q4 |
| `Slow response` | Activar GPU offloading, reducir `max_tokens` |
| `Base URL error` | Verificar `http://localhost:11434/v1` (¡con /v1!) |

---

## 🔗 ENLACES

- **Modelos Ollama:** https://ollama.com/library
- **Repo GenesisCore:** https://github.com/AIGODLIKE/GenesisCore
- **Setup 01:** [blender-mcp Basic](../setups/setup_01_blender_mcp_basic.md)
- **Siguiente:** [Setup 03: Dream Textures](../setups/setup_03_dream_textures.md)
