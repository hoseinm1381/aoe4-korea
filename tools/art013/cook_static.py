"""Native cook of the curated Korean static models from repository inputs."""
from pathlib import Path
import sys,json,tempfile,shutil,hashlib,subprocess,struct,zlib,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));sys.path.insert(0,str(R/'tools/art013'))
from runtime import EXT,read_json,write_json
from prepare_model_tools import prepare
stage=Path(tempfile.gettempdir())/'k13/static-project';template=R/'source/art013/cook-template'
if not stage.exists():shutil.copytree(template,stage)
source=stage/'source'
records=read_json(R/'docs/update_013/static-export.json')['assets']
def png(color):
 def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',4,4,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\x00'+bytes(color)*4 for _ in range(4))))+chunk(b'IEND',b'')
defaults={}
for role,color in {'normal':(128,128,255,255),'roughness':(190,190,190,255),'metalness':(0,0,0,255),'pattern':(0,0,0,255)}.items():
 f=source/'art/kr013/shared'/('default-'+role+'.png');f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(png(color));defaults[role]=str(f)
for row in records:
 stem='art/kr013/static/'+row['asset'].lower();dest=source/stem;dest.mkdir(parents=True,exist_ok=True)
 export=R/'output/art-current/static-exports'/row['asset']
 for name in ['model.fbx','model.rgo','model.rgotemplate','model.rig']:shutil.copy2(export/name,dest/name)
 material=ET.Element('materialSet')
 for mat in row['materials']:
  m=ET.SubElement(material,'material',name=mat['name'],type='shader',source='unit')
  for role,p in (defaults|mat['textures']).items():
   f=Path(p);h=hashlib.sha256(f.read_bytes()).hexdigest();rel='art/kr013/shared/'+h+'.png';target=source/rel;target.parent.mkdir(exist_ok=True)
   if not target.exists():shutil.copy2(f,target)
   assert target.read_bytes()==f.read_bytes()
   param={'albedo':'albedoTexture','normal':'normalMap','roughness':'roughnessTex','metalness':'metalTex','pattern':'patternTex'}[role]
   ET.SubElement(m,'param',name=param,type='tex2D',value=rel)
 ET.ElementTree(material).write(dest/'model.material',encoding='utf-8',xml_declaration=True)
recolors=read_json(R/'docs/update_013/ordinary-native.json')['texture_sources']
for member,p in recolors.items():
 target=source/(member[:-6]+'.png');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
burn=source/'_default.burnproj';text=burn.read_text()
rule='''<BurnRule><Alias>data</Alias><Burner>RRTextureBurner</Burner><Configurations>Debug Release Profile RTM</Configurations><Excludes></Excludes><Includes>art\\kr013\\recolors\\*.png</Includes><IsEnabled>true</IsEnabled><NamedParameters>Static Textures</NamedParameters><PathOverride i:nil="true"/><Target>Archive</Target></BurnRule>'''
if 'art\\kr013\\recolors\\*.png' not in text:burn.write_text(text.replace('</Rules>',rule+'</Rules>'))
run=Path(tempfile.gettempdir())/'k13/static-model-cook-partition-names'
assert not run.exists(),'Prior native diagnostics protected'
editor=prepare()
cmd=[EXT/'bin/core/garrison-core.exe','essence','build-mod','--editor',editor,'--mod',stage/'k013.aoe4mod','--run-root',run,'--timeout','1200','--console-burn-log']
log=R/'docs/update_013/static-cook-partition-names.log'
with log.open('w',encoding='utf8') as f:p=subprocess.run(list(map(str,cmd)),stdout=f,stderr=subprocess.STDOUT)
assert p.returncode==0,log
archives=list((run/'output').rglob('*.sga'));assert len(archives)==1,archives
write_json(R/'docs/update_013/static-cook.json',{'archive':str(archives[0]),'archive_sha256':hashlib.sha256(archives[0].read_bytes()).hexdigest(),'archive_bytes':archives[0].stat().st_size,'models':len(records),'exit_code':p.returncode,'source_project':str(stage)})
print('STATIC_NATIVE_COOK_COMPLETE',len(records),archives[0],flush=True)
