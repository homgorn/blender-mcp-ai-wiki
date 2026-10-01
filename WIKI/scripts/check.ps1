#Requires -Version 5.1
# Check: короткая проверка без пересборки DB (быстро). Запуск: powershell -ExecutionPolicy Bypass -File "C:\BLENDER ai\WIKI\scripts\check.ps1"
$ErrorActionPreference = "Stop"
python -c "import json; db=json.load(open(r'C:\BLENDER ai\WIKI\db\wiki_database.json',encoding='utf-8')); print('entries',db.get('total_entries',len(db['entries']))); assert db.get('total_entries',len(db['entries']))>0"
python "C:\BLENDER ai\WIKI\scripts\check_missing.py"
Write-Host "CHECK OK"
