"""Independent native readback of every Korean rigid model and lifecycle set."""
from pathlib import Path
import sys,tempfile,json,subprocess,hashlib,concurrent.futures
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));sys.path.insert(0,str(R/'tools/art013'))
from runtime import EXT,read_json,write_json
import readback_probe as private
core=EXT/'bin/core/garrison-core.exe';arch=EXT/'bin/sga-archiver.exe';rec=read_json(R/'docs/update_013/static-cook.json');archive=Path(rec['archive'])
base=Path(tempfile.gettempdir())/('k13/static-readbacks-'+rec['archive_sha256'][:8]);base.mkdir(exist_ok=True)
listing=json.loads(subprocess.check_output([str(arch),'list',str(archive),'--verify'],text=True));assert listing['archive']['verification']['verified']
private.INDEX=base/'index.sqlite3'
if not private.INDEX.exists():private.create_index(archive,listing['members'],listing['archive']['name'])
config=read_json(private.ORIGINAL_CONFIG);config['index_path']=str(private.INDEX);write_json(base/'config.json',config)
extraction=base/'native'
if not extraction.exists():subprocess.run([str(arch),'extract',str(archive),str(extraction),'--filter','art/kr013/'],stdout=subprocess.DEVNULL,check=True)
rows=read_json(R/'docs/update_013/static-export.json')['assets'];records=[]
def one(row):
 asset=row['asset'];out=base/asset;out.mkdir(exist_ok=True);receipt=out/'readback.json'
 if receipt.exists():return read_json(receipt)
 cmd=[str(core),'convert','decode-static','--logical-path','art/kr013/static/'+asset.lower()+'/model.rgm','--config',str(base/'config.json'),'--index',str(private.INDEX),'--output-root',str(out/'decoded')]
 p=subprocess.run(cmd,capture_output=True,text=True,errors='replace',timeout=300);(out/'decode.log').write_text(p.stdout+'\n'+p.stderr)
 assert p.returncode==0,(asset,p.stdout,p.stderr)
 decoded=read_json(json.loads(p.stdout)['manifest_path']);groups=decoded['geometry']['groups']
 result={'asset':asset,'manifest':json.loads(p.stdout)['manifest_path'],'blockers':decoded['blockers'],'warnings':decoded['warnings'],'completeness':decoded['completeness'],'groups':[{'mesh':g.get('mesh_index'),'group':g.get('group_index'),'name':g.get('mesh_name',g.get('name')),'lod':g.get('lod_level'),'triangles':g['triangle_count']} for g in groups],'native_triangles':sum(g['triangle_count'] for g in groups),'source_triangles':sum(row['lod_triangles'].values()),'native_collection_contract':decoded.get('structure_collection_contract'),'source_sha256':row['source_sha256']}
 assert not result['blockers'],(asset,result['blockers'])
 assert result['completeness']['missing_texture_references']==0,(asset,result['completeness'])
 assert result['native_triangles']==result['source_triangles'],(asset,result['native_triangles'],result['source_triangles'])
 write_json(receipt,result);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futures={pool.submit(one,row):row['asset'] for row in rows}
 for f in concurrent.futures.as_completed(futures):
  try:record=f.result()
  except Exception as e:record={'asset':futures[f],'error':str(e)}
  records.append(record);write_json(R/'docs/update_013/static-native-readback.json',{'archive_sha256':rec['archive_sha256'],'assets':records,'completed':len(records),'expected':len(rows),'all_passed':len(records)==len(rows) and not any('error' in x for x in records)})
  print('STATIC_NATIVE_READBACK',len(records),len(rows),record['asset'],record.get('error','PASS'),flush=True)
assert not any('error' in x for x in records)
