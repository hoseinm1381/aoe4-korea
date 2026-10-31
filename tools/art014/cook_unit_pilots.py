"""Repository-only cook and receiver compatibility readback for all Korean units."""
from pathlib import Path
import sys,json,tempfile,shutil,hashlib,subprocess,struct,zlib,xml.etree.ElementTree as ET,concurrent.futures,collections
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));sys.path.insert(0,str(R/'tools/art013'))
from common import *
from current_model_tools import prepare
import readback_probe as reader
base=W;stage=base/'unit-pilot-project';source=stage/'source'
if not stage.exists():shutil.copytree(R/'source/art013/cook-template',stage)
def png(color):
 def c(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b))
 return b'\x89PNG\r\n\x1a\n'+c(b'IHDR',struct.pack('>2I5B',4,4,8,6,0,0,0))+c(b'IDAT',zlib.compress(b''.join(b'\0'+bytes(color)*4 for _ in range(4))))+c(b'IEND',b'')
defaults={'normal':(128,128,255,255),'roughness':(190,190,190,255),'metalness':(0,0,0,255),'pattern':(0,0,0,255)}
rows=[]
for p in sorted((W/'unit-exports').glob('*/export.json')):
 row=read_json(p)
 if row['asset'] not in ['kr_archer_a2','kr_lancer_a3','kr_mount_lancer_a3']:continue
 rows.append(row);stem='art/kr013/units/'+row['asset'];dest=source/stem;dest.mkdir(parents=True,exist_ok=True)
 for name in ['model.fbx','model.rig']:shutil.copy2(p.parent/name,dest/name)
 for name in ['model.rgo','model.rgotemplate']:shutil.copy2(R/'source/art013/cook-template'/name,dest/name)
 mat=ET.Element('materialSet');m=ET.SubElement(mat,'material',name=row['material_name'],type='shader',source='unit')
 for role,param in {'albedo':'albedoTexture','normal':'normalMap','roughness':'roughnessTex','metalness':'metalTex','pattern':'patternTex'}.items():
  f=p.parent/(role+'.png');target=dest/(role+'.png')
  if f.exists():shutil.copy2(f,target)
  else:target.write_bytes(png(defaults[role]))
  ET.SubElement(m,'param',name=param,type='tex2D',value=stem+'/'+target.name)
 ET.ElementTree(mat).write(dest/'model.material',encoding='utf8',xml_declaration=True)
assert len(rows)==3
run=base/'unit-pilot-cook-current'
if '--verify-only' not in sys.argv:
 assert not run.exists(),'Prior native diagnostics protected'
 cmd=[EXT/'bin/core/garrison-core.exe','essence','build-mod','--editor',prepare(),'--mod',stage/'k013.aoe4mod','--run-root',run,'--timeout','1200','--console-burn-log']
 with (D/'unit-pilot-cook-current.log').open('w',encoding='utf8') as f:p=subprocess.run(list(map(str,cmd)),stdout=f,stderr=subprocess.STDOUT)
 assert p.returncode==0,'Inspect unit-compatible-cook.log'

print('NATIVE_UNIT_PILOT_COMPLETE',run,flush=True)
