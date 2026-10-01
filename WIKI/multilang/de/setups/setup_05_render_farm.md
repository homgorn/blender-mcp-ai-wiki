---
id: setup_05_render_farm
lang: de
orig_lang: ru
category: setups
type: setup
difficulty: 3
translation: template
---
# СЕТАП 05: RENDER FARM (FLAMENCO)

> Ziel: 

**ID:** setup_05_render_farm | **Lang:** de | **Orig:** ru | **Category:** setups | **Tags:** **

## Verwendung
Dies ist die deutsche Version von 'setup_05_render_farm'. Code-Blöcke sind sprachunabhängig. Schritte der Reihe nach ausführen und prüfen.

## MCP-Prompt (kopieren)
```
setup_05_render_farm / setups / **
```

> Hinweis: Code/Pfade bleiben englisch (Blender/Python-Kompatibilität).

---

---
id: setup_05_render_farm
lang: ru
orig_lang: ru
category: setups
type: setup
difficulty: 3
---

# СЕТАП 05: RENDER FARM (FLAMENCO)

> Цель: ## 🌍 MULTILANG

**ID:** setup_05_render_farm | **Lang:** ru | **Orig:** ru | **Category:** setups | **Tags:** 

---

# SETUP 05: RENDER FARM (FLAMENCO)

**ID:** SETUP-05 | **Type:** Distributed Rendering | **Difficulty:** ⭐⭐⭐ | **Time:** 30-60 min

---

## 🎯 ЦЕЛЬ
Настроить Flamenco (официальный рендер-ферма Blender) для распределённого рендеринга на кластере машин

---

## 📋 АРХИТЕКТУРА FLAMENCO

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   MANAGER   │────▶│   WORKER 1  │     │   WORKER N  │
│  (Server)   │     │  (Render)   │     │  (Render)   │
│  Port 8080  │     │  Port 8081  │     │  Port 8081  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────┐
│              SHARED STORAGE (NFS/SMB)               │
│  .blend files  |  Textures  |  Output  |  Logs      │
└─────────────────────────────────────────────────────┘
```

---

## 🖥️ ТРЕБОВАНИЯ

| Компонент | Manager | Worker |
|-----------|---------|--------|
| **OS** | Linux (Ubuntu 22.04+) | Linux / Windows / macOS |
| **CPU** | 4+ cores | 8+ cores (по ядру на таск) |
| **RAM** | 8 GB | 16-32 GB |
| **GPU** | Не обязательно | NVIDIA RTX (CUDA) |
| **Storage** | 100 GB+ (SSD) | 50 GB+ |
| **Network** | 1 Gbps+ | 1 Gbps+ |
| **Blender** | 4.0+ | 4.0+ (та же версия) |

---

## 📦 УСТАНОВКА MANAGER (SERVER)

### 1. Скачать Flamenco
```bash
# Последний релиз:
# https://github.com/blender/flamenco/releases/latest

# Скачать flamenco-manager-linux.tar.gz
wget https://github.com/blender/flamenco/releases/download/v3.6/flamenco-manager-linux.tar.gz
tar -xzf flamenco-manager-linux.tar.gz
cd flamenco-manager
```

### 2. Конфигурация (flamenco-manager.yaml)
```yaml
# flamenco-manager.yaml
manager:
  listen_addr: "0.0.0.0:8080"
  auth:
    jwt_secret: "your-super-secret-jwt-key-change-me"
    allow_anonymous: false
  
storage:
  local:
    path: "/mnt/flamenco-storage"
    # или NFS: "nfs://server:/path"

database:
  sqlite:
    path: "/var/lib/flamenco/flamenco.sqlite"

blender:
  executable: "/usr/bin/blender"
  # или путь к конкретной версии

log:
  level: "info"
  json: false
```

### 3. Запуск Manager
```bash
# Создать storage
sudo mkdir -p /mnt/flamenco-storage/{jobs,output,logs}
sudo chown -R $USER:$USER /mnt/flamenco-storage

# Запуск
./flamenco-manager -config flamenco-manager.yaml

# Как systemd сервис:
sudo cp flamenco-manager.service /etc/systemd/system/
sudo systemctl enable flamenco-manager
sudo systemctl start flamenco-manager
```

### 4. Проверка
```bash
# Web UI: http://server-ip:8080
# API: http://server-ip:8080/api
curl http://localhost:8080/api/health
```

---

## 🖥️ УСТАНОВКА WORKER (RENDER NODES)

### 1. Установка Worker
```bash
# На каждой рендер-машине:
wget https://github.com/blender/flamenco/releases/download/v3.6/flamenco-worker-linux.tar.gz
tar -xzf flamenco-worker-linux.tar.gz
cd flamenco-worker
```

### 2. Конфигурация Worker (flamenco-worker.yaml)
```yaml
worker:
  manager_url: "http://MANAGER_IP:8080"
  worker_name: "worker-gpu-01"  # уникальное имя
  platform: "linux"  # linux/windows/macos
  
  # GPU настройки
  gpu_devices: ["cuda:0", "cuda:1"]  # или ["all"]
  
  # Blender
  blender_executable: "/usr/bin/blender"
  blender_args: ["--cycles-device", "CUDA"]
  
  # Ресурсы
  max_concurrent_tasks: 2  # по одному на GPU
  cpu_affinity: "auto"
  
  # Storage (shared с Manager)
  storage:
    local:
      path: "/mnt/flamenco-storage"

  # Logs
  log_level: "info"
