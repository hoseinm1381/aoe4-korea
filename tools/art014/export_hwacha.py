"""Export the saved editable Hwacha with the exact official cannon rig contract."""
import bpy,sys,shutil,json
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/art014'));from common import *
from rig_contract import read_contract
sys.path.insert(0,str(EXT.parent));import garrison;sys.modules['garrison.garrison_shared']=sys.modules['garrison_shared'];garrison.register()
from garrison import unit_export
from garrison_shared import unit_model_export as core
A=R/'authoring/art014/hwacha';bpy.ops.wm.open_mainfile(filepath=str(A/'kr_hwacha.blend'),load_ui=False,use_scripts=False)
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');meshes=[bpy.data.objects['kr_hwacha_lod'+str(i)] for i in [1,2,3]]
source='art/civilizations/chinese/team_weapons/chi_nest_of_bees/chi_nest_of_bees'
stock=stock_game.current().model_files(source,required=('.rgm',));contract=read_contract(stock['.rgm']);records=unit_export.skeleton_records(rig)
assert [r['name'].lower() for r in records]==[r['name'].lower() for r in contract['bones']]
out=W/'hwacha-export';out.mkdir(exist_ok=True)
counts=tuple(contract['lod_counts']);counts=counts if len(counts)==3 else (len(records),)*3
unit_export.export_unit_model(rig,[meshes[0]],out/'model.fbx',records,three_lods=True,lod_counts=counts,lod_meshes={2:meshes[1],3:meshes[2]})
parts=[(p['name'],p['start'],p['count']) for p in contract['partitions']];core.write_rig(out,core.rig_text(records,partitions=parts))
for role in ['albedo','pattern','normal','roughness','metalness']:shutil.copy2(A/(role+'.png'),out/(role+'.png'))
write_json(out/'export.json',{'asset':'kr_hwacha','official_source':source,'official_contract':contract,'material_name':meshes[0].data.materials[0].name,'triangles':[sum(len(f.vertices)-2 for f in o.data.polygons) for o in meshes],'source_sha256':sha((A/'kr_hwacha.blend').read_bytes())})
print('HWACHA_EXPORTED',out,flush=True)
