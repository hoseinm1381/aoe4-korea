"""Repository-only cook and receiver compatibility readback for all Korean units."""
from pathlib import Path
import sys,json,tempfile,shutil,hashlib,subprocess,struct,zlib,xml.etree.ElementTree as ET,concurrent.futures,collections
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));sys.path.insert(0,str(R/'tools/art013'))
from runtime import EXT,read_json,write_json
from prepare_model_tools import prepare
import readback_probe as reader
base=Path(tempfile.gettempdir())/'k13';stage=base/'current-unit-project';source=stage/'source'
if not stage.exists():shutil.copytree(R/'source/art013/cook-template',stage)
def png(color):
 def c(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b))
 return b'\x89PNG\r\n\x1a\n'+c(b'IHDR',struct.pack('>2I5B',4,4,8,6,0,0,0))+c(b'IDAT',zlib.compress(b''.join(b'\0'+bytes(color)*4 for _ in range(4))))+c(b'IEND',b'')
defaults={'normal':(128,128,255,255),'roughness':(190,190,190,255),'metalness':(0,0,0,255),'pattern':(0,0,0,255)}
rows=[]
for p in sorted((R/'output/art-current/unit-exports').glob('*/export.json')):
 row=read_json(p);rows.append(row);stem='art/kr013/units/'+row['asset'];dest=source/stem;dest.mkdir(parents=True,exist_ok=True)
 for name in ['model.fbx','model.rig']:shutil.copy2(p.parent/name,dest/name)
 for name in ['model.rgo','model.rgotemplate']:shutil.copy2(R/'source/art013/cook-template'/name,dest/name)
 mat=ET.Element('materialSet');m=ET.SubElement(mat,'material',name=row['material_name'],type='shader',source='unit')
 for role,param in {'albedo':'albedoTexture','normal':'normalMap','roughness':'roughnessTex','metalness':'metalTex','pattern':'patternTex'}.items():
  f=p.parent/(role+'.png');target=dest/(role+'.png')
  if f.exists():shutil.copy2(f,target)
  else:target.write_bytes(png(defaults[role]))
  ET.SubElement(m,'param',name=param,type='tex2D',value=stem+'/'+target.name)
 ET.ElementTree(mat).write(dest/'model.material',encoding='utf8',xml_declaration=True)
assert len(rows)==72
run=base/'unit-model-cook-compatible'
if '--verify-only' not in sys.argv:
 assert not run.exists(),'Prior native diagnostics protected'
 cmd=[EXT/'bin/core/garrison-core.exe','essence','build-mod','--editor',prepare(),'--mod',stage/'k013.aoe4mod','--run-root',run,'--timeout','1200','--console-burn-log']
 with (R/'docs/update_013/unit-compatible-cook.log').open('w',encoding='utf8') as f:p=subprocess.run(list(map(str,cmd)),stdout=f,stderr=subprocess.STDOUT)
 assert p.returncode==0,'Inspect unit-compatible-cook.log'
archives=list((run/'output').rglob('*.sga'));assert len(archives)==1;archive=archives[0];sha=hashlib.sha256(archive.read_bytes()).hexdigest()
arch=EXT/'bin/sga-archiver.exe';core=EXT/'bin/core/garrison-core.exe'
listing=json.loads(subprocess.check_output([str(arch),'list',str(archive),'--verify'],text=True));assert listing['archive']['verification']['verified']
out=base/('compatible-unit-readbacks-'+sha[:8]);out.mkdir(exist_ok=True);reader.INDEX=out/'index.sqlite3'
if not reader.INDEX.exists():reader.create_index(archive,listing['members'],listing['archive']['name'])
config=read_json(reader.ORIGINAL_CONFIG);config['index_path']=str(reader.INDEX);write_json(out/'config.json',config)
before=read_json(R/'docs/update_013/unit-native-readbacks.json');baseline={x['asset']:x for x in before['assets']};write_json(R/'docs/update_013/original-unit-native-readbacks.json',before)
allowed={b['name'].lower() for b in read_json(R/'source/art013/cavalry-owner-contract.json')['contract']['bones']}
def influences(doc,group):
 palettes=doc['skeleton']['skin_palettes'];p=next((x for x in palettes if x.get('name')==group.get('skin_palette')),None)
 # The qualified models keep one full palette per LOD. Resolve through the
 # decoder's explicit group palette index when available, else identical names.
 if p is None:
  pi=group.get('rig_projection',{}).get('palette_index')
  p=palettes[pi] if isinstance(pi,int) else palettes[0]
 names={b['palette_index']:b['name'] for b in p['bones']}
 return [{names[i]:sum(w for j,w in zip(indices,weights) if j==i) for i in set(indices) if sum(w for j,w in zip(indices,weights) if j==i)>0} for indices,weights in zip(group['skin_indices'],group['skin_weights'])]
