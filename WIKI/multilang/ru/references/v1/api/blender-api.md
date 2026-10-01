---
lang: ru
orig_lang: en
translation: ai
---
# СПРАВОЧНИК ПО BLENDER PYTHON API (4.x)

## Быстрая справка

### Контекст и доступ к данным
```python
import bpy

# Контекст (в фоновом режиме только для чтения)
bpy.context.scene              # Текущая сцена
bpy.context.view_layer         # Текущий view layer
bpy.context.active_object      # Активный объект (может быть None)
bpy.context.selected_objects   # Список выделенных объектов
bpy.context.object             # То же, что active_object
bpy.context.mode               # Текущий режим ('OBJECT', 'EDIT' и т.д.)

# Данные (доступны всегда)
bpy.data.objects               # Все объекты
bpy.data.meshes                # Все меши
bpy.data.materials             # Все материалы
bpy.data.collections           # Все коллекции
bpy.data.scenes                # Все сцены
bpy.data.images                # Все изображения
bpy.data.node_groups           # Все группы нод
```

### Создание объектов
```python
# Примитивы (bpy.ops — требует контекста)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0,0,0), rotation=(0,0,0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=32, ring_count=16)
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, vertices=32)
bpy.ops.mesh.primitive_plane_add(size=2)
bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2)
bpy.ops.mesh.primitive_torus_add(major_radius=1, minor_radius=0.3)

# Низкоуровневый способ (контекст не нужен) — ПРЕДПОЧТИТЕЛЬНО
mesh = bpy.data.meshes.new("MyMesh")
obj = bpy.data.objects.new("MyObject", mesh)
bpy.context.collection.objects.link(obj)

# Создание данных меша
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(mesh)
# ... операции bmesh ...
bmesh.update_edit_mesh(mesh)
bpy.ops.object.mode_set(mode='OBJECT')
```

### Операции трансформации
```python
obj = bpy.data.objects["Cube"]

# Location / Rotation / Scale
obj.location = (1.0, 2.0, 3.0)
obj.rotation_euler = (0, 0, 1.5708)  # Радианы
obj.scale = (2.0, 2.0, 2.0)

# Матрица (мировое преобразование)
obj.matrix_world = mathutils.Matrix.Translation((1,2,3)) @ \
                   mathutils.Matrix.Rotation(1.57, 4, 'Z')

# Применить преобразования (Ctrl+A)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Origin (начало координат)
bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
```

### Редактирование меша (bmesh)
```python
import bmesh

# bmesh в режиме редактирования
bm = bmesh.from_edit_mesh(obj.data)

# Создание геометрии
v1 = bm.verts.new((0,0,0))
v2 = bm.verts.new((1,0,0))
v3 = bm.verts.new((0,1,0))
bm.faces.new((v1, v2, v3))

# Операции bmesh вместо модификаторов
bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2)
bmesh.ops.bevel(bm, geom=bm.edges, offset=0.1, segments=3)
bmesh.ops.extrude_face_region(bm, geom=[f for f in bm.faces])

# Обновление
bmesh.update_edit_mesh(obj.data)

# bmesh в режиме объекта (новый меш)
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
bm.to_mesh(mesh)
bm.free()
```

### Материалы и ноды
```python
# Создать материал
mat = bpy.data.materials.new("MyMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Очистить ноды по умолчанию
nodes.clear()

# Principled BSDF (стандартный)
principled = nodes.new('ShaderNodeBsdfPrincipled')
principled.location = (0, 0)
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (400, 0)
links.new(principled.outputs['BSDF'], output.inputs['Surface'])

# Задать параметры
principled.inputs['Base Color'].default_value = (1.0, 0.0, 0.0, 1.0)  # RGBA
principled.inputs['Roughness'].default_value = 0.5
principled.inputs['Metallic'].default_value = 0.0
principled.inputs['Transmission'].default_value = 0.0
principled.inputs['Emission Strength'].default_value = 0.0

# Текстурные ноды
tex_image = nodes.new('ShaderNodeTexImage')
tex_image.image = bpy.data.images.load("path/to/texture.png")
tex_coord = nodes.new('ShaderNodeTexCoord')
mapping = nodes.new('ShaderNodeMapping')
links.new(tex_coord.outputs['UV'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], tex_image.inputs['Vector'])
links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])

# Назначить объекту
if obj.data.materials:
    obj.data.materials[0] = mat
else:
    obj.data.materials.append(mat)
```

