"""Seal exact diagnostic package and rollback evidence before scoped staging cleanup."""
from pathlib import Path
import json,hashlib,gzip,zipfile,shutil,datetime
R=Path(__file__).resolve().parents[1];D=R/'docs/update_024'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 from release024 import verify
 verify();b=read(R/'docs/BUILD_VERIFICATION.json');c=read(R/'project.json');old=read(D/'baseline-build.json')
 assert b['version']==c['version']=='0.2.4' and b['all_member_readback_sha256'] and b['native_crc_sha1'] and b['zip_crc']
 z=R/'release'/b['zip_name'];assert z.stat().st_size==b['zip_bytes']<600000000 and sha(z)==b['zip_sha256']
 with zipfile.ZipFile(z) as f:
  assert f.testzip() is None;names=[n for n in f.namelist() if Path(n).name=='garrison.json'];assert len(names)==1
  name=names[0];m=json.loads(f.read(name));assert m['bundle_key']=='korea' and m['details']['version']=='0.2.4' and m['details']['min_garrison']=='0.1.13'
  assert len(m['members'])==1 and m['members'][0]['role']=='civilization'
  with f.open(name[:-len('garrison.json')]+m['members'][0]['path']) as a:assert hashlib.file_digest(a,'sha256').hexdigest()==b['archive_sha256']
 assembly=Path(b['assembly_path']);report=read(assembly/'report.json');before=json.loads(gzip.decompress((D/'baseline-members.json.gz').read_bytes()))['members'];now=report['members'];policy=read(R/'source/update-024-policy.json')
 changed=[n for n in before if before[n]!=now.get(n)];assert set(changed)==set(policy['allowed_changed']),(changed,policy)
 assert set(now)-set(before)=={'scar/korea/diagnostics_024.scar'} and not set(before)-set(now)
 for n,row in before.items():
  if n not in changed:assert now[n]==row,n
 assert b['media_bytes']==old['media_bytes']==354433993
 assert now['scar/garrison/garrison.scar']['sha256']=='d52f13f4f3e77dd23b6ad12b708b3a10399337398936c7f3c14b378e3d6d5966'
 assert now['scar/korea/voice_bank_020.scar']==before['scar/korea/voice_bank_020.scar']
 reg=read(D/'REGRESSIONS.json');assert reg['tests']==56 and reg['successful']
 static=read(D/'SCAR_STATIC.json');assert sum(x['summary']['errors'] for x in static)==0
 assert read(D/'LUA_COMPILE.json')['all_compile']
 rollback=R/'archives/diagnostic024-baseline'/old['zip_sha256'][:12]/old['zip_name'];assert rollback.stat().st_size==old['zip_bytes'] and sha(rollback)==old['zip_sha256']
 saved=D/'package';saved.mkdir(exist_ok=True)
 for name in ('build-recipe.json','expected-members.json','verification.json','codex-report.json'):(saved/(name+'.gz')).write_bytes(gzip.compress((R/'output/current'/name).read_bytes(),mtime=0))
 for name in ('validate.log','assembly.log'):shutil.copyfile(R/'output/current'/name,saved/name)
 (saved/'assembly-report.json.gz').write_bytes(gzip.compress((assembly/'report.json').read_bytes(),mtime=0))
 result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':'0.2.4','status':'Local crash-diagnostic ZIP verified; owner reproduction is the next gate','zip_path':str(z),'zip_bytes':b['zip_bytes'],'zip_sha256':b['zip_sha256'],'archive_bytes':b['archive_bytes'],'archive_sha256':b['archive_sha256'],'owner':c['owner'],'namespace':c['owner'].replace('-',''),'bundle_race_audio_key':'korea','changed_members':sorted(changed),'added_members':b['added_members'],'preserved_members':b['preserved_baseline_members'],'members_full_readback':b['members'],'native_typed_tables':b['tables'],'current_tests':56,'lua_compiled_files':17,'static_errors':0,'all_original_scar_statements_and_order_preserved':True,'all_models_audio_gameplay_values_and_master_index_unchanged':True,'zip_increment_vs_023_bytes':b['zip_bytes']-old['zip_bytes'],'media_bytes_unchanged':354433993,'dialogue_clips_unchanged':7632,'effort_clips_unchanged':827,'native_sheep_unchanged':5,'trace_limits':{'game_seconds':1200,'lines':100000},'rollback':{'path':str(rollback),'bytes':old['zip_bytes'],'sha256':old['zip_sha256']},'native_crash_cause_confirmed':False,'crash_fixed_claim':False,'mounted_hwarang_model_repair':'Explicitly deferred; distant missing horse legs and extra bow recorded with original screenshot','next_test':'Fresh single-player Korean Standard/None, same speed/cheats first, past eight game minutes; mounted/foot Hwarang cycles, move/attack, train/lose units near Seowon; preserve warnings/scarlog before relaunch. Compare no-conversion fresh match if needed.','not_performed':['Game/client installation, mutation or match execution','Other-civilization mutation','Push/tag/publication','Broad E/F cleanup']}
 write(D/'COMPLETION.json',result);write(D/'RUN_CHECKPOINT.json',{'state':result['status'],'completion':'COMPLETION.json','next':result['next_test'],'root_cause_confirmed':False})
 write(R/'docs/SOURCE_TESTS.json',{'version':'0.2.4','current_tests':reg,'preservation':'release024.py proves exact original SCAR bytes after removing diagnostic lines and unchanged native/master manifests. Final package proof in update_024/COMPLETION.json.','native_runtime':'Owner reproduction pending; diagnostic-only, not a confirmed crash fix.'})
 p=R/'docs/UPDATE_024_DIAGNOSTIC.md';p.write_text(p.read_text(encoding='utf-8')+f'\nVerified local package: {z}\n\nZIP: {b["zip_bytes"]:,} bytes; SHA256 {b["zip_sha256"]}.\nSGA: {b["archive_bytes"]:,} bytes; SHA256 {b["archive_sha256"]}.\nAll {b["members"]:,} member SHA256 readbacks, namespace/CRC/ZIP checks and exact unchanged-member preservation passed.\nExact 0.2.3 rollback: {rollback}.\n',encoding='utf-8')
 print(json.dumps({k:result[k] for k in ('status','zip_path','zip_bytes','zip_sha256','zip_increment_vs_023_bytes','native_crash_cause_confirmed')},indent=2),flush=True)
if __name__=='__main__':main()
