---
id: setup_53_flamenco_farm
lang: ru
category: setups
type: setup
status: full
tags: [render-farm, setup]
---
# SETUP 53: FLAMENCO FARM CLUSTER

**ID:** SETUP-53 | **Type:** Render Farm | **Difficulty:** ⭐⭐⭐ | **Time:** 40 min
**RU/EN Bilingual**

> Когда применять: когда одна машина не справляется и нужно собрать ферму из
> нескольких узлов с общим диском.

---

## 🎯 ЦЕЛЬ

Разобрать архитектуру Flamenco (менеджер + воркеры + общее хранилище) и собрать
рабочий кластер. Статья намеренно **не выдумывает имена флагов**: конкретные
ключи конфигурации менялись между релизами 3.x, поэтому ниже приведена
проверяемая схема и то, что точно можно проверить самому.

Проверяемые факты ниже относятся к Blender 5.2.1 LTS и shell-утилитам Linux/Windows.

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Flamenco | релиз 3.x (см. репозиторий проекта) | Менеджер и воркеры |
| Blender | одна и та же версия на всех узлах | Иначе разный результат кадра |
| Общее хранилище | NFS (Linux↔Linux) или SMB (с Windows) | Сцена на всех узлах |
| GPU | NVIDIA + драйвер, `nvidia-smi` на каждом узле | Рендер на GPU, не CPU |
| Сеть | 1 Gbps между узлами | Сцена и результаты ходят туда-сюда |

---

## 🛠️ НАСТРОЙКА

### 1. Понять архитектуру

```
┌──────────────────────┐   HTTP    ┌──────────────────────────┐
│  Браузер / API-клиент│──────────▶│  Flamenco manager        │
└──────────────────────┘           │  очередь, деплой, логи    │
                                   └───────────┬──────────────┘
                                               │ очередь задач
                       ┌───────────────────────┼───────────────────────┐
                       ▼                       ▼                       ▼
              ┌────────────────┐      ┌────────────────┐      ┌────────────────┐
              │ worker node 01 │      │ worker node 02 │      │ worker node N  │
              │ blender -b     │      │ blender -b     │      │ blender -b     │
              └────────┬───────┘      └────────┬───────┘      └────────┬───────┘
                       └───────────────────────┼───────────────────────┘
                                               ▼
                        ┌──────────────────────────────────┐
                        │  Shared storage (NFS / SMB)      │
                        │  сцены, текстуры, output, логи   │
                        └──────────────────────────────────┘
```

Ключевое: **менеджер не рендерит**. Он только раздаёт задания и собирает статусы.
Если менеджер видит «idle workers» при полной очереди — проблема в сетевом
хранилище или в том, что воркер не смог открыть файл сцены.

### 2. Поставить один менеджер

```bash
# Источник сборок — официальный репозиторий проекта:
# https://github.com/blender/flamenco
# Конкретные имена релизов и файлов проверяйте в Releases, а не по памяти:
curl -s https://api.github.com/repos/blender/flamenco/releases/latest \
  | grep -E '"tag_name"|browser_download_url'
```

```bash
# Первый запуск: посмотреть справку своей сборки, а не гадать.
./flamenco --help
./flamenco --version
```

> [!NOTE]
> Имя бинарника, набор подкоманд и ключи YAML-конфигурации менялись между
> релизами Flamenco 3.x: в ранних версиях это были отдельные `flamenco-manager`
> и `flamenco-worker`, позже роль воркера переименовали в «агент». Поэтому
> здесь нет ни одной строки конфига — она была бы выдумкой. Правильный путь:
> открыть README той версии, которую вы ставите, и сверить с выводом
> `flamenco --help` на своей машине.

### 3. Поднять воркер и проверить его до подключения к ферме

Префлайт-скрипт ловит 90 % проблем до того, как они станут «воркер молча
падает на втором кадре».

```bash
#!/usr/bin/env bash
# node-preflight.sh — запускать на КАЖДОМ воркере
set -euo pipefail
echo "== blender =="
blender --version | head -3
echo "== gpu =="
command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv || echo "NO NVIDIA GPU"
echo "== storage write/read =="
STORAGE_MOUNT="${STORAGE_MOUNT:-/mnt/farm}"
mkdir -p "$STORAGE_MOUNT/_selftest"
dd if=/dev/urandom of="$STORAGE_MOUNT/_selftest/t.bin" bs=1M count=64 status=none
sync   # NFS: без sync кэш может не уехать до следующей проверки
md5sum "$STORAGE_MOUNT/_selftest/t.bin"
rm -f "$STORAGE_MOUNT/_selftest/t.bin"
echo "== ok =="
```

### 4. Смонтировать общее хранилище