### Модификаторы
```python
mod = obj.modifiers.new("Subdivision", 'SUBSURF')
mod.levels = 2
mod.render_levels = 3

mod = obj.modifiers.new("Bevel", 'BEVEL')
mod.width = 0.02
mod.segments = 3
mod.profile = 0.5

mod = obj.modifiers.new("Array", 'ARRAY')
mod.count = 5
mod.use_relative_offset = True
mod.relative_offset_displace = (1.5, 0, 0)

mod = obj.modifiers.new("Boolean", 'BOOLEAN')
mod.operation = 'DIFFERENCE'  # UNION, INTERSECT
mod.object = other_obj
mod.solver = 'EXACT'  # 'FAST' для простых случаев

# Применить модификатор
bpy.ops.object.modifier_apply(modifier="Subdivision")
```

### Коллекции и иерархия
```python
# Создать коллекцию
col = bpy.data.collections.new("MyCollection")
bpy.context.scene.collection.children.link(col)

# Переместить объект в коллекцию
col.objects.link(obj)
bpy.context.scene.collection.objects.unlink(obj)

# Родитель
child.parent = parent
child.parent_type = 'OBJECT'  # 'BONE', 'VERTEX'

# Коллекции для организации
bpy.context.view_layer.active_layer_collection = \
    bpy.context.view_layer.layer_collection.children["MyCollection"]
```

### Анимация
```python
# Ключевые кадры
obj.location = (0, 0, 0)
obj.keyframe_insert(data_path="location", frame=1)
obj.location = (10, 0, 0)
obj.keyframe_insert(data_path="location", frame=250)

# Интерполяция
for fcurve in obj.animation_data.action.fcurves:
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'BEZIER'  # 'LINEAR', 'CONSTANT'

# Драйверы
driver = obj.driver_add("location", 0).driver
driver.type = 'SCRIPTED'
var = driver.variables.new()
var.name = "target_x"
var.targets[0].id = target_obj
var.targets[0].data_path = "location[0]"
driver.expression = "target_x * 2"

# NLA
track = obj.animation_data.nla_tracks.new()
strip = track.strips.new("ActionName", 1, obj.animation_data.action)
strip.scale = 2.0  # Масштаб времени
```

### Geometry Nodes
```python
# Создать группу нод
ng = bpy.data.node_groups.new("MyGeoNodes", 'GeometryNodeTree')
nodes = ng.nodes
links = ng.links

# Вход / выход
input_node = nodes.new('NodeGroupInput')
output_node = nodes.new('NodeGroupOutput')

# Добавить сокеты
ng.interface.new_socket(name="Count", in_out='INPUT', socket_type='NodeSocketInt')
ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

# Ноды
mesh_line = nodes.new('GeometryNodeMeshLine')
mesh_line.location = (-200, 0)
mesh_line.mode = 'POINTS'
links.new(input_node.outputs['Count'], mesh_line.inputs['Count'])

instance = nodes.new('GeometryNodeInstanceOnPoints')
instance.location = (200, 0)
links.new(mesh_line.outputs['Mesh'], instance.inputs['Points'])
links.new(input_node.outputs['Geometry'], instance.inputs['Instance'])

links.new(instance.outputs['Instances'], output_node.inputs['Geometry'])

# Применить к объекту
mod = obj.modifiers.new("GeoNodes", 'NODES')
mod.node_group = ng
```

### Рендеринг
```python
scene = bpy.context.scene

# Движок
scene.render.engine = 'CYCLES'  # 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'

# Настройки Cycles
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.cycles.device = 'GPU'  # 'CPU', 'GPU'

# Настройки EEVEE
scene.eevee.taa_render_samples = 64
scene.eevee.use_bloom = True
scene.eevee.use_ssr = True
scene.eevee.use_ssr_refraction = True

# Вывод
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.filepath = "//render_"
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.film_transparent = True

# Рендер
bpy.ops.render.render(write_still=True)
bpy.ops.render.render(animation=True)
```

