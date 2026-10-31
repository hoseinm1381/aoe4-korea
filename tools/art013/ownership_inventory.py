"""Read current stock attachment ownership; does not edit gameplay or allocate identities."""
from pathlib import Path
import sys,json,tempfile,hashlib,collections
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
from runtime import stock_game,rgd,refs,read_json,import_table
G=stock_game.current();cache=Path(tempfile.gettempdir())/'k13/blueprint-cache';cache.mkdir(exist_ok=True)
index=G.blueprint_index(cache);by_name=collections.defaultdict(list)
for p in index:
 if p.startswith('attachments/attachment_lists/'):by_name[p.rsplit('/',1)[-1]].append(p)
cat=read_json(R/'authoring/art013/catalog.json');donors=collections.defaultdict(list)
def norm(s):
 s=s.replace('\\','/').lower().removeprefix('data:')
 for ext in ['.rgm','.rgo']:
  if s.endswith(ext):s=s[:-4]
 return s
for a in cat['sources']:
 recipe=read_json(R/a['metadata']['recipe.json']) if 'recipe.json' in a['metadata'] else {}
 donor=recipe.get('donor')
 if 'native-state-contract.json' in a['metadata']:donor=read_json(R/a['metadata']['native-state-contract.json'])['donor']['logical_path']
 if isinstance(donor,str):donors[norm(donor)].append(a['id'])
nodes={};unresolved=[]
def resolve(name):
 name=name.split(':',1)[-1].replace('\\','/').lower().removesuffix('.rgd')
 if name.startswith('attachments/attachment_lists/'):return name if name in index else None
 rows=by_name[name.rsplit('/',1)[-1]]
 return rows[0] if len(rows)==1 else None

def visit(p):
 if p in nodes:return
 raw=G.blueprint(p);d=rgd.read(raw)
 models=[{'field':path,'resource':n.value,'matches':donors.get(norm(n.value),[]),'is_animation_owner':path.endswith('/parent_animator')} for path,n in rgd.flatten(d.nodes) if n.kind=='CString' and isinstance(n.value,str) and norm(n.value).startswith('art/')]
 node={'source_sha256':hashlib.sha256(raw).hexdigest(),'references':[],'resources':models};nodes[p]=node
 for path,family,name,_ in refs(d.nodes):
  if not name or not ('attachments/attachment_lists' in family.lower() or path.endswith('/parent_pbg')):continue
  target=resolve(name)
  if not target:unresolved.append({'from':p,'field':path,'family':family,'name':name});continue
  node['references'].append({'field':path,'name':name,'target':target});visit(target)
consumers=[]
for number,p in enumerate(sorted((R/'source/tables/attrib/ebps').rglob('*.rgd.json')),1):
 d=rgd.read(import_table(read_json(p)));roots=[]
 for path,family,name,_ in refs(d.nodes):
  if not name or 'attachments/attachment_lists' not in family.lower():continue
  target=resolve(name)
  if not target:unresolved.append({'from':p.relative_to(R).as_posix(),'field':path,'family':family,'name':name});continue
  roots.append({'field':path,'name':name,'target':target});visit(target)
 consumers.append({'source':p.relative_to(R).as_posix(),'roots':roots})
 if number%10==0:print('OWNERSHIP_READ',number,'stock_lists',len(nodes),flush=True)
result={'schema':'korea.art013-official-ownership-inventory/v1','read_only':True,'source_consumers':consumers,'stock_attachment_lists':nodes,'unresolved':unresolved,'model_donors':dict(donors)}
(R/'docs/update_013/ownership-inventory.json').write_text(json.dumps(result,indent=2)+'\n');print('OFFICIAL_OWNERSHIP_INVENTORY',len(consumers),len(nodes),'unresolved',len(unresolved),flush=True)
