"""Retain official dependencies in the readback index; never alter the installed library."""
import sys,sqlite3,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import *
import readback_probe as p
base=W/'merged-decode';base.mkdir(exist_ok=True);index=base/'index.sqlite3'
if not index.exists():
 src=sqlite3.connect('file:'+p.ORIGINAL_INDEX.as_posix()+'?mode=ro',uri=True);dst=sqlite3.connect(index);src.backup(dst);src.close();dst.close()
db=sqlite3.connect(index);db.execute('attach database ? as custom',(str(W/'readbacks014/index.sqlite3'),))
if db.execute('select count(*) from archives where path like ?',('%all-model-cook-r2%',)).fetchone()[0]==0:
 archive_max=db.execute('select max(id) from archives').fetchone()[0];asset_max=db.execute('select max(id) from assets').fetchone()[0]
 for row in db.execute('select * from custom.archives').fetchall():db.execute('insert into archives values('+','.join('?' for _ in row)+')',(row[0]+archive_max,)+row[1:])
 for row in db.execute('select * from custom.assets').fetchall():db.execute('insert into assets values('+','.join('?' for _ in row)+')',(row[0]+asset_max,row[1]+archive_max)+row[2:])
 for row in db.execute('select * from custom.resolved_assets').fetchall():
  db.execute('delete from resolved_assets where logical_path=?',(row[1],));db.execute('insert into resolved_assets values('+','.join('?' for _ in row)+')',(row[0]+asset_max,)+row[1:])
 db.commit()
db.close();config=read_json(p.ORIGINAL_CONFIG);config['index_path']=str(index);write_json(base/'config.json',config)
print('MERGED_INDEX_READY',index,flush=True)