```bash
# --- Сервер (экспорт NFS) ---
sudo apt install -y nfs-kernel-server
echo "/mnt/farm *(rw,sync,no_subtree_check)" >> /etc/exports
sudo exportfs -ra
systemctl restart nfs-server

# --- Воркер (клиент NFS) ---
sudo apt install -y nfs-common
mkdir -p /mnt/farm
echo "FARM_HOST:/mnt/farm /mnt/farm nfs defaults,vers=4.1 0 0" >> /etc/fstab
sudo mount -a
df -h /mnt/farm
```

С `sync` в экспорте NFS запись идёт сразу на диск — медленнее, но после
перезагрузки узла не теряются готовые кадры. `no_root_squash` добавляйте
осознанно: без него воркер, запущенный не от root, не сможет писать в
директорию, созданную менеджером.

### 5. Разбить анимацию на чанки

Менеджер сам раздаёт отдельные кадры, но рендер крупными блоками устойчивее к
перезапускам: упал узел — потерян блок, а не 400 кадров.

```python
# split_chunks.py — обычный Python, без зависимостей от Flamenco.
def chunks(start: int, end: int, size: int):
    """Вернуть список (first, last) включительно. end >= start, size > 0."""
    if end < start or size <= 0:
        raise ValueError("bad range")
    return [(f, min(f + size - 1, end))
            for f in range(start, end + 1, size)]

for first, last in chunks(1, 250, 25):
    print(f"-s {first} -e {last}")
```

```bash
# Команда, которую воркер выполнит на одном блоке.
# Все флаги проверены: -b (background), -E (движок), -o (шаблон имени),
# -s/-e (диапазон), -j (потоки), -a (анимация).
blender -b //scenes/main.blend \
  -E CYCLES \
  -o "//output/anim_####" \
  -s 1 -e 25 -j 1 \
  -a
```

### 6. Считать прогресс по логам

Blender печатает в stdout построчный прогресс и строку сохранения кадра. Эти
две подстроки стабильны и годятся как якоря для парсинга.

```bash
# Следить за прогрессом на узле:
tail -f worker.log | grep --line-buffered -E "Fra:|Saved:"

# Сколько кадров реально готово на общем диске:
ls //output/anim_####.exr 2>/dev/null | wc -l
```

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
# Быстрая проверка, что менеджер и воркер одной версии — иначе они не договорятся
flamenco --version            # на менеджере
flamenco --version            # на каждом воркере: строки должны совпадать
```

| Параметр / понятие | Значение | Когда менять |
|---|---|---|
| Размер чанка | 25–50 кадров | Крупнее — больше потеряешь при падении узла |
| `max_concurrent_tasks` | 1 на GPU | Два процесса на одной карте делят VRAM и оба падают |
| Версия Blender | строго одна | Иначе часть кадров уйдёт в другой результат |
| NFS `sync` | включён | Выключить только если готовы терять кадры при ребуте узла |
| `-E CYCLES` | явно | Не полагаться на движок из сохранённой сцены |
| Превью-рендер | 1 кадр на узел | Проверить, что GPU вообще считает, до отправки 250 кадров |

> [!NOTE]
> Список ключей конфигурации воркера (имя файла конфига, ключи GPU, лимит
> задач) не приводится: он различается между релизами Flamenco 3.x. Откройте
> README и `--help` вашей версии. Проверяемые вещи — `flamenco --version`,
> `--help`, префлайт-скрипт выше и флаги самого Blender.

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Воркер подключается и сразу отваливается | Несовпадение версий менеджера и воркера | Сверить `flamenco --version` на обеих сторонах |
| Очередь растёт, воркеры «idle» | Воркер не видит сцену на общем диске | Проверить `mount`, права на каталог, `no_root_squash` |
| Кадры пересчитываются дважды | Два воркера взяли один и тот же блок | Уменьшить блок; проверить, что не запущено два менеджера на одном хранилище |
| Часть кадров темнее остальных | Разные версии Blender или разные GPU-драйверы | Свести версии и драйверы к одному; перерендерить несогласованный блок |
| OOM на тяжёлом кадре, узел уходит в swap | Нет лимита памяти на задачу | Ограничить RAM на воркере; упростить сцену (см. P30) |
| NFS-монтирование есть, но файлы «долгие» | Забыт `sync` в экспорте, кэш на клиенте | Добавить `sync` в `/etc/exports`, `exportfs -ra`, перемонтировать |
| Панель показывает статусы, которых нет в UI менеджера | Ожидание полей от другой версии | Не опираться на скриншоты: смотрите фактический веб-интерфейс своей версии |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [P29: BATCH PROCESSING & CLI](../prompts/29_batch_cli.md), [P47: ALEMBIC CACHE PIPELINE](../prompts/47_alembic_cache.md), [P49: RENDER FARM SUBMIT](../prompts/49_farm_submit.md)
- **Теги:** #render-farm, #setup
