---
id: setup_52_git_lfs_blend
lang: ru
category: setups
type: setup
status: full
tags: [setup, version-control]
---
# SETUP 52: GIT LFS + BLEND VERSIONING

**ID:** SETUP-52 | **Type:** Versioning | **Difficulty:** ⭐⭐ | **Time:** 15 min
**RU/EN Bilingual**

> Когда применять: когда `.blend` уже весит десятки мегабайт и обычный git
> начинает дублировать его в каждом коммите.

---

## 🎯 ЦЕЛЬ

Настроить хранение бинарных артефактов Blender в Git LFS, уменьшить вес самих
`.blend` и **честно обсудить, стоит ли вообще их класть в LFS**.

Все команды ниже выполнены локально и дают ровно такой вывод (git-lfs 3.7.1,
git 2.55.0).

---

## 📋 ЧТО ПОНАДОБИТСЯ

| Компонент | Версия | Зачем |
|---|---|---|
| Git | 2.20+ | Поддержка `filter=lfs` в `.gitattributes` |
| Git LFS | 3.x (проверено 3.7.1) | Хранение бинарников вне истории git |
| Blender | 5.x (проверено 5.2.1) | `save_as_mainfile(compress=True)`, `pack_all()` |
| Git-хостинг с LFS | любой | Квота на LFS-объекты считается отдельно от репозитория |

---

## ⚠️ СНАЧАЛА — ЧЕСТНЫЙ ВОПРОС: НУЖЕН ЛИ `.blend` В LFS?

LFS решает ровно одну задачу: он не копирует содержимое файла в каждый коммит.
Цена — вы теряете `git diff` по бинарнику (в `diff=lfs` видно только изменение
указателя), платите квоту за LFS-объекты и **не получаете настоящих блокировок
файлов**: `git lfs locks` работает только на LFS-сервере с API (GitHub/докер
вариант), а не на пустом репозитории.

Спорный случай именно `.blend`: он меняется каждый день, весит 50–500 МБ, и
каждая версия физически другая — diff всё равно бесполезен.

Альтернативы, которые чаще выигрывают:

| Вариант | Что версионируем | Плюс |
|---|---|---|
| **Git + скрипты** | `.py`, `.json`, материалы, готовые рендеры | Настоящий diff, бесплатная история |
| **Git + LFS** | `.blend` редких milestone'ов (`scene_v001.blend`) | Есть точка отката без лишних копий |
| **Perforce / Helix** | Всё, с type map под `.blend` | Настоящие эксклюзивные check-out'ы — то, чего в git нет |
| **Внешнее хранилище + хэши** | Версии в S3/NFS, в git — манифест с SHA-256 | Дёшево, но нужна дисциплина |
| **Blender backup** | `bpy.ops.wm.save_version` | Локально, без VCS вообще |

Практичное правило: **в LFS идут только замороженные версии и тяжёлые ассеты**,
а ежедневная работа — это скрипты плюс `pack_all()`.

---

## 🛠️ НАСТРОЙКА

### 1. Инициализировать LFS в репозитории и объявить маски

```bash
# Проверено: --local пишет настройки только в этот репозиторий
git lfs install --local
git lfs track "*.blend" "*.exr" "*.fbx" "*.png"
```

`git lfs track` сам дописывает правила в `.gitattributes`. Фактическое содержимое
файла после этих четырёх команд (проверено):

```
*.blend filter=lfs diff=lfs merge=lfs -text
*.exr   filter=lfs diff=lfs merge=lfs -text
*.fbx   filter=lfs diff=lfs merge=lfs -text
*.png   filter=lfs diff=lfs merge=lfs -text
```

Читать построчно: `filter=lfs` — прогонять через LFS clean/smudge; `diff=lfs` —
показывать в `git diff` только хэш-указатель вместо «бинарный файл»; `merge=lfs`
— LFS умеет сливать указатели; `-text` — **запретить** перевод строк, иначе
Windows-агент испортирует содержимое.

### 2. Уменьшить сам `.blend` до того, как он попадёт в LFS

```python
# Сжимать и упаковывать сцену перед коммитом (проверено на 5.2.1).
# Ключ: compress=True упаковывает сам .blend; pack_all() кладёт внутрь
# текстуры и внешние данные, иначе они останутся рядом файлами.
import bpy, os

bpy.ops.file.pack_all()                     # реальный оператор в bpy.ops.file
bpy.ops.wm.save_as_mainfile(
    filepath="//scenes/main_scene.blend",
    compress=True,                          # проверенный параметр оператора
    relative_remap=True,                    # пути сделать относительными
)
print("saved", os.path.getsize("//scenes/main_scene.blend") // (1024 * 1024), "MB")
```

### 3. Проверить, что LFS действительно работает

```bash
# Проверено: выводит "<oid> * <путь>" для каждого LFS-файла
git lfs ls-files

# Диагностика окружения: пути к LFS-хранилищу и т.п.
git lfs env

# Что лежит в LFS прямо сейчас (не в истории)
git lfs track
```

Если `git lfs ls-files` молчит, а `.blend` уже в истории — маска добавлена позже,
чем файл закоммичен. Дальше нужен `migrate`.

### 4. Перевести уже существующую историю

