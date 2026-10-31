"""Real faulty 014 fixtures, official donors and complete preservation checks."""
import sys, unittest, struct, gzip, json, hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/art015')]
from runtime import read_json
from contracts import *
F=R/'tests/fixtures/art015-before'

class Repair015(unittest.TestCase):
    def test_real_missing_material_key_is_repaired_without_shader_changes(self):
        geom=rc.pack_document([rc.pack_chunk(b'DATA',b'GOHD',(F/'villager.gohd').read_bytes(),version=2)])
        names=geometry_materials(geom); raw=(F/'villager.rrmaterial').read_bytes()
        self.assertTrue(names-material_keys(raw))
        patched=repair_material(raw,names)
        self.assertEqual(material_keys(patched),names)
        self.assertEqual(rc.parse(patched).roots[0].payload,rc.parse(raw).roots[0].payload)
        self.assertEqual(repair_material(patched,names),patched)

    def test_real_landmark_condition_matches_two_current_official_donors(self):
        raw=(F/'landmark-condition.bin').read_bytes();before=lifecycle_terms(raw)
        self.assertEqual([t['join'] for t in before],[0,1,1])
        doc=rc.pack_document([rc.pack_chunk(b'DATA',b'CNBP',raw,version=4)])
        fixed,count=repair_conditions(doc);self.assertEqual(count,1)
        payload=rc.parse(fixed).roots[0].payload;after=lifecycle_terms(payload)
        self.assertEqual([t['value'] for t in after],[t['value'] for t in before])
        self.assertEqual([t['join'] for t in after],[1,1,1])
        self.assertEqual([i for i,(a,b) in enumerate(zip(raw,payload)) if a!=b],[before[0]['join_offset']])
        for row in read_json(R/'docs/update_015/OFFICIAL_CONDITIONS.json'):
            official=(F/row['condition']).read_bytes()
            self.assertEqual(hashlib.sha256(official).hexdigest(),row['condition_sha256'])
            self.assertTrue(all(t['join']==1 for t in lifecycle_terms(official)))
        self.assertEqual(repair_conditions(fixed),(fixed,0))

    def test_all_108_current_models_pass_actual_material_and_selector_contracts(self):
        self.assertEqual(verify_native(R/'inputs/native')['models'],108)

    def test_real_nil_call_fixture_and_documented_replacement(self):
        old=(F/'effects.scar').read_text('utf-8')
        new=(R/'source/scar/korea/effects.scar').read_text('utf-8')
        self.assertIn('Squad_GetActiveCommand(squad)',old)
        self.assertNotIn('Squad_GetActiveCommand(squad)',new)
        for symbol in ['Squad_HasActiveCommand','Squad_IsMoving','Squad_HasAcceptedCommands']:
            self.assertIn(symbol+'(squad)',new)

    def test_actual_014_baseline_preserves_geometry_textures_rigs_hwacha_and_gameplay(self):
        snap=json.loads(gzip.decompress((R/'docs/update_015/before-source.json.gz').read_bytes()))
        policy=read_json(R/'source/update-015-policy.json')
        old=json.loads(snap['inputs/native-manifest.json']);now=read_json(R/'inputs/native-manifest.json')
        if (R/'docs/update_016/before-source.json.gz').exists():
            historical=json.loads(gzip.decompress((R/'docs/update_016/before-source.json.gz').read_bytes()))
            now=json.loads(historical['inputs/native-manifest.json']) # actual 015 boundary; 016 has its own preservation test
        self.assertEqual(set(old),set(now))
        changed={m for m in old if old[m]['sha256']!=now[m]['sha256']}
        self.assertEqual(changed,set(policy['native_changed']))
        self.assertEqual(len(changed),108)
        for m in old:
            if m.endswith(('.rrgeom','.rrtex')) or m.startswith('art/kr014/'):
                self.assertEqual(old[m]['sha256'],now[m]['sha256'],m)
        for name,raw in snap.items():
            if name.startswith('source/tables/') or (name.startswith('source/scar/') and name!='source/scar/korea/effects.scar'):
                self.assertEqual(raw,(R/name).read_text('utf-8'),name)
        sys.path.insert(0,str(R/'tools/art013'))
        for row in policy['source_changes']:self.assertEqual(row,'scar/korea/effects.scar')
        cfg=read_json(R/'project.json')
        self.assertEqual(cfg['owner'],json.loads(snap['project.json'])['owner'])
        self.assertEqual(cfg['bundle_key'],json.loads(snap['project.json'])['bundle_key'])

if __name__=='__main__':unittest.main()
