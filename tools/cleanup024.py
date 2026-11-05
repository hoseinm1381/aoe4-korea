"""Remove only verified diagnostic build staging; retain compact evidence and rollback."""
from pathlib import Path
import json,gzip,subprocess,sys,os,shutil,hashlib
R=Path(__file__).resolve().parents[1];D=R/'docs/update_024'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 c=json.loads((D/'COMPLETION.json').read_text());assert c['version']=='0.2.4' and sha(c['zip_path'])==c['zip_sha256']
 out=(R/'output/current').resolve();assert out.is_relative_to(R.resolve()) and not out.is_symlink() and not out.is_junction()
 names=['build-recipe.json','expected-members.json','verification.json','codex-report.json','validate.log','assembly.log']
 for name in names:
  saved=D/'package'/name;raw=gzip.decompress(saved.with_suffix(saved.suffix+'.gz').read_bytes()) if name.endswith('.json') else saved.read_bytes()
  assert (out/name).read_bytes()==raw,name
 subprocess.run([sys.executable,'-B',str(R/'tools/cleanup_staging.py'),'--apply'],check=True)
 assert set(x.name for x in out.iterdir())==set(names)
 for directory,dirs,files in os.walk(out,followlinks=False):
  for name in dirs+files:
   p=Path(directory)/name;assert not p.is_symlink() and not p.is_junction() and p.resolve().is_relative_to(out)
 size=sum((out/name).stat().st_size for name in names);shutil.rmtree(out)
 assert sha(c['zip_path'])==c['zip_sha256'];assert sha(c['rollback']['path'])==c['rollback']['sha256']
 report={'version':'0.2.4','staging':json.loads((R/'docs/STAGING_CLEANUP.json').read_text()),'extra_compacted_metadata_bytes':size,'logical_bytes_removed':json.loads((R/'docs/STAGING_CLEANUP.json').read_text())['logical_bytes']+size,'player_and_rollback_zip_hashes_verified_after_cleanup':True,'native_inputs_master_indexes_sources_audio_models_diagnostic_logs_and_recipes':'preserved','broad_cleanup':False}
 (D/'CLEANUP.json').write_text(json.dumps(report,indent=2)+'\n');print('DIAGNOSTIC024_SCOPED_CLEANUP_BYTES',report['logical_bytes_removed'])
if __name__=='__main__':main()
