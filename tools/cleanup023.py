"""Retire only verified 0.2.3 regenerable staging; preserve every source/input/ZIP."""
from pathlib import Path
import os,json,gzip,hashlib,subprocess,sys,shutil
R=Path(__file__).resolve().parents[1];D=R/'docs/update_023'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def inventory(target,owner):
 target=target.resolve();assert target.is_relative_to(owner.resolve()) and target!=owner.resolve()
 assert not target.is_symlink() and not target.is_junction()
 files=[]
 for directory,dirs,names in os.walk(target,followlinks=False):
  for name in dirs+names:
   p=Path(directory)/name;assert not p.is_symlink() and not p.is_junction() and p.resolve().is_relative_to(target)
  for name in names:
   p=Path(directory)/name;files.append({'path':p.relative_to(target).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)})
 return files
def main():
 c=read(D/'COMPLETION.json');assert read(R/'project.json')['version']=='0.2.3' and c['zip_sha256']==read(R/'docs/BUILD_VERIFICATION.json')['zip_sha256']
 assert sha(c['zip_path'])==c['zip_sha256']
 out=R/'output/current';remaining=['build-recipe.json','expected-members.json','verification.json','codex-report.json','validate.log','assembly.log']
 for name in remaining:
  p=out/name;saved=D/'package'/name
  assert p.read_bytes()==(gzip.decompress(saved.with_suffix(saved.suffix+'.gz').read_bytes()) if name.endswith('.json') else saved.read_bytes()),name
 subprocess.run([sys.executable,'-B',str(R/'tools/cleanup_staging.py'),'--apply'],check=True)
 stage=read(R/'docs/STAGING_CLEANUP.json');extra=[]
 if out.exists():
  assert set(p.name for p in out.iterdir())==set(remaining)
  files=inventory(out,R/'output');extra.append({'path':str(out.resolve()),'logical_bytes':sum(x['bytes'] for x in files),'files':files,'preserved_as':'docs/update_023/package, byte-verified before deletion'})
  shutil.rmtree(out)
 audit=Path('F:/aoe_4_temp/Temp_aoe4/k20/quality023-native-audit')
 if audit.exists():
  files=inventory(audit,Path('F:/aoe_4_temp/Temp_aoe4/k20'))
  assert all(x['path'].startswith('verified-dds/') and x['path'].endswith('.dds') for x in files)
  extra.append({'path':str(audit.resolve()),'logical_bytes':sum(x['bytes'] for x in files),'files':files,'regeneration':'Current Native016.test_all_bound_masks_have_valid_bc3_mip_streams_and_digests from retained indexed rrtex and recipe'})
  shutil.rmtree(audit)
 assert sha(c['zip_path'])==c['zip_sha256']
 for row in c['rollbacks']:assert Path(row['path']).stat().st_size==row['bytes'] and sha(row['path'])==row['sha256']
 report={'version':'0.2.3','scoped_staging':stage,'additional_regenerable_targets':extra,'logical_bytes_removed':stage['logical_bytes']+sum(x['logical_bytes'] for x in extra),'final_zip_sha256':sha(c['zip_path']),'rollback_hashes_verified_after_cleanup':True,'protected':'All editable/native inputs, both dialogue generations and all masters, weights/tools/downloads, sources/recipes/checkpoints, current 0.2.3 ZIP, exact 0.2.2/older rollbacks, failed-build evidence and compact receipts preserved. No broad E/F cleanup.'}
 (D/'CLEANUP.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
 print('QUALITY023_SCOPED_CLEANUP_BYTES',report['logical_bytes_removed'],flush=True)
if __name__=='__main__':main()
