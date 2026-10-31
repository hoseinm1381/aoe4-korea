"""Fold only unsupported mount skin influences to an existing animated ancestor.

Editable sources, geometry, UVs, rig hierarchy and animation owners stay intact.
The current common cavalry animator has no rein bones; this is a visual binding
adaptation, recorded separately from the original exact-source qualification.
"""
from pathlib import Path
import bpy,sys,json,os,hashlib,inspect,shutil
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
from runtime import EXT,read_json,write_json,stock_game
sys.path.insert(0,str(EXT.parent));import garrison;sys.modules['garrison.garrison_shared']=sys.modules['garrison_shared'];garrison.register()
from garrison import unit_export
from garrison_shared import unit_model_export as core
contract=read_json(R/'source/art013/cavalry-owner-contract.json')
raw=stock_game.current().model_files(contract['source'][:-4],required=('.rgm',))['.rgm'];assert hashlib.sha256(raw).hexdigest()==contract['sha256']
allowed={b['name'].lower() for b in contract['contract']['bones']}
code=inspect.getsource(unit_export.export_unit_model);ns=dict(vars(unit_export));exec(compile(code.replace('filepath=str(output),','filepath=str(output), use_triangles=True,'),'explicit-triangulated-cavalry-export','exec'),ns)
rows=[x for x in read_json(R/'authoring/art013/catalog.json')['sources'] if x['id'].startswith('kr_mount_')]
reports=[]
for row in rows:
 out=R/'output/art-current/unit-exports'/row['id'];old=read_json(out/'export.json')
 if old.get('animation_owner_compatibility')==contract['sha256']:reports.append(old);continue
 bpy.ops.wm.open_mainfile(filepath=str(R/row['blend']),load_ui=False,use_scripts=False)
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');records=unit_export.skeleton_records(rig);parents={x['name'].lower():(x.get('parent_name') or '').lower() for x in records};actual={x['name'].lower():x['name'] for x in records}
 meshes=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:sum(len(f.vertices)-2 for f in o.data.polygons),reverse=True);assert len(meshes)==3
 folds={}
 for o in meshes:
  groups={g.index:g.name for g in o.vertex_groups};weights=[]
  for v in o.data.vertices:
   rowweights={}
   for g in v.groups:
    if g.weight<=0:continue
    name=groups[g.group];target=name.lower();seen=set()
    while target not in allowed:
     assert target not in seen and parents.get(target),(row['id'],name,'No compatible animated ancestor');seen.add(target);target=parents[target]
    if target!=name.lower():folds[name]=actual[target]
    target=actual[target];rowweights[target]=rowweights.get(target,0)+g.weight
   weights.append(rowweights)
  o.vertex_groups.clear()
  for name in sorted({n for w in weights for n in w}):o.vertex_groups.new(name=name)
  for vi,w in enumerate(weights):
   for name,value in w.items():o.vertex_groups[name].add([vi],value,'REPLACE')
 assert all('rein' in name.lower() for name in folds),(row['id'],folds)
 n=len(records);ns['export_unit_model'](rig,[meshes[0]],out/'model.fbx',records,three_lods=True,lod_counts=(n,n,n),lod_meshes={2:meshes[1],3:meshes[2]})
 core.write_rig(out,core.rig_text(records,partitions=[('FullBody_LOD3',0,n)]))
 old.update(animation_owner_compatibility=contract['sha256'],weight_compatibility_folds=folds,original_geometry_uv_rig_and_lod_triangles_preserved=True)
 old['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='export.json'}
 write_json(out/'export.json',old);reports.append(old);print('MOUNT_REIN_COMPATIBLE',row['id'],len(folds),flush=True)
write_json(R/'docs/update_013/mount-compatibility-exports.json',{'animation_owner':contract['source'],'owner_sha256':contract['sha256'],'assets':reports,'source_blends_changed':False,'geometry_uv_and_rig_hierarchy_changed':False,'native_readback':'pending'})
