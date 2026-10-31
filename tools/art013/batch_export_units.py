"""Export only curated Korean unit/mount sources; no generated actors or animation replacements."""
from pathlib import Path
import bpy,sys,json,os,hashlib,shutil,argparse,inspect
R=Path(__file__).resolve().parents[2]
EXT=Path(os.environ.get('GARRISON_EXTENSION',Path.home()/'AppData/Roaming/Blender Foundation/Blender/5.2/extensions/raw_githubusercontent_com/garrison'))
sys.path.insert(0,str(EXT));from garrison_shared import unit_model_export as core
sys.path.insert(0,str(EXT.parent));import garrison;sys.modules['garrison.garrison_shared']=sys.modules['garrison_shared'];garrison.register()
from garrison import unit_export
p=argparse.ArgumentParser();p.add_argument('--ids',nargs='*');p.add_argument('--triangulate',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
cat=json.loads((R/'authoring/art013/catalog.json').read_text('utf-8'));rows=[x for x in cat['sources'] if '/units/' in x['blend']]
assert len(rows)==72
if a.ids:rows=[x for x in rows if x['id'] in a.ids];assert len(rows)==len(a.ids)
export_model=unit_export.export_unit_model
if a.triangulate:
 code=inspect.getsource(export_model);assert code.count('filepath=str(output),')==1
 namespace=dict(vars(unit_export));exec(compile(code.replace('filepath=str(output),','filepath=str(output), use_triangles=True,'),'garrison-explicit-fbx-triangulation','exec'),namespace);export_model=namespace['export_unit_model']
base=R/'output/art-current/unit-exports';base.mkdir(parents=True,exist_ok=True)
for number,row in enumerate(rows,1):
 out=base/row['id'];source=R/row['blend'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
 if (out/'export.json').is_file():
  old=json.loads((out/'export.json').read_text());assert old['source_sha256']==row['sha256']
  assert all(hashlib.sha256((out/n).read_bytes()).hexdigest()==h for n,h in old['files'].items())
  if not a.triangulate or old.get('fbx_explicit_triangulation'):
   print('EXPORT_REUSED',number,len(rows),row['id'],flush=True);continue
 if out.exists():assert (out/'export.json').exists() or {f.name for f in out.iterdir()}<={'model.fbx','model.rig'},'Unknown incomplete export is protected'
 else:out.mkdir()
 bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
 rigs=[o for o in bpy.data.objects if o.type=='ARMATURE'];meshes=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:sum(len(f.vertices)-2 for f in o.data.polygons),reverse=True)
 assert len(rigs)==1 and len(meshes)==3
 rig=rigs[0];records=unit_export.skeleton_records(rig);n=len(records)
 # For non-civilian rigs use the exact imported skeleton for all authored LODs;
 # native cook/readback must separately qualify palette reduction/bind records.
 if n==73:counts=(73,50,32);partitions=None;mode='documented_73_bone_partitions'
 else:counts=(n,n,n);partitions=[('FullBody_LOD3',0,n)];mode='exact_full_native_skeleton_all_lods_pending_palette_and_runtime_cost_readback'
 export_model(rig,[meshes[0]],out/'model.fbx',records,three_lods=True,lod_counts=counts,lod_meshes={2:meshes[1],3:meshes[2]})
 core.write_rig(out,core.rig_text(records,partitions=partitions))
 roles={}
 for role in ['albedo','normal','roughness','metalness','pattern']:
  matches=[x for x in row['textures'] if x['name'].split('.')[0]==role]
  assert len(matches)<=1,(row['id'],role)
  if matches:shutil.copy2(R/matches[0]['file'],out/(role+'.png'));roles[role]=role+'.png'
 assert 'albedo' in roles
 record={'schema':'korea.art013-unit-model-export/v1','asset':row['id'],'source':row['blend'],'source_sha256':row['sha256'],'native_geometry_only':True,'fbx_explicit_triangulation':a.triangulate,'animation_replacements':False,'bones':n,'rig_mode':mode,'lod_triangles':[sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes],'textures':roles,'material_name':meshes[0].data.materials[0].name,'records':records,'native_cook_readback':'pending'}
 record['files']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file() and f.name!='export.json'}
 (out/'export.json').write_text(json.dumps(record,indent=2)+'\n');print('KOREAN_UNIT_EXPORTED',number,len(rows),row['id'],'bones',n,'lod_triangles',record['lod_triangles'],flush=True)
print('UNIT_EXPORT_BATCH_COMPLETE',len(rows),flush=True)
