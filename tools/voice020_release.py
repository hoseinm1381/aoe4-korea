"""Verified local Korea 0.2.0 voice integration, with an explicit source allowlist."""
import argparse,collections,copy,gzip,hashlib,json,re,shutil,sys
from pathlib import Path,PurePosixPath
from runtime import ROOT as R,read_json,write_json,import_table,rgd,refs,child
D=R/'docs/voices020';A=R/'authoring/voices020';O=R/'output/voices020';OWNER='748d61b94d3e4cf3a506a9ac1f992d1d'
def digest(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rawhash(raw):return hashlib.sha256(raw).hexdigest()
def gzread(p):return json.loads(gzip.decompress(p.read_bytes()))
def gzsave(p,d):
 payload=gzip.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),mtime=0)
 if p.exists():assert p.read_bytes()==payload,'Protected baseline differs: '+str(p)
 else:p.write_bytes(payload)
def lua(value):
 if value is True:return 'true'
 if value is False:return 'false'
 if value is None:return 'nil'
 if isinstance(value,str):return json.dumps(value,ensure_ascii=False)
 if isinstance(value,(int,float)):return str(value)
 if isinstance(value,list):return '{'+','.join(lua(x) for x in value)+'}'
 if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v) for k,v in value.items())+'}'
 raise TypeError(type(value))
def receipts():
 rows={}
 source=A/'ENCODED_BANK.jsonl';assert source.exists(),'Run decoded-headroom finalization before packaging'
 for line in source.read_text(encoding='utf-8').splitlines():
  row=json.loads(line);assert row['id'] not in rows,'Duplicate generation receipt '+row['id'];rows[row['id']]=row
 return rows

def make_bank():
 from voice020 import profile
 manifest=read_json(A/'VOICE_SCRIPTS.json');generated=receipts();planned={r['id']:r for r in manifest['records']};assert generated.keys()==planned.keys()
 completion=read_json(D/'GENERATION_COMPLETE.json');assert completion['rows']==len(planned) and completion['audio_full_decode_verified']
 quality=read_json(D/'AUDIO_AUDIT.json');assert quality['all_pass'] and quality['manifest_sha256']==digest(A/'VOICE_SCRIPTS.json')
 language=read_json(D/'LANGUAGE_SCREENING.json');assert language['clips_screened']==len(planned)
 assert language['flagged_groups']==0,'Unexpected language groups require review before shipping'
 samples=read_json(D/'TRANSCRIPTION_SAMPLES.json');assert samples['banks']==128
 # Modern ASR differences on archaic forms remain explicit review evidence.
 efforts=read_json(A/'STOCK_EFFORTS.json');units={};excluded=[]
 def add(runtime,role):
  assert role in manifest['bank_ids'] and role in efforts['role_speakers'],(runtime,role)
  c={'role':role,'private':True,'stock_speaker':efforts['role_speakers'][role]}
  if role in ('VILLAGER_M','SCOUT'):
   c['female_role']='VILLAGER_F' if role=='VILLAGER_M' else 'SCOUT_F';c['stock_female_speaker']=efforts['role_speakers'][c['female_role']]
  units[runtime.lower()]=c
 for row in read_json(D/'UNIT_INVENTORY.json')['units']:
  if row['runtime'].endswith('_dummy'):
   excluded.append({'runtime':row['runtime'],'reason':'Default Standard loadout is an invisible population/action controller without a renderable human body. Real visible Gapsa/Hwacha/Tiger Hunter owners are separately covered. HRE-brawl/XP3 proxy variants are not claimed as supported game modes.'});continue
  add(row['runtime'],row['profile'])
 shared=read_json(D/'SHARED_ISOLATION_PREVIEW.json')
 for row in shared['redirects']:
  if row['category']=='sbps':add(row['private'],'SPRINGALD' if 'springald' in row['original'] else profile(row['original']))
 clips={}
 for role,ages in manifest['bank_ids'].items():
  clips[role]={}
  for age,events in ages.items():
   clips[role][age]={}
   for event,ids in events.items():
    # Cycle six different phrases before returning to the next directed take.
    ids=sorted(ids,key=lambda i:(planned[i]['take'],planned[i]['line']))
    choices=[]
    for ident in ids:
     x=generated[ident];p=R/'inputs/native'/x['member'];assert digest(p)==x['encoded_sha256']
     choices.append([x['member'],round(x['quality']['seconds'],6)])
    assert len({planned[i]['line'] for i in ids})==6
    clips[role][age][event]=choices
 bank={'schema':'korea.unit-voices/0.2.0','complete':True,'units':units,'clips':clips,'stock_efforts':efforts['stock_efforts']}
 output=O/'scar/korea/voice_bank_020.scar';output.parent.mkdir(parents=True,exist_ok=True);output.write_text('-- Generated from editable Korean scripts and hash-checked generation receipts.\nKoreaVoiceBank='+lua(bank)+'\n',encoding='utf-8')
 coverage={'units':units,'excluded_proxies':excluded,'profiles':len(clips),'age_banks':sum(len(a) for a in clips.values()),'dialogue_clips':len(generated),'effort_files':len(efforts['files']),'supported_commands':'selection, move/patrol, attack/attack-move, stop/hold/retreat, build, trade, load/unload, generic ability/default acknowledgement; observed wood/gold/stone/food/fishing work','context_limits':'Repair and religious conversion/healing orders use semantically neutral acknowledgements because the maintained command boundary does not verify their target. Authored repair-specific recordings are retained for a later qualified target dispatcher; no false repair/conversion success announcement. HRE-brawl/XP3 are not qualified modes.','age_policy':'Current owner/player age, checked again when a reply is played; same speaker family across model/tier changes.','historical_pronunciation':'Researched compositions and phonetic approximations. Not validated ancient pronunciation.','native_listening':'pending','bank_sha256':digest(output),'noncombatant_combat_ack_roles':['SCHOLAR','TRADER','NAVAL_FISHING','NAVAL_TRADE','NAVAL_TRANSPORT'],'controller_sha256':digest(O/'scar/korea/voices_020.scar')}
 write_json(D/'BANK_COVERAGE.json',coverage);write_json(O/'bank-preview.json',bank);print('BANK_READY',len(units),'SQUAD_BLUEPRINTS',len(generated),'CLIPS')
 return bank

