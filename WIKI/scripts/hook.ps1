#Requires -Version 5.1
# Hook: полная проверка проекта. Запуск: powershell -ExecutionPolicy Bypass -File "C:\BLENDER ai\WIKI\scripts\hook.ps1"
$ErrorActionPreference = "Stop"
Set-Location "C:\BLENDER ai"
Write-Host "== validate.py =="
python "C:\BLENDER ai\WIKI\scripts\validate.py"
if ($LASTEXITCODE -ne 0) { Write-Host "HOOK FAIL: validate"; exit 1 }
Write-Host "HOOK OK"
