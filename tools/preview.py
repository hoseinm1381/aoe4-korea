"""Render the nine shipped healthy Korean meshes with their new palettes."""
from pathlib import Path
import json, sys, struct
import bpy
from mathutils import Vector
import numpy as np

root, stage, extension=map(Path,sys.argv[sys.argv.index('--')+1:])
sys.path[:0]=[str(root/'tools/art035'),str(extension)]
from preview_blender import aim, light, material, mesh_group
from garrison_shared import relic_chunky as rc

def position_data(geom):
    _, vp, _, ip=[c.payload for c in geom.children if c.tag in (b'GEOC',b'GEOB')]
    n,_,stride,_=struct.unpack_from('<4I',vp)
    m,_,istride,_=struct.unpack_from('<4I',ip)
    assert stride in (20,24,28,32)
    raw=np.ndarray((n,3),dtype='<f2',buffer=vp,offset=16,strides=(stride,2)).astype(float)
    xyz=raw[:,[0,2,1]]
    xyz[:,1]*=-1
    uv=np.ndarray((n,2),dtype='<f2',buffer=vp,offset=28,strides=(stride,2)).astype(float)
    uv[:,1]=1-uv[:,1]
    idx=np.frombuffer(ip,dtype='<u'+str(istride),count=m,offset=16).reshape(-1,3)
    return {'name':'Healthy geometry','positions':xyz.tolist(),'triangles':idx.tolist(),
            'uv_layers':{'UVMap':uv.tolist()}}

out=stage/'palette/preview'
out.mkdir(exist_ok=True)
masters=stage/'palette/masters'
for png in sorted(masters.glob('*.png')):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=bpy.context.scene
    scene.world=bpy.data.worlds.new('Review')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.20,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.6
    mask=root/'authoring/art036/raised-owner.png'
    mat=material(png.stem,png,mask,(.06,.23,.65,1))
    bpy.data.images[mask.name].alpha_mode='CHANNEL_PACKED'
    path=root/f'inputs/native/art/kr013/static/{png.stem}/model.rrgeom'
    model=rc.parse(path.read_bytes())
    groups=[]
    for c in rc.walk(model.roots):
        if c.tag!=b'GEOM':continue
        header=next(x for x in c.children if x.tag==b'GOHD')
        if 'healthy' in rc.read_lp_string(header.payload,0)[0]:
            group=position_data(c);groups.append(group);mesh_group(group,mat,scene)
    assert groups
    xyz=np.array([p for g in groups for p in g['positions']])
    center=Vector((xyz.min(0)+xyz.max(0))*.5)
    span=np.ptp(xyz,axis=0).max()
    lens=bpy.data.cameras.new('Game camera')
    lens.type='ORTHO'
    lens.ortho_scale=span*1.55
    camera=bpy.data.objects.new('Game camera',lens)
    scene.collection.objects.link(camera)
    camera.location=center+Vector((.72,-.95,.82))*span*2
    aim(camera,center)
    scene.camera=camera
    light(scene,'Key',center+Vector((-1,-2,3))*span,span**2*530,span,center)
    light(scene,'Fill',center+Vector((2,1,2))*span,span**2*240,span*1.5,center)
    scene.render.engine='CYCLES'
    scene.cycles.samples=4
    scene.render.resolution_x=360
    scene.render.resolution_y=300
    scene.render.resolution_percentage=100
    scene.render.filepath=str(out/f'{png.stem}.png')
    bpy.ops.render.render(write_still=True)

