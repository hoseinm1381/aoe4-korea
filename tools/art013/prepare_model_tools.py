"""Prepare the exact locally qualified editor pair; does not change installed tools."""
from pathlib import Path
import sys,json,os,argparse,tempfile,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
from runtime import EXT
from garrison_shared import editor_overlay as overlay,kit_data

def prepare(output=None):
 evidence=json.loads((R/'docs/update_013/native-conversion-qualification.json').read_text('utf-8'))
 comparison=R/'docs/update_013/native-conversion-comparison.json'
 assert hashlib.sha256(comparison.read_bytes()).hexdigest()==evidence['comparison_report_sha256']
 assert evidence['status']=='actual_model_conversion_verified' and evidence['native_archive']['verified']
 game=Path(kit_data.connection_game_root(kit_data.read_connection()))
 editor=overlay.sha256_file(game/overlay.EDITOR_NAME);core=overlay.sha256_file(game/overlay.CORE_NAME)
 assert editor==evidence['editor_sha256'] and core==evidence['core_source_sha256'],'Editor pair changed: fresh conversion qualification required'
 raw=(game/overlay.CORE_NAME).read_bytes();assert raw.count(overlay.EXCLUDED_FEATURES)==1
 patched=overlay.patch_feature_list(raw)
 assert patched==raw.replace(overlay.EXCLUDED_FEATURES,overlay.OBJECT_EDITOR_REPLACEMENT,1)
 assert hashlib.sha256(patched).hexdigest()==evidence['core_trial_sha256']
 target=Path(output) if output else Path(tempfile.gettempdir())/'k13/experimental-current-model-tools'
 target=target.resolve();owned=(Path(tempfile.gettempdir())/'k13').resolve()
 assert target.is_relative_to(owned) and target!=owned,'Use the task-owned temporary model-tools folder'
 key=evidence['overlay_profile'];previous=overlay.SUPPORTED_PROFILES.get(key)
 # Local, exact-hash admission backed by a real native cook/readback. Never an
 # official support declaration or a mutation of the installed SDK/profile file.
 overlay.SUPPORTED_PROFILES[key]={'editor_sha256':editor,'core_sha256':core}
 try:
  if not target.exists():overlay.create_overlay(game,target)
  status=overlay.inspect_overlay(target,game)
  assert status['status']=='ready',status
  assert (target/overlay.CORE_NAME).read_bytes()==patched
 finally:
  if previous is None:overlay.SUPPORTED_PROFILES.pop(key,None)
  else:overlay.SUPPORTED_PROFILES[key]=previous
 assert overlay.sha256_file(game/overlay.EDITOR_NAME)==editor and overlay.sha256_file(game/overlay.CORE_NAME)==core
 return target/overlay.EDITOR_NAME
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path);a=p.parse_args();print('LOCALLY_QUALIFIED_MODEL_EDITOR',prepare(a.output))
