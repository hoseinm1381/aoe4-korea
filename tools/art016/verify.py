"""Bounded native readback contracts; no game, cook, assembly, or ZIP operation."""
import sys,unittest,json,gzip,base64,hashlib,struct,math
from pathlib import Path
import repair as p
from garrison_shared import relic_chunky as rc,model_variants as mv,rrtex_decoder as rr
from rig_contract import read_contract
import os,tempfile
R=p.R;W=Path(os.environ.get('KOREA_ART016_DIAGNOSTICS',str(Path(tempfile.gettempdir())/'korea-art016-readback')));W.mkdir(parents=True,exist_ok=True);N=R/'inputs/native'
rows=json.loads((R/'docs/update_016/changes.json').read_text());before=json.loads(gzip.decompress((R/'docs/update_016/before-native.json.gz').read_bytes()))
def old(stem,suffix):return base64.b64decode(before['inputs/native/'+stem+suffix])
def chunks(raw,tag):return [c for c in rc.walk(rc.parse(raw).roots) if c.tag==tag]
def geometry_names(raw):
 names=[]
 for c in chunks(raw,b'GOHD'):
  off=0;strings=[]
  for _ in range(4):s,off=rc.read_lp_string(c.payload,off);strings.append(s)
  names.append(strings)
 return names
