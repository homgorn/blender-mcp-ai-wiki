---
id: setup_54_cloud_render_aws
lang: ru
category: setups
type: setup
status: full
tags: [cloud, render, setup]
---
# SETUP 54: CLOUD RENDER AWS/GCP

**ID:** SETUP-54 | **Type:** Cloud | **Difficulty:** ⭐⭐⭐ | **Time:** 40 min
**RU/EN Bilingual**

> Когда применять: когда дедлайн не ждёт, а рендер занимает 20 часов на одной
> машине.

---

## 🎯 ЦЕЛЬ

Собрать повторяемый облачный рендер: сцена в объектном хранилище, контейнер с
Blender на GPU-инстансе, результат возвращается обратно, счётчик стоимости не
уезжает в космос.

Главный принцип статьи: **сначала измерить, потом покупать**. Один кадр на своём
железе — это честная цифра, из которой считается смета; без неё любой Spot-инстанс
становится азартной игрой.

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| AWS CLI | v2 (проверено: команды `aws s3 sync`) | Синхронизация сцены и результатов |
| Объектное хранилище | S3-совместимое | Промежуточное состояние между узлами |
| Контейнерный образ | CUDA-база + Blender | Инстанс должен запускать то же, что и CI |
| Blender | та же версия, что локально | Иначе другой результат кадра |
| Бюджет-алерт | Billing → Budgets | Страховка от ночного разгона |

---

## 🛠️ НАСТРОЙКА

### 1. Измерить один кадр локально

Единственная цифра, которая нужна до всех облачных трат. Рендерите кадр в фоне
и засекаете время.

```bash
# Проверено: -f рендерит один кадр; -E CYCLES задаёт движок явно.
# Время в конце лога строки вида "Time: 00:12.34" — то, что нужно.
time blender -b scene.blend -E CYCLES -o //bench/frame_#### -f 42
```

Смета считается просто, без допущений о забытых множителях:

```python
# estimate.py — калькулятор сметы. Подавайте ему реальные числа.
def estimate(seconds_per_frame, frames, price_per_hour,
             startup_seconds=180, waste_ratio=0.15):
    """Вернуть (сек, стоимость) с запасом на холодный старт и переделки."""
    compute = seconds_per_frame * frames
    total = compute * (1 + waste_ratio) + startup_seconds
    return total, total / 3600 * price_per_hour

t, cost = estimate(seconds_per_frame=37.4, frames=250, price_per_hour=1.3)
print(f"{t/3600:.2f} h, ${cost:.2f}")   # 2.86 h, $3.72 — до первого Spot
```

Если смета на порядок выше сметы на «обычной машине» — проблема не в облаке, а в
сцене: уменьшайте разрешение, samples, включайте адаптивный семплинг.

### 2. Упаковать сцену в контейнер

```dockerfile
# Dockerfile.blender — проверенная база; версию CUDA подставь под свой драйвер.
FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

ARG BLENDER_VERSION=5.2.1
ARG BLENDER_SHA256=REPLACE_ME   # обязательно: не качайте непроверенные сборки

RUN apt-get update && apt-get install -y --no-install-recommends \
      xz-utils wget python3 \
 && wget -q "https://download.blender.org/release/Blender${BLENDER_VERSION%.*}/blender-${BLENDER_VERSION}-linux-x64.tar.xz" -O /tmp/b.tar.xz \
 && echo "${BLENDER_SHA256}  /tmp/b.tar.xz" | sha256sum -c - \
 && tar -xJf /tmp/b.tar.xz -C /opt \
 && ln -s /opt/blender-${BLENDER_VERSION}-linux-x64/blender /usr/local/bin/blender \
 && rm /tmp/b.tar.xz

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /work
ENTRYPOINT ["blender", "-b"]
```

```bash
docker build -f Dockerfile.blender -t blender-render:5.2.1 .

# Проверка на локальной машине с GPU — обязательна до отправки в облако.
# Несовпадение результатов здесь сэкономит деньги на инстансах.
docker run --rm --gpus all \
  -v "$(pwd)/scenes:/work" -v "$(pwd)/output:/work/output" \
  blender-render:5.2.1 scene.blend -E CYCLES -o //output/anim_#### -s 1 -e 5 -a
```

### 3. Положить и забрать через S3

```bash
# Проверено на AWS CLI: upload — положить, download — забрать.
# --only-show-errors прячет поштучные строки на тысячах файлов.

# 1) Сцена вверх (один раз; дальше меняется только .blend)
aws s3 sync ./scenes s3://acme-render/in/scene_v001/ --only-show-errors

# 2) Результаты вниз, с инкрементальной докачкой (докачка не перезаливает готовое)
aws s3 sync s3://acme-render/out/scene_v001/ ./output/ --only-show-errors

# 3) Что именно улетело — до отправки, а не после
aws s3 ls s3://acme-render/in/scene_v001/ --recursive --summarize
```

