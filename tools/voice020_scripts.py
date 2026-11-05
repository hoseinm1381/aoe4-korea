"""Build deterministic, editable Korean voice recording scripts. Does not run TTS."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,re,unicodedata
R=Path(__file__).resolve().parents[1];A=R/'authoring/voices020';D=R/'docs/voices020'
def load_rules():
 spec=importlib.util.spec_from_file_location('korea020_language',A/'language_data.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--takes',type=int,default=1);p.add_argument('--selection-takes',type=int,default=3);p.add_argument('--action-takes',type=int,default=2);args=p.parse_args()
 assert 1<=args.takes<=3 and args.takes<=args.selection_takes<=3
 L=load_rules();plan=json.loads((A/'production-plan.json').read_text(encoding='utf-8-sig'));profiles=plan['profiles'];assert {x['id'] for x in profiles}==set(L.ITEMS)
 # Warships may use sails rather than oars. Keep every movement cue valid for
 # all actual naval models rather than inventing an oar animation/crew order.
 L.POOLS['sail'][1]=['I follow the waterway.','믈길 따르노라.','앞 믈길 따르노라.','앞 믈길 따르리라.','앞 믈길 따르리이다.']
 L.POOLS['sail'][5]=['I steer our course.','길 잡노라.','믈길 잡고 가노라.','믈길 잡고 가리라.','믈길 잡고 가리이다.']
 L.ITEMS['NAVAL_COMBAT_SHIP']=('쏠 것','ranged weapons');L.ITEMS['NAVAL_WAR_GALLEY']=('전선','warship')
 L.ITEMS['HWARANG_MOUNTED']=('ᄆᆞᆯ','horse')
 manifest=[];bank_maps={};unique_lines=set()
 for profile in profiles:
  role=profile['id'];naval=role.startswith('NAVAL_');contexts=['select','acknowledge','sail' if naval else 'move','shoot' if role in L.RANGED else 'attack','under_attack']
  if role in ('VILLAGER_M','VILLAGER_F'):contexts+=['build','repair','wood','gold','stone','food']
  if role in ('TRADER','NAVAL_TRADE'):contexts+=['trade']
  if role=='NAVAL_FISHING':contexts+=['fish']
  bank_maps[role]={}
  for age in range(1,5):
   events={}
   for context in contexts:
    lines=copy.deepcopy(L.POOLS[context]);assert len(lines)==6
    if context=='select':
     item,gloss=L.ITEMS[role]
     if age<=2 and role in ('HANDCANNON','BOMBARD','HWACHA'):item='쏠 것'
     if age<=2 and role=='NAVAL_TURTLE':item='맡은 것'
     anchor=[item+' 갖추노라.',item+' 갖추고 듣노라.',item+' 갖추리라.',item+' 갖추리이다.']
     lines[0]=['I am ready with '+gloss+'.']+anchor
    if role=='NAVAL_TRADE' and context=='trade':
     for row in lines:
      for i in range(1,5):row[i]=row[i].replace('먼 길','먼 믈길').replace('길 가','믈길 가')
    ids=[];seen=set()
    for number,row in enumerate(lines,1):
     target=unicodedata.normalize('NFC',row[age]);assert target not in seen,(role,age,context,target);seen.add(target)
     text=target
     changes=[]
     for old,new in sorted(L.RESPELL.items(),key=lambda kv:len(kv[0]),reverse=True):
      if old in text:changes.append({'target':old,'synthesis':new,'claim':'phonetic approximation, not validated recovered sound'});text=text.replace(old,new)
     text=unicodedata.normalize('NFC',text)
     if any(0x1100<=ord(c)<=0x11ff or 0xe000<=ord(c)<=0xf8ff for c in text):raise ValueError('Unresolved old Hangul in synthesis input '+text)
     assert len(text)<90
     take_count=args.selection_takes if context=='select' else (args.takes if context in ('acknowledge','under_attack') else args.action_takes)
     for take in range(1,take_count+1):
      ident=f'{role}_A{age}_{context}_L{number:02}_T{take}'
      punctuation={1:'.',2:'!',3:'...'}[take];spoken=text.rstrip('.!…')+punctuation
      seed=int.from_bytes(hashlib.sha256(ident.encode()).digest()[:4],'big')%2147483647
      sources=list(L.AGE_NOTES[age]['basis'])
      if context=='wood':sources+=['wood_primary']
      if context=='repair':sources+=['gotida']
      if changes:sources+=['alphabet']
      record={'id':ident,'profile':role,'age':age,'context':context,'line':number,'take':take,'seed':seed,'meaning':row[0],'historical_target':('*' if age==1 else '')+target,'synthesis_text':spoken,'phonetic_respellings':changes,'linguistic_status':L.AGE_NOTES[age],'utterance_status':'original composed game dialogue; not a historical quotation','source_locators':[{'id':k,'url':L.SOURCES[k],'scope':'period/constituent form only; not attestation of this full game sentence'} for k in dict.fromkeys(sources)],'take_control':'independent stochastic synthesis plus punctuation; delivered emotion requires listening review','pronunciation_acceptance':'pending historical/native-speaker review'}
      manifest.append(record);ids.append(ident)
     unique_lines.add((role,age,context,target))
    event=context
    if context=='shoot':event='naval_attack' if naval else 'attack'
    if context=='sail':event='sail'
    if naval and context=='attack':event='naval_attack'
    events[event]=ids
   # Deliberate semantic aliases: unknown/default/ability targets get neutral
   # acknowledgements, never invented healing/conversion success claims.
   ack=events['acknowledge']
   for e in ('stop','hold','retreat','garrison','unload','ability_ack','gather'):events[e]=ack
   events['attack_move']=events.get('attack',events.get('naval_attack',ack))
   if naval:
    events['naval_stop']=ack;events['transport_load']=ack;events['transport_unload']=ack
    events['naval_trade']=events.get('trade',ack)
   bank_maps[role]['A'+str(age)]=events
 result={'schema':'korea.voice-recording-scripts/v1','version':'0.2.0','language':'Korean historical diction / explicit phonetic approximations','complete_historical_pronunciation_claim':False,'take_policy':{'preferred_target':'six lines x three takes','selected_lines_per_context':6,'selected_takes':args.takes,'selection_takes':args.selection_takes,'movement_combat_work_takes':args.action_takes,'reason':'Measured 2-second Vorbis minimum approximately 9169 bytes; 67,091,360-byte remaining civilization media budget. Keep phrase variation, add extra selection takes, preserve art and intelligibility.'},'age_notes':L.AGE_NOTES,'sources':L.SOURCES,'records':manifest,'bank_ids':bank_maps,'aliases':'Stops, holds, retreats, loading/unloading and unknown ability/default targets use correctly neutral acknowledgements.'}
 write(A/'VOICE_SCRIPTS.json',result)
 write(D/'SCRIPT_COVERAGE.json',{'profiles':len(profiles),'age_banks':len(profiles)*4,'unique_profile_age_context_lines':len(unique_lines),'planned_dialogue_clips':len(manifest),'takes_per_regular_line':args.takes,'takes_per_movement_combat_work_line':args.action_takes,'takes_per_selection_line':args.selection_takes,'historical_pronunciation':'not independently qualified','semantic_aliases':result['aliases']})
 plan['state']='owner-confirmed researched approximations; historical/native pronunciation review pending';plan['variation_target']['budget_selected_takes']=result['take_policy'];plan['release_gates']['historical_script_and_pronunciation_policy_resolved']='candidate approximations explicitly documented; native/expert qualification pending';write(A/'production-plan.json',plan)
 print('KOREAN_SCRIPT_RECORDS',len(manifest),'PROFILE_AGE_BANKS',len(profiles)*4,'DISTINCT_LINES',len(unique_lines))
if __name__=='__main__':main()