class Native016(unittest.TestCase):
 def test_geometry_vertex_index_buffers_are_byte_identical_all_lods(self):
  for row in rows:
   if not row['unit']:continue
   raw=(N/(row['stem']+'.rrgeom')).read_bytes()
   self.assertEqual([c.payload for c in chunks(raw,b'GEOB')],[c.payload for c in chunks(old(row['stem'],'.rrgeom'),b'GEOB')],row['asset'])
 def test_mesh_and_material_keys_resolve_without_cross_mesh_collisions(self):
  materials=[];meshes=[]
  for row in rows:
   if not row['unit']:continue
   stem=N/row['stem'];model=stem.with_suffix('.rgm').read_bytes();geom=stem.with_suffix('.rrgeom').read_bytes();mat=stem.with_suffix('.rrmaterial').read_bytes()
   self.assertEqual({c.decoded_name for c in chunks(mat,b'GMat')},{row['material_name']})
   self.assertEqual({c.decoded_name for c in chunks(model,b'SKMS')},{row['mesh_name']})
   self.assertEqual({x[1] for x in geometry_names(geom)},{row['material_name']})
   self.assertFalse(b'unit_mesh' in model);self.assertFalse(b'unit_mesh' in geom)
   materials.append(row['material_name']);meshes.append(row['mesh_name'])
  self.assertEqual(len(materials),72);self.assertEqual(len(set(materials)),72);self.assertEqual(len(set(meshes)),72)
 def test_real_old_cavalry_root_and_duplicate_names_are_rejected(self):
  bad=old('art/kr013/units/kr_horseman_a2/model','.rgm');good=(N/'art/kr013/units/kr_horseman_a2/model.rgm').read_bytes()
  names={b['name'] for b in read_contract(good)['bones']}
  self.assertIn('metarig_root',{b['name'] for b in p.skins(p.one(bad,b'SKIN').payload)}-names)
  for a in ['kr_horseman_a2','kr_mount_horseman_a2']:
   self.assertEqual(p.one(old('art/kr013/units/'+a+'/model','.rgm'),b'SKMS').decoded_name,'unit_mesh')
 def test_every_cavalry_skin_maps_to_owner_hierarchy_and_lod_domains(self):
  expected=json.loads((R/'source/art013/cavalry-owner-contract.json').read_text())['contract'];seen=[]
  for row in rows:
   if not row['cavalry']:continue
   raw=(N/(row['stem']+'.rgm')).read_bytes();contract=read_contract(raw);skin=p.skins(p.one(raw,b'SKIN').payload);owner={b['name']:i for i,b in enumerate(contract['bones'])}
   for key in ['bones','groups','partitions','lod_counts']:self.assertEqual(contract[key],expected[key],(row['asset'],key))
   self.assertEqual(skin[0]['name'],'gaia_root');self.assertEqual(len(p.one(raw,b'SKEL').payload),40*len(skin))
   for b in skin:
    self.assertIn(b['name'],owner);oi=contract['bones'][owner[b['name']]]['parent'];names=[s['name'] for s in skin]
    while oi>=0 and contract['bones'][oi]['name'] not in names:oi=contract['bones'][oi]['parent']
    parent=names.index(contract['bones'][oi]['name']) if oi>=0 else -1
    # Native skin palettes can have independent roots (e.g. stirrups), even
    # when the complete animation owner parents those bones. Preserve that
    # exact donor-derived layout rather than inventing skin reparenting.
    if b['parent']>=0:self.assertEqual(parent,b['parent'],(row['asset'],b['name']))
   self.assertEqual([b['parent'] for b in skin],[b['parent'] for b in p.skins(p.one(old(row['stem'],'.rgm'),b'SKIN').payload)])
   seen.append(row['asset'])
  self.assertEqual(len(seen),16)
 def test_scout_and_infantry_animation_data_are_untouched(self):
  for row in rows:
   if not row['unit'] or row['cavalry']:continue
   a=old(row['stem'],'.rgm');b=(N/(row['stem']+'.rgm')).read_bytes()
   for tag in [b'SKLN',b'SKIN',b'SKEL']:
    self.assertEqual([c.payload for c in chunks(a,tag)],[c.payload for c in chunks(b,tag)],(row['asset'],tag))
 def test_all_bound_masks_have_valid_bc3_mip_streams_and_digests(self):
  dst=W/'verified-dds';dst.mkdir(exist_ok=True)
  for row in rows:
   mat=(N/(row['stem']+'.rrmaterial')).read_bytes();slots=mv.material_slots(mat)['textures'];self.assertEqual(slots['patternTex'].replace('\\','/'),row['pattern'])
   info=rr.decode_rrtex(N/row['pattern'],output_dds=dst/(row['asset']+'.dds'),validate_stream=True)
   self.assertEqual(info['projection']['format'],'BC3_UNORM');self.assertEqual(info['mip_count'],len(row['mask']['mips']))
   self.assertEqual((info['width'],info['height']),(row['mask']['mips'][0]['width'],row['mask']['mips'][0]['height']))
 def test_non_pattern_shader_slots_and_parameters_preserved(self):
  for row in rows:
   a=mv.material_slots(old(row['stem'],'.rrmaterial'));b=mv.material_slots((N/(row['stem']+'.rrmaterial')).read_bytes())
   a['textures'].pop('patternTex');b['textures'].pop('patternTex');self.assertEqual(a,b,row['asset'])
 def test_model_metadata_changes_are_exact_and_all_other_records_preserved(self):
  for row in rows:
   if not row['unit']:continue
   for ext in ['.rgm','.rrgeom']:
    current=(N/(row['stem']+ext)).read_bytes();original=old(row['stem'],ext)
    normalized=p.rename_model(p.rename_model(current,row['mesh_name'],'unit_mesh'),row['material_name'],'korean unified atlas')
    if row['cavalry'] and ext=='.rgm':
     previous={tag:p.one(original,tag).payload for tag in [b'SKLN',b'SKIN',b'SKEL']}
     normalized=rc.rebuild(rc.parse(normalized),lambda c:previous.get(c.tag))
    self.assertEqual(normalized,original,(row['asset'],ext))
 def test_current_native_changes_and_gameplay_match_exact_source_allowlist(self):
  snap=json.loads(gzip.decompress((R/'docs/update_016/before-source.json.gz').read_bytes()))
  baseline=json.loads(snap['inputs/native-manifest.json']);current=json.loads((R/'inputs/native-manifest.json').read_text());policy=json.loads((R/'source/update-016-policy.json').read_text())
  self.assertEqual(set(current)-set(baseline),set(policy['native_added']));self.assertFalse(set(baseline)-set(current))
  self.assertEqual({m for m in baseline if baseline[m]['sha256']!=current[m]['sha256']},set(policy['native_changed']))
  for member in policy['native_changed']+policy['native_added']:
   raw=(N/member).read_bytes();self.assertEqual(len(raw),current[member]['bytes']);self.assertEqual(hashlib.sha256(raw).hexdigest(),current[member]['sha256'])
  protected=json.loads((R/'docs/update_016/PROTECTED_BEFORE.json').read_text())
  for member,h in protected.items():
   if member.startswith(('source/tables/','source/scar/')):self.assertEqual(hashlib.sha256((R/member).read_bytes()).hexdigest(),h,member)
  project=json.loads((R/'project.json').read_text());oldproject=json.loads(snap['project.json'])
  for key in ['owner','race','bundle_key','version','dispatcher']:self.assertEqual(project[key],oldproject[key])
 def test_build_hold_stops_before_verification_staging_or_assembly(self):
  import importlib.util
  from unittest.mock import patch
  spec=importlib.util.spec_from_file_location('korea_build_016_guard',R/'tools/build.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  target=W/'must-not-be-created'
  with patch.object(module,'verify',side_effect=AssertionError('Guard must run before verification')):
   with self.assertRaisesRegex(ValueError,'Owner is playing'):module.build(target)
  self.assertFalse(target.exists());self.assertFalse((R/'output/current').exists())
 def test_actual_new_masks_expand_unit_colour_and_preserve_skin_hair_sources(self):
  for row in rows:
   mask=row['mask'];self.assertTrue(mask['skin_hair_byte_preserved']);self.assertTrue(mask['stock_alpha_restored'])
   if row['unit']:
    self.assertGreater(mask['owner_atlas_mean_after'],mask['owner_atlas_mean_before'],row['asset'])
    if not row['asset'].startswith('kr_mount_'):self.assertGreater(mask['owner_atlas_mean_after']/255,.15,row['asset'])

def export_geometry():
 output=[]
 for row in rows:
  if not row['unit']:continue
  buf=chunks((N/(row['stem']+'.rrgeom')).read_bytes(),b'GEOB');vertices=buf[0].payload;indices=buf[1].payload;n,_,stride,_=struct.unpack_from('<4I',vertices);assert stride==28
  positions=[];uv=[]
  for i in range(n):
   offset=16+i*stride;x,y,z,_=struct.unpack_from('<4e',vertices,offset);positions.append([-x,-z,y]);uv.append(struct.unpack_from('<2e',vertices,offset+12))
  count,_,size,_=struct.unpack_from('<4I',indices);assert size==2
  faces=list(struct.iter_unpack('<3H',indices[16:]));assert count==len(faces)*3
  slots=mv.material_slots((N/(row['stem']+'.rrmaterial')).read_bytes())['textures']
  output.append({'asset':row['asset'],'positions':positions,'uv':uv,'faces':faces,'albedo':slots['albedoTexture'].replace('\\','/'),'mask':row['pattern']})
 (W/'geometry.json.gz').write_bytes(gzip.compress(json.dumps(output).encode(),mtime=0))
if __name__=='__main__':
 suite=unittest.defaultTestLoader.loadTestsFromTestCase(Native016);result=unittest.TextTestRunner(verbosity=2).run(suite)
 if not result.wasSuccessful():sys.exit(1)
 if '--export-geometry' in sys.argv:export_geometry()
