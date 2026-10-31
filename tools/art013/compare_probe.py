"""Compare decoded native skin/UV/LOD data to the saved Korean Blender source."""
from pathlib import Path
import bpy,json,sys,argparse,math,hashlib
from mathutils import Vector
from mathutils.kdtree import KDTree
R=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--manifest',required=True,type=Path);p.add_argument('--asset',default='kr_villager_male_a1');p.add_argument('--report',required=True,type=Path);a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
cat=json.loads((R/'authoring/art013/catalog.json').read_text('utf-8'));row=next(x for x in cat['sources'] if x['id']==a.asset)
source=R/row['blend'];assert hashlib.sha256(source.read_bytes()).hexdigest()==row['sha256']
bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');meshes=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:sum(len(f.vertices)-2 for f in o.data.polygons),reverse=True)
d=json.loads(a.manifest.read_text('utf-8'));assert not d['blockers'] and not d['warnings']
assert d['completeness']['status']=='complete' and d['completeness']['rig_projection_status']=='complete'
assert len(meshes)==3
by_lod={1:[],2:[],3:[]}
for group in d['geometry']['groups']:
 name=group['rig_projection']['lod_palette']['name'];level=int(name.rsplit('_lod',1)[1]);assert level in by_lod;by_lod[level].append(group)
assert all(by_lod.values())
groups=[]
for level in [1,2,3]:
 parts=by_lod[level];merged=dict(parts[0])
 for key in ['positions','skin_indices','skin_weights']:merged[key]=sum((g[key] for g in parts),[])
 merged['uv_layers']={'UVMap':sum((next(iter(g['uv_layers'].values())) for g in parts),[])}
 merged['triangle_count']=sum(g['triangle_count'] for g in parts);merged['vertex_count']=sum(g['vertex_count'] for g in parts);merged['native_parts']=len(parts);groups.append(merged)
bones=d['skeleton']['bones'];assert len(bones)==len(rig.data.bones)
assert {b['name'].lower():(b['parent_name'] or '').lower() for b in bones}=={b.name.lower():(b.parent.name if b.parent else '').lower() for b in rig.data.bones}
palette=d['skeleton']['skin_palettes'];assert len(palette)==1
native_names={b['palette_index']:b['name'].lower() for b in palette[0]['bones']}
assert {l['name'] for l in palette[0]['lod_palettes']}=={'unit_mesh_lod1','unit_mesh_lod2','unit_mesh_lod3'}
results=[]
for index,(obj,g) in enumerate(zip(meshes,groups)):
 triangles=sum(len(f.vertices)-2 for f in obj.data.polygons);assert triangles==g['triangle_count'],('Triangle count drift',index)
 placement=rig.matrix_world.inverted()@obj.matrix_world;mat=placement.to_3x3();normal_matrix=mat.inverted().transposed()
 points=[placement@v.co for v in obj.data.vertices]
 # A half-float coordinate can move by one ULP in the native truncation path.
 def half_step(v):return 2**(math.floor(math.log2(abs(v)))-10) if abs(v)>=2**-14 else 2**-24
 position_limit=max(.0011,max((math.sqrt(sum(half_step(v)**2 for v in point)) for point in points),default=0)+1e-5)
 tree=KDTree(len(points))
 for i,pos in enumerate(points):tree.insert(pos,i)
 tree.balance();uvs={i:[] for i in range(len(points))}
 for face in obj.data.polygons:
  for loop in face.loop_indices:uvs[obj.data.loops[loop].vertex_index].append((float(obj.data.uv_layers.active.data[loop].uv.x),1.0-float(obj.data.uv_layers.active.data[loop].uv.y)))
 uv_limit=max(.00075,max((math.hypot(half_step(u),half_step(1-v)) for rows in uvs.values() for u,v in rows),default=0)+1e-6)
 weights=[]
 for v in obj.data.vertices:
  w={obj.vertex_groups[x.group].name.lower():x.weight for x in v.groups if x.weight>1e-8};total=sum(w.values());weights.append({k:x/total for k,x in w.items()})
 native_uv=next(iter(g['uv_layers'].values()));max_pos=max_uv=max_weight=0.;unmatched=0;native_used=set()
 for i,pos in enumerate(g['positions']):
  candidates=tree.find_range(Vector(pos),position_limit);expected={native_names[n]:w for n,w in zip(g['skin_indices'][i],g['skin_weights'][i]) if w>0}
  matches=[]
  for _,j,distance in candidates:
   uv=min((math.dist(native_uv[i],u) for u in uvs[j]),default=999)
   weight=max((abs(expected.get(k,0)-weights[j].get(k,0)) for k in set(expected)|set(weights[j])),default=0)
   omitted=set(weights[j])-set(expected)
   # Sub-byte influences may be dropped before the surviving channels are
   # renormalized. No new bone and no omitted influence >= one byte is admitted.
   admitted=set(expected)<=set(weights[j]) and all(weights[j][k]<1/255+1e-6 for k in omitted)
   surviving={k:weights[j][k] for k in expected if k in weights[j]};total=sum(surviving.values())
   surviving={k:w/total for k,w in surviving.items()} if total else {}
   dominant=max(surviving,key=surviving.get) if surviving else None
   quantized_ok=admitted and bool(surviving) and all(abs(expected.get(k,0)-w)<=((len(surviving)-1)/255 if k==dominant else 1/255)+1e-6 for k,w in surviving.items())
   if uv<=uv_limit and quantized_ok:matches.append((distance,uv,weight,j))
  if not matches:
   if unmatched<2:
    nearest=tree.find(Vector(pos));j=nearest[1]
    print('NATIVE_SOURCE_DIAGNOSTIC',index,'native_pos',pos,'source_pos',list(nearest[0]),'distance',nearest[2],'native_uv',native_uv[i],'source_uv',uvs[j][:3],'native_weights',expected,'source_weights',weights[j],flush=True)
   unmatched+=1;continue
  distance,uv,weight,j=min(matches);native_used.add(j);max_pos=max(max_pos,distance);max_uv=max(max_uv,uv);max_weight=max(max_weight,weight)
 assert unmatched==0,('Native corners do not match source positions/UVs/weights',index,unmatched)
 results.append({'lod':index+1,'source_mesh':obj.name,'source_vertices':len(points),'native_vertices':g['vertex_count'],'triangles':triangles,'matched_native_vertices':g['vertex_count'],'unmatched_native_vertices':unmatched,'max_position_error_m':max_pos,'max_uv_error':max_uv,'max_normalized_weight_error':max_weight,'lod_palette':g['rig_projection']['lod_palette']['name'],'rig_projection':g['rig_projection']['status'],'native_parts':g['native_parts'],'position_limit_m':position_limit,'uv_limit':uv_limit})
report={'schema':'korea.art013-native-conversion-comparison/v1','asset':a.asset,'source_blend_sha256':row['sha256'],'manifest_sha256':hashlib.sha256(a.manifest.read_bytes()).hexdigest(),'status':'three_lods_positions_uv_weights_rig_hierarchy_qualified','skeleton_bones':len(bones),'native_blockers':d['blockers'],'native_warnings':d['warnings'],'lods':results,'native_gameplay_or_animation_acceptance':False,'uv_convention':'Source V flipped exactly as Garrison unit_export._prepare_mesh_copy specifies','position_limit_m':.0011,'uv_limit':'per-LOD mathematical half-float bound in native pre-projection coordinates; minimum 0.00075','weight_quantization_rule':'Sub-byte influences may be omitted and survivors renormalized; smaller channels within 1/255, dominant remainder within (surviving_count-1)/255; no new bone influences'}
a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
