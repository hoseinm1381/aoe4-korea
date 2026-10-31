from pathlib import Path
import bpy,sys,json
R=Path(__file__).resolve().parents[2];EXT=Path(__import__('os').environ.get('GARRISON_EXTENSION',Path.home()/'AppData/Roaming/Blender Foundation/Blender/5.2/extensions/raw_githubusercontent_com/garrison'))
sys.path.insert(0,str(EXT));from garrison_shared import unit_model_export as core
sys.path.insert(0,str(EXT.parent));import garrison;sys.modules['garrison.garrison_shared']=sys.modules['garrison_shared'];garrison.register()
from garrison import unit_export
p=R/'authoring/art013/art/korea/units/kr_villager_male_a1/kr_villager_male_a1.blend'
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
rigs=[o for o in bpy.data.objects if o.type=='ARMATURE'];assert len(rigs)==1
meshes=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:sum(len(p.vertices)-2 for p in o.data.polygons),reverse=True);assert len(meshes)==3
records=unit_export.skeleton_records(rigs[0]);out=R/'output/art-current/export/villager_pilot';out.mkdir(parents=True,exist_ok=True)
print('PILOT_SOURCE',len(records),'bones',[(o.name,len(o.data.vertices),len(o.data.polygons)) for o in meshes],flush=True)
unit_export.export_unit_model(rigs[0],[meshes[0]],out/'model.fbx',records,three_lods=True,lod_meshes={2:meshes[1],3:meshes[2]})
core.write_rig(out,core.rig_text(records))
(out/'records.json').write_text(json.dumps(records,indent=2))
(out/'source-snapshot.json').write_text(json.dumps({'meshes':[{'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons)} for o in meshes],'rig':rigs[0].name,'bones':len(records)},indent=2))
print('PILOT_EXPORTED',str(out),flush=True)