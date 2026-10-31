"""Real preserved source and native qualification regressions for Korean art."""
from pathlib import Path
import unittest,sys,json,gzip,hashlib
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from runtime import read_json,import_table,rgd
class Art013(unittest.TestCase):
 def test_original_gameplay_numbers_and_nonvisual_strings_preserved(self):
  before=json.loads(gzip.decompress((R/'docs/update_013/source-before-promotion.json.gz').read_bytes()))
  for name,raw in before.items():
   if not name.startswith('source/tables/'):continue
   # This test preserves the historical 012 -> 013 contract. 014 has its own
   # real-before-source regression for the explicitly approved repair exceptions.
   current=read_json(R/name)
   if read_json(R/'project.json')['version'] in ('0.1.4','0.1.5'):
    snapshot={k.replace('\\','/'):v for k,v in json.loads(gzip.decompress((R/'docs/update_014/before-source.json.gz').read_bytes())).items()}
    current=json.loads(snapshot[name])
   a=rgd.read(import_table(json.loads(raw)));b=rgd.read(import_table(current))
   def protected(d):
    return {p:(n.kind,n.value) for p,n in rgd.flatten(d.nodes) if not isinstance(n.value,list) and n.key!='$PBGNAME'}
   self.assertEqual(protected(a),protected(b),name)
 def test_old_native_inputs_exactly_preserved_and_only_planned_art_added(self):
  before=json.loads(gzip.decompress((R/'docs/update_013/source-before-promotion.json.gz').read_bytes()));old=json.loads(before['inputs/native-manifest.json']);now=read_json(R/'inputs/native-manifest.json');policy=read_json(R/'source/update-013-policy.json')
  if read_json(R/'project.json')['version'] in ('0.1.4','0.1.5'):
   snapshot={k.replace('\\','/'):v for k,v in json.loads(gzip.decompress((R/'docs/update_014/before-source.json.gz').read_bytes())).items()};now=json.loads(snapshot['inputs/native-manifest.json'])
  self.assertEqual({m:now[m] for m in old},old)
  self.assertEqual(set(now)-set(old),set(policy['native_added']))
  self.assertTrue(all(m.startswith('art/kr013/') for m in set(now)-set(old)))
 def test_native_units_static_geometry_and_lifecycle_qualified(self):
  for name,count in [('unit-native-readbacks.json',72),('static-native-readback.json',36),('static-source-comparison.json',36)]:
   d=read_json(R/'docs/update_013'/name);self.assertTrue(d['all_passed'],name);self.assertEqual(len(d['assets']),count)
  for row in read_json(R/'docs/update_013/static-source-comparison.json')['assets']:
   self.assertTrue(row['native_lifecycle_selector_semantics_match']);self.assertTrue(row['native_lifecycle_condition_bytes_match'])
  from garrison_shared import relic_chunky as rc
  import struct
  defaults=read_json(R/'source/art013/building-lifecycle-defaults.json')['states']
  rows=read_json(R/'docs/update_013/static-export.json')['assets']
  for row in rows:
   if row['kind'] not in ['unique','camp_module']:continue
   member='art/kr013/static/'+row['asset'].lower()+'/model.rgo'
   payload=next(c.payload for c in rc.walk(rc.parse((R/'inputs/native'/member).read_bytes()).roots) if c.tag==b'DTBP')
   pos=payload.index(b'life_cycle_state')+16;count=struct.unpack_from('<I',payload,pos)[0];pos+=4;states=[]
   for i in range(count):
    size=struct.unpack_from('<I',payload,pos)[0];pos+=4;states.append(payload[pos:pos+size].decode());pos+=size
   self.assertEqual(states,defaults,row['asset'])
   self.assertTrue(set(state for _,_,values in row['selectors'] for state in values)<=set(states),row['asset'])
 def test_camp_and_inherited_consumers_isolated(self):
  d=read_json(R/'docs/update_013/visual-integration.json')
  self.assertEqual({x['family'] for x in d['inherited_consumers']},{'trader','monk'})
  self.assertTrue({'Korea_lumber_camp01','Korea_mining_camp01'}<=set(d['assets_selected']))
  self.assertTrue(all(x['private'].startswith('attrib/attachments/attachment_lists/garrison/korea/') for x in d['private_lists']))
 def test_stable_independent_identity_and_no_original_source_changes(self):
  self.assertEqual(read_json(R/'project.json')['owner'],'748d61b9-4d3e-4cf3-a506-a9ac1f992d1d')
  for row in read_json(R/'authoring/art013/catalog.json')['sources']:
   self.assertEqual(hashlib.sha256((R/row['blend']).read_bytes()).hexdigest(),row['sha256'])
if __name__=='__main__':unittest.main()
