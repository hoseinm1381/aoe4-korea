"""Korea 0.2.0 voice inventory and explicit production gates. No gameplay mutation."""
import argparse,datetime,hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OWNER='748d61b94d3e4cf3a506a9ac1f992d1d'
DOC=ROOT/'docs/voices020'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def walk(nodes,path=''):
 for i,n in enumerate(nodes):
  here=path+'/'+str(n['key'])+'['+str(i)+']'
  yield here,n
  if n['kind'] in ('List','List2'):yield from walk(n['value'],here)
def profile(name):
 if 'dummy' in name:return {'gapsa':'GAPSA','hwacha':'HWACHA','tiger_hunter':'TIGER_HUNTER'}[next(k for k in ('gapsa','hwacha','tiger_hunter') if k in name)]
 if 'naval_' in name:
  for k in ('fishing','trade','transport','turtle','fireship','scout','war_galley','combat_warship','combat_ship'):
   if k in name:return 'NAVAL_'+k.upper()
 if 'monk' in name:return 'MONK'
 if 'trader' in name or 'trade_cart' in name:return 'TRADER'
 for k,v in [('leader','RIGHTEOUS_MONK'),('militia','MILITIA'),('nest_of_bees','HWACHA'),('official','SCHOLAR'),('repeater_crossbowman','TIGER_HUNTER'),('manatarms','GAPSA'),('crossbowman','CROSSBOW'),('handcannon','HANDCANNON'),('archer','HWARANG_FOOT' if '_ayy' in name else 'ARCHER'),('horseman','HWARANG_MOUNTED' if '_ayy' in name else 'HORSEMAN'),('knight','LANCER'),('spearman','SPEARMAN'),('villager','VILLAGER_M'),('scout','SCOUT'),('trebuchet','TREBUCHET'),('bombard','BOMBARD'),('ram','RAM')]:
  if k in name:return v
 raise ValueError('Unclassified squad '+name)
def inventory():
 tables={p.relative_to(ROOT/'source/tables').as_posix()[:-5]:(p,read(p)) for p in (ROOT/'source/tables').rglob('*.rgd.json')}
 units=[]; speech=[]; references=[]
 for member,(p,d) in sorted(tables.items()):
  flat=list(walk(d['nodes']))
  if '/sbps/' in member:
   name=p.name[:-9]; role=profile(name)
   units.append({'member':member,'runtime':OWNER+':'+name,'profile':role,'female_profile':'VILLAGER_F' if role=='VILLAGER_M' else None,'pbgid':next((n['value'] for _,n in flat if n['key']=='pbgid'),None),'age_policy':'current_player_age','sha256':sha(p),'speech_owner':'human crew' if role.startswith('NAVAL_') or role in ('RAM','TREBUCHET','BOMBARD','HWACHA') else 'human'})
  for path,n in flat:
   if n['key'] in ('speech_ext','squad_speech_ext') or (n['key']=='attachment_speaker_code' and n['value']):
    speech.append({'member':member,'path':path,'key':n['key'],'value':n['value'] if n['kind'] not in ('List','List2') else '<table>','kind':n['kind']})
   if n['key']=='$PBGNAME' and isinstance(n['value'],str) and ('unit_' in n['value'] or 'kr013_' in n['value']):references.append({'consumer':member,'path':path,'target':n['value']})
 private={r['runtime'].split(':',1)[1] for r in units}
 unresolved=sorted({r['target'] for r in references if r['target'].split(':')[-1].split('\\')[-1].split('/')[-1] not in private and 'unit_' in r['target']})
 bank={'schema':'korea.voice-inventory/v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'inventory_only_no_audio','owner':OWNER,'units':units,'profiles':sorted({r['profile'] for r in units}|{'VILLAGER_F'}),'speech_consumers':speech,'unit_references':references,'references_requiring_category_and_scope_resolution':unresolved,'coverage_claim':'Private squad inventory only; shared stock scout/naval/siege references require resolution before complete coverage.'}
 write(DOC/'UNIT_INVENTORY.json',bank)
 baseline=DOC/'BASELINE.json'
 if not baseline.exists():
  write(baseline,{'source_files':{p.relative_to(ROOT).as_posix():sha(p) for folder in ('source','tools') for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts},'project_sha256':sha(ROOT/'project.json'),'rollback_zip_sha256':sha(ROOT/'release/Koreans-Garrison-0.1.6.zip'),'version':read(ROOT/'project.json')['version']})
 print(json.dumps({'private_squads':len(units),'profiles':bank['profiles'],'speech_bindings_and_tables':len(speech),'unresolved_unit_references':len(unresolved),'inventory':str(DOC/'UNIT_INVENTORY.json')},indent=2))
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['inventory']);args=parser.parse_args();inventory()
