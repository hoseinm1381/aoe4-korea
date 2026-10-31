"""Carry curated building geometry into exact private native owners.

Preserves topology, UVs, packed masks, skin records and native lifecycle sets.
Uses current installed official resources; no old donor directory is required.
"""
from pathlib import Path
import bpy,sys,json,hashlib,struct,tempfile
import numpy as np
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
from runtime import read_json,write_json,stock_game
from garrison_shared import relic_chunky as rc,model_variants as mv
G=stock_game.current();BASE=R/'output/art-current/ordinary-native';BASE.mkdir(parents=True,exist_ok=True)
rows=[x for x in read_json(R/'authoring/art013/catalog.json')['sources'] if x['group']=='Ordinary buildings']
records=[];texture_sources={}
for i,row in enumerate(rows,1):
 out=BASE/row['id'];out.mkdir(exist_ok=True);receipt=out/'export.json'
 if receipt.exists():
  old=read_json(receipt);assert old['source_sha256']==row['sha256'];records.append(old)
  texture_sources.update(old['texture_sources']);print('ORDINARY_REUSED',i,len(rows),row['id'],flush=True);continue
 contract=read_json(R/row['metadata']['native-state-contract.json']);stem=contract['donor']['logical_path'][:-4]
 native=G.model_files(stem,required=('.rgm','.rgo','.rrgeom','.rrmaterial'))
 assert hashlib.sha256(native['.rrgeom']).hexdigest()==contract['native_resources']['geometry']['sha256'],'Official model changed; requalify source'
 bpy.ops.wm.open_mainfile(filepath=str(R/row['blend']),load_ui=False,use_scripts=False)
 meshes=[o for c in bpy.data.collections if c.name.startswith('01_NATIVE_ALL_STATES') for o in c.all_objects if o.type=='MESH']
 assert meshes,(row['id'],'missing complete native source')
 ordered=sorted(meshes,key=lambda o:(int(o['garrison_mesh_index']),int(o.get('garrison_group_index',0))))
 assert len({(int(o['garrison_mesh_index']),int(o.get('garrison_group_index',0))) for o in ordered})==len(ordered)
 by_index=dict(enumerate(ordered))
 doc=rc.parse(native['.rrgeom']);chunks=[c for c in rc.walk(doc.roots) if c.tag==b'GEOB'];assert len(chunks)==len(meshes)*2
 changes={};counts=[];textures={};edits={}
 for gi,(c,idx) in enumerate(zip(chunks[::2],chunks[1::2])):
  o=by_index[gi];data=bytearray(c.payload);n,_,stride,_=struct.unpack_from('<4I',data);assert n==len(o.data.vertices) and stride>=24
  pos=np.array([o.matrix_world@v.co for v in o.data.vertices],dtype=np.float64)
  nativepos=np.ndarray((n,4),dtype='<f2',buffer=data,offset=16,strides=(stride,2))
  before=nativepos.copy();nativepos[:,0]=-pos[:,0];nativepos[:,1]=pos[:,2];nativepos[:,2]=-pos[:,1]
  quant=np.stack((-nativepos[:,0],-nativepos[:,2],nativepos[:,1]),axis=1).astype(float)
  assert np.isfinite(quant).all() and float(np.abs(quant-pos).max())<.04
  moved=np.any(before[:,:3]!=nativepos[:,:3],axis=1)
  # Preserve artist-saved split-normal records and every byte outside positions.
  for vi in range(n):
   a=16+vi*stride;assert data[a+6:a+stride]==c.payload[a+6:a+stride]
  changes[c.offset]=bytes(data)
  counts.append({'group':gi,'vertices':n,'stride':stride,'changed_vertices':int(moved.sum()),'position_error_max_m':float(np.abs(quant-pos).max()),'index_buffer_sha256':hashlib.sha256(idx.payload).hexdigest()})
  mat=o.data.materials[0];slot=o.get('garrison_material_slot')
  for node in mat.node_tree.nodes:
   if node.type!='TEX_IMAGE' or not node.image or 'albedo' not in node.name.lower():continue
   image=Path(bpy.path.abspath(node.image.filepath))
   if image.suffix.lower()!='.png':continue
   role=node.name.split(' · ')[-1];assert role.startswith('albedo'),node.name
   h=hashlib.sha256(image.read_bytes()).hexdigest();member='art/kr013/recolors/'+h+'.rrtex'
   edits.setdefault(slot,{})[role]=member
   textures[member]=str(image)
 encoded=rc.rebuild(doc,lambda c:changes.get(c.offset))
 check=rc.parse(encoded);aa=list(rc.walk(doc.roots));bb=list(rc.walk(check.roots));assert len(aa)==len(bb)
 for a,b in zip(aa,bb):
  if not a.children and a.offset not in changes:assert a.payload==b.payload
 final='art/kr013/ordinary/'+row['id'].lower()+'/model'
 model=rc.parse(native['.rgm']);bana=[c for c in rc.walk(model.roots) if c.tag==b'BANA'];assert len(bana)==1
 rgm=rc.rebuild(model,lambda c:rc.lp_string(final.replace('/','\\')) if c.offset==bana[0].offset else None)
 material=rc.parse(native['.rrmaterial']);material_changes={}
 for c in material.roots:
  name=c.decoded_name.removesuffix('_collection')
  if c.tag!=b'GMat' or name not in edits:continue
  one=rc.pack_document([rc.pack_chunk(c.kind,c.tag,c.payload,version=c.version,name=c.name)])
  updated=mv.rewrite_material(one,edits[name],{});material_changes[c.offset]=rc.parse(updated).roots[0].payload
 rrmat=rc.rebuild(material,lambda c:material_changes.get(c.offset))
 for ext,raw in {'.rgm':rgm,'.rgo':native['.rgo'],'.rrgeom':encoded,'.rrmaterial':rrmat}.items():(out/('model'+ext)).write_bytes(raw)
 record={'asset':row['id'],'source_sha256':row['sha256'],'stock_model':stem,'private_model':final,'route':'Exact native topology with curated source vertex positions; installed stock material/state owners','native_selectors_preserved':True,'uv_index_skin_and_masks_byte_identical':True,'groups':counts,'texture_sources':textures,'material_edits':edits,'native_lod_contract':'Original native structure retained; lower-detail source previews are not claimed as activated native LODs','files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='export.json'}}
 write_json(receipt,record);records.append(record);texture_sources.update(textures);print('ORDINARY_NATIVE_READY',i,len(rows),row['id'],sum(x['changed_vertices'] for x in counts),flush=True)
write_json(R/'docs/update_013/ordinary-native.json',{'assets':records,'texture_sources':texture_sources,'source_blends_unchanged':True,'native_runtime':'pending'})
