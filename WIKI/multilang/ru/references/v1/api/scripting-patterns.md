---
lang: ru
orig_lang: en
translation: ai
---
# ПАТТЕРНЫ СКРИПТИНГА В BLENDER — БЕЗОПАСНО И ЭФФЕКТИВНО

## Базовые принципы

### 1. Всегда проверяйте существование
```python
# ПЛОХО
obj = bpy.data.objects["Cube"]
obj.location.x = 1

# ХОРОШО
obj = bpy.data.objects.get("Cube")
if obj:
    obj.location.x = 1
else:
    print("Object not found")
```

### 2. Явный контекст важнее неявного
```python
# ПЛОХО (полагается на bpy.context.active_object)
bpy.ops.object.shade_smooth()

# ХОРОШО (явно)
obj = bpy.data.objects["Cube"]
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.shade_smooth()
```

### 3. Учитывайте режим
```python
# Перед операциями убедиться, что задан правильный режим
def ensure_mode(mode='OBJECT'):
    if bpy.context.mode != mode:
        bpy.ops.object.mode_set(mode=mode)

# Использование
ensure_mode('OBJECT')
# ... операции с объектом ...

ensure_mode('EDIT')
bm = bmesh.from_edit_mesh(obj.data)
# ... операции bmesh ...
bmesh.update_edit_mesh(obj.data)

ensure_mode('OBJECT')
```

---

## Шаблон безопасного выполнения

### Для MCP `execute_blender_code`
```python
def safe_execute(operation_name, func):
    """
    Обёртка для безопасного выполнения кода в MCP.
    Возвращает dict с информацией об успехе/ошибке.
    """
    try:
        # Убедиться, что мы в режиме объекта
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        
        result = func()
        
        # Принудительное обновление
        bpy.context.view_layer.update()
        
        return {
            "success": True,
            "result": result,
            "operation": operation_name
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "operation": operation_name,
            "traceback": traceback.format_exc()
        }

# Использование
def create_scene():
    # ... ваш код ...
    return {"created": ["Cube", "Light", "Camera"]}

result = safe_execute("create_scene", create_scene)
```

---

## Общие паттерны

### Паттерн 1: создание объекта с материалом
```python
def create_object_with_material(name, primitive_type, location, material_name, color):
    """Создать примитив, добавить материал, назначить"""
    # Создать меш
    if primitive_type == 'CUBE':
        bpy.ops.mesh.primitive_cube_add(location=location)
    elif primitive_type == 'SPHERE':
        bpy.ops.mesh.primitive_uv_sphere_add(location=location)
    # ... другие типы
    
    obj = bpy.context.active_object
    obj.name = name
    
    # Создать материал
    mat = bpy.data.materials.new(material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    
    principled.inputs['Base Color'].default_value = color + (1.0,) if len(color) == 3 else color
    principled.inputs['Roughness'].default_value = 0.5
    principled.inputs['Metallic'].default_value = 0.0
    
    # Назначить
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    return obj
```

### Паттерн 2: пакетное создание с вариациями
```python
def create_variations(base_name, count, position_func, variation_func):
    """Создать несколько объектов с вариациями"""
    objects = []
    for i in range(count):
        loc = position_func(i)
        obj = create_object_with_material(
            f"{base_name}_{i:03d}",
            'CUBE',
            loc,
            f"Mat_{base_name}_{i:03d}",
            variation_func(i)
        )
        objects.append(obj)
    return objects

# Использование
def grid_position(i, cols=5):
    row = i // cols
    col = i % cols
    return (col * 3, row * 3, 0)

def color_variation(i):
    import colorsys
    hue = (i * 0.618) % 1.0  # распределение по золотому сечению
    r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
    return (r, g, b)

objs = create_variations("Brick", 20, grid_position, color_variation)
```

