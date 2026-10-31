from pathlib import Path
import bpy,sys,json,shutil,tempfile
R=Path(__file__).resolve().parents[2];EXT=Path(__import__('os').environ.get('GARRISON_EXTENSION',Path.home()/'AppData/Roaming/Blender Foundation/Blender/5.2/extensions/raw_githubusercontent_com/garrison'))
sys.path.insert(0,str(EXT));import garrison_shared
sys.path.insert(0,str(EXT.parent));import garrison;sys.modules['garrison.garrison_shared']=garrison_shared;garrison.register()
from garrison import unit_export,unit_prototype_panel as panel
catalog=json.loads((R/'authoring/art013/catalog.json').read_text());row=next(x for x in catalog['sources'] if x['id']=='kr_villager_male_a1')
bpy.ops.wm.open_mainfile(filepath=str(R/row['blend']),load_ui=False,use_scripts=False)
mesh=max([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:len(o.data.polygons))
doc=json.loads(next((Path(tempfile.gettempdir())/'k13/prototype-cli').rglob('prototype.json')).read_text())
rig=panel.create_unit(doc,bpy.context)
clone=mesh.copy();clone.data=mesh.data.copy();bpy.context.scene.collection.objects.link(clone)
for m in clone.modifiers:
 if m.type=='ARMATURE':m.object=rig
rig.garrison_unit.mesh=clone
folder=Path(tempfile.gettempdir())/'k13/control';folder.mkdir(exist_ok=True)
record=panel.export_document(rig);assert record['fingerprint']==doc['fingerprint'] and not record['overrides'] and not record['attachments']
record['material_name']=clone.data.materials[0].name
record['textures']=[role for role in ['albedo','normal','roughness','metalness','pattern'] if any(x['name'].split('.')[0]==role for x in row['textures'])]
for role in record['textures']:
 matches=[x for x in row['textures'] if x['name'].split('.')[0]==role];assert len(matches)==1,(role,[x['name'] for x in row['textures']]);shutil.copy2(R/matches[0]['file'],folder/(role+'.png'))
unit_export.export_unit_model(rig,[clone],folder/'model.fbx',unit_export.skeleton_records(rig),three_lods=True)
(folder/'action.json').write_text(json.dumps(record,indent=2))
print('GENUINE_TEMPLATE_ONLY_EXPORT',folder,record['fingerprint'],flush=True)