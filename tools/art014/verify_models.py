"""Decode the fresh 014 cook; fail on incomplete geometry, material or rig contracts."""
import sys,json,subprocess,concurrent.futures,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
import readback_probe as private
from rig_contract import read_contract
from garrison_shared import relic_chunky as rc
rec=read_json(D/'native-cook.json');archive=Path(rec['archive'])
assert sha(archive.read_bytes())==rec['sha256']
base=W/'readbacks014';base.mkdir(exist_ok=True)
G=stock_game.current();listing=G.archiver.run(['list',str(archive),'--verify'])
assert listing['archive']['verification']['verified']
private.INDEX=base/'index.sqlite3'
if not private.INDEX.exists():private.create_index(archive,listing['members'],listing['archive']['name'])
config=read_json(private.ORIGINAL_CONFIG);config['index_path']=str(private.INDEX);write_json(base/'config.json',config)
rows=read_json(D/'cook-inputs.json');official=read_json(D/'OFFICIAL_RIG_CONTRACTS.json')
if '--static-only' in sys.argv:
 rows=[row for row in rows if row['kind']=='static']
 private.INDEX=W/'merged-decode/index.sqlite3';config=read_json(W/'merged-decode/config.json');write_json(base/'config.json',config)
def one(row):
 out=base/row['asset'];out.mkdir(exist_ok=True);receipt=out/'receipt.json'
 if receipt.exists():return read_json(receipt)
 cmd=[EXT/'bin/core/garrison-core.exe','convert','decode-static','--logical-path',row['stem']+'/model.rgm','--config',base/'config.json','--index',private.INDEX,'--output-root',out/'decoded']
 p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,errors='replace',timeout=300)
 (out/'decode.log').write_text(p.stdout+'\n'+p.stderr,encoding='utf8');assert p.returncode==0,(row['asset'],p.stdout,p.stderr)
 manifest=Path(json.loads(p.stdout)['manifest_path']);d=read_json(manifest)
 assert not d['blockers'],(row['asset'],d['blockers'])
 assert d['completeness']['missing_texture_references']==0,(row['asset'],d['completeness'])
 raw=(W/'cooked014'/row['stem']/'model.rgm').read_bytes()
 if row['kind']=='unit':
  expected=official[row['asset']]['contract'];actual=read_contract(raw)
  for key in ['bones','partitions','groups','lod_counts']:assert actual[key]==expected[key],(row['asset'],key)
  assert d['completeness']['rig_projection_status']=='complete',(row['asset'],d['completeness'])
  export=read_json(W/'unit-exports'/row['asset']/'export.json')
  assert sum(g['triangle_count'] for g in d['geometry']['groups'])==sum(export['lod_triangles'])
 else:
  assert not any(c.tag==b'SKLN' for c in rc.walk(rc.parse(raw).roots)),row['asset']
  export=read_json(W/'static-exports'/row['asset']/'export.json')
  assert sum(g['triangle_count'] for g in d['geometry']['groups'])==sum(export['lod_triangles'].values()),row['asset']
 result={'asset':row['asset'],'kind':row['kind'],'passed':True,'manifest':str(manifest),'manifest_sha256':sha(manifest.read_bytes()),'triangles':sum(g['triangle_count'] for g in d['geometry']['groups']),'warnings':d['warnings'],'missing_textures':0,'official_skeleton_groups_partitions_lods_equal':row['kind']=='unit','rigid_has_no_skeleton':row['kind']=='static'}
 write_json(receipt,result);return result
records=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futures={pool.submit(one,row):row['asset'] for row in rows}
 for future in concurrent.futures.as_completed(futures):
  try:record=future.result()
  except Exception as e:record={'asset':futures[future],'passed':False,'error':str(e)}
  records.append(record);print('MODEL_READBACK',len(records),len(rows),record['asset'],record.get('error','PASS'),flush=True)
  write_json(D/('STATIC_READBACK.json' if '--static-only' in sys.argv else 'MODEL_READBACK.json'),{'archive_sha256':rec['sha256'],'all_passed':len(records)==len(rows) and all(x['passed'] for x in records),'assets':sorted(records,key=lambda x:x['asset'])})
assert len(records)==len(rows) and all(x['passed'] for x in records)
