"""Read every cooked Korean unit model from one verified archive. Decodes use NTFS temp."""
from pathlib import Path
import sys,json,subprocess,hashlib,tempfile,concurrent.futures,time
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));sys.path.insert(0,str(Path(__file__).parent))
from runtime import EXT
import readback_probe as private
CORE=EXT/'bin/core/garrison-core.exe';ARCH=EXT/'bin/sga-archiver.exe'
archive=Path(tempfile.gettempdir())/'k13/unit-model-cook/output/extension/k013/k013.sga'
base=Path(tempfile.gettempdir())/'k13/unit-readbacks';assert not base.exists(),'Preserve prior native readback';base.mkdir()
listing=json.loads(subprocess.check_output([str(ARCH),'list',str(archive),'--verify'],text=True));assert listing['archive']['verification']['verified']
rows=json.loads((R/'docs/update_013/unit-cook-staging.json').read_text())['export_receipts'];assert len(rows)==72
members={m['path']:m for m in listing['members']}
for row in rows:
 assert all('art/kr013/units/'+row['asset']+'/model'+s in members for s in ['.rgm','.rgo','.rrgeom','.rrmaterial']),row['asset']
private.INDEX=base/'index.sqlite3';private.create_index(archive,listing['members'],listing['archive']['name'])
config=json.loads(private.ORIGINAL_CONFIG.read_text('utf-8'));config['index_path']=str(private.INDEX);cp=base/'config.json';cp.write_text(json.dumps(config,indent=2))
(R/'docs/update_013/unit-model-cook-members.json').write_text(json.dumps(listing,indent=2)+'\n')

def one(row):
 name=row['asset'];out=base/name;out.mkdir();logical='art/kr013/units/'+name+'/model.rgm'
 cmd=[str(CORE),'convert','decode-static','--logical-path',logical,'--config',str(cp),'--index',str(private.INDEX),'--output-root',str(out/'decoded')]
 result=subprocess.run(cmd,capture_output=True,text=True,errors='replace',timeout=300)
 (out/'decode.log').write_text(result.stdout+'\nSTDERR:\n'+result.stderr,encoding='utf-8')
 record={'asset':name,'exit_code':result.returncode,'source_sha256':row['source_sha256'],'expected_bones':row['bones'],'expected_lod_triangles':row['lod_triangles']}
 if result.returncode==0:
  response=json.loads(result.stdout);manifest=Path(response['manifest_path']);d=json.loads(manifest.read_text('utf-8'))
  record.update(manifest=str(manifest),manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),native_bones=len(d['skeleton']['bones']),native_lod_triangles=[g['triangle_count'] for g in d['geometry']['groups']],blockers=d['blockers'],warnings=d['warnings'],completeness=d['completeness'])
  record['basic_native_contract_passed']=not record['blockers'] and record['native_bones']==record['expected_bones'] and record['native_lod_triangles']==record['expected_lod_triangles'] and d['completeness']['rig_projection_status']=='complete' and d['completeness']['missing_texture_references']==0
 else:record['basic_native_contract_passed']=False
 return record

records=[];start=time.monotonic()
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 futures={pool.submit(one,row):row['asset'] for row in rows}
 for future in concurrent.futures.as_completed(futures):
  try:record=future.result()
  except Exception as e:record={'asset':futures[future],'basic_native_contract_passed':False,'error':str(e)}
  records.append(record);print('NATIVE_UNIT_DECODED',len(records),72,record['asset'],record['basic_native_contract_passed'],flush=True)
  receipt={'schema':'korea.art013-unit-native-readback/v1','archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_bytes':archive.stat().st_size,'namespace':listing['archive']['name'],'archive_integrity_passed':True,'expected_assets':72,'completed':len(records),'assets':sorted(records,key=lambda x:x['asset']),'source_corner_comparisons':'pending','elapsed_seconds':round(time.monotonic()-start,2)}
  (R/'docs/update_013/unit-native-readbacks.json').write_text(json.dumps(receipt,indent=2)+'\n')
assert len(records)==72 and all(x['basic_native_contract_passed'] for x in records),'Some native model readbacks failed; inspect receipt'
print('ALL_72_UNIT_MODELS_NATIVE_DECODED',flush=True)
