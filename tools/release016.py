"""Preflight for the authorized Korea 0.1.6 build; preserve historical gates."""
import ast,base64,gzip,json,hashlib,re
from runtime import ROOT as R,read_json,import_table,rgd,at
import research016_ui

def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def resolve(parent,path):
 for part in path.split('/'):
  match=re.fullmatch(r'(.*?)(?:\[(\d+)\])?',part);name,index=match.group(1),int(match.group(2) or 0)
  nodes=parent.nodes if hasattr(parent,'nodes') else parent.value
  parent=[n for n in nodes if n.key==name or n.key is None and n.hash==rgd.dictionary_hash(name)][index]
 return parent
def verify_source():
 d=R/'docs/update_016_build';report=read_json(d/'SPEAR_REPAIR.json')
 before=json.loads(gzip.decompress((d/'before-source.json.gz').read_bytes()))
 for change in report['changes']:
  path=R/change['source'];doc=rgd.read(import_table(read_json(path)))
  for row in change['fields']:
   assert resolve(doc,row['path']).value==row['after'],(change['source'],row['path'])
   parent=resolve(doc,row['path'].rsplit('/',1)[0]);assert at(parent,'attach_data/marker_name_parent').value=='MetaRig_LArmPalmSocket'
   resolve(doc,row['path']).value=row['before']
  old=import_table(json.loads(base64.b64decode(before[change['source']])))
  assert rgd.write(doc)==old,'Non-shield changes in Gapsa tier list'
 for relative,key in [('inputs/native-manifest.json','before_native_manifest_sha256'),('source/master-index.json','before_master_index_sha256'),('source/scar/korea/research.scar','before_scar_research_sha256')]:
  assert digest(R/relative)==report[key],relative
 config=read_json(R/'project.json');oldconfig=json.loads(base64.b64decode(before['project.json']))
 for key in ['owner','race','bundle_key','dispatcher','shared_entities']:assert config[key]==oldconfig[key],key
 assert config['version']=='0.1.6' and not config.get('build_hold')
 research016_ui.verify()
 print('RELEASE016_SOURCE_VERIFIED 12 shield paths; native inputs, research, and identity preserved',flush=True)

def mapper(source):
 tree=ast.parse(source);node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='rigid')
 module=ast.Module(body=[node],type_ignores=[]);env={'equipment':{'gapsa':[]},'cat':{'Korea_gapsa_heavy_spear':{}},'used':set()}
 exec(compile(module,'gapsa-original-mapper','exec'),env);return env['rigid']
if __name__=='__main__':verify_source()
