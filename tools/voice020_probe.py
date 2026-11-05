"""Offline Qwen Korean voice qualification. This does not generate historical game lines.
Run only after the pinned model and Suite setup have completed.
"""
import argparse,datetime,hashlib,json,os,sys,time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
W=Path('F:/aoe_4_temp/ai_voice/tts-workstation')
SUITE=W/'ComfyUI_windows_portable/ComfyUI/custom_nodes/TTS-Audio-Suite'
MODELS=W/'ComfyUI_windows_portable/ComfyUI/models/TTS/qwen3_tts'
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
os.environ['HF_HOME']=str(W/'model-cache');os.environ['TORCH_HOME']=str(W/'torch-cache')
# Production uses official qwen-tts==0.1.1 in the isolated runtime.
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--all-personas',action='store_true');parser.add_argument('--clone-check',action='store_true');a=parser.parse_args()
 import faulthandler,logging
 # This Windows embedded/isolated stack crashed inside LogRecord async task-name lookup.
 # Keep warnings/errors, but omit the unused asyncio task-name decoration.
 logging.logAsyncioTasks=False
 faulthandler.enable();faulthandler.dump_traceback_later(120,repeat=True)
 print('PROBE_IMPORTING_TORCH',flush=True)
 import torch,numpy as np,soundfile as sf
 print('PROBE_IMPORTING_QWEN',flush=True)
 import qwen_tts
 from qwen_tts import Qwen3TTSModel
 print('PROBE_OFFICIAL_QWEN',qwen_tts.__file__,flush=True)
 print('PROBE_IMPORTS_READY',flush=True)
 assert torch.cuda.is_available(),'CUDA unavailable; do not silently fall back to slow CPU inference'
 plan=json.loads((R/'authoring/voices020/production-plan.json').read_text(encoding='utf-8-sig'))
 profiles=plan['profiles'] if a.all_personas else [p for p in plan['profiles'] if p['id'] in ('VILLAGER_M','VILLAGER_F','GAPSA')]
 output=R/'authoring/voices020/qualification-references';output.mkdir(parents=True,exist_ok=True)
 model_dir=MODELS/'Qwen3-TTS-12Hz-1.7B-VoiceDesign'
 assert sha(model_dir/'model.safetensors')=='391e8db219f292c515297cdceeb43e4eae67cdde35fa57e79a6a8a532fca0522','Unverified model weights'
 print('PROBE_DESIGN_WEIGHTS_VERIFIED',flush=True)
 torch.set_num_threads(4);torch.cuda.reset_peak_memory_stats();start=time.monotonic()
 model=Qwen3TTSModel.from_pretrained(str(model_dir),device_map='cuda:0',dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True)
 print('PROBE_DESIGN_MODEL_LOADED',flush=True)
 report={'schema':'korea.qwen-technical-qualification/v1','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':torch.cuda.get_device_name(0),'model':'Qwen3-TTS-12Hz-1.7B-VoiceDesign','suite_pin':'27eef5b85db27ede27d04a44a39e0cfb262bf9a4','engine_package':'qwen-tts==0.1.1 official','engine_module':qwen_tts.__file__,'historical_pronunciation_verified':False,'native_audible_acceptance':False,'clips':[]}
 for p in profiles:
  dest=output/(p['id']+'.wav');receipt=dest.with_suffix('.json')
  if receipt.exists() and dest.exists():
   row=json.loads(receipt.read_text(encoding='utf-8-sig'));assert sha(dest)==row['sha256'];report['clips'].append(row);continue
  torch.manual_seed(p['seed']);torch.cuda.manual_seed_all(p['seed']);t=time.monotonic()
  with torch.inference_mode():
   wavs,sr=model.generate_voice_design(text=p['qualification_reference_text'],language='Korean',instruct=p['design_prompt'],max_new_tokens=1024,do_sample=True,temperature=0.8,top_p=0.95)
  audio=np.asarray(wavs[0],dtype=np.float32).reshape(-1)
  if not np.isfinite(audio).all():raise ValueError('Non-finite audio '+p['id'])
  duration=len(audio)/sr;rms=float(np.sqrt(np.mean(audio**2)));peak=float(np.max(np.abs(audio)))
  if not .5<duration<30 or rms<.002:raise ValueError('Invalid speech duration/silence '+p['id'])
  if peak>1:audio=audio*(.98/peak)
  part=dest.with_suffix('.part.wav');sf.write(str(part),audio,sr,subtype='PCM_16');os.replace(part,dest)
  row={'profile':p['id'],'file':str(dest.relative_to(R)),'sha256':sha(dest),'sample_rate':sr,'channels':1,'pcm_bits':16,'seconds':round(duration,3),'rms':rms,'raw_peak':peak,'generation_seconds':round(time.monotonic()-t,3),'seed':p['seed'],'transcript':p['qualification_reference_text'],'instruction':p['design_prompt'],'linguistic_status':'Modern Korean technical reference only; no historical claim','listening_review':'pending'}
  receipt.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');report['clips'].append(row)
  print('QUALIFIED_WAVE',p['id'],duration,'seconds','generation',row['generation_seconds'],flush=True)
 if a.clone_check:
  import gc
  del model;gc.collect();torch.cuda.empty_cache()
  base_dir=MODELS/'Qwen3-TTS-12Hz-1.7B-Base'
  assert sha(base_dir/'model.safetensors')=='38fc7fc51c5e776e840414b6fd443962e9411b9654888fd7913e4da643cb857c','Unverified Base weights'
  model=Qwen3TTSModel.from_pretrained(str(base_dir),device_map='cuda:0',dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True)
  reference=json.loads((output/'GAPSA.json').read_text(encoding='utf-8'))
  prompt=model.create_voice_clone_prompt(ref_audio=str(output/'GAPSA.wav'),ref_text=reference['transcript'],x_vector_only_mode=False)
  torch.manual_seed(2026110202)
  t=time.monotonic()
  text='여기에 있겠습니다. 맡은 일을 시작하겠습니다.'
  with torch.inference_mode():wavs,sr=model.generate_voice_clone(text=text,language='Korean',voice_clone_prompt=prompt,max_new_tokens=512,do_sample=True,temperature=.8,top_p=.95)
  audio=np.asarray(wavs[0],dtype=np.float32).reshape(-1);duration=len(audio)/sr
  assert np.isfinite(audio).all() and .5<duration<25 and float(np.sqrt(np.mean(audio**2)))>.002
  peak=float(np.max(np.abs(audio)))
  if peak>1:audio*=.98/peak
  dest=output/'GAPSA-clone-check.wav';sf.write(str(dest),audio,sr,subtype='PCM_16')
  clone={'file':str(dest.relative_to(R)),'sha256':sha(dest),'transcript':text,'sample_rate':sr,'channels':1,'seconds':round(duration,3),'generation_seconds':round(time.monotonic()-t,3),'original_reference':reference['sha256'],'language':'modern Korean technical qualification','historical_pronunciation_verified':False,'listening_review':'pending'}
  dest.with_suffix('.json').write_text(json.dumps(clone,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  report['base_clone_check']=clone
  print('QUALIFIED_CLONE_WAVE',duration,'seconds',flush=True)
 faulthandler.cancel_dump_traceback_later()
 report.update(elapsed_seconds=round(time.monotonic()-start,2),peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),audio_integrity_pass=True)
 doc=R/'docs/voices020/TECHNICAL_INFERENCE.json';doc.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k!='clips'},indent=2),flush=True)
if __name__=='__main__':main()

