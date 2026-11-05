"""Independent typed semantic preservation check for staged Korean voice tables."""
import copy,gzip,hashlib,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from runtime import *
D=R/'docs/voices020';O=R/'output/voices020/integration-preview';G=stock_game.current()
def canon(nodes):return [(n.hash,n.kind,canon(n.value) if isinstance(n.value,list) else n.value) for n in nodes]
def prune(nodes):
 for n in list(nodes):
  if n.key in ('speech_ext','squad_speech_ext'):nodes.remove(n)
  elif n.key=='attachment_speaker_code' and n.value:assert n.kind=='CString';n.value=''
  elif isinstance(n.value,list):prune(n.value)
def proof():
 ledger=read_json(D/'INTEGRATION_PREVIEW.json');before=json.loads(gzip.decompress((D/'before-voice-tables.json.gz').read_bytes()));suppressed=set(read_json(D/'SUPPRESSION_PREVIEW.json')['changed_members']);shared=read_json(D/'SHARED_ISOLATION_PREVIEW.json');extra=read_json(D/'EXTRA_ISOLATION_PREVIEW.json');newfiles=shared['files']+extra['files'];newmap={x['private_member']:x for x in newfiles}
 redirects={(x['category'],x['original']):x['private'] for x in shared['redirects'] if x['category']=='sbps'};redirects.update({(x['category'],x['original']):x['private'] for x in extra['redirects']})
 all_private={('attachments/attachment_lists' if x['official_source'].startswith('attachments/') else x['official_source'].split('/')[0],x['official_source'].rsplit('/',1)[-1]):x['private_reference'] for x in newfiles}
 proven=[]
 for row in ledger['files']:
  member=row['member'];candidate=rgd.read(import_table(read_json(O/(member+'.json'))))
  if row['new']:
   source=newmap[member];raw=G.blueprint(source['official_source']);assert hashlib.sha256(raw).hexdigest()==source['official_sha256'];expected=rgd.read(raw)
   for variant in expected.nodes:
    if not isinstance(variant.value,list):continue
    for field in ('pbgid','parent_pbg/$PBGNAME','parent_pbg/$PBGMAP'):
     try:at(variant,field).value=at(candidate,variant.key+'/'+field).value
     except StopIteration:pass
   prune(expected.nodes)
   er=list(refs(expected.nodes));cr=list(refs(candidate.nodes));assert len(er)==len(cr),(member,len(er),len(cr))
   for (p,c,n,node),(pp,cc,nn,_) in zip(er,cr):
    assert (p,c)==(pp,cc),(member,p,pp,c,cc)
    if n!=nn:
     assert all_private.get((c,n))==nn,(member,p,n,nn);child(node,'$PBGNAME').value=nn
  else:
   expected=rgd.read(import_table(before[member]))
   if member in suppressed:prune(expected.nodes)
   for p,c,n,node in refs(expected.nodes):
    target=redirects.get((c,n))
    if target and '/parent_pbg' not in p:child(node,'$PBGNAME').value=target
  assert canon(expected.nodes)==canon(candidate.nodes),('Non-voice typed change',member)
  proven.append(member)
 write_json(D/'SEMANTIC_PRESERVATION.json',{'tables':len(proven),'members':proven,'all_typed_non_speech_values_order_and_types_preserved':True,'private_alias_identity_fields':'Only SDK-assigned PBG identity and supported empty parent identity; incoming private owner references explicitly admitted.','stock_donors':'Current installed official exact SHA256 verified','proof':'Independent reconstruction from the pre-voice source or official donor, not merely a candidate hash allowlist.'});print('SEMANTIC_VOICE_PRESERVATION_PASS',len(proven),flush=True)
if __name__=='__main__':proof()