def retained_codex(tables,config):
 from codex import validate_native_layout
 report=read_json(D/'baseline-codex-report.json');doc=next(d for m,d in tables.items() if m.startswith('attrib/codex/'));validate_native_layout(doc)
 redirects={r['original']:r['private'] for r in read_json(D/'SHARED_ISOLATION_PREVIEW.json')['redirects'] if r['category']=='sbps'}
 def map_value(x):
  if isinstance(x,str):return redirects.get(x,x)
  if isinstance(x,list):return [map_value(y) for y in x]
  if isinstance(x,dict):return {k:map_value(v) for k,v in x.items()}
  return x
 report=map_value(report);report['voice020']='Retained 0.1.6 layout and age metadata; only isolated speech-owner PBG references translated. No construction-tree regeneration.'
 return doc,report

def promote():
 assert read_json(R/'project.json')['version']=='0.1.6','Use verify after promotion; do not re-promote'
 assert digest(R/'release/Koreans-Garrison-0.1.6.zip')=='e48869987e4c7159290a911d263e06288b6ddf8da7cd3c34e236eaadf0a3a788'
 assert not read_json(D/'ATTACHMENT_CLOSURE.json')['unmuted_payloads']
 make_bank()
 old_media=sum(x['bytes'] for m,x in read_json(R/'inputs/native-manifest.json').items() if m.startswith(('art/','audio/')))
 assert old_media+read_json(D/'AUDIO_AUDIT.json')['new_audio_encoded_bytes']<=300000000,'Review packaging budget before source promotion'
 assert read_json(D/'SEMANTIC_PRESERVATION.json')['all_typed_non_speech_values_order_and_types_preserved']
 baseline=read_json(D/'BASELINE.json');current=read_json(R/'project.json');previous=read_json(R/'docs/BUILD_VERIFICATION.json')
 assert previous['version']=='0.1.6'
 old_manifest=read_json(R/'inputs/native-manifest.json');old_masters=read_json(R/'source/master-index.json')
 gzsave(D/'baseline-native-manifest.json.gz',old_manifest);gzsave(D/'baseline-master-index.json.gz',old_masters);write_json(D/'baseline-project.json',current);write_json(D/'baseline-build.json',previous);write_json(D/'baseline-codex-report.json',read_json(R/'docs/CODEX_GRAPH.json'))
 report=gzread(R/'docs/update_016_build/assembly-report.json.gz');assert report['owner']==current['owner'].replace('-','')
 gzsave(D/'baseline-members.json.gz',{'members':report['members']})
 table_ledger=read_json(D/'INTEGRATION_PREVIEW.json');before=gzread(D/'before-voice-tables.json.gz')
 for row in table_ledger['files']:
  member=row['member'];path=R/'source/tables'/(member+'.json')
  if not row['new']:assert rawhash(import_table(read_json(path)))==row['before_native_sha256']
  else:assert not path.exists()
  candidate=read_json(O/'integration-preview'/(member+'.json'));assert rawhash(import_table(candidate))==row['after_native_sha256'];write_json(path,candidate)
 for name in ('voices_020.scar','voice_bank_020.scar'):
  target=R/'source/scar/korea'/name;assert not target.exists();shutil.copyfile(O/'scar/korea'/name,target)
 init=R/'source/scar/korea/initialization.scar';dispatcher=R/'source/scar/garrison/korea/dispatcher.scar'
 gzsave(D/'before-voice-scar.json.gz',{str(p.relative_to(R)):p.read_text(encoding='utf-8') for p in (init,dispatcher)})
 redirects={x['original']:x['private'] for x in read_json(D/'SHARED_ISOLATION_PREVIEW.json')['redirects'] if x['category']=='sbps'}
 t=init.read_text(encoding='utf-8');old='BP_GetSquadBlueprint("unit_scout_1_chi")';assert t.count(old)==1;t=t.replace(old,'BP_GetSquadBlueprint("'+redirects['unit_scout_1_chi']+'")');init.write_text(t,encoding='utf-8')
 t=dispatcher.read_text(encoding='utf-8');t=t.replace('import("korea/lifecycle.scar")','import("korea/lifecycle.scar")\nimport("korea/voices_020.scar")')
 t=t.replace('    KoreaLifecycle_Start(state.civilizations)','    KoreaLifecycle_Start(state.civilizations)\n    if KoreaVoice_Start then KoreaVoice_Start(state.civilizations) end')
 t=t.replace('    -- Retained restore hooks do not establish save/load acceptance.','    -- Retained restore hooks do not establish save/load acceptance.\n    if KoreaVoice_Stop then KoreaVoice_Stop() end\n    if KoreaVoice_Start then KoreaVoice_Start(state.civilizations) end')
 t=t.replace('    state.ending=true\n    if state.active then','    state.ending=true\n    if KoreaVoice_Stop then KoreaVoice_Stop() end\n    if state.active then');dispatcher.write_text(t,encoding='utf-8')
 generated=receipts();efforts=read_json(A/'STOCK_EFFORTS.json');native=copy.deepcopy(old_manifest)
 for x in generated.values():native[x['member']]={'sha256':x['encoded_sha256'],'bytes':x['encoded_bytes'],'toc':'data','change':'Original Korean 0.2.0 dialogue; retained FLOAT WAV master and recording script'}
 native.update(efforts['files']);write_json(R/'inputs/native-manifest.json',native)
 originals={}
 for line in (A/'generation.jsonl').read_text(encoding='utf-8').splitlines():
  x=json.loads(line)
  if x['member'] not in native:originals['inputs/native/'+x['member']]={'bytes':x['encoded_bytes'],'sha256':x['encoded_sha256'],'role':'Original pre-headroom encoding retained for exact generation resume and codec comparison; not runtime-packaged.'}
 write_json(A/'ORIGINAL_ENCODINGS.json',{'schema':'korea.original-encoding-inputs/v1','files':originals,'policy':'Protected rebuild/history inputs; selected final files are separately registered in inputs/native-manifest.json.'})
 plan=read_json(A/'production-plan.json');plan['state']='All recordings, codec finalization and automatic language checks complete; local candidate source promoted; historical/native listening pending';write_json(A/'production-plan.json',plan)
 index=copy.deepcopy(old_masters);existing={x['path'] for x in index['files']}
 for p in sorted(A.rglob('*')):
  if not p.is_file() or '__pycache__' in p.parts:continue
  path=p.relative_to(R/'authoring').as_posix();assert path not in existing
  index['files'].append({'path':path,'bytes':p.stat().st_size,'sha256':digest(p),'role':'Korean 0.2.0 editable recording source, original voice reference, lossless master or reproducible generation/validation receipt'})
 index['korean_voice_toolchain']='Free pinned external F:/aoe_4_temp/ai_voice/tts-workstation; native and lossless audio are locally retained, so ordinary builds do not need models or the network.';write_json(R/'source/master-index.json',index)
 speech=read_json(R/'source/speech-policy.json');speech['unit_suppression']='Korean paired private SBPS/EBPS plus traced active attachment overrides; see docs/voices020. Stock nonverbal efforts are locally packaged; race/intel/music fields preserved.';speech['unit_dialogue']='Garrison.audio.forMod(korea), local presentation-only role/age/gender dispatcher';speech['native_audible_test']='pending';write_json(R/'source/speech-policy.json',speech)
 changes=[x['member'] for x in table_ledger['files'] if not x['new']]+['scar/korea/initialization.scar','scar/garrison/korea/dispatcher.scar','garrison/civilizations.json']
 added=[x['member'] for x in table_ledger['files'] if x['new']]+['scar/korea/voices_020.scar','scar/korea/voice_bank_020.scar']+list(set(native)-set(old_manifest))
 write_json(R/'source/update-020-policy.json',{'allowed_changed':sorted(changes),'allowed_added':sorted(added),'allowed_removed':[],'scope':'Korean scripted voices, paired native speech suppression and private canonical-owner isolation only. Existing world media/gameplay values retained; namespace/identity preserved.'})
 current.update(version='0.2.0',update_policy='source/update-020-policy.json',baseline_members='docs/voices020/baseline-members.json.gz',build_stage='voices020-current',rollback_folder='archives/voices020-baseline',native_game_acceptance='0.2.0 Korean scripted voice candidate; import/audible/native historical review pending',publication='Local authorized candidate only; no push, tag, game installation or publication')
 write_json(R/'project.json',current)
 shutil.copyfile(O/'README-020.md',R/'README.md');shutil.copyfile(O/'START-HERE-020.md',R/'START-HERE.md')
 write_json(D/'PROMOTION.json',{'table_members':[x['member'] for x in table_ledger['files']],'source_promoted':True,'build_completed':False,'native_game_acceptance':False})
 verify_source();print('KOREA020_SOURCE_PROMOTED')

