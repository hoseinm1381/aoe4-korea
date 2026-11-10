"""Render the authored palettes and the two owner colours against one light rig."""
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/art035'))
from preview_blender import aim, light, material, mesh_group


def render(stage, asset, owner_name, owner):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.world=bpy.data.worlds.new('Architecture review')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.1,.14,.19,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.55
    path=stage/'preview-geometry'/(asset+'.json')
    groups=json.loads(path.read_text(encoding='utf-8'))
    art=stage/'candidate/authoring/art036'
    mat=material(asset,art/(asset+'.png'),art/'raised-owner.png',owner)
    bpy.data.images['raised-owner.png'].alpha_mode='CHANNEL_PACKED'
    for group in groups:
        mesh_group(group,mat,scene)
    points=[p for g in groups for p in g['positions']]
    bounds=[Vector(tuple(fun(p[i] for p in points) for i in range(3))) for fun in (min,max)]
    center=(bounds[0]+bounds[1])*.5
    span=max(bounds[1]-bounds[0])
    lens=bpy.data.cameras.new('Game angle')
    lens.type='ORTHO'
    lens.ortho_scale=span*1.73
    camera=bpy.data.objects.new('Game angle',lens)
    scene.collection.objects.link(camera)
    camera.location=center+Vector((.70,-.93,.76))*span*2
    aim(camera,center)
    scene.camera=camera
    light(scene,'Key',center+Vector((-1,-2,3))*span,span**2*480,span,center)
    light(scene,'Fill',center+Vector((2,1,2))*span,span**2*210,span*1.5,center)
    scene.render.engine='CYCLES'
    scene.cycles.samples=6
    scene.cycles.use_denoising=True
    scene.view_settings.view_transform='AgX'
    scene.render.resolution_x=416
    scene.render.resolution_y=360
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.render.filepath=str(stage/'preview'/f'{asset}-{owner_name}.png')
    bpy.ops.render.render(write_still=True)


if __name__=='__main__':
    stage=Path(sys.argv[sys.argv.index('--')+1])
    (stage/'preview').mkdir(exist_ok=True)
    for p in sorted((stage/'preview-geometry').glob('*.json')):
        render(stage,p.stem,'blue',(.025,.14,.61,1))
        if p.stem in ('stone_pagoda','gate_of_reverence','seowon_academy'):
            render(stage,p.stem,'green',(.025,.42,.065,1))