### Импорт и экспорт
```python
# Импорт
bpy.ops.import_scene.gltf(filepath="model.glb")
bpy.ops.import_scene.fbx(filepath="model.fbx")
bpy.ops.import_mesh.stl(filepath="model.stl")
bpy.ops.wm.obj_import(filepath="model.obj")
bpy.ops.wm.ply_import(filepath="model.ply")

# Экспорт
bpy.ops.export_scene.gltf(filepath="model.glb", export_format='GLB')
bpy.ops.export_scene.fbx(filepath="model.fbx")
bpy.ops.export_mesh.stl(filepath="model.stl")
bpy.ops.wm.obj_export(filepath="model.obj")
bpy.ops.wm.ply_export(filepath="model.ply")
```

### Утилиты
```python
# Выделение
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# Переключение режимов
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.mode_set(mode='SCULPT')

# Удаление
bpy.data.objects.remove(obj, do_unlink=True)
bpy.data.meshes.remove(mesh, do_unlink=True)

# Дублирование
new_obj = obj.copy()
new_obj.data = obj.data.copy()  # Уникальный меш
bpy.context.collection.objects.link(new_obj)

# Преобразовать в меш
bpy.ops.object.convert(target='MESH')

# Затенение
bpy.ops.object.shade_smooth()
bpy.ops.object.shade_flat()
bpy.ops.object.shade_auto()

# Единицы измерения
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
```

### Советы по производительности
```python
# Пакетные операции
with bpy.context.temp_override(selected_objects=objects):
    bpy.ops.object.shade_smooth()

# Отключить обновления во время пакетной обработки
depsgraph = bpy.context.evaluated_depsgraph_get()
depsgraph.update()

# Использовать foreach для массового задания свойств
mesh.vertices.foreach_set("co", flat_coordinate_list)

# Профилирование
import cProfile, pstats
profiler = cProfile.Profile()
profiler.enable()
# ... код ...
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats(20)
```

---

## Общие паттерны для автоматизации с помощью ИИ

### Безопасный доступ к объектам
```python
# ВСЕГДА проверять существование
obj = bpy.data.objects.get("Name")
if obj is None:
    raise ValueError("Object not found")

# ВСЕГДА использовать явные ссылки
obj = bpy.data.objects["Name"]  # Бросает KeyError, если объекта нет
```

### Потокобезопасное выполнение (для MCP)
```python
# В аддоне blender-mcp: команды выполняются в главном потоке через timer
# В GenesisCore: прямой доступ к bpy (тот же процесс)

# Для фоновых скриптов:
def run_in_main_thread(func):
    def wrapper():
        return func()
    bpy.app.timers.register(wrapper, first_interval=0.01)
```

### Шаблон обработки ошибок
```python
def safe_execute(code_func):
    try:
        result = code_func()
        return {"success": True, "result": result}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

# Использование
result = safe_execute(lambda: create_complex_scene())
```

### Совместимость версий
```python
# Проверка версии Blender
if bpy.app.version >= (4, 0, 0):
    # Новый API
    bpy.ops.mesh.primitive_cube_add(size=2)
else:
    # Старый API
    bpy.ops.mesh.primitive_cube_add(radius=1)

# Определение наличия возможности
has_asset_browser = hasattr(bpy.ops, 'asset')
```

---

## Ссылки на документацию
- [Документация Blender Python API](https://docs.blender.org/api/current/)
- [Документация bpy.types](https://docs.blender.org/api/current/bpy.types.html)
- [Документация bmesh](https://docs.blender.org/api/current/bmesh.html)
- [Документация mathutils](https://docs.blender.org/api/current/mathutils.html)

**Теги:** #api, #blender, #reference

## 🎯 ЦЕЛЬ

Референс категории «Референсы», сложность —.
