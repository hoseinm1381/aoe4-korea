"""Resumable CPU-only 24 kHz Vorbis rebuild from immutable Korean masters.

Exact approved preview recipe: existing trim, gain, 8 ms fade and per-take
headroom; no resynthesis, denoising, actor, text or gameplay changes.
"""
from pathlib import Path
import json,hashlib,gzip,shutil,os,time
import numpy as np
import soundfile as sf
import voice020_generate as recipe
R=Path(__file__).resolve().parents[1];D=R/'docs/update_023';N=R/'inputs/native'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rows(p):return [json.loads(s) for s in Path(p).read_text(encoding='utf-8').splitlines() if s.strip()]
def baseline():
 D.mkdir(parents=True,exist_ok=True)
 if (D/'BASELINE.json').exists():return
 c=read(R/'project.json');b=read(R/'docs/BUILD_VERIFICATION.json')
 assert c['version']==b['version']=='0.2.2'
 z=R/'release'/b['zip_name'];assert z.stat().st_size==145864393 and sha(z)=='6175fcef8fffb0b6a59c1e02f3b4524b42dc14b84d36de591b760c42936ca94e'
 for name,p in [('baseline-project.json','project.json'),('baseline-build.json','docs/BUILD_VERIFICATION.json'),('baseline-native-manifest.json','inputs/native-manifest.json'),('baseline-master-index.json','source/master-index.json')]:shutil.copyfile(R/p,D/name)
 for name in ('voice_bank_020.scar','voices_020.scar'):
  (D/(name+'.before.gz')).write_bytes(gzip.compress((R/'source/scar/korea'/name).read_bytes(),mtime=0))
 report=json.loads(gzip.decompress((R/'docs/update_022/package/assembly-report.json.gz').read_bytes()))
 (D/'baseline-members.json.gz').write_bytes(gzip.compress(json.dumps({'members':report['members']}).encode(),mtime=0))
 inventory={p.relative_to(R).as_posix():sha(p) for p in (R/'source').rglob('*') if p.is_file()}
 write(D/'baseline-source.json',inventory)
 write(D/'BASELINE.json',{'version':'0.2.2','zip_sha256':sha(z),'zip_bytes':z.stat().st_size,'encoded_bank_sha256':sha(R/'authoring/voices020/ENCODED_BANK.jsonl'),'scripts_sha256':sha(R/'authoring/voices020/VOICE_SCRIPTS.json'),'native_manifest_sha256':sha(R/'inputs/native-manifest.json'),'master_index_sha256':sha(R/'source/master-index.json'),'approved_sample_recipe':'24 kHz mono OGG/VORBIS compression_level=0.35, existing trim/gain/fades/headroom','authorization':'Owner approved increased size and requested 0.2.3 rebuild; narrow audio-only media-budget exception; ZIP remains below 600000000 bytes.'})
 print('BASELINE_022_SEALED',flush=True)
def encode():
 baseline();base=read(D/'BASELINE.json')
 assert sha(R/'authoring/voices020/ENCODED_BANK.jsonl')==base['encoded_bank_sha256']
 assert sha(R/'authoring/voices020/VOICE_SCRIPTS.json')==base['scripts_sha256']
 old=rows(R/'authoring/voices020/ENCODED_BANK.jsonl');assert len(old)==7632
 scripts={x['id']:x for x in read(R/'authoring/voices020/VOICE_SCRIPTS.json')['records']}
 receipt=D/'ENCODED_BANK.jsonl';done={x['id']:x for x in rows(receipt)} if receipt.exists() else {}
 target=N/'audio/korea_023';target.mkdir(parents=True,exist_ok=True)
 temp=D/'encoding.part.ogg';start=time.monotonic()
 for i,row in enumerate(old):
  if row['id'] in done:
   x=done[row['id']];assert x['master_sha256']==row['master_sha256'] and sha(N/x['member'])==x['encoded_sha256'];continue
  master=R/row['master'];assert sha(master)==row['master_sha256'],master
  raw,sr=sf.read(str(master),dtype='float32');assert sr==24000 and raw.ndim==1
  gain=row.get('headroom_fix',{}).get('pre_codec_additional_gain',1.)
  recipe.RATE=16000;_,oldpcm,_=recipe.prepare_wave(raw,sr,scripts[row['id']]);oldpcm=(oldpcm*gain).astype(np.float32)
  assert hashlib.sha256(oldpcm.astype('<f4').tobytes()).hexdigest()==row['processed_pcm_sha256'],row['id']+' original recipe differs'
  recipe.RATE=24000;_,pcm,q=recipe.prepare_wave(raw,sr,scripts[row['id']]);pcm=(pcm*gain).astype(np.float32)
  extra=1.
  for attempt in range(4):
   sf.write(str(temp),(pcm*extra).astype(np.float32),24000,format='OGG',subtype='VORBIS',compression_level=.35)
   decoded,rate=sf.read(str(temp),dtype='float32');peak=float(np.max(np.abs(decoded)));rms=float(np.sqrt(np.mean(decoded**2)))
   assert rate==24000 and len(decoded)==len(pcm) and np.isfinite(decoded).all() and rms>.005
   if peak<.99:break
   extra*=.96/peak
  else:raise ValueError('codec overshoot '+row['id'])
  h=sha(temp);member='audio/korea_023/'+h+'.ogg';dest=N/member
  if dest.exists():assert sha(dest)==h;temp.unlink()
  else:os.replace(temp,dest)
  x={**row,'previous_member':row['member'],'previous_encoded_bytes':row['encoded_bytes'],'previous_processed_pcm_sha256':row['processed_pcm_sha256'],'member':member,'encoded_sha256':h,'encoded_bytes':dest.stat().st_size,'sample_rate':24000,'compression_level':.35,'processed_pcm_sha256':hashlib.sha256((pcm*extra).astype('<f4').tobytes()).hexdigest(),'quality':q,'decoded_peak':peak,'decoded_rms':rms,'previous_headroom_gain':gain,'additional_codec_headroom_gain':extra,'encoding_revision':'korea023-approved-24khz-vorbis-v1','seconds':len(pcm)/24000}
  with receipt.open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n');f.flush()
  done[x['id']]=x
  if (i+1)%100==0:print('ENCODED',i+1,'/7632',round(time.monotonic()-start,1),'seconds',flush=True)
 audit()
