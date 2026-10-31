"""Fresh native conversion of Korea 0.1.4 rigs, rigid models and full RGB masks."""
from pathlib import Path
import sys,json,shutil,hashlib,subprocess,struct,zlib,xml.etree.ElementTree as ET,copy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from current_model_tools import prepare
stage=W/'all-model-project'; source=stage/'source'
if not stage.exists():shutil.copytree(R/'source/art013/cook-template',stage)
def png(c):
 def chunk(t,b):return struct.pack('>I',len(b))+t+b+struct.pack('>I',zlib.crc32(t+b))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',4,4,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(b'\0'+bytes(c)*4 for _ in range(4))))+chunk(b'IEND',b'')
defaults={}
for role,c in {'normal':(128,128,255,255),'roughness':(190,190,190,255),'metalness':(0,0,0,255),'pattern':(0,0,0,255)}.items():
 p=stage/('default-'+role+'.png');p.write_bytes(png(c));defaults[role]=p
records=[]
for kind,total in [('unit',72),('static',36)]:
 rows=list((W/(kind+'-exports')).glob('*/export.json'));assert len(rows)==total,(kind,len(rows))
 for p in sorted(rows):
  row=read_json(p);stem='art/kr013/'+('units' if kind=='unit' else 'static')+'/'+row['asset'].lower();dest=source/stem;dest.mkdir(parents=True,exist_ok=True)
  for name in ['model.fbx','model.rgo','model.rgotemplate']+(['model.rig'] if kind=='unit' else []):
   src=p.parent/name
   if not src.exists():src=R/'source/art013/cook-template'/name
   shutil.copy2(src,dest/name)
  if kind=='unit':mats=[{'name':row['material_name'],'textures':{role:str(p.parent/(role+'.png')) for role in ['albedo','normal','roughness','metalness','pattern'] if (p.parent/(role+'.png')).exists()}}]
  else:mats=row['materials']
  root=ET.Element('materialSet');patterns={}
  for mat in mats:
   node=ET.SubElement(root,'material',name=mat['name'],type='shader',source='unit')
   for role,f in (defaults|mat['textures']).items():
    f=Path(f);h=sha(f.read_bytes());rel='art/kr014/'+('patterns/' if role=='pattern' else 'shared/')+h+'.png';target=source/rel;target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():shutil.copy2(f,target)
    ET.SubElement(node,'param',name={'albedo':'albedoTexture','normal':'normalMap','roughness':'roughnessTex','metalness':'metalTex','pattern':'patternTex'}[role],type='tex2D',value=rel)
    if role=='pattern':patterns[mat['name']]=rel[:-4]+'.rrtex'
  ET.ElementTree(root).write(dest/'model.material',encoding='utf-8',xml_declaration=True)
  records.append({'asset':row['asset'],'kind':kind,'stem':stem,'patterns':patterns})
burn=source/'_default.burnproj';text=(R/'source/art013/cook-template/source/_default.burnproj').read_text('utf-8')
import re
block=next(m.group(0) for m in re.finditer(r'<NamedParameters>.*?</NamedParameters>',text,re.S) if '<Name>Static Textures</Name>' in m.group(0))
new=block.replace('<Name>Static Textures</Name>','<Name>Korean RGB Masks</Name>')
for k,v in {'ColourSpace':'Linear','PreferredFormat':'BC3','ForceFormat':'true','MipmapFilter':'Kaiser','FlipImage':'true','ShrinkSingleColorTextures':'false','PremultiplyAlpha':'false'}.items():
 new,n=re.subn(r'(<d4p1:'+k+r'>).*?(</d4p1:'+k+r'>)',lambda m:m[1]+v+m[2],new);assert n==1,k
text=text.replace('</NamedBurnerParameters>',new+'</NamedBurnerParameters>')
rule='<BurnRule><Alias>data</Alias><Burner>RRTextureBurner</Burner><Configurations>Debug Release Profile RTM</Configurations><Excludes></Excludes><Includes>art\\kr014\\patterns\\*.png</Includes><IsEnabled>true</IsEnabled><NamedParameters>Korean RGB Masks</NamedParameters><PathOverride i:nil="true"/><Target>Archive</Target></BurnRule>'
burn.write_text(text.replace('</Rules>',rule+'</Rules>'),encoding='utf-8');write_json(D/'cook-inputs.json',records)
run=W/'all-model-cook-r2';assert not run.exists(),'Preserve native diagnostics'
cmd=[EXT/'bin/core/garrison-core.exe','essence','build-mod','--editor',prepare(),'--mod',stage/'k013.aoe4mod','--run-root',run,'--timeout','1800','--console-burn-log']
with (D/'all-model-cook.log').open('w',encoding='utf-8') as f:p=subprocess.run(list(map(str,cmd)),stdout=f,stderr=subprocess.STDOUT)
assert p.returncode==0,'Inspect all-model-cook.log';archives=list((run/'output').rglob('*.sga'));assert len(archives)==1
write_json(D/'native-cook.json',{'archive':str(archives[0]),'sha256':sha(archives[0].read_bytes()),'bytes':archives[0].stat().st_size,'models':len(records),'exit_code':0});print('NATIVE_014_MODELS_COMPLETE',len(records),flush=True)
