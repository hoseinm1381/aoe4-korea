"""Render decoded geometry with the authored materials for visual review in Blender."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


def texture(path):
    image = bpy.data.images.load(str(path), check_existing=True)
    image.colorspace_settings.name = 'sRGB'
    return image


def material(name, color_path, mask_path, owner):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    base = nodes.new('ShaderNodeTexImage')
    base.image = texture(color_path)
    output = nodes.get('Principled BSDF')
    output.inputs['Roughness'].default_value = .79
    if mask_path is None:
        links.new(base.outputs['Color'], output.inputs['Base Color'])
        return mat
    mask = nodes.new('ShaderNodeTexImage')
    mask.image = bpy.data.images.load(str(mask_path), check_existing=True)
    mask.image.colorspace_settings.name = 'Non-Color'
    separate = nodes.new('ShaderNodeSeparateColor')
    links.new(mask.outputs['Color'], separate.inputs[0])
    mix = nodes.new('ShaderNodeMixRGB')
    links.new(separate.outputs[0], mix.inputs[0])
    links.new(base.outputs['Color'], mix.inputs[1])
    mix.inputs[2].default_value = owner
    links.new(mix.outputs['Color'], output.inputs['Base Color'])
    return mat


def mesh_group(group, mat, scene):
    mesh = bpy.data.meshes.new(group['name'])
    mesh.from_pydata(group['positions'], [], group['triangles'])
    mesh.update()
    uv = mesh.uv_layers.new(name='UVMap')
    source_uv = group['uv_layers']['UVMap']
    for loop in mesh.loops:
        uv.data[loop.index].uv = source_uv[loop.vertex_index]
    obj = bpy.data.objects.new(group['name'], mesh)
    scene.collection.objects.link(obj)
    mesh.materials.append(mat)
    return obj


def aim(obj, target):
    obj.rotation_euler = (target - obj.location).to_track_quat('-Z', 'Y').to_euler()


def light(scene, name, location, energy, size, center):
    data = bpy.data.lights.new(name, 'AREA')
    data.energy, data.shape, data.size = energy, 'DISK', size
    obj = bpy.data.objects.new(name, data)
    scene.collection.objects.link(obj)
    obj.location = location
    aim(obj, center)


def render(stage, name, variant, owner):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new('Review background')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.1, .14, .19, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = .4
    path, = (stage/'decoded-isolated/static'/name).glob('*/decoded-static.json')
    decoded = json.loads(path.read_text(encoding='utf-8'))
    shelter = name.startswith('korea_')
    groups = [g for g in decoded['geometry']['groups']
              if g['name'].startswith('mesh_healthy') and
              (shelter or g['rig_projection']['lod_palette']['name'].endswith('lod1'))]
    assert groups
    paint = stage/'candidate/authoring/art035'
    mats = {}
    for group in groups:
        slot = group['material']
        if slot not in mats:
            if variant == 'before':
                color, mask = (stage/'camp-albedo.dds', None) if shelter else (stage/'albedo.dds', stage/'mask.dds')
            elif shelter:
                color = paint/(slot.removeprefix('korea_camp_') + '.png')
                mask = paint/'shelter-owner.png' if slot.endswith('weathered_timber') else None
            else:
                color, mask = paint/'landmark-albedo.png', paint/'landmark-owner.png'
            mats[slot] = material(slot, color, mask, owner)
        mesh_group(group, mats[slot], scene)
    points = [p for group in groups for p in group['positions']]
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    center = (low + high) / 2
    scale = max(high - low)
    camera_data = bpy.data.cameras.new('Architecture review')
    camera_data.type, camera_data.ortho_scale = 'ORTHO', scale * 1.70
    camera = bpy.data.objects.new('Architecture review', camera_data)
    scene.collection.objects.link(camera)
    camera.location = center + Vector((.76, -.92, .7))*scale*2
    aim(camera, center)
    scene.camera = camera
    light(scene, 'Key', center + Vector((-1, -2, 3))*scale, scale**2*350, scale, center)
    light(scene, 'Fill', center + Vector((2, 1, 2))*scale, scale**2*140, scale*1.5, center)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 8
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = 'AgX'
    scene.render.resolution_x = 460
    scene.render.resolution_y = 325
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = str(stage/f'{name}-{variant}.png')
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    stage = Path(sys.argv[sys.argv.index('--') + 1])
    for asset in ('seon_deok_observatory', 'bulguksa_temple', 'korea_mining_camp01'):
        render(stage, asset, 'before', (.035, .16, .65, 1))
        render(stage, asset, 'after', (.035, .16, .65, 1))
        if asset == 'korea_mining_camp01':
            render(stage, asset, 'red', (.65, .05, .03, 1))
