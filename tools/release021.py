"""Scoped 0.2.1 native starting-sheep and Berber-parity voice routing repair."""
from pathlib import Path
import copy,gzip,hashlib,json,shutil,sys,datetime
from runtime import ROOT as R,read_json,write_json,stock_game,rgd,at,export_table,import_table
D=R/'docs/update_021'
ARMY='source/tables/attrib/army/garrison/korea/korea_standard.rgd.json'
VOICE='source/scar/korea/voices_020.scar'
BANK='source/scar/korea/voice_bank_020.scar'
DISPATCH='source/scar/garrison/korea/dispatcher.scar'
CHANGED=[ARMY,VOICE,BANK,DISPATCH]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def jc(d,path):
 for key in path.split('/'):d=next(n for n in (d['nodes'] if 'nodes' in d else d['value']) if n['key']==key)
 return d
def prepare():
 assert R.resolve()==R and R.drive.upper()=='F:' and not R.is_symlink() and not R.is_junction()
 assert shutil.disk_usage(R).free>8_000_000_000
 cfg=read_json(R/'project.json');assert cfg['version']=='0.2.0'
 b=read_json(R/'docs/BUILD_VERIFICATION.json');z=R/'release'/b['zip_name']
 assert z.stat().st_size==145863445 and sha(z)=='7aeab3dfd39c06000b7c925726b273fbeb359c8442cb746be4b440ac273b631a'
 if D.exists():
  assert not (D/'BANK_ROUTING.json').exists(),'Preparation already applied; use seal/verify.'
  assert read_json(D/'baseline-project.json')==cfg
  for n in CHANGED:assert (R/n).read_bytes()==gzip.decompress((D/(Path(n).name+'.before.gz')).read_bytes())
 else:
  D.mkdir()
  for n in CHANGED:
   p=R/n;target=D/(p.name+'.before.gz');target.write_bytes(gzip.compress(p.read_bytes(),mtime=0))
  shutil.copyfile(R/'docs/voices020/package/assembly-report.json.gz',D/'baseline-members.json.gz')
  write_json(D/'baseline-project.json',cfg);write_json(D/'baseline-build.json',b)
  source={p.relative_to(R).as_posix():sha(p) for p in (R/'source').rglob('*') if p.is_file()}
  write_json(D/'baseline-source.json',source)
  write_json(D/'baseline-inputs.json',{'native_manifest_sha256':sha(R/'inputs/native-manifest.json'),'master_index_sha256':sha(R/'source/master-index.json')})
 raw=stock_game.current().blueprint('army/standard_mode/normal_english');official=export_table(raw)
 units=jc(official,'default/army_bag/starting_units')['value'][-5:];positions=jc(official,'default/army_bag/starting_units_spawner/spawn_positions')['value'][-5:]
 assert [jc(n,'$PBGNAME')['value'] for n in units]==['gaia_herdable_sheep','gaia_herdable_sheep','gaia_herdable_sheep_black','gaia_herdable_sheep_brown','gaia_herdable_sheep_brown']
 write_json(D/'OFFICIAL_SHEEP_LAYOUT.json',{'source':'Current installed Attrib.sga: army/standard_mode/normal_english/default','native_blueprint_sha256':hashlib.sha256(raw).hexdigest(),'units':units,'positions':positions})
 doc=read_json(R/ARMY)
 for variant in ('default','campaign'):
  u=jc(doc,variant+'/army_bag/starting_units')['value'];pos=jc(doc,variant+'/army_bag/starting_units_spawner/spawn_positions')['value'];assert len(u)==len(pos)==(7 if variant=='default' else 6)
  u.extend(copy.deepcopy(units));pos.extend(copy.deepcopy(positions))
 # Roundtrip the exact native types before saving lossless JSON.
 assert export_table(import_table(doc))['nodes']==doc['nodes']
 write_json(R/ARMY,doc)
 routing={}
 coverage=read_json(R/'docs/voices020/BANK_COVERAGE.json')
 for name,config in coverage['units'].items():
  short=name.split(':')[1];matches=list((R/'source/tables/attrib/sbps').rglob(short+'.rgd.json'));assert len(matches)==1,(name,matches)
  t=read_json(matches[0])
  for variant in t['nodes']:
   if variant['kind'] not in ('List','List2'):continue
   ids=[n['value'] for n in variant['value'] if n['key']=='pbgid']
   for ident in ids:
    if ident in routing:assert routing[ident]==name,(ident,name)
    routing[ident]=name
 bank=(R/BANK).read_text(encoding='utf-8')
 bank+='\n-- 0.2.1: use compiled native identities as Berber does; keep every existing clip unchanged.\nKoreaVoiceBank.pbgids={\n'
 bank+=''.join(' ['+str(i)+']=KoreaVoiceBank.units['+json.dumps(name)+'],\n' for i,name in sorted(routing.items()))
 bank+='}\n';(R/BANK).write_text(bank,encoding='utf-8')
 write_json(D/'BANK_ROUTING.json',{'squads':len(coverage['units']),'pbgids':{str(i):n for i,n in sorted(routing.items())},'dialogue_clips':7632,'audio_files_changed':0,'reference':'Read-only current Berber berber_scripted_speech.scar family(squad)'})
 policy={'allowed_changed':['attrib/army/garrison/korea/korea_standard.rgd','scar/korea/voices_020.scar','scar/korea/voice_bank_020.scar','scar/garrison/korea/dispatcher.scar','garrison/civilizations.json'],'allowed_added':[],'allowed_removed':[]}
 write_json(R/'source/update-021-policy.json',policy)
 cfg.update(version='0.2.1',update_policy='source/update-021-policy.json',baseline_members='docs/update_021/baseline-members.json.gz',build_stage='voices021-current',rollback_folder='archives/voices021-baseline',native_game_acceptance='0.2.0 reported silent and missing sheep; 0.2.1 native test pending',publication='Local authorized 0.2.1 candidate; no push, installation or publication')
 cfg['shared_entities']=sorted(set(cfg['shared_entities'])|{'gaia_herdable_sheep','gaia_herdable_sheep_black','gaia_herdable_sheep_brown'})
 write_json(R/'project.json',cfg)
 print('PREPARED_021 native sheep=5 in both variants; PBG routes=',len(routing),flush=True)
