"""Apply the exact reviewed patch after explicit owner confirmation; fail on source drift."""
import sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import *
preview=W/'source-preview014';policy=read_json(preview/'source/update-014-policy.json')
assert read_json(R/'project.json')['version']=='0.1.3'
for row in policy['source_changes']:
 p=R/row['file']
 if row.get('added'):assert not p.exists(),p
 else:assert sha(p.read_bytes())==row['before_sha256'],p
for member in policy['native_changed']+policy['native_added']:
 sources=[p/member for p in [W/'repaired-native',Path(read_json(D/'HWACHA_NATIVE_COOK.json')['native_stage'])] if (p/member).is_file()]
 assert sources,member
 source=sources[-1];expected=read_json(preview/'inputs/native-manifest.json')[member]
 assert sha(source.read_bytes())==expected['sha256'],member
 target=R/'inputs/native'/member;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
for p in sorted(preview.rglob('*')):
 if not p.is_file():continue
 target=R/p.relative_to(preview);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
print('REVIEWED_014_PATCH_APPLIED',len(policy['source_changes']),'tables',len(policy['native_changed'])+len(policy['native_added']),'native files',flush=True)
