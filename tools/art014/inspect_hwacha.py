from pathlib import Path
import bpy,sys,json,math
from mathutils import Vector
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/art014'));from common import *
bpy.ops.wm.open_mainfile(filepath=str(W/'hwacha-donor.blend'),load_ui=False,use_scripts=False)
for o in list(bpy.data.objects):
 if o.name in ['Camera','Cube','Light'] or 'geo_pole' in o.name or o.name.endswith(('.001','.002')):bpy.data.objects.remove(o,do_unlink=True)
for o in bpy.data.objects:
 if o.type=='MESH':print('DONOR_MESH',o.name,'bounds',[(min(v.co[i] for v in o.data.vertices),max(v.co[i] for v in o.data.vertices)) for i in range(3)],'vertex_groups',[(g.index,g.name) for g in o.vertex_groups],flush=True)
bpy.ops.object.camera_add(location=(5,-6,4.5));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4.9;bpy.context.scene.camera=cam
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.render.resolution_x=850;s.render.resolution_y=750;s.render.resolution_percentage=100;s.render.filepath=str(W/'hwacha-donor.png');bpy.ops.render.render(write_still=True)
print('RIG',[(o.name,list(o.keys())) for o in bpy.data.objects if o.type=='ARMATURE'],flush=True)