def seal():
 write_json(D/'expected-repair.json',{n:sha(R/n) for n in CHANGED})
 verify()
def verify():
 cfg=read_json(R/'project.json');old=read_json(D/'baseline-project.json');assert cfg['version']=='0.2.1'
 assert all(cfg[k]==old[k] for k in ('owner','race','bundle_key','name','dispatcher'))
 assert set(cfg['shared_entities'])-set(old['shared_entities'])=={'gaia_herdable_sheep','gaia_herdable_sheep_black','gaia_herdable_sheep_brown'}
 assert not set(old['shared_entities'])-set(cfg['shared_entities'])
 inputs=read_json(D/'baseline-inputs.json');assert sha(R/'inputs/native-manifest.json')==inputs['native_manifest_sha256'] and sha(R/'source/master-index.json')==inputs['master_index_sha256']
 baseline=read_json(D/'baseline-source.json');changed=[]
 for path,h in baseline.items():
  assert (R/path).is_file()
  if sha(R/path)!=h:changed.append(path)
 assert set(changed)==set(CHANGED),(changed,CHANGED)
 added={p.relative_to(R).as_posix() for p in (R/'source').rglob('*') if p.is_file()}-set(baseline)
 assert added=={'source/update-021-policy.json'},added
 for path,h in read_json(D/'expected-repair.json').items():assert sha(R/path)==h,path
 original=json.loads(gzip.decompress((D/'korea_standard.rgd.json.before.gz').read_bytes()))
 doc=read_json(R/ARMY);layout=read_json(D/'OFFICIAL_SHEEP_LAYOUT.json')
 for variant in ('default','campaign'):
  u=jc(doc,variant+'/army_bag/starting_units')['value'];pos=jc(doc,variant+'/army_bag/starting_units_spawner/spawn_positions')['value']
  assert len(u)==len(pos)==(12 if variant=='default' else 11) and u[-5:]==layout['units'] and pos[-5:]==layout['positions']
  del u[-5:];del pos[-5:]
 assert doc==original,'Non-sheep native army data changed'
 before=gzip.decompress((D/'voice_bank_020.scar.before.gz').read_bytes())
 assert (R/BANK).read_bytes().startswith(before),'Existing dialogue bank changed'
 assert read_json(R/'docs/voices020/AUDIO_AUDIT.json')['all_pass']
 print('KOREA021_SCOPE_VERIFIED: 5 native sheep; original audio/models/gameplay and 0.2.0 master indexes preserved.',flush=True)
if __name__=='__main__':globals()[sys.argv[1] if len(sys.argv)>1 else 'verify']()
