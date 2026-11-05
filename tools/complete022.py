"""Finish verified 0.2.2 package receipts; audio/client and freeze gates stay open."""
from pathlib import Path
import json,gzip,hashlib,zipfile,shutil,datetime
R=Path(__file__).resolve().parents[1];D=R/'docs/update_022'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 from release022 import verify
 verify();b=read(R/'docs/BUILD_VERIFICATION.json');c=read(R/'project.json')
 assert b['version']==c['version']=='0.2.2' and b['all_member_readback_sha256'] and b['native_crc_sha1'] and b['zip_crc']
 z=R/'release'/b['zip_name'];assert z.stat().st_size==b['zip_bytes']<600000000 and sha(z)==b['zip_sha256']
 with zipfile.ZipFile(z) as f:
  assert f.testzip() is None
  names=[n for n in f.namelist() if Path(n).name=='garrison.json'];assert len(names)==1
  n=names[0];m=json.loads(f.read(n));assert m['bundle_key']=='korea' and m['details']['version']=='0.2.2' and m['details']['min_garrison']=='0.1.13'
  assert len(m['members'])==1 and m['members'][0]['role']=='civilization'
  with f.open(n[:-len('garrison.json')]+m['members'][0]['path']) as a:assert hashlib.file_digest(a,'sha256').hexdigest()==b['archive_sha256']
 rollbacks=[]
 for rel,size,h in [('archives/voices022-baseline/275dd0ae0ab0/Koreans-Garrison-0.2.1.zip',145866303,'275dd0ae0ab008b19c3155560393bccaf018167186402e3bff4ddb6d282f2011'),('archives/voices021-baseline/7aeab3dfd39c/Koreans-Garrison-0.2.0.zip',145863445,'7aeab3dfd39c06000b7c925726b273fbeb359c8442cb746be4b440ac273b631a'),('archives/voices020-baseline/e48869987e4c/Koreans-Garrison-0.1.6.zip',107644580,'e48869987e4c7159290a911d263e06288b6ddf8da7cd3c34e236eaadf0a3a788')]:
  p=R/rel;assert p.stat().st_size==size and sha(p)==h;rollbacks.append(dict(path=str(p),bytes=size,sha256=h))
 assert sha(R/'inputs/native-manifest.json')==sha(D/'baseline-native-manifest.json') and sha(R/'source/master-index.json')==sha(D/'baseline-master-index.json')
 assembly=Path(b['assembly_path']);report=read(assembly/'report.json');baseline=json.loads(gzip.decompress((D/'baseline-members.json.gz').read_bytes()))['members'];now=report['members']
 for member,row in baseline.items():
  if member.startswith(('art/','audio/')):assert now[member]==row,member
 assert set(now)-set(baseline)=={'audio/events.json','scar/garrison/garrison.scar'}
 assert not set(baseline)-set(now)
 media=sum(v['bytes'] for n,v in now.items() if n.startswith(('art/','audio/')));assert media<300000000
 helper=read(D/'HELPER_PROVENANCE.json');assert now[helper['member']]['sha256']==helper['sha256']
 assert now['audio/events.json']['sha256']==sha(R/'source/resources/audio/events.json')
 reg=read(D/'REGRESSIONS.json');assert reg['successful'] and reg['tests']==46
 saved=D/'package';saved.mkdir(exist_ok=True)
 for name in ('build-recipe.json','expected-members.json','verification.json','codex-report.json'):
  (saved/(name+'.gz')).write_bytes(gzip.compress((R/'output/current'/name).read_bytes(),mtime=0))
 for name in ('validate.log','assembly.log'):shutil.copyfile(R/'output/current'/name,saved/name)
 (saved/'assembly-report.json.gz').write_bytes(gzip.compress((assembly/'report.json').read_bytes(),mtime=0))
 budget=read(R/'docs/SIZE_REPORT.json');budget.update(version='0.2.2',archive_bytes=b['archive_bytes'],zip_bytes=b['zip_bytes'],zip_increment_vs_021_bytes=b['zip_bytes']-145866303,zip_increment_vs_016_bytes=b['zip_bytes']-107644580,archive_increment_vs_016_bytes=b['archive_bytes']-249360028,packaged_media_bytes=media,compressed_increment_scope='0.2.2 adds matching helper/speech-bus JSON and bounded trace text. All existing voice/media bytes unchanged.',original_audio_inputs_unchanged=True)
 write(D/'ASSET_BUDGET.json',budget);write(R/'docs/SIZE_REPORT.json',budget)
 result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'0.2.2 documentation-compliant local diagnostic candidate built; shared client no-consumer failure and native freeze cause unresolved','zip_path':str(z),'zip_bytes':b['zip_bytes'],'zip_sha256':b['zip_sha256'],'archive_bytes':b['archive_bytes'],'archive_sha256':b['archive_sha256'],'owner':c['owner'],'namespace':c['owner'].replace('-',''),'race_bundle_audio_key':'korea','current_contract':'Installed 0.1.13 guide and unmodified runtime helper; Berber treated as unverified','new_members':b['added_members'],'changed_members':b['changed_members'],'unchanged_members':b['preserved_baseline_members'],'native_starting_sheep':5,'retained_audio':{'dialogue':7632,'efforts':827,'profiles':32,'age_banks':128,'squad_routes':50,'changed_existing_audio_files':0},'regressions':reg['tests'],'native_validation_tables':b['tables'],'members_full_readback_crc_sha_zip':b['members'],'packaged_media_bytes':media,'native_and_master_manifest_sha256_unchanged':True,'rollbacks':rollbacks,'helper_sha256':helper['sha256'],'isolated_backend_four_samples':'decoded/admitted with gain zero; not audible proof','audio_playback_resolved':False,'native_freeze_cause_resolved':False,'freeze_investigation':'No unique 35-second trigger; documented feature timers retained; brief 25-45 second phase logging and first-minute Lua replay pass. No correlated system/GPU diagnosis established.','remaining':['Successful normal client launch creating the client-owned audio backend','Fresh native listening and no original speech overlap','Reproduce/investigate 35-second native freeze using phase evidence','Native five-sheep materialization and retained model/research checks','Expert/native-speaker history review; save/load, AI, multiplayer, performance'],'not_performed':['Game/client installation, mutation, restart or process attachment','Other-civilization source changes','Push/tag/publication','Broad E/F cleanup']}
 write(D/'COMPLETION.json',result)
 write(D/'RUN_CHECKPOINT.json',{'state':result['status'],'completion':'COMPLETION.json','source':'Existing standalone Korea only. tools/release022.py verify then tools/build.py --replace-current.','remaining':result['remaining'],'preserve':'Current ZIP, 0.2.1/0.2.0/0.1.6 rollback, all native/editable inputs, voice weights/masters, compact reports and failed-build evidence.'})
 write(R/'docs/SOURCE_TESTS.json',{'version':'0.2.2','current_scope':reg,'preservation':'release022.py: entire original scripts recovered by undo of diagnostic statements; CRLF normalized explicitly. All other prior source/input hashes unchanged.','native_acceptance':'Blocked by shared client launch/no-consumer failure; native freeze cause unresolved','historical_tests':'Unchanged.'})
 p=R/'docs/UPDATE_022.md';s=p.read_text();s+=f'\nBuilt: {z}\n\nZIP bytes: {b["zip_bytes"]:,}; SHA256 {b["zip_sha256"]}.\nSGA SHA256 {b["archive_sha256"]}.\n46 tests, {b["tables"]} native tables, {b["members"]} full member readbacks and ZIP/CRC/namespace checks passed.\nOriginal art/audio unchanged; 0.2.1, 0.2.0 and 0.1.6 rollbacks verified.\nThis is build/package proof only. Shared audio startup and native freeze remain open.\n';p.write_text(s)
 print(json.dumps({k:result[k] for k in ('status','zip_path','zip_bytes','zip_sha256','regressions','audio_playback_resolved','native_freeze_cause_resolved')},indent=2),flush=True)
if __name__=='__main__':main()
