"""Release-specific regressions; do not rewrite historical source-only gates."""
import sys,unittest,base64,gzip,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
import release016
class Release016(unittest.TestCase):
 def test_only_12_left_hand_shield_paths_change(self):release016.verify_source()
 def test_actual_old_mapper_reproduces_extra_spear_and_new_mapper_preserves_shield(self):
  before=json.loads(gzip.decompress((R/'docs/update_016_build/before-source.json.gz').read_bytes()))
  old=release016.mapper(base64.b64decode(before['tools/art013/integrate.py']).decode())
  new=release016.mapper((R/'tools/art013/integrate.py').read_text('utf-8'))
  for material in ['metal','gold']:
   shield=f'art/civilizations/common/weapons/defense/shield_round_{material}_wicker/shield_round_{material}_wicker'
   self.assertEqual(old(shield,'gapsa',3),'art/kr013/static/korea_gapsa_heavy_spear/model')
   self.assertIsNone(new(shield,'gapsa',3))
 def test_final_policy_is_based_on_verified_015_and_contains_pending_repairs(self):
  from runtime import read_json
  cfg=read_json(R/'project.json');self.assertEqual(cfg['baseline_members'],'docs/update_016_build/baseline-members.json.gz')
  baseline=json.loads(gzip.decompress((R/cfg['baseline_members']).read_bytes()))['members'];self.assertEqual(len(baseline),1734)
  policy=read_json(R/cfg['update_policy']);self.assertEqual(len(policy['native_changed']),242);self.assertEqual(len(policy['native_added']),51)
  self.assertIn('ui/hud/controls/issuabletooltip.xaml',policy['allowed_added'])
  self.assertEqual(policy['allowed_removed'],['attrib/resource_type_info/merc_byz.rgd'])
if __name__=='__main__':unittest.main()
