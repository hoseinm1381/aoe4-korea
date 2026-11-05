"""Audio-only release contract against the exact owner-accepted 0.2.2 package."""
from pathlib import Path
import json,gzip,hashlib
from runtime import ROOT as R,read_json,write_json
D=R/'docs/update_023'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def verify():
 c=read_json(R/'project.json');old=read_json(D/'baseline-project.json');assert c['version']=='0.2.3'
 for k in ('owner','race','bundle_key','name','dispatcher','shared_entities','excluded_tables','codex_mode'):assert c[k]==old[k],k
 assert sha(R/'source/master-index.json')==sha(D/'baseline-master-index.json')
 base=read_json(D/'BASELINE.json')
 assert sha(R/'authoring/voices020/ENCODED_BANK.jsonl')==base['encoded_bank_sha256']
 assert sha(R/'authoring/voices020/VOICE_SCRIPTS.json')==base['scripts_sha256']
 baseline=read_json(D/'baseline-source.json')
 changed={n for n,h in baseline.items() if sha(R/n)!=h};assert changed=={'source/scar/korea/voice_bank_020.scar'},changed
 added={p.relative_to(R).as_posix() for p in (R/'source').rglob('*') if p.is_file()}-set(baseline)
 assert added=={'source/update-023-policy.json'},added
 mapping=read_json(D/'PATH_MAP.json');assert len(mapping)==len(set(mapping.values()))==7632
 before=gzip.decompress((D/'voice_bank_020.scar.before.gz').read_bytes())
 after=(R/'source/scar/korea/voice_bank_020.scar').read_bytes()
 for oldpath,newpath in mapping.items():assert after.count(newpath.encode())==before.count(oldpath.encode());after=after.replace(newpath.encode(),oldpath.encode())
 assert after==before,'voice-bank timing, contexts, roles, ages or PBG mappings changed'
 oldnative=read_json(D/'baseline-native-manifest.json');native=read_json(R/'inputs/native-manifest.json')
 assert set(oldnative)-set(native)==set(mapping) and set(native)-set(oldnative)==set(mapping.values())
 assert all(native[m]==row for m,row in oldnative.items() if m not in mapping),'non-dialogue native inputs changed'
 audit=read_json(D/'AUDIO_AUDIT.json');assert audit['all_clips_decoded'] and audit['dialogue_clips']==7632 and audit['unique_dialogue_files']==7632
 assert audit['sample_rate']==24000 and audit['compression_level']==.35 and audit['max_decoded_peak']<.99
 assert audit['encoded_receipts_sha256']==sha(D/'ENCODED_BANK.jsonl')
 entries=[json.loads(x) for x in (D/'ENCODED_BANK.jsonl').read_text(encoding='utf-8').splitlines()]
 for x in entries:
  assert native[x['member']]['sha256']==x['encoded_sha256'] and native[x['member']]['bytes']==x['encoded_bytes']
  assert mapping[x['previous_member']]==x['member']
 assert read_json(R/'source/resources/audio/events.json')=={'volume_bus':'speech','events':{}}
 assert sha(R/'source/resources/scar/garrison/garrison.scar')=='d52f13f4f3e77dd23b6ad12b708b3a10399337398936c7f3c14b378e3d6d5966'
 policy=read_json(R/'source/update-023-policy.json')
 assert policy=={'allowed_changed':['scar/korea/voice_bank_020.scar'],'allowed_added':sorted(mapping.values()),'allowed_removed':sorted(mapping)}
 media=sum(x['bytes'] for m,x in native.items() if m.startswith(('audio/','art/')))+35
 art=sum(x['bytes'] for m,x in native.items() if m.startswith('art/'))
 oldart=sum(x['bytes'] for m,x in oldnative.items() if m.startswith('art/'));assert art==oldart
 assert media==read_json(D/'baseline-build.json')['media_bytes']-audit['old_dialogue_bytes']+audit['dialogue_bytes']
 assert media<400000000,'narrow owner-approved higher-fidelity audio cap exceeded'
 write_json(D/'SCOPE_VERIFICATION.json',{'version':'0.2.3','source_changes':sorted(changed),'source_additions':sorted(added),'all_non_dialogue_native_inputs_identical':True,'editable_master_index_identical':True,'bank_semantics_byte_identical_after_reversing_paths':True,'art_bytes_unchanged':art,'media_bytes':media,'audio_only_budget_exception':'Owner accepted estimated +67 MB ZIP for higher-quality audio; media cap 400000000 applies only to 0.2.3; art unchanged and final ZIP cap 600000000 retained.','native_runtime_qualified':False})
 print('KOREA023_SCOPE_VERIFIED: only 7632 dialogue encodes and bank paths changed; all gameplay/art/helpers/efforts and bank semantics retained.',flush=True)
 return audit
if __name__=='__main__':verify()
