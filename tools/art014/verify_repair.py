"""Real 0.1.3 regression and current native rig/material checks; no gameplay simulation claims."""
import sys,json,gzip,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import *
from garrison_shared import relic_chunky as rc,model_variants as mv
from rig_contract import read_contract
before={k.replace('\\','/'):v for k,v in json.loads(gzip.decompress((D/'before-source.json.gz').read_bytes())).items()}
policy=read_json(R/'source/update-014-policy.json');allowed={r['file'] for r in policy['source_changes']};source_changes=[]
def tree(value):return rgd.read(import_table(json.loads(value) if isinstance(value,str) else value))
for name,value in before.items():
 if not name.startswith('source/tables/'):continue
 old=tree(value);new=rgd.read(import_table(read_json(R/name)))
 def leaves(doc):return {p:(n.kind,n.value) for p,n in rgd.flatten(doc.nodes) if not isinstance(n.value,list)}
 a,b=leaves(old),leaves(new);diff={p:(a.get(p),b.get(p)) for p in a.keys()|b.keys() if a.get(p)!=b.get(p)}
 if not diff:continue
 assert name in allowed,(name,diff)
 if '/attachments/' not in name:
  permitted=({'default/construction_ext/on_construction_complete_state_tree_refs/on_construction_complete_entity_state_tree_ref'} if 'town_center_capital_chi_ha_01' in name else {p for p in diff if p.endswith('/attachments/$PBGNAME')})
  assert set(diff)==permitted,(name,diff)
  if 'town_center_capital_chi_ha_01' in name:assert list(diff.values())[0][1]==('CString','')
  else:assert all(y[1].endswith(':kr014_hwacha_visual') for x,y in diff.values())
 else:
  assert all('/animator_skin_attachment/' in p or '/animator_sim_attachment/' in p for p in diff),diff
 source_changes.append({'file':name,'changed_scalar_paths':sorted(diff)})
oldnative=json.loads(before['inputs/native-manifest.json']);native=read_json(R/'inputs/native-manifest.json')
assert set(native)-set(oldnative)==set(policy['native_added']);assert not set(oldnative)-set(native)
actual_changed={m for m in oldnative if oldnative[m]['sha256']!=native[m]['sha256']}
assert actual_changed<=set(policy['native_changed']),actual_changed-set(policy['native_changed'])
units=[];G=stock_game.current();official=read_json(D/'OFFICIAL_RIG_CONTRACTS.json')
for asset,donor in sorted(official.items()):
 member='art/kr013/units/'+asset+'/model.rgm';raw=(R/'inputs/native'/member).read_bytes();stock=G.model_files(donor['source'],required=('.rgm',))['.rgm'];assert sha(stock)==donor['sha256']
 def skeleton(raw):return next(c.payload for c in rc.walk(rc.parse(raw).roots) if c.tag==b'SKLN')
 assert skeleton(raw)==skeleton(stock),asset
 assert read_contract(raw)==read_contract(stock),asset
 units.append({'asset':asset,'exact_official_skeleton_and_bind_payload':True,'model_sha256':sha(raw)})
repairs=read_json(D/'NATIVE_CONTRACT_REPAIR.json');patterns=repairs['patterns']
for row in repairs['assets']:
 stem='art/kr013/'+('units/' if row['kind']=='unit' else 'static/')+row['asset'].lower()+'/model'
 slots=mv.material_slots((R/'inputs/native'/(stem+'.rrmaterial')).read_bytes())['textures']
 assert slots['patternTex'].replace('\\','/')==row['actual_bound_pattern'],row['asset']
 if row.get('native_tint_lut_preserved'):assert slots['skinTintLUT']==row['native_tint_lut_preserved']
 assert patterns[row['actual_bound_pattern']]['format']=='BC3_UNORM'
static=read_json(D/'STATIC_CONTRACT_RETAINED.json')
for row in static['assets']:
 p=R/'inputs/native/art/kr013/static'/row['asset'].lower()/'model.rrgeom';assert sha(p.read_bytes())==row['source_geometry_sha256']
write_json(D/'REPAIR_VERIFICATION.json',{'source_regression_passed':True,'original_tables_checked':sum(n.startswith('source/tables/') for n in before),'source_changes':source_changes,'unit_exact_native_rig_checks':len(units),'units':units,'static_original_geometry_preserved':len(static['assets']),'actual_bound_rgb_mask_materials_checked':len(repairs['assets']),'native_members_changed':len(actual_changed),'native_members_added':len(policy['native_added']),'native_game_appearance_animation_and_performance':'pending','full_unit_preview_decode':'times out in optional animation_discovery at 94 percent; not promoted to a pass'})
print('REPAIR_VERIFIED tables',sum(n.startswith('source/tables/') for n in before),'exact_rigs',len(units),'static',len(static['assets']),'actual_RGB_bindings',len(repairs['assets']),flush=True)
