"""Read the maintained generated Vietnam Lua bank as data, never execute SCAR."""
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parents[1]
class Reader:
 def __init__(self,s):self.s=s;self.i=0
 def ws(self):
  while self.i<len(self.s) and self.s[self.i].isspace():self.i+=1
 def value(self):
  self.ws();c=self.s[self.i]
  if c=='{':
   self.i+=1;self.ws();obj={};arr=[];named=False
   while self.s[self.i]!='}':
    self.ws()
    if self.s[self.i]=='[':
     named=True;self.i+=1;key=self.value();self.ws();assert self.s[self.i:self.i+2]==']=';self.i+=2;obj[key]=self.value()
    else:arr.append(self.value())
    self.ws()
    if self.s[self.i]==',':self.i+=1;self.ws()
    else:assert self.s[self.i]=='}'
   self.i+=1;assert not(named and arr);return obj if named else arr
  if c=='"':v,n=json.JSONDecoder().raw_decode(self.s[self.i:]);self.i+=n;return v
  for token,v in [('true',True),('false',False),('nil',None)]:
   if self.s.startswith(token,self.i):self.i+=len(token);return v
  m=re.match(r'-?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?',self.s[self.i:]);assert m,self.s[self.i:self.i+50];self.i+=len(m[0]);return float(m[0]) if any(c in m[0] for c in '.eE') else int(m[0])
def source_bank():
 p=Path('F:/aoe_4_temp/New_custom_civilization/aoe4-vietnam/source/scar/vietnam/voice_bank_084.scar');s=p.read_text(encoding='utf-8');return Reader(s.split('VietnamVoiceBank=',1)[1]).value(),p
if __name__=='__main__':
 bank,p=source_bank();efforts=bank['stock_efforts'];print('NONVERBAL_STOCK_SPEAKERS',json.dumps({k:{e:len(v) for e,v in events.items()} for k,events in efforts.items()},indent=2))

ROLE_SPEAKERS={
 'VILLAGER_M':'villagermale','VILLAGER_F':'villagerfemale','SCOUT':'scout','SCOUT_F':'scoutfemale',
 'SPEARMAN':'spearman','ARCHER':'archer','HWARANG_FOOT':'archer','TIGER_HUNTER':'archer','CROSSBOW':'crossbowman',
 'GAPSA':'manatarms','MILITIA':'manatarms','HANDCANNON':'handcannon','HORSEMAN':'horseman',
 'HWARANG_MOUNTED':'horseman','LANCER':'knight','SCHOLAR':'monk','MONK':'monk','RIGHTEOUS_MONK':'monk',
 'TRADER':'villagermale','RAM':'seige','TREBUCHET':'seigeranged','HWACHA':'seigeranged','BOMBARD':'seigeranged','SPRINGALD':'seigeranged',
 'NAVAL_FISHING':'scoutship','NAVAL_TRANSPORT':'scoutship','NAVAL_TRADE':'tradeship','NAVAL_COMBAT_SHIP':'ship','NAVAL_WAR_GALLEY':'ship','NAVAL_COMBAT_WARSHIP':'warship','NAVAL_TURTLE':'warship','NAVAL_FIRESHIP':'fireship'}
def copy_efforts():
 import shutil
 src=Path('F:/aoe_4_temp/New_custom_civilization/aoe4-vietnam');bank,source=source_bank();original=json.loads((src/'inputs/native-manifest.json').read_text(encoding='utf-8'));groups={};files={}
 for speaker in sorted(set(ROLE_SPEAKERS.values())):
  groups[speaker]={}
  for event,choices in bank['stock_efforts'][speaker].items():
   assert event in ('death','pain_light','pain_heavy');groups[speaker][event]=[]
   for member,seconds in choices:
    p=src/'inputs/native'/member;digest=hashlib.sha256(p.read_bytes()).hexdigest();assert digest==original[member]['sha256']
    target='audio/korea_020_efforts/'+digest+'.ogg';dest=R/'inputs/native'/target;dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():assert hashlib.sha256(dest.read_bytes()).hexdigest()==digest
    else:shutil.copyfile(p,dest)
    groups[speaker][event].append([target,seconds]);files[target]={'sha256':digest,'bytes':dest.stat().st_size,'toc':'data','source_member':member,'provenance':'Unchanged official nonverbal effort preserved by the maintained Vietnam bank; copied into Korea, no runtime dependency.'}
 result={'schema':'korea.stock-effort-import/v1','source_bank_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'role_speakers':ROLE_SPEAKERS,'stock_efforts':groups,'files':files,'total_bytes':sum(x['bytes'] for x in files.values()),'native_audible_acceptance':'pending; existing effort mapping reused; custom dialogue separately generated'}
 out=R/'authoring/voices020/STOCK_EFFORTS.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('SELF_CONTAINED_STOCK_EFFORTS',len(files),'BYTES',result['total_bytes'])
if __name__=='__main__':
 import sys
 if '--copy' in sys.argv:copy_efforts()
