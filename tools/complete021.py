"""Compact local 0.2.1 package receipt; native listening remains a separate gate."""
from pathlib import Path
import datetime,gzip,hashlib,json,shutil,zipfile
R=Path(__file__).resolve().parents[1];D=R/'docs/update_021'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def compact(p,q):Path(q).write_bytes(gzip.compress(Path(p).read_bytes(),mtime=0))
def main():
 b=read(R/'docs/BUILD_VERIFICATION.json');assert b['version']=='0.2.1' and b['all_member_readback_sha256'] and b['native_crc_sha1'] and b['zip_crc']
 z=R/'release'/b['zip_name'];assert z.stat().st_size<600000000 and sha(z)==b['zip_sha256']
 with zipfile.ZipFile(z) as f:
  assert f.testzip() is None;n=next(n for n in f.namelist() if n.endswith('garrison.json'));m=json.loads(f.read(n));assert m['details']['version']=='0.2.1' and m['bundle_key']=='korea'
  with f.open(n[:-len('garrison.json')]+m['members'][0]['path']) as a:assert hashlib.file_digest(a,'sha256').hexdigest()==b['archive_sha256']
 old=R/'archives/voices021-baseline/7aeab3dfd39c/Koreans-Garrison-0.2.0.zip'
 assert old.stat().st_size==145863445 and sha(old)=='7aeab3dfd39c06000b7c925726b273fbeb359c8442cb746be4b440ac273b631a'
 prior=R/'archives/voices020-baseline/e48869987e4c/Koreans-Garrison-0.1.6.zip'
 assert prior.stat().st_size==107644580 and sha(prior)=='e48869987e4c7159290a911d263e06288b6ddf8da7cd3c34e236eaadf0a3a788'
 reg=read(D/'REGRESSIONS.json');assert reg['successful'] and reg['tests']==39
 native=read(R/'inputs/native-manifest.json');inputs=read(D/'baseline-inputs.json')
 assert sha(R/'inputs/native-manifest.json')==inputs['native_manifest_sha256'] and sha(R/'source/master-index.json')==inputs['master_index_sha256']
 assembly=Path(b['assembly_path']);current=read(assembly/'report.json')['members']
 baseline=json.loads(gzip.decompress((D/'baseline-members.json.gz').read_bytes()))['members']
 assert set(current)==set(baseline) and all(current[m]==row for m,row in baseline.items() if m.startswith(('art/','audio/')))
 media=sum(v['bytes'] for m,v in current.items() if m.startswith(('art/','audio/')));assert media==298524568
 saved=D/'package';saved.mkdir(exist_ok=True)
 for name in ('build-recipe.json','expected-members.json','verification.json','codex-report.json'):compact(R/'output/current'/name,saved/(name+'.gz'))
 for name in ('validate.log','assembly.log'):shutil.copyfile(R/'output/current'/name,saved/name)
 compact(assembly/'report.json',saved/'assembly-report.json.gz')
 budget=read(R/'docs/voices020/ASSET_BUDGET.json');budget.update(version='0.2.1',archive_bytes=b['archive_bytes'],zip_bytes=b['zip_bytes'],zip_increment_vs_020_bytes=b['zip_bytes']-145863445,zip_increment_vs_016_bytes=b['zip_bytes']-107644580,archive_increment_vs_016_bytes=b['archive_bytes']-249360028,packaged_media_bytes=media,compressed_increment_scope='0.2.1 changes only source/controller/metadata and native sheep entries; all encoded audio and art bytes unchanged.',original_audio_inputs_unchanged=True)
 write(D/'ASSET_BUDGET.json',budget);write(R/'docs/SIZE_REPORT.json',budget)
 result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'0.2.1 local package built and verified; client audio startup and native acceptance pending','zip_path':str(z),'zip_bytes':b['zip_bytes'],'zip_sha256':b['zip_sha256'],'archive_bytes':b['archive_bytes'],'archive_sha256':b['archive_sha256'],'identity':'748d61b9-4d3e-4cf3-a506-a9ac1f992d1d','namespace':'748d61b94d3e4cf3a506a9ac1f992d1d','race_bundle_audio_key':'korea','native_starting_sheep':5,'default_start':'6 Villagers, 1 Scout, 5 sheep; existing resources/research allowances unchanged','campaign_start':'Existing six Villagers plus five sheep; original no-Scout variant retained','voice_routing':'50 compiled PBG-ID mappings, known-owner names; local cosmetic dispatcher follows Berber API route','retained_audio':{'dialogue':7632,'efforts':827,'profiles':32,'age_banks':128,'changed_audio_files':0},'regressions':reg['tests'],'baseline_new_regression_replay':'7 checks; original 0.2.0 fails 5. Existing foreign-owner rejection and captured-unit startup pass.','static_check':'0 errors; external/project API warnings resolved by current official MCP evidence, inspected imports and installed Garrison source.','native_validation_tables':b['tables'],'native_members':b['members'],'native_full_readback_crc_zip':'pass','packaged_media_bytes':media,'native_inputs':len(native),'editable_inputs':len(read(R/'source/master-index.json')['files']),'rollback_020':{'path':str(old),'bytes':old.stat().st_size,'sha256':sha(old)},'rollback_016_untouched':True,'client_failure':'Observed 0.2.0 session had audio.korea transport none/no_consumer after Garrison startup readiness failure. Client recognized audio in both Korea and Berber. A mod cannot start the missing client playback process.','required_next_test':'Exit the existing game normally, import the new ZIP and start a fresh successful normal Garrison Play session; verify voices and five sheep. If launch fails, do not treat the still-running game as a successful audio session.','pending':['Fresh client import and successful launch','Audible select/move/attack/work voices, no original overlap and five actual starting sheep','Historical/native-speaker pronunciation review','Save/load, AI, multiplayer and measured performance'],'not_performed':['Game/client installation, restart or interruption','GitHub push/tag/publication','Changes to other civilizations','Broad drive cleanup']}
 write(D/'COMPLETION.json',result)
 write(R/'docs/SOURCE_TESTS.json',{'version':'0.2.1','current_scope':reg,'preservation':'docs/update_021/expected-repair.json and release021.py verify; all native/master manifests unchanged','native_acceptance':'pending; see exact client no_consumer failure evidence','historical_tests':'Unchanged; older 0.2.0 historical baseline failures remain recorded separately.'})
 p=R/'docs/UPDATE_021.md';s=p.read_text(encoding='utf-8');s+=f'\nBuilt local ZIP: {z}\n\nBytes: {b["zip_bytes"]:,}; SHA-256: {b["zip_sha256"]}.\nPackaged SGA SHA-256: {b["archive_sha256"]}.\nAll {reg["tests"]} current regressions, {b["tables"]} native tables and {b["members"]} full member readbacks passed. Exact 0.2.0 and 0.1.6 rollback ZIPs are preserved. Media remains {media:,} bytes. See update_021/COMPLETION.json and ASSET_BUDGET.json.\n';p.write_text(s,encoding='utf-8')
 header='# Korea 0.2.1 local repair - 2026-11-02\n\nRead the current UPDATE_021 handoff and update_021/COMPLETION.json. The five native sheep and Berber-parity voice routing repair are packaged. The observed Garrison launch failure left no audio consumer; successful fresh client launch and audible/native acceptance remain pending. Prior notes below are historical.\n\n---\n\n'
 for rel in ('RELEASES.md','docs/DEVELOPMENT.md','docs/KOREA_KNOWN_ISSUES.md'):
  p=R/rel;p.write_text(header+p.read_text(encoding='utf-8'),encoding='utf-8')
 write(D/'RUN_CHECKPOINT.json',{'state':'local package verified; fresh client/native acceptance pending','completion':'COMPLETION.json','source':'Use existing standalone Korea source only. Ordinary rebuild: tools/release021.py verify then tools/build.py --replace-current.','remaining':result['pending'],'preserve':'Current ZIP, exact 0.2.0/0.1.6 rollbacks, all indexed native/master inputs, original recordings/weights, compact evidence and failure logs.','no_extra_actions':'No further regeneration, push, installation or broad cleanup implied.'})
 print(json.dumps({k:result[k] for k in ('status','zip_path','zip_bytes','zip_sha256','regressions','native_starting_sheep')},indent=2))
if __name__=='__main__':main()
