"""Representative CPU transcription evidence; not historical/native listening approval."""
from pathlib import Path
import os,sys,logging,json,time,collections,re,hashlib
logging.logAsyncioTasks=False
R=Path(__file__).resolve().parents[1];W=Path(r'F:\aoe_4_temp\ai_voice\tts-workstation');sys.path.insert(0,str(W/'validation-packages'));os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba')
import numpy as np,soundfile as sf,torch,whisper
torch.set_num_threads(2);torch.set_num_interop_threads(1);model=whisper.load_model(str(W/'models/whisper/base.pt'),device='cpu');scripts=json.loads((R/'authoring/voices020/VOICE_SCRIPTS.json').read_text());groups=collections.defaultdict(list)
for r in scripts['records']:
 if r['take']==1 and ((r['context']=='select' and r['line']==1) or (r['context'] in ('move','sail') and r['line']==3) or (r['context'] in ('attack','shoot') and r['line']==5)):groups[(r['profile'],r['age'])].append(r)
out=R/'authoring/voices020/transcription-samples.jsonl';done={}
if out.exists():
 for line in out.read_text(encoding='utf-8').splitlines():
  x=json.loads(line);done[(x['profile'],x['age'])]=x

def clean(s):return re.sub(r'[^가-힣]','',s)
def cer(a,b):
 prev=list(range(len(b)+1))
 for i,x in enumerate(a,1):
  cur=[i]
  for j,y in enumerate(b,1):cur.append(min(cur[-1]+1,prev[j]+1,prev[j-1]+(x!=y)))
  prev=cur
 return prev[-1]/max(1,len(a))
while len(done)<len(groups):
 rows={}
 for line in (R/'authoring/voices020/generation.jsonl').read_text(encoding='utf-8').splitlines():
  try:x=json.loads(line)
  except json.JSONDecodeError:continue
  rows[x['id']]=x
 worked=False
 for key,requests in groups.items():
  if key in done or not all(r['id'] in rows for r in requests):continue
  pieces=[]
  for r in requests:
   a,sr=sf.read(str(R/'inputs/native'/rows[r['id']]['member']),dtype='float32');assert sr==16000;pieces.extend([a,np.zeros(5600,dtype=np.float32)])
  audio=np.concatenate(pieces);assert len(audio)<16000*30
  mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(audio),n_mels=model.dims.n_mels)
  with torch.inference_mode():result=whisper.decode(model,mel,whisper.DecodingOptions(language='ko',fp16=False,sample_len=100,temperature=0))
  expected=' '.join(r['synthesis_text'] for r in requests);error=cer(clean(expected),clean(result.text));x={'profile':key[0],'age':key[1],'ids':[r['id'] for r in requests],'expected_synthesis':expected,'transcript':result.text,'modern_recognizer_cer':error,'average_log_probability':result.avg_logprob,'no_speech_probability':result.no_speech_prob,'status':'review' if error>.65 or result.no_speech_prob>.6 else 'recognizer_comparison_only','limits':'Modern Whisper base may normalize or misrecognize archaic forms; this is evidence for review, never historical pronunciation or native-speaker acceptance.'}
  with out.open('a',encoding='utf-8') as f:f.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
  done[key]=x;worked=True;print('TRANSCRIBED',len(done),'/',len(groups),key,'CER',round(error,3),flush=True)
 if not worked:time.sleep(12)
report={'banks':len(done),'sampled_clips':sum(len(x['ids']) for x in done.values()),'high_disagreement_banks':sum(x['status']=='review' for x in done.values()),'mean_modern_recognizer_cer':sum(x['modern_recognizer_cer'] for x in done.values())/len(done),'historical_native_speaker_review':'pending','limits':'Modern recognition screening with archaic spellings; differences require interpretation, not an automatic pronunciation pass/fail.'}
(R/'docs/voices020/TRANSCRIPTION_SAMPLES.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