```

### 3. GPU Настройка (NVIDIA)
```bash
# Установить драйверы
sudo apt install -y nvidia-driver-535 nvidia-cuda-toolkit

# Проверить
nvidia-smi
nvcc --version

# В worker конфиге указать GPU
# gpu_devices: ["cuda:0"]  # для одного GPU
# gpu_devices: ["cuda:0", "cuda:1"]  # для двух GPU
```

### 4. Запуск Worker
```bash
# Тестовый запуск
./flamenco-worker -config flamenco-worker.yaml

# Как systemd сервис (на каждой машине):
sudo cp flamenco-worker.service /etc/systemd/system/
sudo systemctl enable flamenco-worker
sudo systemctl start flamenco-worker

# Проверить статус
sudo systemctl status flamenco-worker
```

---

## 🌐 НАСТРОЙКА СТОРАДЖ (SHARED STORAGE)

### Вариант А: NFS (Linux)
```bash
# На Manager (Server)
sudo apt install nfs-kernel-server
echo "/mnt/flamenco-storage *(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports
sudo exportfs -ra

# На Workers (Client)
sudo apt install nfs-common
sudo mkdir -p /mnt/flamenco-storage
echo "MANAGER_IP:/mnt/flamenco-storage /mnt/flamenco-storage nfs defaults 0 0" >> /etc/fstab
sudo mount -a
```

### Вариант Б: SMB (Cross-platform)
```bash
# На Manager
sudo apt install samba
# smb.conf:
# [flamenco]
#   path = /mnt/flamenco-storage
#   read only = no
#   guest ok = yes

# На Windows Worker
net use Z: \\MANAGER_IP\flamenco /persistent:yes
```

---

## 🚀 ИСПОЛЬЗОВАНИЕ

### 1. Web UI (http://MANAGER_IP:8080)
```
1. Login (admin / пароль из конфига)
2. Jobs → Submit Job
3. Выбрать .blend файл
4. Настроить: Frames, Resolution, Samples, Output
5. Submit
```

### 2. CLI Submission
```bash
# flamenco-cli
pip install flamenco-client

# Submit job
flamenco-cli job submit \
  --manager http://MANAGER:8080 \
  --blend-file scene.blend \
  --frame-start 1 --frame-end 250 \
  --output //renders/anim_#### \
  --engine CYCLES --samples 256
```

### 3. Python API
```python
from flamenco_client import FlamencoClient

client = FlamencoClient("http://MANAGER:8080", token="YOUR_JWT")

job = client.submit_job(
    blend_file="scene.blend",
    frame_range=(1, 250),
    output_path="//renders/anim_####",
    render_settings={
        "engine": "CYCLES",
        "samples": 256,
        "resolution": (3840, 2160),
    }
)

# Poll status
while True:
    status = client.get_job_status(job.id)
    print(f"Progress: {status.progress}%")
    if status.state in ["finished", "failed"]:
        break
    time.sleep(30)
```

---

## 📊 МОНИТОРИНГ И ОПТИМИЗАЦИЯ

### Мониторинг (Prometheus + Grafana)
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'flamenco'
    static_configs:
      - targets: ['MANAGER_IP:8080', 'WORKER1:8081', 'WORKER2:8081']
```

### Ключевые метрики
| Метрика | Норма | Action |
|---------|-------|--------|
| **Queue Length** | < 10 | Добавить workers |
| **Worker Utilization** | 80-95% | Баланс нагрузки |
| **Frame Time** | < 5 мин | Оптимизировать сцену |
| **VRAM Usage** | < 90% | Уменьшить samples/textures |
| **Failed Frames** | < 1% | Проверить логи |

---

## 🔧 ОПТИМИЗАЦИЯ ПРОИЗВОДИТЕЛЬНОСТИ

### Worker Tuning
```yaml
worker:
  max_concurrent_tasks: 2  # 1 на GPU
  blender_args: [
    "--cycles-device", "CUDA",
    "--cycles-feature-set", "SUPPORTED"
  ]
  
  # Для больших сцен
  memory_limit_gb: 20  # лимит RAM на таск
```

### Job Splitting (для больших анимаций)
```yaml
# Разбить 1000 кадров на чанки по 50
frame_chunks: 50
# Flamenco сам распределит между workers
```

---

## 🔗 LINKS

- **Flamenco Repo:** https://github.com/blender/flamenco
- **Docs:** https://flamenco.io/docs/
- **Releases:** https://github.com/blender/flamenco/releases
- **Setup 04:** [Headless Render](../setups/setup_04_headless_render.md)
- **Next:** [Setup 06: Custom MCP Tools](../setups/setup_06_custom_mcp_tools.md)

---

## 🌍 MULTILANG

| Language | File |
|----------|------|
| English | `multilang/en/setups/setup_05_render_farm.md` |
| Russian | `multilang/ru/setups/setup_05_render_farm.md` |