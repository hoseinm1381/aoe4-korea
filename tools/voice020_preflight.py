"""Early native schema/reference validation of staged Korean voice owners."""
from pathlib import Path
import sys,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from runtime import *
from build import run,digest
cfg=read_json(R/'project.json');assert cfg['version']=='0.1.6'
O=R/'output/voices020/native-preflight';O.mkdir(parents=True,exist_ok=True)
recipe={k:cfg[k] for k in ('schema','owner','race','dispatcher','shared_entities')};recipe.update(attributes=[],members=[])
def add(member,p,toc):
 row={'member':member,'file':str(p.resolve()),'sha256':digest(p)}
 if toc=='attrib':recipe['attributes'].append(row)
 else:row['toc']=toc;recipe['members'].append(row)
for m,row in read_json(R/'inputs/native-manifest.json').items():add(m,R/'inputs/native'/m,row.get('toc','data'))
for p in (R/'source/resources').rglob('*'):
 if p.is_file():add(p.relative_to(R/'source/resources').as_posix(),p,'data')
tables={p.relative_to(R/'source/tables').as_posix()[:-5]:p for p in (R/'source/tables').rglob('*.rgd.json')}
for row in read_json(R/'docs/voices020/INTEGRATION_PREVIEW.json')['files']:tables[row['member']]=R/'output/voices020/integration-preview'/(row['member']+'.json')
for member,p in sorted(tables.items()):
 if member in cfg.get('excluded_tables',{}):continue
 raw=import_table(read_json(p));target=O/'prepared'/member;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw);add(member,target,'attrib')
for p in (R/'source/scar').rglob('*.scar'):add('scar/'+p.relative_to(R/'source/scar').as_posix(),p,'data')
write_json(O/'recipe.json',recipe);run([EXT/'bin/core/garrison-core.exe','civilization','validate',O/'recipe.json'],O/'validate.log')
write_json(R/'docs/voices020/NATIVE_PREFLIGHT.json',{'staged_native_schema_and_references':'pass','attributes':len(recipe['attributes']),'source_promoted':False,'audio_complete':False,'runtime_or_build_acceptance':False,'recipe_sha256':digest(O/'recipe.json')});print('STAGED_NATIVE_SCHEMA_PASS',len(recipe['attributes']))
