"""Retire only owner-approved Korea 014 scratch data after preserved-input/ZIP verification."""
import sys,os,stat,zipfile,shutil,hashlib,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import *
from inputs import verify
rec=read_json(R/'docs/BUILD_VERIFICATION.json');done=read_json(D/'COMPLETION.json');assert rec['version']=='0.1.4' and done['archive_and_zip_integrity_passed']
package=R/'release'/rec['zip_name'];assert sha(package.read_bytes())==rec['zip_sha256'];verify()
old=read_json(D/'BASELINE_013.json');rollback=R/'archives/art013-baseline'/old['zip_sha256'][:12]/old['zip_name'];assert sha(rollback.read_bytes())==old['zip_sha256']
assert (R/'authoring/art014/hwacha/donor_geometry.blend').is_file()
scratch=Path('F:/aoe_4_temp/Temp_aoe4');tools=Path('E:/aoe4_korea_014_model_tools')
assert W==scratch.resolve() and not scratch.is_junction() and not scratch.is_symlink()
marker=read_json(scratch/'korea-014-owner.json');assert marker['repo']==str(R) and marker['version']=='0.1.4' and marker['initially_empty'] is True
assert tools.resolve()==tools and not tools.is_junction() and not tools.is_symlink()
game=Path('E:/Games/steamapps/common/Age of Empires IV').resolve()
def inventory(root,allow_links):
 files=[];links=[];directories=[];stack=[root]
 while stack:
  base=stack.pop();assert base.resolve().is_relative_to(root.resolve())
  for entry in os.scandir(base):
   p=Path(entry.path);s=entry.stat(follow_symlinks=False)
   if getattr(s,'st_file_attributes',0)&stat.FILE_ATTRIBUTE_REPARSE_POINT:
    assert allow_links and (p.is_symlink() or p.is_junction()) and p.resolve().is_relative_to(game),(p,'Unexpected reparse target')
    links.append({'path':str(p),'target':str(p.resolve())});continue
   assert p.resolve().is_relative_to(root.resolve()),p
   if entry.is_dir(follow_symlinks=False):directories.append(p);stack.append(p)
   else:files.append((p,s.st_size))
 return files,links,directories
f_files,f_links,f_dirs=inventory(scratch,False);e_files,e_links,e_dirs=inventory(tools,True)
if '--dry-run' in sys.argv:
 print('CLEANUP_REVIEW',{'scratch_files':len(f_files),'scratch_logical_bytes':sum(s for _,s in f_files),'editor_files':len(e_files),'editor_logical_bytes':sum(s for _,s in e_files),'editor_junction_objects_to_detach':len(e_links),'game_targets_to_preserve':sorted({r['target'] for r in e_links})},flush=True);raise SystemExit(0)
# Keep compact exact logs, recipe/verification JSON and progress receipts. Do not
# duplicate native models, source blends, decoded texture/geometry caches or ZIPs.
diagnostic=D/'temporary-diagnostics.zip';assert not diagnostic.exists()
kept=[]
with zipfile.ZipFile(diagnostic,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for root,files in [(scratch,f_files),(tools,e_files)]:
  for p,size in files:
   if p.suffix.lower() in ['.log','.json'] and size<=6_000_000:
    name=('scratch/' if root==scratch else 'editor-tools/')+p.relative_to(root).as_posix();z.write(p,name);kept.append(name)
with zipfile.ZipFile(diagnostic) as z:assert z.testzip() is None
before={drive:shutil.disk_usage(drive+':/').free for drive in ['E','F']}
removed=[]
for root,files,links,dirs in [(scratch,f_files,f_links,f_dirs),(tools,e_files,e_links,e_dirs)]:
 # Detach verified junction objects only; never traverse/delete their game targets.
 for link in links:
  p=Path(link['path']);assert p.resolve()==Path(link['target'])
  if p.is_junction():os.rmdir(p)
  else:p.unlink()
 for p,size in files:p.unlink()
 for p in sorted(dirs,key=lambda x:len(x.parts),reverse=True):p.rmdir()
 if root==tools:root.rmdir()
 removed.append({'root':str(root),'files':len(files),'logical_bytes':sum(size for _,size in files),'detached_junctions':links,'root_retained_empty':root==scratch})
after={drive:shutil.disk_usage(drive+':/').free for drive in ['E','F']}
assert sha(package.read_bytes())==rec['zip_sha256'];assert sha(rollback.read_bytes())==old['zip_sha256'];verify()
write_json(D/'CLEANUP.json',{'version':'0.1.4','removed':removed,'total_logical_bytes_removed':sum(r['logical_bytes'] for r in removed),'observed_free_space_change':{d:after[d]-before[d] for d in before},'current_zip_sha256':rec['zip_sha256'],'rollback_013_sha256':old['zip_sha256'],'diagnostics_zip_sha256':sha(diagnostic.read_bytes()),'diagnostic_files_retained':len(kept),'inputs_verified_after':True,'installed_game_junction_targets_preserved':True,'C_or_D_drive_mutations':False})
print('AUTHORIZED_014_CLEANUP_COMPLETE',sum(r['logical_bytes'] for r in removed),'logical bytes',flush=True)