### Паттерн 3: иерархическая структура сцены
```python
def setup_scene_hierarchy():
    """Создать организованную иерархию коллекций"""
    # Корневая коллекция
    root = bpy.data.collections.new("Scene_Root")
    bpy.context.scene.collection.children.link(root)
    
    # Вложенные коллекции
    collections = {}
    for name in ["Geometry", "Lights", "Cameras", "FX", "References"]:
        col = bpy.data.collections.new(name)
        root.children.link(col)
        collections[name] = col
    
    return collections

def move_to_collection(obj, collection_name, collections):
    """Переместить объект в коллекцию по имени"""
    # Отвязать от всех
    for col in obj.users_collection:
        col.objects.unlink(obj)
    # Привязать к целевой
    collections[collection_name].objects.link(obj)
```

### Паттерн 4: ключевые кадры анимации
```python
def animate_property(obj, prop_path, keyframes, interpolation='BEZIER'):
    """
    keyframes: {frame: value, ...}
    prop_path: например, "location", "rotation_euler", "scale"
    """
    for frame, value in keyframes.items():
        setattr(obj, prop_path, value)
        obj.keyframe_insert(data_path=prop_path, frame=frame)
    
    # Задать интерполяцию
    if obj.animation_data and obj.animation_data.action:
        for fcurve in obj.animation_data.action.fcurves:
            if fcurve.data_path == prop_path:
                for kp in fcurve.keyframe_points:
                    kp.interpolation = interpolation

# Использование
animate_property(obj, "location", {
    1: (0, 0, 0),
    50: (10, 0, 0),
    100: (10, 10, 0),
    150: (0, 10, 0),
    200: (0, 0, 0)
})
```

### Паттерн 5: настройка драйвера
```python
def add_driver(obj, prop_path, target_obj, target_prop, expression="var"):
    """Добавить драйвер к obj.prop_path, управляемый target_obj.target_prop"""
    driver = obj.driver_add(prop_path).driver
    driver.type = 'SCRIPTED'
    
    var = driver.variables.new()
    var.name = "var"
    var.targets[0].id = target_obj
    var.targets[0].data_path = target_prop
    
    driver.expression = expression
    return driver

# Использование
# Вращать gear_b по вращению gear_a (соотношение 2:1)
add_driver(gear_b, "rotation_euler[2]", gear_a, "rotation_euler[2]", "-var * 2")
```

---

## Паттерны обработки ошибок

### Контекстный менеджер для смены режимов
```python
from contextlib import contextmanager

@contextmanager
def temp_mode(mode='OBJECT'):
    """Временно переключить режим, затем восстановить"""
    original_mode = bpy.context.mode
    if original_mode != mode:
        bpy.ops.object.mode_set(mode=mode)
    try:
        yield
    finally:
        if original_mode != mode:
            bpy.ops.object.mode_set(mode=original_mode)

# Использование
with temp_mode('EDIT'):
    bm = bmesh.from_edit_mesh(obj.data)
    # ... операции ...
    bmesh.update_edit_mesh(obj.data)
# Автоматический возврат к исходному режиму
```

### Контекстный менеджер для выделения
```python
@contextmanager
def temp_selection(objects, active=None):
    """Временно выделить объекты, затем восстановить выделение"""
    # Сохранить текущее
    prev_active = bpy.context.view_layer.objects.active
    prev_selected = bpy.context.selected_objects[:]
    
    # Задать новое
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)
    if active:
        bpy.context.view_layer.objects.active = active
    elif objects:
        bpy.context.view_layer.objects.active = objects[0]
    
    try:
        yield
    finally:
        # Восстановить
        bpy.ops.object.select_all(action='DESELECT')
        for obj in prev_selected:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = prev_active

# Использование
with temp_selection([obj1, obj2, obj3], active=obj1):
    bpy.ops.object.join()
```

### Группировка в Undo
```python
def with_undo_step(name, func):
    """Обернуть операцию в шаг Undo"""
    bpy.ops.ed.undo_push(message=name)
    try:
        return func()
    except Exception:
        bpy.ops.ed.undo()
        raise

# Использование
with_undo_step("Create Building", lambda: create_building())
```

---

## Паттерны производительности

### Пакетная обработка
```python
def process_objects_batch(objects, process_func, batch_size=100):
    """Обрабатывать объекты пачками, чтобы избежать проблем с памятью"""
    results = []
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i+batch_size]
        with bpy.context.temp_override(selected_objects=batch):
            batch_results = [process_func(obj) for obj in batch]
            results.extend(batch_results)
        # Опционально: принудительный сбор мусора
        import gc
        gc.collect()
    return results
```