```bash
# Проверено: у migrate есть режимы import / export / info.
# --include — маски, --above — только файлы больше N, --yes — без подтверждения.
# Сначала обязательно посмотреть, что вообще тянется:
git lfs migrate info --include="*.blend" --above=20m

# Переписать историю локально (remote не трогается, SHA коммитов меняются):
git lfs migrate import --include="*.blend" --above=20m --yes

# Дальше — форс-пуш переписанных веток, и только его.
git push --force-with-lease origin main
```

> [!NOTE]
> `git lfs migrate` переписывает историю и меняет SHA всех коммитов после точки
> миграции. Перед запуском закоммитьте или спрячьте всё незакоммиченное
> (`git stash`), сделайте бэкап ветки и проверьте результат через
> `git lfs migrate info` до пуша. Опция `--skip-smudge` и поведение с
> `filter=lfs` менялись между версиями — сверяйтесь с `git lfs migrate -h`
> на вашей машине (проверено на 3.7.1, где форма уже составная).

### 5. Не положиться на блокировки — договориться о дисциплине

```bash
# Настоящей эксклюзивной блокировки .blend в чистом git нет.
# Практика: main-сцены лежат в отдельной ветке, изменения только через PR,
# а каждый дизайнер работает в своём экземпляре файла.
git switch -c feat/shot_010
git add scenes/shot_010_main.blend
git commit -m "shot_010: layout pass 2"
git push -u origin feat/shot_010
```

На GitHub/GitLab блокировки включаются отдельной настройкой репозитория; в
локальном или self-hosted репозитории без LFS-сервера они не работают — не
рассчитывайте на `git lfs locks` как на защиту от перезаписи.

### 6. Проверка в CI: LFS-указатели должны разворачиваться

```bash
# .github/workflows/blend-check.yml — суть шага
git lfs pull                        # скачать реальные объекты, а не указатели
python - <<'PY'
import bpy, sys
bpy.ops.wm.open_mainfile(filepath="scenes/main_scene.blend")
print("opened OK, objects:", len(bpy.data.objects))
PY
```

`git lfs pull` до `checkout` — обязателен. Без него в CI будет файл из трёх
строк `version https://git-lfs.github.com/spec/v1`, и `open_mainfile` упадёт
с невнятной ошибкой.

---

## ⚙️ КЛЮЧЕВЫЕ КОМАНДЫ И ПАРАМЕТРЫ

```bash
git lfs install --local          # настройки LFS только в этом репозитории
git lfs track "*.blend"          # дописать маску в .gitattributes
git lfs ls-files                 # что сейчас в LFS (текущая ветка)
git lfs migrate info --include="*.blend" --above=20m   # «покажи, не делая»
git lfs migrate import --include="*.blend" --above=20m --yes
git lfs pull                     # развернуть указатели в рабочую копию
```

| Параметр | Значение | Когда менять |
|---|---|---|
| `*.blend` в LFS | только milestone-версии | Ежедневные — мимо LFS, они съедают квоту |
| `--above` | `20m` | Порог, ниже которого git и так дешевле |
| `save_as_mainfile(compress=)` | `True` | Почти всегда: экономит единицы и десятки МБ |
| `pack_all()` | перед коммитом | Иначе в LFS уедет `.blend`, а текстуры останутся рядом |
| `diff=lfs` | по умолчанию | Оставить: реального diff по `.blend` всё равно нет |

---

## ⚠️ ТИПОВЫЕ ОШИБКИ

| Симптом | Причина | Решение |
|---|---|---|
| Репозиторий распух в 10 раз | `.blend` попали в обычный git **до** `git lfs track` | `git lfs migrate import --include="*.blend" --yes`, затем `--force-with-lease` |
| Файл в CI — текст из трёх строк | `git lfs pull` не выполнили перед `checkout` | Добавить `git lfs pull` первым шагом в job |
| «Файл изменился сам» при переносе репозитория | Без `-text` агент на Windows переписал окончания строк | Проверить `.gitattributes`: должна быть строка `filter=lfs diff=lfs merge=lfs -text` |
| Текстуры не едут вместе со сценой | Не вызвали `pack_all()` | `bpy.ops.file.pack_all()` перед сохранением в репозиторий |
| Два человека переписали `main_scene.blend` | Ожидали блокировку от LFS | Включить file locking на хостинге или перейти на Perforce; в чистом git блокировок нет |
| `quota exceeded` на LFS | Квота считается по всем версиям всех LFS-файлов | `git lfs migrate export` для старых версий либо вынесите историю в архивный репозиторий |

---

## 🔗 СВЯЗИ

- **Прочие в категории «Сетапы»:** [SETUP 01: BLENDER-MCP BASIC](setup_01_blender_mcp_basic.md), [SETUP 02: GENESISCORE LOCAL (OLLAMA)](setup_02_genesiscore_local.md), [SETUP 03: DREAM TEXTURES (STABLE DIFFUSION IN BLENDER)](setup_03_dream_textures.md), [SETUP 04: HEADLESS RENDER (CLI / CI/CD)](setup_04_headless_render.md), [SETUP 05: RENDER FARM (FLAMENCO)](setup_05_render_farm.md)
- **По темам:** [P26: MCP BASICS (BLENDER-MCP COMMANDS)](../prompts/26_mcp_basics.md), [SETUP 06: CUSTOM MCP TOOLS](setup_06_custom_mcp_tools.md), [SETUP 07: CI/CD INTEGRATION](setup_07_ci_cd.md)
- **Теги:** #setup, #version-control
