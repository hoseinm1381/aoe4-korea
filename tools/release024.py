"""Diagnostic-only source contract against exact current 0.2.3; no gameplay fix claim."""
from pathlib import Path
import hashlib,json
from runtime import ROOT as R,read_json,write_json
D=R/'docs/update_024';TAG=b' -- KOREA024_DIAGNOSTIC'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def verify():
 c=read_json(R/'project.json');old=read_json(D/'baseline-project.json');assert c['version']=='0.2.4'
 for k in ('owner','race','bundle_key','name','dispatcher','shared_entities','excluded_tables','codex_mode'):assert c[k]==old[k],k
 assert sha(R/'inputs/native-manifest.json')==sha(D/'baseline-native-manifest.json')
 assert sha(R/'source/master-index.json')==sha(D/'baseline-master-index.json')
 source=read_json(D/'baseline-source.json');changed={n for n,h in source.items() if sha(R/n)!=h}
 ledger=read_json(D/'INSTRUMENTATION.json');assert changed=={x['file'] for x in ledger}
 for name in changed:
  raw=(R/name).read_bytes();restored=b''.join(line for line in raw.splitlines(keepends=True) if TAG not in line)
  assert hashlib.sha256(restored).hexdigest()==source[name],name+' gameplay/ordering escaped instrumentation-only scope'
 added={p.relative_to(R).as_posix() for p in (R/'source').rglob('*') if p.is_file()}-set(source)
 assert added=={'source/scar/korea/diagnostics_024.scar','source/update-024-policy.json'},added
 diag=(R/'source/scar/korea/diagnostics_024.scar').read_text()
 for forbidden in ('pcall(', 'xpcall(', 'loadstring(', 'os.', 'io.', 'Network_CallEvent(', 'Rule_AddInterval(', 'Player_AddResource(', 'Squad_CreateAndSpawnToward('):assert forbidden not in diag,forbidden
 assert 'maxLines=100000' in diag and 'maxGameTime=1200' in diag
 assert sha(R/'source/resources/scar/garrison/garrison.scar')=='d52f13f4f3e77dd23b6ad12b708b3a10399337398936c7f3c14b378e3d6d5966'
 policy=read_json(R/'source/update-024-policy.json');expected=sorted([n[len('source/'):] for n in changed]+['garrison/civilizations.json'])
 assert policy=={'allowed_changed':expected,'allowed_added':['scar/korea/diagnostics_024.scar'],'allowed_removed':[]}
 for name,h in read_json(D/'SEALED_DIAGNOSTIC_SOURCE.json').items():assert sha(R/name)==h,name+' changed after diagnostic qualification'
 write_json(D/'SCOPE_VERIFICATION.json',{'version':'0.2.4','all_original_scar_statements_order_and_bytes_restored_after_removing_marked_lines':True,'changed_source':sorted(changed),'new_diagnostic_module':True,'native_and_editable_indexes_identical':True,'all_art_models_audio_bank_scripts_gameplay_tables_unchanged':True,'no_engine_globals_replaced':True,'logging_only_no_error_swallowing_or_retry':True,'crash_cause_confirmed':False,'fixed_crash_claim':False})
 print('KOREA024_DIAGNOSTIC_SCOPE_VERIFIED: original SCAR bytes recover exactly; all native inputs/master index unchanged.',flush=True)
if __name__=='__main__':verify()