def audit():
 data=rows(D/'ENCODED_BANK.jsonl');old=rows(R/'authoring/voices020/ENCODED_BANK.jsonl');assert len(data)==len(old)==7632 and len({x['id'] for x in data})==7632
 seconds=0.;peak=0.;pcmbytes=0
 for x in data:
  p=N/x['member'];assert sha(p)==x['encoded_sha256'] and p.stat().st_size==x['encoded_bytes']
  a,sr=sf.read(str(p),dtype='float32');assert sr==24000 and a.ndim==1 and np.isfinite(a).all()
  assert float(np.max(np.abs(a)))<.99 and float(np.sqrt(np.mean(a**2)))>.005
  assert len(a)/sr==x['seconds'] and abs(x['seconds']-x['quality']['seconds'])<1e-10
  seconds+=len(a)/sr;pcmbytes+=len(a)*4;peak=max(peak,float(np.max(np.abs(a))))
 unique={x['member']:x['encoded_bytes'] for x in data};assert len(unique)==7632,'unexpected duplicate encoded outputs'
 samples=read(R/'docs/audio-quality-review-022/COMPARISON.json')['clips'];approved=[]
 for s in samples:
  x=next(x for x in data if x['id']==s['id']);p=R/'docs/audio-quality-review-022'/(s['id']+'-higher-quality.ogg')
  a,sr=sf.read(str(p),dtype='float32');b,br=sf.read(str(N/x['member']),dtype='float32');assert sr==br==24000 and np.array_equal(a,b),s['id']
  approved.append(s['id'])
 write(D/'AUDIO_AUDIT.json',{'all_clips_decoded':True,'dialogue_clips':len(data),'unique_dialogue_files':len(unique),'profiles':len({x['profile'] for x in data}),'age_banks':len({(x['profile'],x['age']) for x in data}),'sample_rate':24000,'channels':1,'codec':'OGG/VORBIS','compression_level':.35,'old_dialogue_bytes':sum(x['encoded_bytes'] for x in old),'dialogue_bytes':sum(unique.values()),'seconds':seconds,'decoded_float32_bank_bytes':pcmbytes,'max_decoded_peak':peak,'additional_headroom_cases':sum(x['additional_codec_headroom_gain']!=1 for x in data),'approved_preview_pcm_exact_matches':approved,'encoded_receipts_sha256':sha(D/'ENCODED_BANK.jsonl'),'historical_pronunciation_qualified':False,'full_native_listening':'pending','reconstruction':'Same original masters/scripts/takes, existing source trim/gain/fade/headroom; no resynthesis or denoising; 16 kHz original processed PCM hashes checked for every take.'})
 print('AUDIO_AUDIT',read(D/'AUDIO_AUDIT.json'),flush=True)
def promote():
 audit();data=rows(D/'ENCODED_BANK.jsonl');native=read(D/'baseline-native-manifest.json');mapping={x['previous_member']:x for x in data}
 assert len(mapping)==7632
 oldbank=gzip.decompress((D/'voice_bank_020.scar.before.gz').read_bytes()).decode('utf-8')
 bank=oldbank
 for old,x in mapping.items():
  assert old in bank;bank=bank.replace(old,x['member'])
  assert old in native;del native[old]
  native[x['member']]={'toc':'data','bytes':x['encoded_bytes'],'sha256':x['encoded_sha256'],'origin':'korea023-approved-higher-quality-from-lossless'}
 (R/'source/scar/korea/voice_bank_020.scar').write_bytes(bank.encode('utf-8'))
 write(R/'inputs/native-manifest.json',native)
 write(R/'source/update-023-policy.json',{'allowed_changed':['scar/korea/voice_bank_020.scar'],'allowed_added':sorted(x['member'] for x in data),'allowed_removed':sorted(mapping)})
 c=read(D/'baseline-project.json');c.update(version='0.2.3',update_policy='source/update-023-policy.json',baseline_members='docs/update_023/baseline-members.json.gz',build_stage='quality023-current',rollback_folder='archives/quality023-baseline',publication='Local authorized 0.2.3 audio-quality candidate only; no push or installation',native_game_acceptance='Owner confirmed 0.2.2 voice repair worked; higher-quality preview approved; complete 0.2.3 native listening pending.')
 write(R/'project.json',c)
 write(D/'PATH_MAP.json',{old:x['member'] for old,x in mapping.items()})
 print('PROMOTED_023_AUDIO_ONLY',flush=True)
if __name__=='__main__':
 import sys
 globals()[sys.argv[1] if len(sys.argv)>1 else 'encode']()