Отдельная папка на версию сцены (`scene_v001`, `scene_v002`) — то, что спасает,
когда два инстанса пишут в один префикс: результаты не смешиваются и можно
досчитаться, какой именно набор кадров к какой версии относится.

### 4. Запустить инстанс через user-data

```bash
#!/usr/bin/env bash
# user-data.sh — выполняется один раз при старте инстанса.
set -euo pipefail
exec > >(tee /var/log/render-bootstrap.log | logger -t render -s 2>/dev/console) 2>&1

echo "== обновление пакетов =="
apt-get update -qq && apt-get install -y -qq awscli

echo "== сцена из S3 =="
aws s3 sync s3://${S3_BUCKET}/in/scene_v001/ /work --only-show-errors

echo "== рендер =="
blender -b /work/scene.blend -E CYCLES -o /work/output/anim_#### -s 1 -e 250 -a

echo "== результат в S3 =="
aws s3 sync /work/output s3://${S3_BUCKET}/out/scene_v001/ --only-show-errors
echo "== DONE =="
```

Ключевое: скрипт **идемпотентен**. Инстанс можно перезапустить — `s3 sync`
не перезальёт уже готовые кадры, а `blender -b` пересчитает недостающие.

### 5. Страховать бюджет

```bash
# Личный счёт и регион: без этого все остальные команды уйдут не туда.
aws sts get-caller-identity
aws configure set region eu-central-1

# Бюджеты и пороговые алерты создаются в консоли Billing → Budgets
# (или через CloudWatch Billing Alerts). Настраивайте ДО первого запуска:
# лимит + оповещение на 50/80/100% — это разница между «инцидентом»
# и «дорогим днём».
aws budgets describe-budgets --account-id "$(aws sts get-caller-identity --query Account --output text)"
```

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

| Параметр / понятие | Значение | Когда менять |
|---|---|---|
| Тип инстанса | GPU-класс с 1 GPU | Две GPU на инстансе — сложнее считать VRAM и лимит памяти |
| On-Demand → Spot | Spot в 2–6 раз дешевле | Spot только если задание умеет повторяться: `s3 sync` и `-b` это позволяют |
| Прерываемость | Обязательно для Spot | Инстанс может забраться в любой момент; всё должно быть повторяемым |
| Префикс S3 | На версию сцены | Иначе результаты двух запусков смешаются |
| `--only-show-errors` | Всегда | Без него лог на 4000 объектов нечитаем |
| Лимит бюджета | Ставить до запуска | Это единственная защита от петли «инстанс × бесконечный ретрай» |

> [!NOTE]
> Флаги запуска Spot-инстансов (`--instance-market-options`,
> `--spot-options`, `--launch-template`) — это параметры AWS CLI, а не Blender.
> Их набор менялся между версиями CLI; точный список берите из
> `aws ec2 run-instances --help` на своей машине
> (документация: https://docs.aws.amazon.com/cli/latest/reference/).
> В GCP аналогично: `gcloud compute instances create --help`.

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Инстанс стартует и сразу `Exited` | В user-data ошибка, лог не в stdout | Писать в `/var/log/render-bootstrap.log`; ошибку искать в console output инстанса |
| Результаты в S3 неполные | Прерванный Spot-запуск | Перезапустить: `s3 sync` докачает, `blender -b` пересчитает недостающее |
| Кадры темнее, чем локально | GPU/driver или версия Blender отличается | Зафиксировать версию образа и драйвера; сверять 1 кадр |
| Счёт вырос, а кадров нет | Бесконечный ретрай Spot | Ставить бюджет-алерт; ограничить число попыток в скрипте |
| S3 `sync` залил пустую папку | Не тот префикс / опечатка в регионе | Проверять `aws s3 ls ... --recursive --summarize` до старта рендера |
| Текстуры потерялись при переносе | `.blend` не упакован | `bpy.ops.file.pack_all()` перед `save_as_mainfile`, либо складывать `//textures` рядом |
| `No space left on device` на инстансе | Местный диск мал, `output` локальный | Складывать вывод сразу в S3 или подключить том нужного размера |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md), [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md)
- **По темам:** [CASE 03: PRODUCT VISUALIZATION](../cases/case_03_product_viz.md), [CASE 05: PROCEDURAL CITY](../cases/case_05_procedural_city.md), [CASE 07: STYLIZED BARREL (HAND-PAINT)](../cases/case_07_stylized_barrel.md), [CASE 08: SCI-FI CORRIDOR MODULAR](../cases/case_08_sci_fi_corridor.md)
- **Теги:** #cloud, #render, #setup
