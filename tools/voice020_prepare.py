"""Prepare and audit the explicit Korean voice table set without promotion."""
import copy,gzip,hashlib,json,sys,collections
from pathlib import Path,PurePosixPath
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from runtime import *
D=R/'docs/voices020';O=R/'output/voices020/integration-preview';OWNER=read_json(R/'project.json')['owner'].replace('-','')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def category(member):return 'attachments/attachment_lists' if '/attachments/attachment_lists/' in member else member.split('/')[1]
def prepare():
 originals={p.relative_to(R/'source/tables').as_posix()[:-5]:read_json(p) for p in (R/'source/tables').rglob('*.rgd.json')};tables=copy.deepcopy(originals);ledger=[]
 suppression=read_json(D/'SUPPRESSION_PREVIEW.json');shared=read_json(D/'SHARED_ISOLATION_PREVIEW.json')
 for row in suppression['files']:
  m=row['member'];assert sha(import_table(originals[m]))==row['source_sha256'];tables[m]=read_json(R/'output/voices020/suppression-preview'/(m+'.json'));assert sha(import_table(tables[m]))==row['candidate_sha256']
 redirects={x['original']:x['private'] for x in shared['redirects'] if x['category']=='sbps'}
 for row in shared['files']:
  m=row['private_member'];assert m not in tables;tables[m]=read_json(R/'output/voices020/shared-preview'/(m+'.json'));assert sha(import_table(tables[m]))==row['candidate_sha256']
 extra=read_json(D/'EXTRA_ISOLATION_PREVIEW.json')
 for row in extra['files']:
  m=row['private_member'];assert m not in tables;tables[m]=read_json(R/'output/voices020/extra-preview'/(m+'.json'));assert sha(import_table(tables[m]))==row['candidate_sha256']
 extra_redirects={(x['category'],x['original']):x['private'] for x in extra['redirects']}
 ref_edits=[]
 for member,data in list(tables.items()):
  doc=rgd.read(import_table(data));edited=False
  for path,cat,name,node in refs(doc.nodes):
   if cat=='sbps' and name in redirects and '/parent_pbg' not in path:
    assert ('/spawner_ext/spawn_items/' in path or '/blueprint_archetypes/' in path or '/army_bag/starting_units/' in path or '/codex_bag/' in path),(member,path,name)
    ref_edits.append({'member':member,'path':path,'before':name,'after':redirects[name]});child(node,'$PBGNAME').value=redirects[name];edited=True
  for path,cat,name,node in refs(doc.nodes):
   private=extra_redirects.get((cat,name))
   if private and '/parent_pbg' not in path:
    ref_edits.append({'member':member,'path':path,'before':name,'after':private,'category':cat});child(node,'$PBGNAME').value=private;edited=True
  if edited:tables[member]=export_table(rgd.write(doc))
 for member,data in tables.items():
  raw=import_table(data);old=originals.get(member)
  if old is None or raw!=import_table(old):
   assert rgd.write(rgd.read(raw))==raw;write_json(O/(member+'.json'),data)
   ledger.append({'member':member,'before_native_sha256':sha(import_table(old)) if old else None,'after_native_sha256':sha(raw),'new':old is None})
 # Snapshot only the intentionally changed tables, not a source/workspace copy.
 snapshot={x['member']:originals[x['member']] for x in ledger if not x['new']}
 payload=gzip.compress(json.dumps(snapshot,ensure_ascii=False,separators=(',',':')).encode(),mtime=0);saved=D/'before-voice-tables.json.gz'
 if saved.exists():assert saved.read_bytes()==payload,'Changed baseline snapshot protected'
 else:saved.write_bytes(payload)
 write_json(D/'INTEGRATION_PREVIEW.json',{'files':ledger,'consumer_redirects':ref_edits,'source_changed':False,'changed_native_tables':len(snapshot),'added_native_tables':sum(x['new'] for x in ledger),'speech_scope':'Main native speech tables and explicit speaker overrides only; stock aliases also change identity and isolated owning references. All other typed values retained.'})
 # Trace all loadout and active attachment owners in every retained native variant.
 private={(category(m),OWNER+':'+PurePosixPath(m).stem):m for m in tables};G=stock_game.current();idx=G.blueprint_index(R/'output/voices020/stock-index');byname=collections.defaultdict(list)
 for path in idx:
  cat='attachments/attachment_lists' if path.startswith('attachments/attachment_lists/') else path.split('/')[0];byname[(cat,path.rsplit('/',1)[-1])].append(path)
 cache={};visited=set();problems=[];parents=[];edges=[]
 def resolve(cat,name):
  if (cat,name) in private:return private[(cat,name)],rgd.read(import_table(tables[private[(cat,name)]]))
  assert ':' not in name,('Unresolved private voice owner',cat,name)
  p=name.replace('\\','/').removesuffix('.rgd')
  if p not in idx:
   opts=byname[(cat,p.rsplit('/',1)[-1])];assert len(opts)==1,(cat,name,opts);p=opts[0]
  if p not in cache:cache[p]=rgd.read(G.blueprint(p))
  return p,cache[p]
 def visit(cat,name):
  if (cat,name) in visited:return
  visited.add((cat,name));member,doc=resolve(cat,name)
  for path,node in rgd.flatten(doc.nodes):
   if node.key in ('speech_ext','squad_speech_ext') or node.key=='attachment_speaker_code' and node.value:problems.append({'member':member,'path':path,'key':node.key,'value':node.value if not isinstance(node.value,list) else '<table>'})
  for path,c,n,node in refs(doc.nodes):
   if not n:continue
   if path.endswith('/parent_pbg') and cat in ('sbps','ebps'):
    # Retained flattened native RGD parent metadata is not an authoring extension
    # append. Main speech payload was explicitly removed in this compiled owner.
    parents.append({'member':member,'path':path,'category':c,'name':n});continue
   relevant=(cat=='sbps' and c=='ebps' and '/squad_loadout_ext/' in path) or c.startswith('attachments/attachment_lists') or (cat=='attachments/attachment_lists' and c=='ebps')
   if relevant:edges.append({'from':member,'path':path,'category':c,'target':n});visit(c,n)
 units=read_json(D/'UNIT_INVENTORY.json')['units'];roots=[u['runtime'] for u in units]+list(redirects.values())
 for n in roots:visit('sbps',n)
 write_json(D/'ATTACHMENT_CLOSURE.json',{'roots':roots,'resolved_owners':len(visited),'edges':edges,'compiled_parent_metadata':parents,'unmuted_payloads':problems,'status':'pass' if not problems else 'remaining owners require private isolation','runtime_audible_suppression':'pending native listening'})
 print('VOICE_TABLES_STAGED',len(ledger),'REDIRECTS',len(ref_edits),'CLOSURE',len(visited),'UNMUTED',len(problems),flush=True)
if __name__=='__main__':prepare()