def verify_source():
 cfg=read_json(R/'project.json');oldcfg=read_json(D/'baseline-project.json');assert cfg['version']=='0.2.0'
 for key in ('owner','race','bundle_key','dispatcher','shared_entities','excluded_tables'):assert cfg[key]==oldcfg[key],key
 baseline=read_json(D/'BASELINE.json');ledger=read_json(D/'INTEGRATION_PREVIEW.json');allowed={'source/tables/'+x['member']+'.json' for x in ledger['files']}|{'source/scar/korea/initialization.scar','source/scar/garrison/korea/dispatcher.scar','source/master-index.json','source/speech-policy.json'}
 for path,h in baseline['source_files'].items():
  if path.startswith('source/') and path not in allowed:assert digest(R/path)==h,'Unrelated source changed '+path
 for row in ledger['files']:assert rawhash(import_table(read_json(R/'source/tables'/(row['member']+'.json'))))==row['after_native_sha256'],row['member']
 old=gzread(D/'baseline-native-manifest.json.gz');new=read_json(R/'inputs/native-manifest.json')
 for m,row in old.items():assert new[m]==row and digest(R/'inputs/native'/m)==row['sha256'],'Baseline native media/input changed '+m
 oldindex=gzread(D/'baseline-master-index.json.gz');newindex=read_json(R/'source/master-index.json');assert newindex['files'][:len(oldindex['files'])]==oldindex['files']
 coverage=read_json(D/'BANK_COVERAGE.json');assert digest(R/'source/scar/korea/voice_bank_020.scar')==coverage['bank_sha256']
 assert digest(R/'source/scar/korea/voices_020.scar')==coverage['controller_sha256']
 media=sum(x['bytes'] for m,x in new.items() if m.startswith(('art/','audio/')));assert media<=300000000,('Civilization media budget',media)
 assert not read_json(D/'ATTACHMENT_CLOSURE.json')['unmuted_payloads'];assert read_json(D/'AUDIO_AUDIT.json')['all_pass'];assert read_json(D/'LANGUAGE_SCREENING.json')['flagged_groups']==0
 from research016_ui import verify
 verify();print('KOREA020_SCOPE_VERIFIED',len(ledger['files']),'TABLES; ORIGINAL MEDIA AND UNRELATED SOURCE PRESERVED; MEDIA_BYTES',media,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['bank','promote','verify']);a=p.parse_args();{'bank':make_bank,'promote':promote,'verify':verify_source}[a.action]()
