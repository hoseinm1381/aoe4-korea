"""Stage exact official shared-unit speech isolation. Does not promote source."""
from pathlib import Path
import sys,copy,hashlib,collections
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from runtime import *
from garrison_shared import derived_blueprints as derive,mod_content
G=stock_game.current();cfg=read_json(R/'project.json');owner=cfg['owner'].replace('-','');O=R/'output/voices020/shared-preview';O.mkdir(parents=True,exist_ok=True)
index=G.blueprint_index(R/'output/voices020/stock-index');byname=collections.defaultdict(list)
for p in index:byname[(p.split('/')[0],p.rsplit('/',1)[-1])].append(p)
raws={};clones={};reports=[];redirects={}
def stock(path):
 if path not in raws:raws[path]=G.blueprint(path)
 return raws[path]
def resolve(family,name):
 name=name.replace('\\','/').removesuffix('.rgd')
 if ':' in name:return None
 if name in index:return name
 matches=byname[(family.split('/')[0],name.rsplit('/',1)[-1])]
 if len(matches)!=1:raise ValueError(('Ambiguous/unresolved official reference',family,name,matches))
 return matches[0]
def allocate(path,family):
 key=(path,family)
 if key in clones:return clones[key]
 name='kr020_voice_'+hashlib.sha256(path.encode()).hexdigest()[:14]
 result,receipt=derive.build([{'name':name,'family':family,'source':path,'changes':[]}],{path:stock(path)},mod_id=cfg['owner'],mod_key='korea',pbgid=mod_content.pbgid,owner=owner)
 assert len(result)==1
 dest,(_,raw)=next(iter(result.items()));item={'reference':owner+':'+name,'member':'attrib/'+dest+'.rgd','doc':rgd.read(raw),'derived_baseline':raw,'source':path,'sdk':receipt,'edits':[]}
 clones[key]=item;return item

def drop_speech(nodes,edits,path=''):
 for n in list(nodes):
  route=path+'/'+str(n.key)
  if n.key in ('speech_ext','squad_speech_ext'):
   edits.append({'operation':'remove_native_speech_table','path':route});nodes.remove(n)
  elif n.key=='attachment_speaker_code' and n.value:
   assert n.kind=='CString';edits.append({'operation':'clear_attachment_speaker','path':route,'before':n.value});n.value=''
  elif isinstance(n.value,list):drop_speech(n.value,edits,route)

attachment_done={};attachment_stack=set()
def attachment(path):
 if path in attachment_done:return attachment_done[path]
 if path in attachment_stack:raise ValueError('Attachment reference cycle '+path)
 attachment_stack.add(path);original=rgd.read(stock(path));doc=copy.deepcopy(original);edits=[]
 for route,cat,name,node in list(refs(doc.nodes)):
  if cat.startswith('attachments/attachment_lists') and name:
   p=resolve('attachments/attachment_lists',name)
   if p:
    ref=attachment(p)
    if ref:child(node,'$PBGNAME').value=ref;edits.append({'operation':'private_speaker_attachment_child','path':route,'before':name,'after':ref})
 drop_speech(doc.nodes,edits)
 if edits:
  item=allocate(path,'attachments/attachment_lists')
  # Keep the exact payload and inject only SDK-allocated private PBG identities.
  for variant in doc.nodes:
   if not isinstance(variant.value,list):continue
   try:child(variant,'pbgid').value=at(item['doc'],variant.key+'/pbgid').value
   except StopIteration:pass
  item['doc']=doc;item['edits']=edits;answer=item['reference']
 else:answer=None
 attachment_stack.remove(path);attachment_done[path]=answer;return answer

squads=read_json(R/'docs/voices020/SHARED_PRODUCTION_CONSUMERS.json')['squads']
for row in squads:
 item=allocate(row['official_path'],'sbps');redirects[('sbps',row['symbol'])]=item['reference']
 for route,cat,name,node in list(refs(item['doc'].nodes)):
  if cat=='ebps' and '/squad_loadout_ext/' in route:
   source=resolve('ebps',name);entity=allocate(source,'ebps');redirects[('ebps',name)]=entity['reference']
   child(node,'$PBGNAME').value=entity['reference'];item['edits'].append({'operation':'private_loadout','path':route,'before':name,'after':entity['reference']})
# Process only actual loadout entities. Ordinary buildings/weapons stay referenced.
for (path,family),item in list(clones.items()):
 if family!='ebps':continue
 for route,cat,name,node in list(refs(item['doc'].nodes)):
  if cat.startswith('attachments/attachment_lists') and name:
   p=resolve('attachments/attachment_lists',name)
   if p:
    ref=attachment(p)
    if ref:child(node,'$PBGNAME').value=ref;item['edits'].append({'operation':'private_speaker_attachment','path':route,'before':name,'after':ref})
for (path,family),item in list(clones.items()):
 drop_speech(item['doc'].nodes,item['edits'])
 raw=rgd.write(item['doc']);assert rgd.write(rgd.read(raw))==raw
 write_json(O/(item['member']+'.json'),export_table(raw))
 reports.append({'official_source':path,'official_sha256':hashlib.sha256(stock(path)).hexdigest(),'private_member':item['member'],'private_reference':item['reference'],'native_roundtrip':True,'candidate_sha256':hashlib.sha256(raw).hexdigest(),'sdk_allocation':item['sdk'],'edits':item['edits']})
write_json(R/'docs/voices020/SHARED_ISOLATION_PREVIEW.json',{'schema':'korea.shared-voice-isolation-preview/v1','status':'preview only; source/callers not promoted; no audio bank active','active_source_changed':False,'files':reports,'redirects':[{'category':a,'original':b,'private':v} for (a,b),v in sorted(redirects.items())]})
print('SHARED_PREVIEW_TABLES',len(reports),'SDK_IDENTITY_ALLOCATION',True,'NATIVE_ROUNDTRIP',True)
