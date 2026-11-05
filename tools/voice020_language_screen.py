"""CPU-only language screening for original Korean synthesis, not historical review."""
import os,sys,logging,json,hashlib,time,collections,urllib.request,subprocess
from pathlib import Path
logging.logAsyncioTasks=False
R=Path(__file__).resolve().parents[1];W=Path(r'F:\aoe_4_temp\ai_voice\tts-workstation');sys.path.insert(0,str(W/'validation-packages'))
os.environ['NUMBA_CACHE_DIR']=str(W/'cache/numba');os.environ['XDG_CACHE_HOME']=str(W/'cache');os.environ['TOKENIZERS_PARALLELISM']='false'
import torch,numpy as np,soundfile as sf,whisper
torch.set_num_threads(2);torch.set_num_interop_threads(1)
M=W/'models/whisper';M.mkdir(parents=True,exist_ok=True);url=whisper._MODELS['base'];expected=url.split('/')[-2];p=M/'base.pt'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
if not p.exists():
 part=p.with_suffix('.pt.part');c=subprocess.run(['curl.exe','--fail','--location','--retry','4','--retry-all-errors','--continue-at','-','--output',str(part),url]);assert c.returncode==0 and sha(part)==expected;part.replace(p)
assert sha(p)==expected
model=whisper.load_model(str(p),device='cpu');print('CPU_LANGUAGE_MODEL_READY',p.stat().st_size,expected,flush=True)
manifest=json.loads((R/'authoring/voices020/VOICE_SCRIPTS.json').read_text());records={r['id']:r for r in manifest['records']};groups=collections.defaultdict(list)
# Screen every synthesized take, grouping adjacent clips to avoid unreliable
# sub-second language guesses. This cannot prove each word's accuracy.
for row in manifest['records']:groups[(row['profile'],row['age'])].append(row['id'])
out=R/'authoring/voices020/language-screening.jsonl';done={}
if out.exists():
 for line in out.read_text().splitlines():
  x=json.loads(line);done[(x['profile'],x['age'])]=x
start=time.monotonic()
while len(done)<len(groups):
 receipt={}
 for line in (R/'authoring/voices020/generation.jsonl').read_text(encoding='utf-8').splitlines():
  try:x=json.loads(line)
  except json.JSONDecodeError:continue
  receipt[x['id']]=x
 worked=False
 for key,ids in groups.items():
  if key in done or not all(i in receipt for i in ids):continue
  chunks=[];current=[];seconds=0
  for ident in ids:
   a,sr=sf.read(str(R/'inputs/native'/receipt[ident]['member']),dtype='float32');assert sr==16000 and a.ndim==1
   if current and seconds+len(a)/sr+.12>26:
    chunks.append(current);current=[];seconds=0
   current.append((ident,a));seconds+=len(a)/sr+.12
  if current:chunks.append(current)
  results=[]
  for chunk in chunks:
   audio=np.concatenate([piece for _,a in chunk for piece in (a,np.zeros(1920,dtype=np.float32))]);mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(audio),n_mels=model.dims.n_mels)
   with torch.inference_mode():_,probs=model.detect_language(mel)
   top=sorted(probs.items(),key=lambda x:x[1],reverse=True)[:5]
   results.append({'ids':[i for i,_ in chunk],'top_languages':top,'ko_probability':probs['ko'],'screen_status':'korean_top' if top[0][0]=='ko' else 'review_required'})
  result={'profile':key[0],'age':key[1],'model':'OpenAI Whisper base multilingual 20250625','model_sha256':expected,'device':'cpu','scope':'Every take included in grouped language detection; group evidence does not establish every word or historical phonology','clips':len(ids),'groups':results,'non_korean_top_groups':sum(x['screen_status']!='korean_top' for x in results),'native_historical_review':'pending'}
  with out.open('a',encoding='utf-8') as f:f.write(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n')
  done[key]=result;worked=True;print('LANGUAGE_SCREENED',len(done),'/',len(groups),key,'FLAGGED',result['non_korean_top_groups'],flush=True)
 if not worked:time.sleep(12)
report={'profiles_age_banks':len(done),'clips_screened':sum(x['clips'] for x in done.values()),'flagged_groups':sum(x['non_korean_top_groups'] for x in done.values()),'model_sha256':expected,'elapsed_seconds':time.monotonic()-start,'historical_native_review':'pending','scope':'Grouped automatic language screening; not pronunciation or word correctness acceptance'}
(R/'docs/voices020/LANGUAGE_SCREENING.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report),flush=True)
