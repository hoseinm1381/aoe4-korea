"""Full-decode, content-integrity and duplicate audit of the Korean release audio."""
from pathlib import Path
import hashlib,json,collections,sys
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[1];A=R/'authoring/voices020';D=R/'docs/voices020'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 manifest=A/'VOICE_SCRIPTS.json';scripts=read(manifest);planned={r['id']:r for r in scripts['records']};generated={};processed=collections.defaultdict(list);decoded=collections.defaultdict(list);errors=[];seconds=0;pcm16=0;pcm32=0;masterbytes=0;peakmax=0;silence_max=0
 for line in (A/'ENCODED_BANK.jsonl').read_text(encoding='utf-8').splitlines():
  x=json.loads(line);assert x['id'] not in generated;generated[x['id']]=x
 assert generated.keys()==planned.keys(),'All requested takes must exist before final audit'
 encoded={}
 for i,(ident,x) in enumerate(generated.items()):
  file=R/'inputs/native'/x['member'];master=R/x['master'];assert sha(file)==x['encoded_sha256'] and sha(master)==x['master_sha256'],ident
  info=sf.info(str(file));a,sr=sf.read(str(file),dtype='float32');original,source_rate=sf.read(str(master),dtype='float32')
  assert info.format=='OGG' and info.subtype=='VORBIS' and info.channels==1 and sr==16000 and a.ndim==1,ident
  assert source_rate==24000 and np.isfinite(original).all() and np.isfinite(a).all(),ident
  duration=len(a)/sr;rms=float(np.sqrt(np.mean(a*a)));peak=float(np.max(np.abs(a)));silence=float(np.mean(np.abs(a)<.0001));clip=int(np.sum(np.abs(a)>=.9999))
  assert .22<=duration<=9 and abs(duration-x['quality']['seconds'])<1/sr+.00001 and rms>=.005 and peak<.9999 and silence<.9,(ident,duration,rms,peak,silence,clip)
  processed[x['processed_pcm_sha256']].append(ident);decoded[hashlib.sha256(np.round(a*32767).astype('<i2').tobytes()).hexdigest()].append(ident)
  seconds+=duration;pcm16+=len(a)*2;pcm32+=len(a)*4;masterbytes+=master.stat().st_size;peakmax=max(peakmax,peak);silence_max=max(silence_max,silence);encoded[x['member']]=file.stat().st_size
  if i%1000==0:print('AUDIO_AUDIT',i,'/',len(generated),flush=True)
 duplicates=[v for v in processed.values() if len(v)>1];duplicates_decoded=[v for v in decoded.values() if len(v)>1];assert not duplicates and not duplicates_decoded,('Duplicated dialogue',duplicates,duplicates_decoded)
 efforts=read(A/'STOCK_EFFORTS.json');effort_seconds=0;effort_pcm16=0;effort_pcm32=0
 for m,row in efforts['files'].items():
  p=R/'inputs/native'/m;assert sha(p)==row['sha256'];a,sr=sf.read(str(p),dtype='float32');info=sf.info(str(p));assert np.isfinite(a).all() and len(a)>0 and sr==48000 and info.channels==1 and info.format=='OGG' and info.subtype=='VORBIS'
  assert float(np.max(np.abs(a)))<.9999 and bool(np.any(np.abs(a)>.0001)),m
  effort_seconds+=len(a)/sr;effort_pcm16+=a.size*2;effort_pcm32+=a.size*4
 report={'all_pass':True,'manifest_sha256':sha(manifest),'dialogue_clips':len(generated),'unique_content_addresses':len(encoded),'effort_clips':len(efforts['files']),'dialogue_encoded_bytes':sum(encoded.values()),'effort_encoded_bytes':efforts['total_bytes'],'new_audio_encoded_bytes':sum(encoded.values())+efforts['total_bytes'],'dialogue_duration_seconds':round(seconds,3),'effort_duration_seconds':round(effort_seconds,3),'decoded_dialogue_pcm16_bytes':pcm16,'decoded_dialogue_float32_bytes':pcm32,'decoded_effort_pcm16_bytes':effort_pcm16,'decoded_effort_float32_bytes':effort_pcm32,'decoded_memory_note':'Potential sum if every file were decoded simultaneously, not measured backend residency. Actual runtime performance remains unqualified.','lossless_dialogue_master_bytes':masterbytes,'peak_max':peakmax,'silence_fraction_max':silence_max,'exact_processed_pcm_duplicates':duplicates,'quantized_decoded_pcm_duplicates':duplicates_decoded,'full_decode_rate_channels_finite_duration_silence_clipping_checks':True,'unexpected_language_check':'See separate all-take grouped Whisper screening; not word-by-word historical or native-speaker validation.','historical_native_speaker_listening':'pending'}
 write(D/'AUDIO_AUDIT.json',report);print(json.dumps(report,indent=2),flush=True)
if __name__=='__main__':main()
