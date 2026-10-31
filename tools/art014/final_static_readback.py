"""Read the actual final archive, including qualified one-root rigid skin streams."""
import sys,subprocess,concurrent.futures,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import *
import readback_probe as p
archive=W/'garrison-independent-builds/748d61b9-4d3e-4cf3-a506-a9ac1f992d1d/art014-current/korea.sga';base=W/'final-static-readback';base.mkdir(exist_ok=True)
listing=stock_game.current().archiver.run(['list',str(archive),'--verify']);assert listing['archive']['verification']['verified']
p.INDEX=base/'index.sqlite3'
if not p.INDEX.exists():p.create_index(archive,listing['members'],listing['archive']['name'])
config=read_json(p.ORIGINAL_CONFIG);config['index_path']=str(p.INDEX);write_json(base/'config.json',config)
rows=[r for r in read_json(D/'cook-inputs.json') if r['kind']=='static'];original={r['asset']:r for r in read_json(R/'docs/update_013/static-export.json')['assets']}
def one(row):
 out=base/row['asset'];out.mkdir(exist_ok=True);cached=out/'receipt.json'
 if cached.exists():return read_json(cached)
 cmd=[EXT/'bin/core/garrison-core.exe','convert','decode-static','--logical-path',row['stem']+'/model.rgm','--config',base/'config.json','--index',p.INDEX,'--output-root',out/'decoded']
 result=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,timeout=90);(out/'decode.log').write_text(result.stdout+'\n'+result.stderr,encoding='utf8');assert result.returncode==0,(row['asset'],result.stderr)
 path=Path(json.loads(result.stdout)['manifest_path']);d=read_json(path)
 assert not d['blockers'],(row['asset'],d['blockers'])
 assert d['completeness']['missing_texture_references']==0
 assert d['completeness']['rig_projection_status']=='complete'
 tris=sum(g['triangle_count'] for g in d['geometry']['groups']);assert tris==sum(original[row['asset']]['lod_triangles'].values())
 receipt={'asset':row['asset'],'passed':True,'native_triangles':tris,'manifest_sha256':sha(path.read_bytes()),'complete_rigid_skin_projection':True,'missing_textures':0,'blockers':d['blockers']};write_json(cached,receipt);return receipt
records=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futures={pool.submit(one,row):row['asset'] for row in rows}
 for future in concurrent.futures.as_completed(futures):
  try:row=future.result()
  except Exception as e:row={'asset':futures[future],'passed':False,'error':str(e)}
  records.append(row);print('FINAL_STATIC_READBACK',len(records),len(rows),row['asset'],row.get('error','PASS'),flush=True)
  write_json(D/'FINAL_STATIC_READBACK.json',{'archive_sha256':sha(archive.read_bytes()),'all_passed':len(records)==len(rows) and all(r['passed'] for r in records),'assets':sorted(records,key=lambda x:x['asset'])})
assert len(records)==36 and all(r['passed'] for r in records)
