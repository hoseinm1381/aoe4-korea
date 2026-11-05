"""Derive only stock speech owners revealed by the complete Korean closure."""
from pathlib import Path
import sys,copy,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from runtime import *
from garrison_shared import derived_blueprints as derive,mod_content
D=R/'docs/voices020';O=R/'output/voices020/extra-preview';G=stock_game.current();cfg=read_json(R/'project.json');owner=cfg['owner'].replace('-','')
closure=read_json(D/'ATTACHMENT_CLOSURE.json');targets=sorted({x['member'] for x in closure['unmuted_payloads']});rows=[];redirects=[]
def canon(nodes):return [(n.hash,n.kind,canon(n.value) if isinstance(n.value,list) else n.value) for n in nodes]
def prune(nodes,edits,path=''):
 for n in list(nodes):
  p=path+'/'+str(n.key)
  if n.key in ('speech_ext','squad_speech_ext'):edits.append({'path':p,'operation':'remove_speech'});nodes.remove(n)
  elif n.key=='attachment_speaker_code' and n.value:edits.append({'path':p,'operation':'clear_speaker','before':n.value});n.value=''
  elif isinstance(n.value,list):prune(n.value,edits,p)
for path in targets:
 assert not path.startswith('attrib/'),'Unexpected private unmuted owner '+path
 family='attachments/attachment_lists' if path.startswith('attachments/attachment_lists/') else 'ebps';raw=G.blueprint(path);original=rgd.read(raw);name='kr020_voice_'+hashlib.sha256(path.encode()).hexdigest()[:14]
 result,receipt=derive.build([{'name':name,'family':family,'source':path,'changes':[]}],{path:raw},mod_id=cfg['owner'],mod_key='korea',pbgid=mod_content.pbgid,owner=owner)
 dest,(_,compiled)=next(iter(result.items()));doc=rgd.read(compiled);normalized=copy.deepcopy(original)
 for variant in normalized.nodes:
  if not isinstance(variant.value,list):continue
  for field in ['pbgid','parent_pbg/$PBGNAME','parent_pbg/$PBGMAP']:
   try:at(variant,field).value=at(doc,variant.key+'/'+field).value
   except StopIteration:pass
 assert canon(normalized.nodes)==canon(doc.nodes),('SDK derivation changed non-identity native values',path)
 edits=[];prune(doc.nodes,edits);out=rgd.write(doc);assert out==rgd.write(rgd.read(out));member='attrib/'+dest+'.rgd';write_json(O/(member+'.json'),export_table(out))
 rows.append({'official_source':path,'official_sha256':hashlib.sha256(raw).hexdigest(),'private_member':member,'private_reference':owner+':'+name,'candidate_sha256':hashlib.sha256(out).hexdigest(),'native_roundtrip':True,'sdk_allocation':receipt,'sdk_only_identity_semantic_proof':True,'edits':edits})
 redirects.append({'category':family,'original':path.rsplit('/',1)[-1],'private':owner+':'+name})
write_json(D/'EXTRA_ISOLATION_PREVIEW.json',{'files':rows,'redirects':redirects,'source_changed':False});print('EXTRA_SPEECH_OWNERS',len(rows),'NON_IDENTITY_SDK_VALUES_PRESERVED',True)