def one(row):
 folder=out/row['asset'];folder.mkdir(exist_ok=True);cached=list((folder/'decoded').rglob('decoded-static.json'))
 if cached:path=str(cached[0])
 else:
  cmd=[str(core),'convert','decode-static','--logical-path','art/kr013/units/'+row['asset']+'/model.rgm','--config',str(out/'config.json'),'--index',str(reader.INDEX),'--output-root',str(folder/'decoded')]
  p=subprocess.run(cmd,capture_output=True,text=True,errors='replace',timeout=300);(folder/'decode.log').write_text(p.stdout+'\n'+p.stderr);assert p.returncode==0,(row['asset'],p.stdout,p.stderr);path=json.loads(p.stdout)['manifest_path']
 d=read_json(path);old=read_json(baseline[row['asset']]['manifest']);assert not d['blockers'] and d['completeness']['missing_texture_references']==0
 def by_lod(doc):
  result={}
  for group in doc['geometry']['groups']:
   key=group['rig_projection']['lod_palette']['name'];merged=result.setdefault(key,{'triangle_count':0,'positions':[],'uv_layers':{'UV':[]},'weights':[]})
   merged['triangle_count']+=group['triangle_count'];merged['positions'].extend(group['positions']);merged['uv_layers']['UV'].extend(next(iter(group['uv_layers'].values())));merged['weights'].extend(influences(doc,group))
  return result
 ag=by_lod(old);bg=by_lod(d);assert set(ag)==set(bg)
 folds=row.get('weight_compatibility_folds',{});foldlower={k.lower():v.lower() for k,v in folds.items()};max_weight=0.0;corners=0
 for key,a in ag.items():
  b=bg[key];assert a['triangle_count']==b['triangle_count'];wa=a['weights'];wb=b['weights']
  # Vertex order and deduplication can change when influences are folded.
  # Match by native-quantized position and authored UV, then compare skin values.
  def uv(g,i):return tuple(next(iter(g['uv_layers'].values()))[i])
  lookup=collections.defaultdict(list)
  for i,pos in enumerate(a['positions']):
   weights={}
   for n,w in wa[i].items():name=foldlower.get(n.lower(),n.lower());weights[name]=weights.get(name,0)+w
   lookup[(tuple(pos),uv(a,i))].append(weights)
  for i,pos in enumerate(b['positions']):
   candidates=lookup[(tuple(pos),uv(b,i))];assert candidates,(row['asset'],'Native geometry/UV changed')
   weights={n.lower():w for n,w in wb[i].items()}
   error=min(max(abs(x.get(n,0)-weights.get(n,0)) for n in set(x)|set(weights)) for x in candidates);max_weight=max(max_weight,error);assert error<=.016,(row['asset'],error)
   if folds:assert set(weights)<=allowed,(row['asset'],set(weights)-allowed)
   corners+=1
 result={'asset':row['asset'],'manifest':path,'basic_native_contract_passed':True,'source_sha256':row['source_sha256'],'geometry_uv_and_triangles_preserved':True,'bone_hierarchy_preserved':[(x['name'],x.get('parent_index')) for x in old['skeleton']['bones']]==[(x['name'],x.get('parent_index')) for x in d['skeleton']['bones']],'weight_compatibility_folds':folds,'maximum_native_weight_difference':max_weight,'vertices_compared':corners,'completeness':d['completeness']};assert result['bone_hierarchy_preserved'];return result
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futures={pool.submit(one,x):x['asset'] for x in rows}
 for future in concurrent.futures.as_completed(futures):
  try:record=future.result()
  except Exception as e:record={'asset':futures[future],'error':str(e),'basic_native_contract_passed':False}
  results.append(record);write_json(R/'docs/update_013/compatible-unit-native-readbacks.json',{'archive':str(archive),'archive_sha256':sha,'archive_bytes':archive.stat().st_size,'assets':results,'completed':len(results),'expected_assets':72,'all_passed':len(results)==72 and all(x['basic_native_contract_passed'] for x in results)})
  print('COMPATIBLE_UNIT_READBACK',len(results),72,record['asset'],record.get('error','PASS'),flush=True)
assert all(x['basic_native_contract_passed'] for x in results),'Inspect native unit compatibility failures'
write_json(R/'docs/update_013/unit-native-readbacks.json',{'archive':str(archive),'archive_sha256':sha,'archive_bytes':archive.stat().st_size,'assets':results,'completed':72,'expected_assets':72,'archive_integrity_passed':True,'all_passed':True})
