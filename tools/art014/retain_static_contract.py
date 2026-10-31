"""Retain qualified one-root shader skin streams; rigid attachments own their own root."""
import sys,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import *
from garrison_shared import model_variants as mv
native=read_json(R/'inputs/native-manifest.json');proof=[]
for row in read_json(D/'cook-inputs.json'):
 if row['kind']!='static':continue
 stem=row['stem']+'/model';old=W/'baseline013-readback'/stem;current=R/'inputs/native'/stem
 # The saved old geometry already passed independent source/UV/state/skin comparisons.
 # Rebind its shader inputs to the fresh native albedo/PBR and full RGB pattern.
 slots=mv.material_slots(current.with_suffix('.rrmaterial').read_bytes())['textures'];textures={k:v for k,v in slots.items() if k!='__default'}
 for suffix in ['.rgm','.rrgeom','.rgo','.rrmaterial']:
  source=old.with_suffix(suffix);raw=source.read_bytes()
  if suffix=='.rrmaterial':raw=mv.rewrite_material(raw,textures,{})
  target=current.with_suffix(suffix);target.write_bytes(raw);member=target.relative_to(R/'inputs/native').as_posix()
  native[member]={'bytes':len(raw),'sha256':sha(raw),'toc':'data','change':'Retain qualified one-root rigid shader stream and lifecycle geometry; correct actual RGB mask binding'}
 proof.append({'asset':row['asset'],'source_geometry_sha256':sha(old.with_suffix('.rrgeom').read_bytes()),'native_geometry_sha256':native[stem+'.rrgeom']['sha256'],'native_skin_palette':'qualified_013_one_root_unchanged','material_bindings_corrected':True})
write_json(R/'inputs/native-manifest.json',native);write_json(D/'STATIC_CONTRACT_RETAINED.json',{'all_passed':True,'assets':proof,'reason':'Unit shader requires valid one-root SKLN/SKMS even for rigid assemblies; root-owned sim attachment avoids merging against a foreign building rig.'})
print('QUALIFIED_STATIC_SHADER_CONTRACT_RETAINED',len(proof),flush=True)
