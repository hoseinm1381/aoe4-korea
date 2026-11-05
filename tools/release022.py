"""Verify narrowly scoped 0.2.2 source and exact 0.2.1 preservation."""
from pathlib import Path
import json,gzip,hashlib,re
from runtime import ROOT as R,read_json,write_json
D=R/'docs/update_022'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def remove_voice_traces(s):
 lines=s.splitlines(keepends=True);result=[]
 for line in lines:
  if any(x in line for x in ('-- Brief, bounded freeze diagnostics;','local second=math.floor(now-(S.traceStart','local trace=second>=25','if trace then','S.traceStart=World_GetGameTime();S.traceSecond=nil')):continue
  result.append(line)
 return ''.join(result)
def remove_gameplay_traces(s):
 lines=s.splitlines(keepends=True);result=[];in_phase=False
 for line in lines:
  if '    local function phase(name)' in line:in_phase=True;continue
  if in_phase:
   if line=='    end\n':in_phase=False
   continue
  if any(x in line for x in ('-- Log phases around the reported freeze window','local second = math.floor(now - (KoreaState.traceStart','local trace = second >= 25','if trace then KoreaState.traceSecond','    phase("','            phase("','KoreaState.traceStart = now; KoreaState.traceSecond = nil')):continue
  result.append(line)
 return ''.join(result)
def verify():
 c=read_json(R/'project.json');old=read_json(D/'baseline-project.json');assert c['version']=='0.2.2'
 for k in ('owner','race','bundle_key','name','dispatcher','shared_entities'):assert c[k]==old[k],k
 assert sha(R/'inputs/native-manifest.json')==sha(D/'baseline-native-manifest.json')
 assert sha(R/'source/master-index.json')==sha(D/'baseline-master-index.json')
 baseline=read_json(D/'baseline-source.json');changed={n for n,h in baseline.items() if sha(R/n)!=h}
 assert changed=={'source/scar/korea/voices_020.scar','source/scar/korea/lifecycle.scar'},changed
 added={p.relative_to(R).as_posix() for p in (R/'source').rglob('*') if p.is_file()}-set(baseline)
 assert added=={'source/resources/audio/events.json','source/update-022-policy.json','source/resources/scar/garrison/garrison.scar'},added
 for stem,undo in [('voices_020.scar',remove_voice_traces),('lifecycle.scar',remove_gameplay_traces)]:
  before=gzip.decompress((D/(stem+'.before.gz')).read_bytes()).decode().replace('\r\n','\n')
  assert undo((R/'source/scar/korea'/stem).read_text())==before,stem+' non-diagnostic logic changed'
 assert read_json(R/'source/resources/audio/events.json')=={'volume_bus':'speech','events':{}}
 provenance=read_json(D/'HELPER_PROVENANCE.json')
 assert sha(R/'source/resources/scar/garrison/garrison.scar')==provenance['sha256']
 assert read_json(D/'BACKEND_CODEC_PROBE.json')['all_samples_decoded']
 for n,h in read_json(D/'SEALED_SOURCE.json').items():assert sha(R/n)==h,n
 print('KOREA022_SCOPE_VERIFIED: native/master indexes and all original controller/gameplay logic retained; matching runtime helper, speech bus and bounded trace added.',flush=True)
def seal():
 names=['source/scar/korea/voices_020.scar','source/scar/korea/lifecycle.scar','source/resources/audio/events.json','source/update-022-policy.json','project.json','source/resources/scar/garrison/garrison.scar']
 write_json(D/'SEALED_SOURCE.json',{n:sha(R/n) for n in names});verify()
if __name__=='__main__':
 import sys
 globals()[sys.argv[1] if len(sys.argv)>1 else 'verify']()
