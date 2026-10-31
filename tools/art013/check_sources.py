"""Verify the self-contained Korean art preparation; optionally check native model tools."""
import sys,json,hashlib,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
from inputs import verify,check

def read(p):return json.loads(p.read_text('utf-8'))
def inside(relative):
 p=(R/relative).resolve()
 if not p.is_relative_to(R):raise ValueError('Input escapes repository: '+relative)
 return p

def verify_art():
 verify();cat=read(R/'authoring/art013/catalog.json');rows=cat['sources']
 assert len(rows)==152 and len({x['id'] for x in rows})==152
 proofs={x['id']:x for x in read(R/'docs/update_013/saved-files.json')['assets']}
 assert len(proofs)==152
 for row in rows:
  check(inside(row['blend']),row);proof=proofs[row['id']]
  assert proof['cold_open'] and proof['blend_sha256']==row['sha256'] and proof['semantic_sha256']==row['semantic_sha256']
  for dep in row['textures']:
   assert dep['file'] in cat['shared_textures'];check(inside(dep['file']),dep)
  for rel in row['metadata'].values():assert inside(rel).is_file()
 for rel,row in cat['shared_textures'].items():check(inside(rel),row)
 for row in cat['original_texture_masters']:check(inside(row['file']),row)
 baseline=read(R/'source/art013/baseline-runtime.json')
 for rel,row in baseline['files'].items():check(inside(rel),row)
 plan=read(R/'source/art013/integration-plan.json')
 assert plan['all_bindings_pending'] and {x['asset'] for x in plan['assets']}=={x['id'] for x in rows}
 for asset in plan['assets']:
  for consumer in asset.get('consumers',[]):
   assert hashlib.sha256(inside(consumer['table']).read_bytes()).hexdigest()==consumer['sha256']
 indexed={x['path'] for x in read(R/'source/master-index.json')['files']}
 actual={p.relative_to(R/'authoring').as_posix() for p in (R/'authoring/art013').rglob('*') if p.is_file()}
 assert actual<indexed or actual==indexed
 assert len(actual)==sum(x.startswith('art013/') for x in indexed)
 print('KOREAN_ART_SOURCE_VERIFIED assets=152 files='+str(len(actual))+' runtime_baseline_unchanged='+str(len(baseline['files'])))
 return cat

def model_tools():
 from runtime import EXT
 from garrison_shared import editor_overlay,kit_data
 game=kit_data.connection_game_root(kit_data.read_connection())
 if game is None:raise RuntimeError('No connected game')
 status=dict(editor_overlay.inspect_overlay(None,game))
 (R/'docs/update_013/editor-readiness.json').write_text(json.dumps(status,indent=2)+'\n')
 print('GARRISON_MODEL_TOOLS',status['status'])
 if status['status']!='ready':
  evidence=R/'docs/update_013/native-conversion-qualification.json'
  if evidence.is_file():
   sys.path.insert(0,str(Path(__file__).parent))
   from prepare_model_tools import prepare
   try:editor=prepare()
   except (AssertionError,RuntimeError,ValueError,OSError) as error:
    print('LOCAL_QUALIFICATION_NOT_APPLICABLE',str(error))
   else:
    print('LOCALLY_QUALIFIED_MODEL_EDITOR',editor)
    print('Official support table is unchanged; exact-hash local conversion qualification applies. Asset bindings and final mod build remain separate gates.')
    return True
  print('KOREA_013_NATIVE_BUILD_BLOCKED: '+'; '.join(status.get('reasons',[])))
  return False
 print('Model tools are ready. Native integration, cook, private bindings and archive proof remain required; this command does not build a player package.')
 return True

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check-model-tools',action='store_true');a=p.parse_args()
 verify_art()
 if a.check_model_tools and not model_tools():raise SystemExit(2)
