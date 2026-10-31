"""Cold-check Korean sources in factory Blender. --original-root is migration-only."""
from pathlib import Path
import bpy,json,hashlib,array,sys,argparse
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--original-root',type=Path);p.add_argument('--deduplicate-packed',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
C=R/'authoring/art013/catalog.json';cat=json.loads(C.read_text('utf-8'))
bpy.context.preferences.filepaths.save_version=0

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def buf(items,attr,n,code='f'):
 x=array.array(code,[0])*n;items.foreach_get(attr,x);return hashlib.sha256(x.tobytes()).hexdigest()
def snapshot():
 objects=[]
 for o in sorted(bpy.data.objects,key=lambda x:x.name):
  d={'name':o.name,'type':o.type,'matrix':[list(r) for r in o.matrix_world],
     'parent':o.parent.name if o.parent else None,'collections':sorted(c.name for c in o.users_collection)}
  if o.type=='MESH':
   m=o.data
   d.update(vertices=len(m.vertices),polygons=len(m.polygons),loops=len(m.loops),
    position=buf(m.vertices,'co',len(m.vertices)*3),
    topology=buf(m.loops,'vertex_index',len(m.loops),'i'),
    faces=buf(m.polygons,'loop_total',len(m.polygons),'i'),
    materials=[s.material.name if s.material else None for s in o.material_slots],
    material_indices=buf(m.polygons,'material_index',len(m.polygons),'i'),
    uv=[{'name':v.name,'data':buf(v.data,'uv',len(v.data)*2)} for v in m.uv_layers],
    weights=hashlib.sha256(json.dumps([[(o.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in m.vertices],separators=(',',':')).encode()).hexdigest(),
    modifiers=[{'name':v.name,'type':v.type,'target':getattr(getattr(v,'object',None),'name',None),'viewport':v.show_viewport,'render':v.show_render} for v in o.modifiers])
  elif o.type=='ARMATURE':
   d['bones']=[{'name':b.name,'parent':b.parent.name if b.parent else None,'matrix':[list(r) for r in b.matrix_local]} for b in o.data.bones]
  objects.append(d)
 images=[]
 for im in bpy.data.images:
  if im.source=='FILE' and im.users:
   file=Path(bpy.path.abspath(im.filepath)).resolve()
   raw=bytes(im.packed_file.data) if im.packed_file else file.read_bytes()
   if file.is_file():assert hashlib.sha256(raw).hexdigest()==sha(file)
   images.append({'name':im.name,'sha256':hashlib.sha256(raw).hexdigest(),'colorspace':im.colorspace_settings.name,'alpha':im.alpha_mode})
 material=[]
 for m in sorted(bpy.data.materials,key=lambda x:x.name):
  if m.use_nodes:
   material.append({'name':m.name,'nodes':[{'name':n.name,'type':n.type,'image':getattr(getattr(n,'image',None),'name',None),'inputs':[(s.name,list(s.default_value) if hasattr(s.default_value,'__len__') and not isinstance(s.default_value,str) else s.default_value) for s in n.inputs if hasattr(s,'default_value')]} for n in m.node_tree.nodes],'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in m.node_tree.links]})
 return hashlib.sha256(json.dumps({'objects':objects,'images':sorted(images,key=lambda x:x['name']),'materials':material},sort_keys=True,separators=(',',':')).encode()).hexdigest(),objects

results=[]
for i,row in enumerate(cat['sources'],1):
 target=R/row['blend'];before=None
 if not a.original_root:assert sha(target)==row['sha256'],('Edited master requires explicit inventory refresh',row['id'])
 if a.original_root:
  original=a.original_root/Path(row['blend']).relative_to('authoring/art013')
  assert sha(original)==row['original_sha256']
  bpy.ops.wm.open_mainfile(filepath=str(original),load_ui=False,use_scripts=False)
  before,_=snapshot()
 bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False,use_scripts=False)
 assert not bpy.data.libraries
 for dep in row['textures']:
  im=bpy.data.images.get(dep['name']);assert im is not None
  im.filepath=bpy.path.relpath(str(R/dep['file']),start=str(target.parent))
 semantic,objects=snapshot()
 if not a.original_root:assert semantic==row['semantic_sha256'],('Semantic source drift',row['id'])
 if before:assert semantic==before,('Source semantics changed',row['id'])
 if a.deduplicate_packed:
  for im in bpy.data.images:
   if im.source=='FILE' and im.users and im.packed_file:
    path=Path(bpy.path.abspath(im.filepath)).resolve();assert path.is_relative_to(R/'authoring/art013/textures')
    assert sha(path)==hashlib.sha256(bytes(im.packed_file.data)).hexdigest()
    im.unpack(method='REMOVE');im.filepath=bpy.path.relpath(str(path),start=str(target.parent))
  bpy.ops.wm.save_as_mainfile(filepath=str(target),compress=True,check_existing=False,relative_remap=False)
  bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False,use_scripts=False)
  again,_=snapshot();assert again==semantic,('Save semantic drift',row['id'])
 row['sha256']=sha(target);row['bytes']=target.stat().st_size;row['semantic_sha256']=semantic
 for dep in row['textures']:dep['packed']=False if a.deduplicate_packed else dep['packed']
 # All active file-image dependencies must now reside in this checkout.
 for im in bpy.data.images:
  if im.source=='FILE' and im.users:
   path=Path(bpy.path.abspath(im.filepath)).resolve();assert path.is_file() and path.is_relative_to(R)
   assert im.filepath.startswith('//')
 results.append({'id':row['id'],'semantic_sha256':semantic,'blend_sha256':row['sha256'],'mesh_objects':sum(o['type']=='MESH' for o in objects),'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in bpy.data.objects if o.type=='MESH'),'original_semantics_equal':before==semantic if before else None,'cold_open':True})
 print('COLD_VERIFIED',i,len(cat['sources']),row['id'],flush=True)
 if a.original_root:assert sha(original)==row['original_sha256']
if a.original_root:C.write_text(json.dumps(cat,indent=2)+'\n',encoding='utf-8')
report={'schema':'korea.art013-saved-file-verification/v1','assets':results,'source_only':True,'native_cook':False,'all_original_semantics_equal':all(r['original_semantics_equal'] for r in results) if a.original_root else None,'packed_texture_deduplication':a.deduplicate_packed}
(R/('docs/update_013/saved-files.json' if a.original_root else 'docs/update_013/saved-files-current.json')).write_text(json.dumps(report,indent=2)+'\n')
print('ALL_SOURCES_COLD_VERIFIED',len(results),flush=True)
