"""Stage Korean-only native speech suppression and prove exact semantic reversal.
Does not alter source tables, source manifests or the active player release.
"""
import copy,hashlib,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from runtime import import_table,export_table,rgd,read_json,write_json
out=R/'output/voices020/suppression-preview';ledger=[];changed=[]
def prune(nodes,path,edits):
 for i in range(len(nodes)-1,-1,-1):
  n=nodes[i];here=path+'/'+str(n['key'])+'['+str(i)+']'
  if n['key'] in ('speech_ext','squad_speech_ext'):
   edits.append({'parent':path,'index':i,'node':copy.deepcopy(n),'operation':'remove_native_speech_table'})
   nodes.pop(i)
  elif n['key']=='attachment_speaker_code' and n['value']:
   if n['kind']!='CString':raise ValueError('Unexpected speaker type '+here)
   edits.append({'path':here,'index':i,'parent':path,'before':n['value'],'operation':'clear_attachment_speaker','kind':n['kind'],'hash':n['hash']});n['value']=''
  elif n['kind'] in ('List','List2'):prune(n['value'],here,edits)
def reverse(nodes,path,edits):
 for edit in reversed(edits):
  if edit.get('parent')==path:
   i=edit['index']
   if edit['operation']=='remove_native_speech_table':nodes.insert(i,copy.deepcopy(edit['node']))
   else:
    n=nodes[i];assert n['key']=='attachment_speaker_code' and n['value']=='' and n['kind']==edit['kind'] and n['hash']==edit['hash'];n['value']=edit['before']
 for i,n in enumerate(nodes):
  if n['kind'] in ('List','List2'):reverse(n['value'],path+'/'+str(n['key'])+'['+str(i)+']',edits)
for p in sorted((R/'source/tables').rglob('*.rgd.json')):
 member=p.relative_to(R/'source/tables').as_posix()[:-5]
 owned_unit=(('/sbps/korea/' in member or '/ebps/korea/' in member) and p.name.startswith(('kr_unit_','kr_gapsa_','kr_hwacha_','kr_tiger_')))
 isolated=('/garrison/korea/' in member and '/sbps/' in member) or ('/garrison/korea/' in member and '/ebps/' in member)
 attachment='/attachments/attachment_lists/garrison/korea/' in member
 if not (owned_unit or isolated or attachment):continue
 before=read_json(p);candidate=copy.deepcopy(before);edits=[];prune(candidate['nodes'],'',edits)
 if not edits:continue
 undo=copy.deepcopy(candidate);reverse(undo['nodes'],'',edits)
 if undo!=before:raise ValueError('Semantic reversal differs: '+member)
 # Actual native serializer/decoder, not just JSON equality.
 before_native=import_table(before);undo_native=import_table(undo)
 if undo_native!=before_native:raise ValueError('Native reversal differs: '+member)
 compiled=import_table(candidate);roundtrip=rgd.write(rgd.read(compiled))
 if compiled!=roundtrip:raise ValueError('Native roundtrip differs: '+member)
 write_json(out/(member+'.json'),candidate)
 changed.append(member);ledger.append({'member':member,'source_sha256':hashlib.sha256(before_native).hexdigest(),'candidate_sha256':hashlib.sha256(compiled).hexdigest(),'native_roundtrip':True,'semantic_undo_byte_identical':True,'edits':edits})
write_json(R/'docs/voices020/SUPPRESSION_PREVIEW.json',{'schema':'korea.voice-suppression-preview/v1','active_source_changed':False,'status':'staged_private_units_only; shared stock consumers still require private derivation; no complete suppression claim','files':ledger,'changed_members':changed})
print('STAGED_PRIVATE_SPEECH_TABLES',len(changed),'EDITS',sum(len(x['edits']) for x in ledger),'EXACT_NATIVE_REVERSAL',True)
