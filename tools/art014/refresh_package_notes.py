"""Replace player instructions while preserving native SGA bytes and all other ZIP members."""
import sys,zipfile,copy,shutil,os,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import *
rec=read_json(R/'docs/BUILD_VERIFICATION.json');p=R/'release'/rec['zip_name'];assert sha(p.read_bytes())==rec['zip_sha256'];out=W/'notes014.zip';assert not out.exists()
with zipfile.ZipFile(p) as source,zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as target:
 names=[n for n in source.namelist() if Path(n).name.lower() in ['start-here.md','start_here.md','start-here.txt']];assert len(names)==1
 for info in source.infolist():
  n=copy.copy(info);n.compress_type=zipfile.ZIP_DEFLATED;n._compresslevel=9
  if info.filename==names[0]:target.writestr(n,(R/'START-HERE.md').read_bytes())
  else:
   with source.open(info) as a,target.open(n,'w') as b:shutil.copyfileobj(a,b,1024*1024)
with zipfile.ZipFile(p) as a,zipfile.ZipFile(out) as b:
 assert b.testzip() is None;assert a.namelist()==b.namelist()
 for n in a.namelist():
  if n not in names:
   with a.open(n) as x,b.open(n) as y:assert hashlib.file_digest(x,'sha256').hexdigest()==hashlib.file_digest(y,'sha256').hexdigest(),n
os.replace(out,p);rec['zip_bytes']=p.stat().st_size;rec['zip_sha256']=sha(p.read_bytes());write_json(R/'docs/BUILD_VERIFICATION.json',rec)
for file in ['COMPLETION.json','ASSET_BUDGET.json']:
 d=read_json(D/file);d.update(zip_bytes=rec['zip_bytes'],zip_sha256=rec['zip_sha256'])
 if file=='ASSET_BUDGET.json':
  d['zip_increase_vs_013']=rec['zip_bytes']-read_json(D/'BASELINE_013.json')['zip_bytes'];d['zip_increase_vs_accepted_011']=rec['zip_bytes']-next((R/'archives/tested_0.1.1').glob('*.zip')).stat().st_size
 write_json(D/file,d)
print('PLAYER_NOTES_REFRESHED_SGA_UNCHANGED',rec['zip_bytes'],rec['zip_sha256'],flush=True)
