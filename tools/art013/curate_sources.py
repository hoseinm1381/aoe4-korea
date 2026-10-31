from pathlib import Path
import bpy,json,hashlib,shutil,sys,time
import argparse
p=argparse.ArgumentParser(description='One-time source promotion, not an ordinary build dependency');p.add_argument('--source-root',required=True,type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
SRC=a.source_root.resolve()
REPO=Path(__file__).resolve().parents[2]
DST=REPO/'authoring/art013';DST.mkdir(parents=True,exist_ok=True)
CAT=json.loads((SRC/'reports/catalogue-index.json').read_text('utf-8'))['assets']
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
bpy.context.preferences.filepaths.save_version=0
rows=[];textures={};start=time.monotonic()
for number,row in enumerate(CAT,1):
 source=SRC/row['path'];target=DST/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
 assert not target.exists(),target
 before=sha(source);bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
 assert not bpy.data.libraries,'External Blender libraries require explicit dependency closure'
 counts={'vertices':sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH'),'polygons':sum(len(o.data.polygons) for o in bpy.data.objects if o.type=='MESH'),'armatures':sum(o.type=='ARMATURE' for o in bpy.data.objects)}
 deps=[]
 for im in bpy.data.images:
  if im.source!='FILE' or im.users==0:continue
  old=Path(bpy.path.abspath(im.filepath));packed=bytes(im.packed_file.data) if im.packed_file else None
  if old.is_file():
   data=old.read_bytes()
   if packed is not None:assert packed==data,('Packed image differs from file',str(source),str(old))
  else:
   assert packed is not None,('Missing external image',str(source),str(old));data=packed
  h=hashlib.sha256(data).hexdigest();suffix=old.suffix.lower() or '.png';dest=DST/'textures'/(h+suffix)
  if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
  else:assert sha(dest)==h
  im.filepath=bpy.path.relpath(str(dest),start=str(target.parent));deps.append({'name':im.name,'file':dest.relative_to(REPO).as_posix(),'sha256':h,'bytes':len(data),'packed':packed is not None})
  textures[dest.relative_to(REPO).as_posix()]={'sha256':h,'bytes':len(data)}
 # Preserve concise source recipes/identity and lifecycle contracts, not renders or decoded caches.
 metadata={}
 for filename in ['recipe.json','native-state-contract.json','native_bind_snapshot.json','atlas_layout.json','camp-module.json']:
  p=source.parent/filename
  if p.exists():
   dest=target.parent/filename;shutil.copy2(p,dest);metadata[filename]=dest.relative_to(REPO).as_posix()
 bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True,check_existing=False,relative_remap=False)
 assert sha(source)==before,'Original source changed'
 saved=sha(target)
 rows.append({'id':source.stem,'group':row['group'],'blend':target.relative_to(REPO).as_posix(),'original_source':str(source),'original_sha256':before,'sha256':saved,'bytes':target.stat().st_size,'geometry_counts':counts,'textures':deps,'metadata':metadata})
 (DST/'catalog.json').write_text(json.dumps({'schema':'korea.art013-curated-sources/v1','sources':rows,'shared_textures':textures,'scope':'Existing authored sources, path-only portability changes, no geometry edits','original_source_preserved':True,'native_integration':'pending'},indent=2)+'\n',encoding='utf-8')
 print('CURATED_KOREA_SOURCE',number,len(CAT),source.stem,'blend_bytes',target.stat().st_size,flush=True)
print('CURATION_COMPLETE','assets',len(rows),'blend_bytes',sum(x['bytes'] for x in rows),'unique_texture_bytes',sum(x['bytes'] for x in textures.values()),'seconds',round(time.monotonic()-start,2),flush=True)