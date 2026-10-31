"""Fresh, isolated native cook of the Korean Hwacha; retain the native siege animation graph."""
import sys,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import *
from current_model_tools import prepare
from garrison_shared import model_variants as mv,relic_chunky as rc
stage=W/'hwacha-project'
if not stage.exists():shutil.copytree(R/'source/art013/cook-template',stage)
source=stage/'source';dest=source/'art/kr014/hwacha';dest.mkdir(parents=True,exist_ok=True)
export=W/'hwacha-export';row=read_json(export/'export.json')
for name in ['model.fbx','model.rig']:shutil.copy2(export/name,dest/name)
for name in ['model.rgo','model.rgotemplate']:shutil.copy2(R/'source/art013/cook-template'/name,dest/name)
burn=(W/'all-model-project/source/_default.burnproj').read_text('utf8').replace('art\\kr013\\','art\\kr014\\');(source/'_default.burnproj').write_text(burn,encoding='utf8')
root=ET.Element('materialSet');mat=ET.SubElement(root,'material',name=row['material_name'],type='shader',source='unit');patterns={}
for role,param in {'albedo':'albedoTexture','normal':'normalMap','roughness':'roughnessTex','metalness':'metalTex','pattern':'patternTex'}.items():
 p=export/(role+'.png');rel='art/kr014/'+('patterns/' if role=='pattern' else 'shared/')+sha(p.read_bytes())+'.png';target=source/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 ET.SubElement(mat,'param',name=param,type='tex2D',value=rel)
 if role=='pattern':patterns['patternTex']=rel[:-4]+'.rrtex'
ET.ElementTree(root).write(dest/'model.material',encoding='utf8',xml_declaration=True)
run=W/'hwacha-cook-r2';cmd=[EXT/'bin/core/garrison-core.exe','essence','build-mod','--editor',prepare(),'--mod',stage/'k013.aoe4mod','--run-root',run,'--timeout','600','--console-burn-log']
if not run.exists():
 with (D/'hwacha-cook-r2.log').open('w',encoding='utf8') as f:p=subprocess.run(list(map(str,cmd)),stdout=f,stderr=subprocess.STDOUT)
 assert p.returncode==0
archives=list((run/'output').rglob('*.sga'));assert len(archives)==1;archive=archives[0];G=stock_game.current();listing=G.archiver.run(['list',str(archive),'--verify']);assert listing['archive']['verification']['verified']
native=W/'hwacha-native-r2';G.archiver.run(['extract',str(archive),str(native),'--filter','art/'])
stem=native/'art/kr014/hwacha/model';raw=stem.with_suffix('.rgm').read_bytes();stock=G.model_files(row['official_source'],required=('.rgm',));skln=next(c.payload for c in rc.walk(rc.parse(stock['.rgm']).roots) if c.tag==b'SKLN');stem.with_suffix('.rgm').write_bytes(rc.rebuild(rc.parse(raw),lambda c:skln if c.tag==b'SKLN' else None))
mp=stem.with_suffix('.rrmaterial');mp.write_bytes(mv.rewrite_material(mp.read_bytes(),{k:v.replace('/','\\') for k,v in patterns.items()},{}))
write_json(D/'HWACHA_NATIVE_COOK.json',{'archive_sha256':sha(archive.read_bytes()),'archive_bytes':archive.stat().st_size,'native_integrity':True,'official_skeleton_payload_preserved':True,'triangles':row['triangles'],'actual_bound_pattern':patterns['patternTex'],'native_stage':str(native),'runtime_animation_acceptance':'pending'})
print('HWACHA_NATIVE_COOK_PASS',flush=True)
