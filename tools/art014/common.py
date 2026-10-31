from pathlib import Path
import os,sys,tempfile,hashlib
R=Path(__file__).resolve().parents[2]
W=Path(r"F:/aoe_4_temp/Temp_aoe4")
assert W.resolve()==W and not W.is_junction() and not W.is_symlink()
os.environ["TEMP"]=str(W);os.environ["TMP"]=str(W);tempfile.tempdir=str(W)
sys.path[:0]=[str(R/"tools"),str(R/"tools/art013")]
from runtime import *
D=R/"docs/update_014";D.mkdir(exist_ok=True)
def sha(b):return hashlib.sha256(b).hexdigest()
