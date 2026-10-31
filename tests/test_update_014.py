"""Current 014 contracts and actual failing 013 fixtures; native match acceptance is separate."""
import sys,unittest,json,gzip,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tools'),str(R/'tools/art013')]
from runtime import *
from rig_contract import read_contract
from garrison_shared import relic_chunky as rc,model_variants as mv
def sha(raw):return hashlib.sha256(raw).hexdigest()
def native_at_015(path):
 # 016 deliberately replaces combined cavalry bindings and owner masks.
 # Retain this historical 014 gate against the exact real 015 native snapshot.
 baseline=R/'docs/update_016/before-native.json.gz'
 if baseline.exists():
  import base64
  records=json.loads(gzip.decompress(baseline.read_bytes()))
  key=path.relative_to(R).as_posix()
  if key in records:return base64.b64decode(records[key])
 return path.read_bytes()
def manifest_at_015():
 baseline=R/'docs/update_016/before-source.json.gz'
 if baseline.exists():return json.loads(json.loads(gzip.decompress(baseline.read_bytes()))['inputs/native-manifest.json'])
 return read_json(R/'inputs/native-manifest.json')
class Repair014(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.before={k.replace('\\','/'):v for k,v in json.loads(gzip.decompress((R/'docs/update_014/before-source.json.gz').read_bytes())).items()};cls.policy=read_json(R/'source/update-014-policy.json')
 def test_real_before_source_only_approved_scalar_differences(self):
  seen=[]
  for name,raw in self.before.items():
   if not name.startswith('source/tables/'):continue
   a=rgd.read(import_table(json.loads(raw)));b=rgd.read(import_table(read_json(R/name)))
   def leaves(d):return {p:(n.kind,n.value) for p,n in rgd.flatten(d.nodes) if not isinstance(n.value,list)}
   x,y=leaves(a),leaves(b);diff={p for p in x.keys()|y.keys() if x.get(p)!=y.get(p)}
   if not diff:continue
   seen.append(name)
   if '/attachments/' in name:self.assertTrue(all('/animator_skin_attachment/' in p or '/animator_sim_attachment/' in p for p in diff))
   elif 'town_center_capital_chi_ha_01' in name:
    key='default/construction_ext/on_construction_complete_state_tree_refs/on_construction_complete_entity_state_tree_ref';self.assertEqual(diff,{key});self.assertEqual(y[key],('CString',''))
   else:self.assertTrue('kr_unit_nest_of_bees' in name);self.assertTrue(all(p.endswith('/attachments/$PBGNAME') for p in diff));self.assertTrue(all(y[p][1].endswith(':kr014_hwacha_visual') for p in diff))
  self.assertEqual(set(seen),{r['file'] for r in self.policy['source_changes'] if not r.get('added')})
 def test_actual_bad_rigs_fail_and_valid_rider_control_is_preserved(self):
  for f in read_json(R/'docs/update_014/PRE_REPAIR_RIG_FIXTURES.json')['fixtures']:
   raw=(R/f['file']).read_bytes();self.assertEqual(sha(raw),f['sha256']);old=read_contract(raw);new=read_contract(native_at_015(R/'inputs/native/art/kr013/units'/f['asset']/'model.rgm'))
   expected=read_json(R/'docs/update_014/OFFICIAL_RIG_CONTRACTS.json')[f['asset']]['contract']
   if f['asset']=='kr_lancer_a3':self.assertEqual(old['lod_counts'],expected['lod_counts']);self.assertEqual(old['groups'],expected['groups'])
   else:self.assertNotEqual(old['lod_counts'],expected['lod_counts']);self.assertNotEqual(old['groups'],expected['groups'])
   self.assertEqual(new['lod_counts'],expected['lod_counts']);self.assertEqual(new['groups'],expected['groups'])
 def test_all_current_unit_native_contracts_and_actual_mask_bindings(self):
  for asset,donor in read_json(R/'docs/update_014/OFFICIAL_RIG_CONTRACTS.json').items():
   actual=read_contract(native_at_015(R/'inputs/native/art/kr013/units'/asset/'model.rgm'))
   for key in ['bones','groups','partitions','lod_counts']:self.assertEqual(actual[key],donor['contract'][key],(asset,key))
  repair=read_json(R/'docs/update_014/NATIVE_CONTRACT_REPAIR.json')
  for row in repair['assets']:
   p=R/'inputs/native/art/kr013'/('units' if row['kind']=='unit' else 'static')/row['asset'].lower()/'model.rrmaterial';slots=mv.material_slots(native_at_015(p))['textures'];self.assertEqual(slots['patternTex'].replace('\\','/'),row['actual_bound_pattern'])
   if row.get('native_tint_lut_preserved'):self.assertEqual(slots['skinTintLUT'],row['native_tint_lut_preserved'])
 def test_original_native_inputs_only_exact_approved_differences(self):
  old=json.loads(self.before['inputs/native-manifest.json']);new=manifest_at_015()
  self.assertEqual(set(new)-set(old),set(self.policy['native_added']));self.assertFalse(set(old)-set(new))
  self.assertTrue({m for m in old if old[m]['sha256']!=new[m]['sha256']}<=set(self.policy['native_changed']))
 def test_static_shader_palette_geometry_and_lifecycle_retained(self):
  for row in read_json(R/'docs/update_014/STATIC_CONTRACT_RETAINED.json')['assets']:
   stem=R/'inputs/native/art/kr013/static'/row['asset'].lower()/'model';self.assertEqual(sha(stem.with_suffix('.rrgeom').read_bytes()),row['source_geometry_sha256']);contract=read_contract(stem.with_suffix('.rgm').read_bytes());self.assertEqual(contract['lod_counts'],[1]);self.assertEqual(len(contract['bones']),1)
 def test_hwacha_uses_owned_native_visual_and_small_editable_mesh(self):
  self.assertTrue((R/'authoring/art014/hwacha/kr_hwacha.blend').is_file());self.assertLess(read_json(R/'authoring/art014/hwacha/validation.json')['triangles'],15000)
  raw=(R/'inputs/native/art/kr014/hwacha/model.rgm').read_bytes();self.assertEqual(len(read_contract(raw)['bones']),5)
  doc=rgd.read(import_table(read_json(R/'source/tables/attrib/attachments/attachment_lists/garrison/korea/kr014_hwacha_visual.rgd.json')));self.assertTrue(any(n.value=='art\\kr014\\hwacha\\model' for _,n in rgd.flatten(doc.nodes) if n.kind=='CString'))
if __name__=='__main__':unittest.main()
