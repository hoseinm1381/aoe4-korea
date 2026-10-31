"""Cold source/native vertex+UV and lifecycle selector comparison, no scene saves."""
from pathlib import Path
import bpy,sys,json,math,struct,re
from mathutils import Vector,kdtree
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
from runtime import read_json,write_json,EXT
from garrison_shared import relic_chunky as rc
catalog={x['id']:x for x in read_json(R/'authoring/art013/catalog.json')['sources']};exports={x['asset']:x for x in read_json(R/'docs/update_013/static-export.json')['assets']}
native=read_json(R/'docs/update_013/static-native-readback.json');assert native['all_passed']
def halfstep(value):
 v=abs(value)
 return 2**(math.floor(math.log2(v))-10) if v else 2**-24
records=[]
for row in sorted(native['assets'],key=lambda x:x['asset']):
 name=row['asset'];source=catalog[name];bpy.ops.wm.open_mainfile(filepath=str(R/source['blend']),load_ui=False,use_scripts=False)
 meshes=[o for o in bpy.data.objects if o.type=='MESH'];groups={}
 for o in meshes:
  if exports[name]['kind']=='unique':
   if any(c.name.startswith('EXPORT_') for c in o.users_collection):continue
   state=o.get('lifecycle_state');lod=int(o.get('source_lod',0))
   if state is None:continue
  elif exports[name]['kind']=='camp_module':
   if not o.name.startswith('Korean_work_shelter_'):continue
   state='healthy';lod=0
  else:state='healthy';lod=int(re.search(r'LOD(\d+)',o.name).group(1))
  groups.setdefault((state,lod),[]).append(o)
 trees={}
 for key,objects in groups.items():
  points=[];uvs=[]
  for o in objects:
   data=o.data;layer=data.uv_layers.active
   for loop in data.loops:
    points.append(o.matrix_world@data.vertices[loop.vertex_index].co);uvs.append((float(layer.data[loop.index].uv.x),1.0-float(layer.data[loop.index].uv.y)))
  tree=kdtree.KDTree(len(points))
  for i,p in enumerate(points):tree.insert(p,i)
  tree.balance();limit=max(.0011,math.sqrt(sum(max(halfstep(p[a]) for p in points)**2 for a in range(3)))+.00001)
  uvlimit=max(.00075,max(math.hypot(halfstep(u),halfstep(v)) for u,v in uvs)+.000001)
  trees[key]=(tree,uvs,limit,uvlimit)
 d=read_json(row['manifest']);compared=0;maxpos=maxuv=0.0;states={}
 for g in d['geometry']['groups']:
  palette=g['rig_projection']['lod_palette']['name'];match=re.fullmatch(r'mesh_(.+?)(?:_part\d+)?_lod([123])',palette.split(':')[0]);assert match,(name,palette)
  key=(match.group(1),int(match.group(2))-1);tree,uvs,limit,uvlimit=trees[key];nativeuv=next(iter(g['uv_layers'].values()))
  for pos,uv in zip(g['positions'],nativeuv):
   candidates=tree.find_range(Vector(pos),limit);matches=[(dist,math.dist(uv,uvs[i])) for _,i,dist in candidates if math.dist(uv,uvs[i])<=uvlimit]
   assert matches,(name,key,pos,uv,'Unmatched native vertex or UV')
   distance,u=min(matches);maxpos=max(maxpos,distance);maxuv=max(maxuv,u);compared+=1
  states.setdefault(key,0);states[key]+=g['triangle_count']
 assert {state+f'_lod{lod}':n for (state,lod),n in states.items()}==exports[name]['lod_triangles'],(name,'State/LOD geometry differs')
 # The native burner must retain the authored lifecycle selectors, including
 # construction, damage and ruins. Ignore unrelated skeleton/buffer metadata.
 def selectors(raw):return [(c.tag,c.payload) for c in rc.walk(rc.parse(raw).roots) if c.tag in [b'MSD ',b'CNBP']]
 actual=Path(d['skeleton']['source']).read_bytes();expected=(R/'output/art-current/static-exports'/name/'model.rgo').read_bytes()
 aliases={}
 for g in d['geometry']['groups']:
  alias=re.sub(r'_lod[123]$','',g['rig_projection']['lod_palette']['name'].split(':')[0]);canonical=g['name']
  assert alias not in aliases or aliases[alias]==canonical
  aliases[alias]=canonical
 def member_set(payload):
  offset=0
  def string():
   nonlocal offset
   length=struct.unpack_from('<I',payload,offset)[0];offset+=4;value=payload[offset:offset+length].decode();offset+=length;return value
  selector=string();count=struct.unpack_from('<I',payload,offset)[0];offset+=4;members=[string() for _ in range(count)];assert offset==len(payload);return selector,set(members)
 aa=selectors(expected);bb=selectors(actual);assert len(aa)==len(bb)
 for (ta,pa),(tb,pb) in zip(aa,bb):
  assert ta==tb
  if ta==b'MSD ' and len(pa)>4:
   sa,ma=member_set(pa);sb,mb=member_set(pb);assert sa==sb and {aliases.get(m,m) for m in ma}==mb,(name,sa,'Native selector membership differs')
  else:assert pa==pb,(name,'Native lifecycle condition bytes differ')
 records.append({'asset':name,'vertices_compared':compared,'max_native_position_error_m':maxpos,'max_native_uv_error':maxuv,'state_and_lod_triangles_match':True,'native_lifecycle_selector_bytes_match':aa==bb,'native_lifecycle_selector_semantics_match':True,'native_lifecycle_condition_bytes_match':True,'native_mesh_aliases':aliases if aa!=bb else {},'source_file_unchanged':True})
 write_json(R/'docs/update_013/static-source-comparison.json',{'all_passed':len(records)==36,'assets':records,'native_game_acceptance':'pending'})
 print('STATIC_SOURCE_NATIVE_MATCH',len(records),36,name,compared,flush=True)
