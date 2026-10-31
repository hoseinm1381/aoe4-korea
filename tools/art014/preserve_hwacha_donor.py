"""Keep the editable donor geometry/rig needed by the recipe, without temporary texture links."""
import bpy
from pathlib import Path
R=Path(__file__).resolve().parents[2];A=R/'authoring/art014/hwacha'
bpy.ops.wm.open_mainfile(filepath='F:/aoe_4_temp/Temp_aoe4/hwacha-donor.blend',load_ui=False,use_scripts=False)
for o in list(bpy.data.objects):
 if o.type not in ['ARMATURE','MESH'] or o.name=='Cube':bpy.data.objects.remove(o,do_unlink=True)
 elif o.type=='MESH':o.data.materials.clear()
for m in list(bpy.data.materials):
 if m.users==0:bpy.data.materials.remove(m)
for i in list(bpy.data.images):
 if i.users==0:bpy.data.images.remove(i)
bpy.ops.wm.save_as_mainfile(filepath=str(A/'donor_geometry.blend'))
print('EDITABLE_HWACHA_DONOR_PRESERVED',flush=True)
