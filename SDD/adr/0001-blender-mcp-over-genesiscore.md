# ADR 0001 — blender-mcp вместо GenesisCore (AIGODLIKE)

- **Статус:** принято
- **Дата:** 2026-09-24

## Контекст
Два кандидата на MCP-мост к Blender: аддон `GenesisCore` из репозитория AIGODLIKE и пакет
`blender-mcp` (`uvx blender-mcp`, TCP :9876). GenesisCore встроен в репозиторий (`addons/AIGODLIKE`)
и выглядел «бесплатным» уже скачанным решением.

## Решение
Основной путь — `blender-mcp`. GenesisCore не является основным.

## Последствия
- **Причина:** GenesisCore падает с `No module named 'mcp'` — pip в
  `C:\Program Files\Blender Foundation\...` даёт Access Denied, доустанавливать пакет в
  системную папку Blender нельзя без прав администратора. `blender-mcp` ставится в пользовательское
  окружение (`uvx`) и работает.
- **Плюсы:** рабочий путь, MCP-инструменты доступны прямо в сессии агента
  (`get_addon_status`, `execute_blender_code`, `set_texture`, `get_viewport_screenshot`).
- **Минусы:** аддон `blender-mcp` в установленном Blender версии 1.6 / protocol 5, а сервер
  ожидает protocol 9 → `search_polyhaven_assets` падает с `unexpected keyword argument 'category'`.
  Обход: брать ассеты напрямую через API Poly Haven + `urllib` внутри `execute_blender_code`
  (проверено: HDRI `studio_small_09` 2k скачан и назначен в world).
- **Лечение:** `uvx mcp-for-blender install-addon` и перезапуск Blender для protocol 9.
- Wiki документирует оба пути, но канонический — `setups/setup_01_blender_mcp_basic.md`.
