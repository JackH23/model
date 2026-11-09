"""Run with Blender --background --factory-startup --python scripts/export-villages.py.

Reads the copied .blend sources; never saves or modifies them. Realizes collection
instances and evaluates modifiers into a temporary scene, retaining source names.
"""
import bpy
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / 'source-models'
OUT = ROOT / '.asset-cache' / 'villages'
OUT.mkdir(parents=True, exist_ok=True)
paths = [SOURCES / 'Crystalbrook_Village.blend'] + sorted((SOURCES / 'Ashwick').glob('*.blend'))
reports = []

for path in paths:
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False)
    source_scene = bpy.context.scene
    temp = bpy.data.scenes.new('WEB_EXPORT_TEMP')
    deps = bpy.context.evaluated_depsgraph_get()
    # Depsgraph iterator entries are ephemeral: copy the values immediately.
    instances = []
    for item in deps.object_instances:
        obj = item.object
        if obj.type not in {'MESH', 'CURVE', 'SURFACE', 'FONT', 'META'} or obj.hide_render:
            continue
        if item.is_instance and item.parent and item.parent.hide_render:
            continue
        if not item.is_instance and obj.original.hide_get():
            continue
        parent = item.parent.name if item.is_instance and item.parent else None
        instances.append((obj.original, item.matrix_world.copy(), parent))

    parts = []
    used_names = set()
    mesh_cache = {}
    material_cache = {}
    for original, matrix, parent in instances:
        if original.as_pointer() not in mesh_cache:
            evaluated = original.evaluated_get(deps)
            mesh_cache[original.as_pointer()] = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=deps)
            # Some Ashwick terrain materials define only their viewport color.
            # Copy that authored color when the shader is still Blender's default;
            # keep deliberate shader colors and the source materials unchanged.
            for index, material in enumerate(mesh_cache[original.as_pointer()].materials):
                if not material or not material.node_tree:
                    continue
                shader = next((node for node in material.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
                if not shader or shader.inputs['Base Color'].is_linked:
                    continue
                base = shader.inputs['Base Color'].default_value
                if all(abs(base[i] - 0.8) < 0.00001 for i in range(3)) and any(abs(base[i] - material.diffuse_color[i]) > 0.01 for i in range(3)):
                    if material.as_pointer() not in material_cache:
                        copied = material.copy()
                        copied.name = material.name + ' Web'
                        next(node for node in copied.node_tree.nodes if node.type == 'BSDF_PRINCIPLED').inputs['Base Color'].default_value = material.diffuse_color
                        material_cache[material.as_pointer()] = copied
                    mesh_cache[original.as_pointer()].materials[index] = material_cache[material.as_pointer()]
        data = mesh_cache[original.as_pointer()]
        if not data.polygons:
            bpy.data.meshes.remove(data)
            continue
        name = f'{parent} / {original.name}' if parent else original.name
        base_name = name
        suffix = 2
        while name in used_names:
            name = f'{base_name} / {suffix}'
            suffix += 1
        used_names.add(name)
        obj = bpy.data.objects.new(name, data)
        temp.collection.objects.link(obj)
        obj.matrix_world = matrix
        collections = [c.name for c in original.users_collection]
        region = parent or (collections[0] if collections and collections[0] != 'Scene Collection' else 'Assembly')
        region = re.sub(r'^\d+\s*[• ]\s*', '', region)
        obj['sourceName'] = name
        obj['label'] = name.replace('_', ' ')
        obj['region'] = region
        data.calc_loop_triangles()
        parts.append({'sourceName': name, 'region': region, 'triangles': len(data.loop_triangles)})

    bpy.context.window.scene = temp
    for obj in temp.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = next(iter(temp.objects))
    bpy.context.view_layer.update()
    slug = re.sub(r'[^a-z0-9]+', '-', path.stem.lower()).strip('-')
    output = OUT / f'{slug}.glb'
    bpy.ops.export_scene.gltf(filepath=str(output), export_format='GLB', use_selection=True,
        use_active_scene=True, export_apply=False, export_extras=True,
        export_animations=False, export_cameras=False, export_lights=False, export_yup=True)
    raw = output.read_bytes()
    length = struct.unpack_from('<I', raw, 12)[0]
    gltf = json.loads(raw[20:20 + length])
    nodes = [n for n in gltf.get('nodes', []) if 'mesh' in n]
    assert len(nodes) == len(parts), (slug, len(nodes), len(parts))
    assert all(n.get('extras', {}).get('sourceName') for n in nodes)
    reports.append({'id': slug, 'name': path.stem.replace('_', ' ').replace(' - ', ' · '),
        'sourceBlend': path.relative_to(ROOT).as_posix(),
        'sourceSha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'partCount': len(parts), 'triangles': sum(p['triangles'] for p in parts),
        'originalBytes': len(raw), 'parts': parts})
    (OUT / 'manifest.json').write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'EXPORTED {slug}: {len(parts)} parts, {len(raw):,} bytes', flush=True)

print(f'COMPLETE: {len(reports)} models', flush=True)