### Отложенные дорогие операции
```python
def defer_to_next_frame(func):
    """Запустить функцию на следующем кадре (полезно для обновления UI)"""
    def wrapper():
        func()
        return None  # Не повторять
    bpy.app.timers.register(wrapper, first_interval=0.01)

# Использование
defer_to_next_frame(lambda: heavy_computation())
```

---

## Вспомогательные функции для отладки

### Печать сводки по сцене
```python
def print_scene_summary():
    scene = bpy.context.scene
    print(f"Scene: {scene.name}")
    print(f"Objects: {len(scene.objects)}")
    print(f"Materials: {len(bpy.data.materials)}")
    print(f"Meshes: {len(bpy.data.meshes)}")
    print(f"Collections: {len(bpy.data.collections)}")
    for obj in scene.objects:
        print(f"  {obj.name} ({obj.type}) - {len(obj.data.vertices) if obj.type=='MESH' else 'N/A'} verts")

# Быстрый вызов
print_scene_summary()
```

### Поиск проблем
```python
def find_mesh_issues():
    """Проверить типичные проблемы меша"""
    issues = []
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
        mesh = obj.data
        
        # Неманфолдные рёбра
        bm = bmesh.new()
        bm.from_mesh(mesh)
        non_manifold = [e for e in bm.edges if not e.is_manifold]
        if non_manifold:
            issues.append(f"{obj.name}: {len(non_manifold)} non-manifold edges")
        
        # Грани нулевой площади
        zero_area = [f for f in bm.faces if f.calc_area() < 0.0001]
        if zero_area:
            issues.append(f"{obj.name}: {len(zero_area)} zero-area faces")
        
        # Дублирующиеся вершины
        coords = [v.co for v in bm.verts]
        if len(coords) != len(set(str(c) for c in coords)):
            issues.append(f"{obj.name}: duplicate vertices")
        
        bm.free()
    
    return issues

# Запуск
for issue in find_mesh_issues():
    print(f"ISSUE: {issue}")
```

---

## Соответствие safe mode (для blender-mcp)

### Только разрешённые импорты
```python
# ✅ РАЗРЕШЕНО
import bpy
import bmesh
import math
import mathutils
import random
import json
import uuid
import itertools
import collections
import functools
import fractions
import decimal
import statistics
import typing
import dataclasses
import enum
import hashlib
import base64
import datetime
import time
import re
import string
import textwrap
import copy
import pprint
import numbers
import fractions
import pathlib
import os.path
import sys

# ❌ ЗАБЛОКИРОВАНО (safe mode)
import os          # файловый ввод-вывод
import subprocess  # запуск процессов
import sys         # доступ к системе
import socket      # сеть
import requests    # HTTP
import urllib      # работа с URL
import threading   # потоки
import multiprocessing
import asyncio
import importlib   # динамические импорты
import pkgutil
import inspect
```

### Шаблон безопасного кода
```python
# Этот шаблон проходит проверку safe mode
import bpy
import bmesh
import math
import mathutils
import random
import json

def main():
    # Здесь ваши операции в Blender
    # Используйте только: bpy.data, bpy.ops, bmesh, mathutils, math, random, json
    
    # Пример: процедурное здание
    for i in range(5):
        bpy.ops.mesh.primitive_cube_add(
            location=(i * 3, 0, 0),
            scale=(1, 1, random.uniform(2, 5))
        )
        obj = bpy.context.active_object
        obj.name = f"Building_{i}"
    
    return {"created": 5}

if __name__ == "__main__":
    result = main()
    print(json.dumps(result))
```

---

## Совместимость версий

### Проверки версий
```python
# Версия Blender
if bpy.app.version >= (4, 0, 0):
    # Новый API
    bpy.ops.mesh.primitive_cube_add(size=2)
else:
    # Старый API
    bpy.ops.mesh.primitive_cube_add(radius=1)

# Определение наличия возможности
has_asset_browser = hasattr(bpy.ops, 'asset')
has_geometry_nodes = 'GeometryNodeTree' in dir(bpy.types)

# Проверка существования свойства
if hasattr(bpy.types.Object, "new_property"):
    obj.new_property = value
```

