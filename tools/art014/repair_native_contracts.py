"""Stage native donor skeletons and actual RGB shader inputs without recooking geometry."""
import sys,struct,shutil,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import *
from garrison_shared import relic_chunky as rc,model_variants as mv
from rig_contract import read_contract
from PIL import Image,ImageStat
from garrison_shared import rrtex_decoder as rr
G=stock_game.current();rows=read_json(D/'cook-inputs.json');official=read_json(D/'OFFICIAL_RIG_CONTRACTS.json')
stage=W/'repaired-native';stage.mkdir(exist_ok=True)
source=W/'cooked014'
receipts=[];pattern_stats={}
for row in rows:
 stem=row['stem'];material=(source/stem/'model.rrmaterial').read_bytes();slots=mv.material_slots(material)['textures'];textures={k:v for k,v in slots.items() if k!='__default'}
 pattern_paths=set(row['patterns'].values())
 assert len(pattern_paths)==1,(row['asset'],'multiple materials require independent slot mappings')
 direct=next(iter(pattern_paths));textures['patternTex']=direct.replace('/','\\')
 model=(source/stem/'model.rgm').read_bytes();record={'asset':row['asset'],'kind':row['kind']}
 if row['kind']=='unit':
  donor=official[row['asset']];stock=G.model_files(donor['source'],required=('.rgm','.rrmaterial'))
  assert sha(stock['.rgm'])==donor['sha256']
  actual=read_contract(model);expected=read_contract(stock['.rgm'])
  for key in ['bones','partitions','groups','lod_counts']:assert actual[key]==expected[key],(row['asset'],key)
  native=next(c for c in rc.walk(rc.parse(stock['.rgm']).roots) if c.tag==b'SKLN')
  model=rc.rebuild(rc.parse(model),lambda c:native.payload if c.tag==b'SKLN' else None)
  # Keep the official unit shader/tint LUT and parameters; replace only material texture slots.
  donor_slots=mv.material_slots(stock['.rrmaterial'])['textures']
  assert set(textures)<=set(donor_slots),(row['asset'],set(textures)-set(donor_slots))
  material=mv.rewrite_material(stock['.rrmaterial'],textures,{})
  record['exact_official_skeleton_payload']=True;record['official_source']=donor['source'];record['native_tint_lut_preserved']=donor_slots.get('skinTintLUT')
 else:
  # Static assemblies can have several materials; the curated unique assets share one atlas.
  material=mv.rewrite_material(material,{'patternTex':direct.replace('/','\\')},{})
 if direct not in pattern_stats:
  p=source/direct;dds=W/'pattern-validation'/Path(direct).with_suffix('.dds').name;dds.parent.mkdir(exist_ok=True)
  decoded=rr.decode_rrtex(p,output_dds=dds,validate_stream=True)
  pattern_stats[direct]={'format':decoded['projection']['format'],'rgba_means':ImageStat.Stat(Image.open(dds)).mean,'mips':decoded['mip_count'],'sha256':sha(p.read_bytes())}
  assert decoded['projection']['format']=='BC3_UNORM'
 for suffix,raw in [('.rgm',model),('.rrmaterial',material),('.rgo',(source/stem/'model.rgo').read_bytes()),('.rrgeom',(source/stem/'model.rrgeom').read_bytes())]:
  dest=stage/stem/('model'+suffix);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 record['actual_bound_pattern']=direct;receipts.append(record)
# Copy textures alone; all cooked model metadata above has an explicit reviewed owner.
for p in source.rglob('*.rrtex'):
 dest=stage/p.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
write_json(D/'NATIVE_CONTRACT_REPAIR.json',{'assets':receipts,'patterns':pattern_stats,'models':len(receipts),'stage':str(stage),'geometry_unchanged':True,'animation_clips_or_graphs_changed':False})
print('NATIVE_CONTRACTS_REPAIRED',len(receipts),'patterns',len(pattern_stats),flush=True)
