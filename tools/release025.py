"""Strict voice-controller-only isolation contract against retained 0.2.4."""
from pathlib import Path
import hashlib,json,gzip
from runtime import ROOT as R,read_json
D=R/'docs/update_025'
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def verify():
    c=read_json(R/'project.json');old=read_json(D/'baseline-project.json')
    assert c['version']=='0.2.5' and c['preserve_previous_release'] is True
    for k in ('owner','race','bundle_key','dispatcher','shared_entities','excluded_tables','codex_mode'):assert c[k]==old[k],k
    source=read_json(D/'baseline-source.json')
    assert {n for n,h in source.items() if sha(R/n)!=h}=={'source/scar/korea/voices_020.scar'}
    assert {p.relative_to(R).as_posix() for p in (R/'source').rglob('*') if p.is_file()}-set(source)=={'source/update-025-policy.json'}
    before=gzip.decompress((D/'voices_020.before.gz').read_bytes())
    header=b'local KoreaVoiceControllerEnabled025 = false -- Diagnostic isolation switch.\n'
    addition=(b'    -- 0.2.5 isolation: retain all voice code/media; do not start its controller.\n'
              b'    if not KoreaVoiceControllerEnabled025 then\n'
              b'        print("KOREA025_VOICE_CONTROLLER_DISABLED; voice scripts and audio retained")\n'
              b'        return\n'
              b'    end\n')
    after=(R/'source/scar/korea/voices_020.scar').read_bytes()
    nl=b'\r\n' if b'\r\n' in before else b'\n'
    header=header.replace(b'\n',nl);addition=addition.replace(b'\n',nl)
    assert after==header+before.replace(b'function KoreaVoice_Start(civilizations)'+nl,b'function KoreaVoice_Start(civilizations)'+nl+addition)
    assert sha(R/'inputs/native-manifest.json')==sha(D/'native-manifest.json')
    assert sha(R/'source/master-index.json')==sha(D/'master-index.json')
    b=read_json(D/'baseline-build.json');assert sha(R/'release'/b['zip_name'])==b['zip_sha256']
    print('KOREA025_SCOPE_VERIFIED: startup guard only; all gameplay, native inputs, masters and 0.2.4 ZIP preserved.',flush=True)
if __name__=='__main__':verify()
