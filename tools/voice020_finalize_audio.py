"""Finalize codec headroom without changing synthesis masters or original receipts."""
from pathlib import Path
import json,hashlib,os,sys
import numpy as np,soundfile as sf
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from voice020_generate import prepare_wave,RATE,COMPRESSION,sha,canonical
A=R/'authoring/voices020';D=R/'docs/voices020';O=R/'output/voices020'
def main():
 assert (D/'GENERATION_COMPLETE.json').exists(),'Synthesis must finish before final encoding'
 scripts=json.loads((A/'VOICE_SCRIPTS.json').read_text(encoding='utf-8'));requests={x['id']:x for x in scripts['records']};rows={}
 for line in (A/'generation.jsonl').read_text(encoding='utf-8').splitlines():
  x=json.loads(line);assert x['id'] not in rows;rows[x['id']]=x
 assert rows.keys()==requests.keys();final=[];fixes=[]
 existing=A/'ENCODED_BANK.jsonl';prior={}
 if existing.exists():
  for line in existing.read_text(encoding='utf-8').splitlines():
   x=json.loads(line);prior[x['id']]=x
 for ident,x in rows.items():
  if ident in prior:
   y=prior[ident];assert y['master_sha256']==x['master_sha256'] and sha(R/'inputs/native'/y['member'])==y['encoded_sha256'];final.append(y)
   if y.get('headroom_fix'):fixes.append(y['headroom_fix'])
   continue
  p=R/'inputs/native'/x['member'];assert sha(p)==x['encoded_sha256'];decoded,sr=sf.read(str(p),dtype='float32');assert sr==RATE and np.isfinite(decoded).all();peak=float(np.max(np.abs(decoded)));y=dict(x);y['encoding_revision']='korea020-decoded-headroom-v1';y['decoded_peak']=peak
  if peak>=.98:
   original,sr=sf.read(str(R/x['master']),dtype='float32');assert sha(R/x['master'])==x['master_sha256'];_,audio,quality=prepare_wave(original,sr,requests[ident]);assert hashlib.sha256(np.asarray(audio,dtype='<f4').tobytes()).hexdigest()==x['processed_pcm_sha256']
   gain=.88/peak;temp=O/(ident+'.headroom.part.ogg')
   for attempt in range(5):
    adjusted=(audio*gain).astype(np.float32);sf.write(str(temp),adjusted,RATE,format='OGG',subtype='VORBIS',compression_level=COMPRESSION);check,check_rate=sf.read(str(temp),dtype='float32');check_peak=float(np.max(np.abs(check)))
    assert check_rate==RATE and len(check)==len(audio) and np.isfinite(check).all()
    if check_peak<.98:break
    gain*=.88/check_peak
   else:raise ValueError('Codec peak could not be bounded '+ident)
   digest=sha(temp);member='audio/korea_020/'+digest+'.ogg';dest=R/'inputs/native'/member
   if dest.exists():assert sha(dest)==digest
   else:os.replace(temp,dest)
   fix={'id':ident,'original_member':x['member'],'original_peak':peak,'final_member':member,'final_peak':check_peak,'pre_codec_additional_gain':gain,'lossless_master_sha256':x['master_sha256'],'semantic_change':'amplitude only; original master and original encoding retained'}
   y.update(member=member,encoded_sha256=digest,encoded_bytes=dest.stat().st_size,processed_pcm_sha256=hashlib.sha256(adjusted.astype('<f4').tobytes()).hexdigest(),decoded_peak=check_peak,headroom_fix=fix)
   y['quality']=dict(quality,post_vorbis_headroom_gain=gain);fixes.append(fix)
  final.append(y)
  # Each committed final receipt makes this finalization resumable too.
  with existing.open('a',encoding='utf-8',newline='\n') as stream:stream.write(canonical(y)+'\n');stream.flush()
  if len(final)%1000==0:print('FINAL_ENCODED',len(final),'/',len(rows),'HEADROOM_FIXES',len(fixes),flush=True)
 report={'clips':len(final),'headroom_fixes':fixes,'fixed_count':len(fixes),'original_masters_and_generation_receipts_preserved':True,'original_encoded_files_preserved':True,'ceiling':.98,'new_codec_recipe':'Amplitude-only pre-codec attenuation when a full decoded original exceeds the ceiling; iterative decode/check. Same script, voice, timing and master.','encoded_bank_sha256':sha(existing)}
 (D/'ENCODING_FINALIZATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print('ENCODING_FINALIZED',len(final),'HEADROOM_FIXES',len(fixes),flush=True)
if __name__=='__main__':main()