---

## Паттерны тестирования

### Шаблон юнит-теста
```python
import unittest
import bpy
import bmesh

class TestMeshOperations(unittest.TestCase):
    def setUp(self):
        # Очистить сцену
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete()
    
    def test_create_cube(self):
        obj = create_object_with_material("TestCube", 'CUBE', (0,0,0), "TestMat", (1,0,0))
        self.assertEqual(obj.name, "TestCube")
        self.assertEqual(obj.type, 'MESH')
        self.assertEqual(len(obj.data.materials), 1)
    
    def test_boolean_difference(self):
        cube = create_object_with_material("Cube", 'CUBE', (0,0,0), "Mat", (1,0,0))
        sphere = create_object_with_material("Sphere", 'SPHERE', (0.5,0,0), "Mat", (0,1,0))
        
        result = boolean_difference(cube, sphere)
        self.assertEqual(result.name, "Cube")
        # Сфера должна быть удалена
        self.assertNotIn("Sphere", bpy.data.objects)

if __name__ == '__main__':
    unittest.main()
```

---

## Лучшие практики интеграции с MCP

### Пошагово для сложных задач
```python
# Вместо одной гигантской операции разбейте задачу на шаги:

# Шаг 1: подготовка
result = execute("Создать коллекции для организации")

# Шаг 2: базовая геометрия
result = execute("Создать плоскость пола 20x20м в начале координат")

# Шаг 3: стены
result = execute("Создать 4 стены по периметру пола, высота 3м")

# Шаг 4: проёмы
result = execute("Булевым вычитанием вырезать дверной проём 1x2м в передней стене")

# Шаг 5: крыша
result = execute("Создать двускатную крышу над стенами")

# Шаг 6: материалы
result = execute("Назначить каменный материал стенам, деревянный полу, плиточный крыше")

# Шаг 7: освещение
result = execute("Добавить трёхточечное освещение: key, fill, rim")

# Шаг 8: камера
result = execute("Добавить камеру в (-10, -15, 5) с направлением на центр, 35мм")

# Шаг 9: настройки рендера
result = execute("Настроить Cycles, 128 сэмплов, 1920x1080, вывод в //renders/")
```

### Проверка после каждого шага
```python
def verify_step(step_name, verification_func):
    """Выполнить шаг и проверить результат"""
    result = execute(step_name)
    if not result.get("success"):
        return {"success": False, "error": f"{step_name} failed: {result.get('error')}"}
    
    # Проверка
    try:
        verification_func()
        return {"success": True, "result": result}
    except AssertionError as e:
        return {"success": False, "error": f"{step_name} verification failed: {e}"}

# Использование
def verify_floor_exists():
    obj = bpy.data.objects.get("Floor")
    assert obj and obj.type == 'MESH'
    assert abs(obj.dimensions.x - 20) < 0.01
    assert abs(obj.dimensions.y - 20) < 0.01

result = verify_step("Create floor", verify_floor_exists)
```

---

## 🔗 СВЯЗИ

- **Прочие в категории «Референсы»:** [BLENDER MATERIALS API REFERENCE](materials.md), [BLENDER MESH OPERATIONS API REFERENCE](mesh-operations.md), [BLENDER PYTHON API REFERENCE (4.x)](blender-api.md), [BLENDER-MCP - FULL DOCUMENTATION](../addons/blender-mcp-full.md), [BLENDER-MCP ADDON - DEEP DIVE](../addons/blender-mcp.md)
- **По темам:** [INSTALLATION GUIDE - COMPLETE SETUP](../guides/installation.md), [MCP ARCHITECTURE - MODEL CONTEXT PROTOCOL FOR BLENDER](../mcp/architecture.md), [PROMPTING GUIDE - EFFECTIVE AI COMMANDS FOR BLENDER](../guides/prompting.md)
- **Теги:** #blender, #reference

---

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.
