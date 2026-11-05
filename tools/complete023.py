"""Seal exact 0.2.3 package, preservation and size receipts before scoped cleanup."""
from pathlib import Path
import json,gzip,hashlib,zipfile,shutil,datetime
R=Path(__file__).resolve().parents[1];D=R/'docs/update_023'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 from release023 import verify
 verify();b=read(R/'docs/BUILD_VERIFICATION.json');c=read(R/'project.json');old=read(D/'baseline-build.json')
 assert b['version']==c['version']=='0.2.3' and b['all_member_readback_sha256'] and b['native_crc_sha1'] and b['zip_crc']
 z=R/'release'/b['zip_name'];assert z.stat().st_size==b['zip_bytes']<600000000 and sha(z)==b['zip_sha256']
 with zipfile.ZipFile(z) as f:
  assert f.testzip() is None
  names=[n for n in f.namelist() if Path(n).name=='garrison.json'];assert len(names)==1
  n=names[0];m=json.loads(f.read(n));assert m['bundle_key']=='korea' and m['details']['version']=='0.2.3' and m['details']['min_garrison']=='0.1.13'
  assert len(m['members'])==1 and m['members'][0]['role']=='civilization'
  sgamember=n[:-len('garrison.json')]+m['members'][0]['path'];sgainfo=f.getinfo(sgamember)
  with f.open(sgamember) as a:assert hashlib.file_digest(a,'sha256').hexdigest()==b['archive_sha256']
 rollbacks=[]
 for rel,size,h in [('archives/quality023-baseline/6175fcef8fff/Koreans-Garrison-0.2.2.zip',145864393,'6175fcef8fffb0b6a59c1e02f3b4524b42dc14b84d36de591b760c42936ca94e'),('archives/voices022-baseline/275dd0ae0ab0/Koreans-Garrison-0.2.1.zip',145866303,'275dd0ae0ab008b19c3155560393bccaf018167186402e3bff4ddb6d282f2011'),('archives/voices021-baseline/7aeab3dfd39c/Koreans-Garrison-0.2.0.zip',145863445,'7aeab3dfd39c06000b7c925726b273fbeb359c8442cb746be4b440ac273b631a'),('archives/voices020-baseline/e48869987e4c/Koreans-Garrison-0.1.6.zip',107644580,'e48869987e4c7159290a911d263e06288b6ddf8da7cd3c34e236eaadf0a3a788')]:
  p=R/rel;assert p.stat().st_size==size and sha(p)==h;rollbacks.append(dict(path=str(p),bytes=size,sha256=h))
 assembly=Path(b['assembly_path']);report=read(assembly/'report.json');baseline=json.loads(gzip.decompress((D/'baseline-members.json.gz').read_bytes()))['members'];now=report['members'];mapping=read(D/'PATH_MAP.json')
 for member,row in baseline.items():
  if member not in mapping and member!='scar/korea/voice_bank_020.scar':assert now[member]==row,member
 assert set(now)-set(baseline)==set(mapping.values()) and set(baseline)-set(now)==set(mapping)
 assert now['scar/garrison/garrison.scar']['sha256']==sha(R/'source/resources/scar/garrison/garrison.scar')=='d52f13f4f3e77dd23b6ad12b708b3a10399337398936c7f3c14b378e3d6d5966'
 assert now['audio/events.json']['sha256']==sha(R/'source/resources/audio/events.json')
 reg=read(D/'REGRESSIONS.json');assert reg['successful'] and reg['tests']==45
 native=read(D/'NATIVE_SAFETY_CONTRACTS.json');assert native['successful'] and native['tests']==12
 assert 'Ran 4 tests' in (D/'safety-stress.log').read_text() and (D/'safety-stress.log').read_text().rstrip().endswith('OK')
 probe=read(D/'BACKEND_CODEC_PROBE.json');assert probe['archive_sha256']==b['archive_sha256'] and probe['all_samples_decoded'] and not probe['game_attached']
 saved=D/'package';saved.mkdir(exist_ok=True)
 for name in ('build-recipe.json','expected-members.json','verification.json','codex-report.json'):
  (saved/(name+'.gz')).write_bytes(gzip.compress((R/'output/current'/name).read_bytes(),mtime=0))
 for name in ('validate.log','assembly.log'):shutil.copyfile(R/'output/current'/name,saved/name)
 (saved/'assembly-report.json.gz').write_bytes(gzip.compress((assembly/'report.json').read_bytes(),mtime=0))
 audio=read(D/'AUDIO_AUDIT.json');media=sum(v['bytes'] for n,v in now.items() if n.startswith(('art/','audio/')))
 # Read exact baseline ZIP SGA compression contribution without extracting it.
 oldzip=Path(rollbacks[0]['path'])
 with zipfile.ZipFile(oldzip) as f:
  mn=next(n for n in f.namelist() if Path(n).name=='garrison.json');mm=json.loads(f.read(mn));info=f.getinfo(mn[:-len('garrison.json')]+mm['members'][0]['path']);oldcompressed=info.compress_size
 budget={'version':'0.2.3','zip_bytes':b['zip_bytes'],'archive_bytes':b['archive_bytes'],'zip_increment_vs_022_bytes':b['zip_bytes']-old['zip_bytes'],'archive_increment_vs_022_bytes':b['archive_bytes']-old['archive_bytes'],'compressed_sga_contribution_increment_vs_022_bytes':sgainfo.compress_size-oldcompressed,'dialogue_bytes':audio['dialogue_bytes'],'old_dialogue_bytes':audio['old_dialogue_bytes'],'dialogue_payload_increment_bytes':audio['dialogue_bytes']-audio['old_dialogue_bytes'],'dialogue_seconds':audio['seconds'],'decoded_dialogue_float32_bank_bytes':audio['decoded_float32_bank_bytes'],'effort_bytes_unchanged':9815249,'art_bytes_unchanged':read(D/'SCOPE_VERIFICATION.json')['art_bytes_unchanged'],'media_bytes':media,'scope':'Only dialogue encodes and corresponding bank paths changed. Compressed SGA increment includes the required path-map text/index effects; ZIP increment includes release text/metadata. No art/GPU-resource or gameplay changes.','budget_exception':'Owner-approved 0.2.3 audio-quality size increase; media<400000000 and ZIP<600000000. No measured runtime memory/performance acceptance.'}
 write(D/'ASSET_BUDGET.json',budget);write(R/'docs/SIZE_REPORT.json',budget)
 result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'0.2.3 higher-fidelity local ZIP built and package verified; random native crash cause remains unconfirmed','zip_path':str(z),'zip_bytes':b['zip_bytes'],'zip_sha256':b['zip_sha256'],'archive_bytes':b['archive_bytes'],'archive_sha256':b['archive_sha256'],'owner':c['owner'],'namespace':c['owner'].replace('-',''),'race_bundle_audio_key':'korea','dialogue_clips':7632,'effort_clips_unchanged':827,'voice_profiles':32,'age_banks':128,'squad_routes':50,'dialogue_sample_rate':24000,'vorbis_compression_level':.35,'changed_source_members':['scar/korea/voice_bank_020.scar'],'preserved_members':b['preserved_baseline_members'],'all_member_readback_count':b['members'],'native_typed_tables':b['tables'],'behavior_tests':45,'voice_safety_stress_tests':4,'native_asset_schema_contract_tests':12,'static_scar_errors':0,'helper_and_speech_bus_preserved':True,'backend_codec_samples':4,'backend_codec_probe':'All decoded/admitted with gain zero and dummy process only; not audible native proof','zip_increment_vs_022_bytes':budget['zip_increment_vs_022_bytes'],'rollbacks':rollbacks,'crash_resolved':False,'remaining':['Fresh Korea 0.2.3 native listening across families/ages/contexts and no doubled Chinese speech','Korea-specific crash log/stack or native reproduction for random single-player crash report','Expert/native-speaker historical pronunciation review','Native save/load, AI, multiplayer and performance qualification'],'not_performed':['Push/tag/publication','Installation/client changes/game interruption','Other-civilization mutations','Broad E:/F: cleanup']}
 write(D/'COMPLETION.json',result);write(D/'RUN_CHECKPOINT.json',{'state':result['status'],'completion':'COMPLETION.json','remaining':result['remaining'],'rebuild':'Existing standalone source; tools/release023.py, tools/check023.py, tools/build.py --replace-current. TEMP/TMP on owned F:.'})
 write(R/'docs/SOURCE_TESTS.json',{'version':'0.2.3','behavior':reg,'native_safety':native,'stress_tests':4,'preservation':'Exact non-dialogue native/source bytes and bank semantics retained against owner-accepted 0.2.2; full fresh native build/readback and ZIP verification passed.','native_acceptance':'Preview quality approved; complete 0.2.3 listening and random crash root cause pending.','historical_tests':'Unchanged.'})
 p=R/'docs/UPDATE_023.md';s=p.read_text();s+=f'\nFinal local ZIP: {z}\n\nBytes: {b["zip_bytes"]:,} (+{budget["zip_increment_vs_022_bytes"]:,} versus 0.2.2).\nSHA256: {b["zip_sha256"]}.\nSGA: {b["archive_bytes"]:,} bytes; SHA256 {b["archive_sha256"]}.\nFresh native validation/build, namespace/CRC, {b["members"]:,} full readbacks, final ZIP CRC/hash and exact non-dialogue preservation passed.\n';p.write_text(s,encoding='utf-8')
 print(json.dumps({k:result[k] for k in ('status','zip_path','zip_bytes','zip_sha256','zip_increment_vs_022_bytes','crash_resolved')},indent=2),flush=True)
if __name__=='__main__':main()
