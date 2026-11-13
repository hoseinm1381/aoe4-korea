import contextlib, io, struct, sys
with contextlib.redirect_stdout(io.StringIO()):
 from inspect_assets import *
from garrison_shared import stock_game
repo=Path('F:/aoe_4_temp/New_custom_civilization')
game=stock_game.current()
stock=('art/civilizations/chinese/structures/wonder_forbidden_palace/'
       'chi_wonder_forbidden_palace_control_age04/chi_wonder_forbidden_palace_control_age04')
sys.path.insert(0,str(repo/'aoe4-korea/tools'))
from repair_landmark_visuals import graft
for p in sorted((rd('korea')/'art/kr013/static').glob('*/model.rgo')):
 if not any(p.parent.name in x for x in ('bulguksa_temple gate_of_reverence gyeongbok_palace hall_of_worthies hwangnyongsa mountain_fortress seon_deok_observatory seowon_academy stone_pagoda',)):continue
 raw=p.read_bytes()
 try:
  out=graft(raw,game.model_files(stock,required=('.rgo',))['.rgo'],rc)
  print('graft',p.parent.name,len(raw),len(out))
 except AssertionError as e: print('fail',p.parent.name,e)
for name in ('berber_tent_age1/model','ribat_lod0/model','fez_lod0/model','tlemcen_age03/tlemcen_age03'):
 for parent in (s/'berbers/older',rd('berbers')):
  for p in parent.glob('art/**/'+name+'.rgm'):
   print(name,parent.name)
   doc=rc.parse(p.read_bytes())
   print([(c.tag,c.decoded_name,len(c.payload)) for c in doc.roots[0].children])
   for c in rc.walk(doc.roots):
    if c.tag in (b'MSCL',b'GOHD',b'STEX',b'MATS') and c.children:print(c.tag,[(t.tag,len(t.payload)) for t in c.children[:6]])
   mats=rc.parse(p.with_suffix('.rrmaterial').read_bytes())
   d=mv.material_slots(rc.pack_document([rc.pack_chunk(mats.roots[0].kind,mats.roots[0].tag,mats.roots[0].payload,version=mats.roots[0].version,name=mats.roots[0].name)]))
   print('textures',d['textures'].keys())
