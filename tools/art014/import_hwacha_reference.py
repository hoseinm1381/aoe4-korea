from pathlib import Path
import bpy,sys,json
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/art014'));from common import *
sys.path.insert(0,str(EXT.parent));import garrison;sys.modules['garrison.garrison_shared']=sys.modules['garrison_shared'];garrison.register()
from garrison.decode_projection import _apply_decoded_static
bpy.ops.object.empty_add();proxy=bpy.context.object;proxy.name='Hwacha donor reference'
p=next((W/'hwacha-donor').rglob('decoded-static.json'));report=read_json(p)
result=_apply_decoded_static(proxy,report,create_controls=False)
print('IMPORTED',[(o.name,o.type) for o in bpy.data.objects],flush=True)
bpy.ops.wm.save_as_mainfile(filepath=str(W/'hwacha-donor.blend'))


