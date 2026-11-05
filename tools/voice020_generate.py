"""Resumable offline Korean dialogue synthesis. Original WAV masters + native Vorbis.
Requires the qualified Qwen 4.57.3 isolated runtime. No mod source promotion/build.
"""
from pathlib import Path
import argparse,collections,datetime,hashlib,json,logging,math,os,re,time
R=Path(__file__).resolve().parents[1];W=Path('F:/aoe_4_temp/ai_voice/tts-workstation');A=R/'authoring/voices020';O=R/'output/voices020';N=R/'inputs/native'
logging.logAsyncioTasks=False
for k,v in {'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','HF_HOME':str(W/'model-cache'),'TORCH_HOME':str(W/'torch-cache'),'NUMBA_CACHE_DIR':str(W/'numba-cache'),'CUDA_CACHE_PATH':str(W/'cuda-cache'),'TORCHINDUCTOR_CACHE_DIR':str(W/'torchinductor-cache'),'TRITON_CACHE_DIR':str(W/'triton-cache')}.items():os.environ[k]=v
RATE=16000;COMPRESSION=.95

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def canonical(d):return json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def jwrite(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def read_receipts():
 p=A/'generation.jsonl';out={}
 if p.exists():
  for line in p.read_text(encoding='utf-8').splitlines():
   if line.strip():
    row=json.loads(line)
    if row['id'] in out and row!=out[row['id']]:raise ValueError('Conflicting generation receipt '+row['id'])
    out[row['id']]=row
 return out

def signature(row,ref):return hashlib.sha256(canonical({'id':row['id'],'text':row['synthesis_text'],'reference_sha256':ref['sha256'],'engine':'qwen-tts==0.1.1','model':'Base fd4b254389122332181a7c3db7f27e918eec64e3','rate':RATE,'vorbis_compression':COMPRESSION}).encode()).hexdigest()

def prepare_wave(raw,sr,row):
 import numpy as np
 from scipy.signal import resample_poly
 raw=np.asarray(raw,dtype=np.float32).reshape(-1)
 if not np.isfinite(raw).all() or len(raw)<sr*.2:raise ValueError('invalid/short waveform')
 rms=float(np.sqrt(np.mean(raw**2)));peak=float(np.max(np.abs(raw)))
 if rms<.002:raise ValueError('silent waveform')
 frame=max(1,sr//100);energy=np.array([np.sqrt(np.mean(raw[i:i+frame]**2)) for i in range(0,len(raw),frame)])
 active=np.where(energy>max(.003,rms*.08))[0]
 if not len(active):raise ValueError('no active speech')
 begin=max(0,int(active[0]*frame-.06*sr));end=min(len(raw),int((active[-1]+1)*frame+.10*sr));audio=raw[begin:end].copy()
 syllables=sum(0xac00<=ord(c)<=0xd7a3 for c in row['synthesis_text']);duration=len(audio)/sr
 if not max(.22,syllables*.04)<=duration<=min(9,syllables*.65+1.1):raise ValueError('unexpected duration '+str(duration)+' for '+str(syllables)+' syllables')
 gain=min(.11/max(1e-7,float(np.sqrt(np.mean(audio**2)))),.94/max(1e-7,float(np.max(np.abs(audio)))),8)
 audio*=gain
 edge=min(int(sr*.008),len(audio)//8)
 if edge:audio[:edge]*=np.linspace(0,1,edge);audio[-edge:]*=np.linspace(1,0,edge)
 if sr!=RATE:
  g=math.gcd(sr,RATE);audio=resample_poly(audio,RATE//g,sr//g).astype(np.float32)
 return raw,audio,{'raw_rms':rms,'raw_peak':peak,'trim_samples_at_source_rate':[begin,end],'gain':gain,'seconds':len(audio)/RATE,'syllables':syllables}

def save_wave(raw,sr,row,ref,batch_id,seed,slot):
 import numpy as np,soundfile as sf
 original,audio,quality=prepare_wave(raw,sr,row)
 assert re.fullmatch(r'[A-Z0-9_]+_A[1-4]_[a-z_]+_L[0-9]{2}_T[1-3]',row['id'])
 masters=A/'generated';masters.mkdir(parents=True,exist_ok=True);master=masters/(row['id']+'.wav')
 if master.exists():raise RuntimeError('Uncommitted master preserved: '+str(master))
 part=O/(row['id']+'.part.wav');encoded=O/(row['id']+'.part.ogg')
 sf.write(str(part),original,sr,format='WAV',subtype='FLOAT')
 sf.write(str(encoded),audio,RATE,format='OGG',subtype='VORBIS',compression_level=COMPRESSION)
 check,check_rate=sf.read(str(encoded));assert check_rate==RATE and len(check)==len(audio) and np.isfinite(check).all()
 if float(np.sqrt(np.mean(check**2)))<.005:raise ValueError('encoded silence')
 digest=sha(encoded);member='audio/korea_020/'+digest+'.ogg';dest=N/member;dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():
  if sha(dest)!=digest:raise ValueError('Existing content address differs')
 else:os.replace(encoded,dest)
 os.replace(part,master)
 receipt={'id':row['id'],'profile':row['profile'],'age':row['age'],'context':row['context'],'line':row['line'],'take':row['take'],'generation_signature':signature(row,ref),'reference_sha256':ref['sha256'],'master':master.relative_to(R).as_posix(),'master_sha256':sha(master),'source_rate':sr,'source_subtype':'FLOAT','member':member,'encoded_sha256':digest,'encoded_bytes':dest.stat().st_size,'codec':'OGG/VORBIS','sample_rate':RATE,'channels':1,'compression_level':COMPRESSION,'processed_pcm_sha256':hashlib.sha256(np.asarray(audio,dtype='<f4').tobytes()).hexdigest(),'batch_id':batch_id,'actual_torch_seed':seed,'batch_slot':slot,'quality':quality,'historical_pronunciation_qualified':False,'native_listening_review':'pending'}
 with (A/'generation.jsonl').open('a',encoding='utf-8',newline='\n') as stream:stream.write(canonical(receipt)+'\n');stream.flush()
 return receipt

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--pilot',action='store_true');parser.add_argument('--batch-size',type=int,default=16);args=parser.parse_args()
 assert 1<=args.batch_size<=32
 O.mkdir(parents=True,exist_ok=True)
 import msvcrt
 lease=(O/'generation.lock').open('a+b');lease.seek(0);msvcrt.locking(lease.fileno(),msvcrt.LK_NBLCK,1)
 import torch,numpy as np,soundfile as sf
 from qwen_tts import Qwen3TTSModel
 assert torch.cuda.is_available();torch.set_num_threads(4);torch.cuda.set_per_process_memory_fraction(.9);torch.cuda.reset_peak_memory_stats()
 source=A/'VOICE_SCRIPTS.json';manifest_sha=sha(source);data=json.loads(source.read_text(encoding='utf-8-sig'));all_rows=data['records']
 rows=[r for r in all_rows if not args.pilot or (r['profile'] in ('GAPSA','VILLAGER_M','NAVAL_TRADE') and r['line']==1 and r['take']==1)]
 completed=read_receipts();refs={}
 for role in {r['profile'] for r in rows}:
  p=A/'qualification-references'/(role+'.json');ref=json.loads(p.read_text(encoding='utf-8-sig'));assert sha(R/ref['file'])==ref['sha256'];refs[role]=ref
 for row in rows:
  old=completed.get(row['id'])
  if old:
   if old['generation_signature']!=signature(row,refs[row['profile']]):raise ValueError('Changed generation request; preserved master '+row['id'])
   assert sha(R/old['master'])==old['master_sha256'] and sha(N/old['member'])==old['encoded_sha256']
 todo=[r for r in rows if r['id'] not in completed];start=time.monotonic();times=[]
 print('GENERATION_PLAN',len(rows),'rows;',len(todo),'pending; batch',args.batch_size,'pilot',args.pilot,flush=True)
 if todo:
  model_dir=W/'ComfyUI_windows_portable/ComfyUI/models/TTS/qwen3_tts/Qwen3-TTS-12Hz-1.7B-Base'
  model=Qwen3TTSModel.from_pretrained(str(model_dir),device_map='cuda:0',dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True)
  grouped=collections.defaultdict(list)
  for row in todo:grouped[row['profile']].append(row)
  batch_size=args.batch_size
  for role,items in grouped.items():
   items.sort(key=lambda r:(len(r['synthesis_text']),r['id']))
   ref=refs[role];prompt=model.create_voice_clone_prompt(ref_audio=str(R/ref['file']),ref_text=ref['transcript'],x_vector_only_mode=False)
   offset=0
   while offset<len(items):
    if sha(source)!=manifest_sha:raise ValueError('Recording scripts changed during generation; existing results preserved')
    batch=items[offset:offset+batch_size];seed=batch[0]['seed'];batch_id=hashlib.sha256(canonical([r['id'] for r in batch]).encode()).hexdigest()[:20]
    jwrite(O/'batches'/(batch_id+'.json'),{'ids':[r['id'] for r in batch],'actual_seed':seed,'texts':[r['synthesis_text'] for r in batch],'reference':ref['sha256'],'manifest_sha256':manifest_sha,'batch_size':len(batch)})
    t=time.monotonic();torch.manual_seed(seed);torch.cuda.manual_seed_all(seed)
    try:
     with torch.inference_mode():wavs,sr=model.generate_voice_clone(text=[r['synthesis_text'] for r in batch],language=['Korean']*len(batch),voice_clone_prompt=prompt,max_new_tokens=160,do_sample=True,temperature=.8,top_p=.95)
    except torch.cuda.OutOfMemoryError:
     torch.cuda.empty_cache()
     if batch_size<=1:raise
     batch_size=max(1,batch_size//2);print('REDUCED_BATCH_AFTER_OOM',batch_size,flush=True);continue
    assert len(wavs)==len(batch)
    for slot,(row,raw) in enumerate(zip(batch,wavs)):
     try:receipt=save_wave(raw,sr,row,ref,batch_id,seed,slot)
     except ValueError as error:
      print('RETRY_CUE',row['id'],str(error),flush=True)
      for attempt in range(1,4):
       retry_seed=(row['seed']+attempt*104729)%2147483647;torch.manual_seed(retry_seed);torch.cuda.manual_seed_all(retry_seed)
       with torch.inference_mode():retry,sr=model.generate_voice_clone(text=row['synthesis_text'],language='Korean',voice_clone_prompt=prompt,max_new_tokens=160,do_sample=True,temperature=.8,top_p=.95)
       try:receipt=save_wave(retry[0],sr,row,ref,batch_id+'-retry'+str(attempt),retry_seed,0);break
       except ValueError:
        if attempt==3:raise
     completed[row['id']]=receipt
    elapsed=time.monotonic()-t;times.append({'rows':len(batch),'seconds':elapsed});offset+=len(batch)
    selected=[completed[r['id']] for r in rows if r['id'] in completed];media={x['member']:x['encoded_bytes'] for x in selected}
    progress={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pilot':args.pilot,'completed_selected':len(selected),'target_selected':len(rows),'all_planned':len(all_rows),'elapsed_seconds':round(time.monotonic()-start,2),'last_batch_size':len(batch),'last_batch_seconds':round(elapsed,2),'encoded_bytes_selected':sum(media.values()),'peak_cuda_reserved_bytes':torch.cuda.max_memory_reserved()}
    jwrite(R/'docs/voices020/GENERATION_PROGRESS.json',progress);print('GENERATED',len(selected),'/',len(rows),'profile',role,'batch',len(batch),'seconds',round(elapsed,2),'media',sum(media.values()),flush=True)
 selected=[completed[r['id']] for r in rows];media={x['member']:x['encoded_bytes'] for x in selected}
 report={'status':'pilot_complete' if args.pilot else 'complete','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifest_sha256':manifest_sha,'profiles':len({r['profile'] for r in rows}),'rows':len(rows),'encoded_unique_files':len(media),'encoded_bytes':sum(media.values()),'mean_clip_bytes':sum(media.values())/len(selected),'projected_full_dialogue_bytes':round(sum(media.values())/len(selected)*len(all_rows)),'elapsed_seconds':round(time.monotonic()-start,2),'batch_runs':times,'peak_cuda_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_cuda_reserved_bytes':torch.cuda.max_memory_reserved(),'audio_full_decode_verified':True,'historical_native_speaker_review':'pending; explicit phonetic approximations','native_game_audible_acceptance':'pending'}
 jwrite(R/'docs/voices020'/('PILOT_GENERATION.json' if args.pilot else 'GENERATION_COMPLETE.json'),report);print(json.dumps({k:v for k,v in report.items() if k!='batch_runs'},indent=2),flush=True)
 lease.close()
if __name__=='__main__':main()
