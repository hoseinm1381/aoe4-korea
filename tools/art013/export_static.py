"""Export the curated equipment, unique lifecycle models and camp modules.

Background Blender only. Never save or modify an editable source file.
"""
import bpy,json,sys,os,hashlib,struct,shutil,re
from pathlib import Path
from mathutils import Matrix
R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools'))
from runtime import EXT,read_json,write_json,stock_game
from garrison_shared import relic_chunky as rc
from garrison_shared import unit_model_export as unit_core
sys.path.insert(0,str(EXT.parent));import garrison;sys.modules['garrison.garrison_shared']=sys.modules['garrison_shared'];garrison.register()
from garrison import unit_export
sys.path.insert(0,str(EXT/'bin/core/src/core/blender_scripts'))
from prepare_static_fbx import partition_mesh_object
ROOT_RECORD=read_json(R/'source/art013/static-root-record.json')['records']
BASE=R/'output/art-current/static-exports';BASE.mkdir(parents=True,exist_ok=True)
CAT=read_json(R/'authoring/art013/catalog.json')
template=(R/'source/art013/cook-template/model.rgo').read_bytes()
static_info=next(c.payload for c in rc.walk(rc.parse(template).roots) if c.tag==b'INFO')

def pack(c,payload):return rc.pack_chunk(c.kind,c.tag,payload,version=c.version,name=c.name)
def rgo(selectors, building=False):
 d=rc.parse(template);ms=next(c for c in rc.walk(d.roots) if c.tag==b'MSBP')
 old=ms.children;hdr=next(c for c in old if c.tag==b'HDR ');msa=next(c for c in old if c.tag==b'MSA ')
 sd=next(c for c in old if c.tag==b'MSD ' and len(c.payload)>4);count=next(c for c in old if c.tag==b'MSD ' and len(c.payload)==4)
 cond=next(c for c in old if c.tag==b'CNBP')
 payload=pack(hdr,hdr.payload)+pack(msa,msa.payload)+pack(count,struct.pack('<I',len(selectors)))
 for i,(name,meshes,states) in enumerate(selectors):
  p=rc.lp_string(name)+struct.pack('<I',len(meshes))+b''.join(rc.lp_string(n) for n in meshes)
  # Exact native single equality record from the qualified template. Repeated
  # states use the native OR term flag observed in official building selectors.
  terms=[]
  for j,state in enumerate(states):terms.append(struct.pack('<IBI',2,0,int(j>0))+rc.lp_string('life_cycle_state')+rc.lp_string(state))
  payload+=pack(sd,p)+pack(cond,struct.pack('<I',len(terms))+b''.join(terms))
 return rc.rebuild(d,lambda c:payload if c.offset==ms.offset else (R/'source/art013/building-lifecycle-defaults.bin').read_bytes() if building and c.tag==b'DTBP' else static_info if c.tag==b'INFO' else None)

def export_group(objects,name,lod):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:
  o.hide_set(False);o.hide_viewport=False;o.hide_select=False;o.hide_render=False;o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.object.duplicate()
 copies=list(bpy.context.selected_objects)
 # Export only the source basis; scene parenting never changes the model origin.
 for o in copies:
  w=o.matrix_world.copy();o.parent=None;o.matrix_world=w
 bpy.context.view_layer.objects.active=copies[0]
 if len(copies)>1:bpy.ops.object.join()
 o=bpy.context.view_layer.objects.active;o.name=name+f'_lod{lod+1}';o.data.name=o.name
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 return o

