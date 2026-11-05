from pathlib import Path
import json
import numpy as np,soundfile as sf
from scipy.signal import resample_poly
r=Path('F:/aoe_4_temp/New_custom_civilization/aoe4-korea');o=r/'output/voices020/codec-preview';o.mkdir(parents=True,exist_ok=True)
a,sr=sf.read(str(r/'authoring/voices020/qualification-references/GAPSA.wav'));a=a[:int(sr*2.0)]
rows=[]
for rate in (16000,24000):
 b=a if rate==sr else resample_poly(a,2,3)
 for compression in (.5,.8,.95):
  p=o/('r'+str(rate)+'_c'+str(round(compression*100))+'.ogg');sf.write(str(p),b,rate,format='OGG',subtype='VORBIS',compression_level=compression)
  decoded,ds=sf.read(str(p));assert ds==rate and len(decoded)==len(b) and np.isfinite(decoded).all()
  rows.append({'rate':rate,'compression':compression,'bytes_for_2_seconds':p.stat().st_size,'format':sf.info(str(p)).format,'subtype':sf.info(str(p)).subtype})
v=next(Path('F:/aoe_4_temp/New_custom_civilization/aoe4-vietnam/inputs/native/audio/voices').glob('*.ogg'));info=sf.info(str(v))
result={'diagnostic_only_not_game_voice_takes':True,'encodings':rows,'existing_vietnam_accepted_format':{'rate':info.samplerate,'channels':info.channels,'format':info.format,'subtype':info.subtype},'voice_raw_media_budget_bytes':300000000-232908640}
(r/'docs/voices020/CODEC_BUDGET_PREVIEW.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