records=[]
rows=[x for x in CAT['sources'] if x['group'] in ['Weapons and equipment','Landmarks and unique buildings'] or x['id'] in ['Korea_lumber_camp01','Korea_mining_camp01']]
for i,row in enumerate(rows,1):
 out=BASE/row['id'];out.mkdir(exist_ok=True)
 receipt=out/'export.json'
 if receipt.exists() and read_json(receipt).get('static_contract')==(5 if row['id']=='hwangnyongsa' else 3):
  prev=read_json(receipt)
  assert prev['source_sha256']==row['sha256']
  assert all(hashlib.sha256((out/n).read_bytes()).hexdigest()==h for n,h in prev['files'].items())
  
  if prev['kind'] in ['unique','camp_module']:
   path=out/'model.rgo';doc=rc.parse(path.read_bytes());path.write_bytes(rc.rebuild(doc,lambda c:(R/'source/art013/building-lifecycle-defaults.bin').read_bytes() if c.tag==b'DTBP' else None));prev['files']['model.rgo']=hashlib.sha256(path.read_bytes()).hexdigest();write_json(receipt,prev)
  records.append(prev);print('STATIC_REUSED',i,len(rows),row['id'],flush=True);continue
 bpy.ops.wm.open_mainfile(filepath=str(R/row['blend']),load_ui=False,use_scripts=False)
 source=[o for o in bpy.data.objects if o.type=='MESH'];groups={};kind='equipment'
 if row['group']=='Landmarks and unique buildings':
  kind='unique'
  # The source has both editable components and joined export duplicates.
  # Use editable lifecycle collections; omit the duplicate EXPORT_* meshes.
  for o in source:
   if any(c.name.startswith('EXPORT_') for c in o.users_collection):continue
   state=o.get('lifecycle_state');lod=int(o.get('source_lod',0))
   if state is not None:groups.setdefault((state,lod),[]).append(o)
  assert ('healthy',0) in groups,(row['id'],list(groups))
 elif row['id'] in ['Korea_lumber_camp01','Korea_mining_camp01']:
  kind='camp_module';source=[o for o in source if o.name.startswith('Korean_work_shelter_')]
  assert source;groups={('healthy',0):source}
 else:
  for o in source:
   lod=int(re.search(r'LOD(\d+)',o.name).group(1)) if re.search(r'LOD(\d+)',o.name) else 0
   groups.setdefault(('healthy',lod),[]).append(o)
  assert len(groups)==3,(row['id'],list(groups))
 # Hidden source collections otherwise prevent FBX export despite object flags.
 for c in bpy.data.collections:c.hide_viewport=False;c.hide_render=False
 def layers(l):
  l.exclude=False;l.hide_viewport=False
  for child in l.children:layers(child)
 layers(bpy.context.view_layer.layer_collection)
 exported=[];selectors=[];counts={}
 for (state,lod),objects in sorted(groups.items()):
  name='mesh_'+state;obj=export_group(objects,name,lod)
  counts[state+f'_lod{lod}']=sum(len(p.vertices)-2 for p in obj.data.polygons)
  parts=[obj]
  if row['id']=='hwangnyongsa':
   bpy.context.view_layer.objects.active=obj
   tri=obj.modifiers.new('Native export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
   import math
   nparts=4 if state=='healthy' else max(1,math.ceil(len(obj.data.polygons)/12000))
   faces=list(range(len(obj.data.polygons)));step=math.ceil(len(faces)/nparts)
   chunks=[faces[j*step:min((j+1)*step,len(faces))] for j in range(nparts)]
   parts=partition_mesh_object(obj,chunks,name,False)
   for j,part in enumerate(parts):part.name=name+f'_part{j}_lod{lod+1}';part.data.name=part.name
  exported.extend(parts)
  if lod==0:
   if kind=='unique':
    if state=='healthy':states=['healthy','preview','targeting']
    elif state.startswith('construction_'):
     start=int(state.rsplit('_',1)[1]);states=[f'construct_{x:02}' for x in range(start,min(start+25,100),5)]
    elif state.startswith('damage_'):
     states={'damage_25':['damage_1','damage_2'],'damage_50':['damage_3'],'damage_75':['damage_4','damage_5']}[state]
    elif state=='ruins':states=['ruins']
    else:raise ValueError(state)
   else:states=['healthy','preview','damage_1','damage_2','damage_3','damage_4','damage_5']
   selectors.append(('sel_'+state,[name+f'_part{j}' for j in range(len(parts))] if row['id']=='hwangnyongsa' else [name],states))
 if row['id']=='hwangnyongsa':
  partition_materials={}
  for o in exported:
   for slot in o.material_slots:
    name=slot.material.name+'_'+re.sub(r'_lod[123]$','',o.name)
    if name not in partition_materials:
     material=slot.material.copy();material.name=name;partition_materials[name]=material
    slot.material=partition_materials[name]
 mats={m.name:m for o in exported for m in o.data.materials if m}
 clean={}
 for name,mat in mats.items():
  mat.name='source-'+name
  cm=bpy.data.materials.new(name);cm.use_nodes=False;clean[name]=cm
 for o in exported:
  for slot in o.material_slots:
   original=slot.material
   slot.material=next(clean[name] for name,m in mats.items() if m==original)
  uv=o.data.uv_layers.active;assert uv is not None
  for other in list(o.data.uv_layers):
   if other!=uv:o.data.uv_layers.remove(other)
  extra=o.data.uv_layers.new(name='UV2',do_init=True)
  # Match Garrison's verified rigid-model UV streams and V pre-compensation.
  for layer in o.data.uv_layers:
   for loop in layer.data:loop.uv.y=1.0-loop.uv.y
 # Camp modules have several ordinary Principled materials. Export each source
 # part with its original material; the material writer below records each one.
 bpy.ops.object.select_all(action='DESELECT')
 for o in exported:o.select_set(True)
 bpy.context.view_layer.objects.active=exported[0]
 # One unchanged official root makes the unit shader's static skin stream valid
 # and preserves its authored RGB owner/skin/hair masks. No clips are supplied.
 arm=bpy.data.armatures.new('Korean_static_native_root');rig=bpy.data.objects.new('Korean_static_native_root',arm);bpy.context.scene.collection.objects.link(rig)
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig;bpy.ops.object.mode_set(mode='EDIT')
 bone=arm.edit_bones.new(ROOT_RECORD[0]['name']);bone.matrix=Matrix(unit_core.rest_matrix(ROOT_RECORD[0]));bone.length=1.0
 root_name=bone.name;bpy.ops.object.mode_set(mode='OBJECT')
 for o in exported:
  o.vertex_groups.clear();group=o.vertex_groups.new(name=root_name);group.add(list(range(len(o.data.vertices))),1.0,'REPLACE')
  mod=o.modifiers.new('Native static-root binding','ARMATURE');mod.object=rig
  # The qualified unit exporter will apply its own V pre-compensation.
  for layer in o.data.uv_layers:
   for loop in layer.data:loop.uv.y=1.0-loop.uv.y
 import inspect
 code=inspect.getsource(unit_export.export_unit_model);namespace=dict(vars(unit_export));exec(compile(code.replace('filepath=str(output),','filepath=str(output), use_triangles=True,'),'korean-explicit-static-triangles','exec'),namespace)
 namespace['export_unit_model'](rig,exported,out/'model.fbx',ROOT_RECORD)
 unit_core.write_rig(out,unit_core.rig_text(ROOT_RECORD,partitions=[('Static_LOD1',0,1)]))
 (out/'model.rgo').write_bytes(rgo(selectors, building=kind in ['unique','camp_module']))
 (out/'model.rgotemplate').write_bytes((R/'source/art013/cook-template/model.rgotemplate').read_bytes())
 # Record actual material graphs for portable native material generation. No
 # player-colour preview is baked; use the authored albedo and pattern maps.
 materials=[]
 for name,mat in mats.items():
  textures={}
  if kind in ['unique','equipment']:
   for role in ['albedo','normal','roughness','metalness','pattern']:
    found=[x for x in row['textures'] if role in x['name'].lower()]
    assert len(found)==1,(row['id'],role,found)
    textures[role]=str(R/found[0]['file'])
  else:
   for n in mat.node_tree.nodes:
    if n.type=='TEX_IMAGE' and n.image:textures['albedo']=bpy.path.abspath(n.image.filepath)
   bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
   if 'albedo' not in textures:
    color=tuple(bs.inputs['Base Color'].default_value)
    image=bpy.data.images.new('export-solid',width=4,height=4,alpha=True);image.generated_color=color;image.filepath_raw=str(out/(hashlib.sha256(name.encode()).hexdigest()[:12]+'.png'));image.file_format='PNG';image.save();textures['albedo']=image.filepath_raw
  materials.append({'name':name,'textures':textures})
 record={'asset':row['id'],'kind':kind,'static_contract':3,'source':row['blend'],'source_sha256':row['sha256'],'lod_triangles':counts,'selectors':selectors,'materials':materials,'animated':False,'native_static_root_bones':1,'root_record':ROOT_RECORD,'lossless_render_partition':row['id']=='hwangnyongsa'}
 if row['id']=='hwangnyongsa':record['static_contract']=5
 record['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file() and p.name!='export.json'}
 write_json(receipt,record);records.append(record);print('STATIC_EXPORTED',i,len(rows),row['id'],counts,flush=True)
write_json(R/'docs/update_013/static-export.json',{'assets':records,'source_files_unchanged':True})
