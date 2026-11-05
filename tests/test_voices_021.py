"""Real Lua regressions for 0.2.1 voice routing/start and native sheep data."""
from pathlib import Path
import gzip,json,os,unittest,copy
from unittest.mock import patch
from test_voices_020 import Voice020
from test_native_start import DirectNativeStart
R=Path(__file__).resolve().parents[1];D=R/'docs/update_021'
class Routing021(Voice020):
 def setUp(self):
  original=Path.read_text
  def read(p,*a,**kw):
   if os.getenv('KOREA021_BASELINE') and p==R/'source/scar/korea/voices_020.scar':
    return gzip.decompress((D/'voices_020.scar.before.gz').read_bytes()).decode()
   return original(p,*a,**kw)
  with patch.object(Path,'read_text',new=read):super().setUp()
 def replace_bp(self,name,ident):
  self.g.KoreaVoice_Stop()
  self.lua.execute('''oldConfig=KoreaVoiceBank.units[actor.bp]
    KoreaVoiceBank.pbgids={[424242]=oldConfig}
    function BP_GetName(bp) return type(bp)=="table" and bp.name or bp end''')
  self.g.actor.bp=self.lua.table_from({'name':name,'PropertyBagGroupID':ident})
  self.g.clips=self.lua.table();self.g.now=20
  self.g.KoreaVoice_Start(self.lua.table_from({1:'korea'}));self.g.KoreaVoice_Tick()
 def test_pbg_identity_matches_when_display_name_differs(self):
  self.replace_bp('native_variant_name',424242);self.assertEqual(self.g.clips[1],'VILLAGER_MA1select')
 def test_bare_name_matches_known_korean_owner_only(self):
  self.replace_bp('voice_test',0);self.assertEqual(self.g.clips[1],'VILLAGER_MA1select')
 def test_other_owner_with_same_basename_is_rejected(self):
  self.replace_bp('foreignowner:voice_test',0);self.assertIsNone(self.g.KoreaVoiceState.actors[10]);self.assertEqual(len(self.g.clips),0)
class Start021(DirectNativeStart):
 def setUp(self):
  original=Path.read_text
  def read(p,*a,**kw):
   if os.getenv('KOREA021_BASELINE') and p==R/'source/scar/garrison/korea/dispatcher.scar':
    return gzip.decompress((D/'dispatcher.scar.before.gz').read_bytes()).decode()
   return original(p,*a,**kw)
  with patch.object(Path,'read_text',new=read):super().setUp()
  self.lua.execute('''function Game_GetLocalPlayer() return player.id end
    function KoreaVoice_Start() calls.voice=calls.voice+1 end
    function KoreaVoice_Stop() end''')
 def test_voice_start_is_independent_of_unsupported_gameplay_age(self):
  g=self.lua.globals();g.advanced_age=True;g.KoreaIndependent_Start();self.assertEqual(g.calls.voice,1);self.assertEqual(g.calls.starts,0)
 def test_voice_restore_without_gameplay_enrollment(self):
  g=self.lua.globals();g.advanced_age=True;g.KoreaIndependent_Start();g.KoreaIndependent_OnGameRestore();self.assertEqual(g.calls.voice,2);self.assertEqual(g.calls.starts,0)
 def test_existing_foreign_player_capture_presentation_stays_started(self):
  self.lua.execute('player.id.race="english";PLAYERS={player,{id={race="748d61b94d3e4cf3a506a9ac1f992d1d:korea"},index=2,isHuman=true}}')
  g=self.lua.globals();g.KoreaIndependent_Start()
  self.assertEqual(g.calls.voice,1);self.assertEqual(g.KoreaIndependentState.civilizations[2],'korea')
class Sheep021(unittest.TestCase):
 def test_exact_five_sheep_and_offsets_preserve_original_army(self):
  def child(d,path):
   for k in path.split('/'):d=next(n for n in (d['nodes'] if 'nodes' in d else d['value']) if n['key']==k)
   return d
  old=json.loads(gzip.decompress((D/'korea_standard.rgd.json.before.gz').read_bytes()))
  p=R/'source/tables/attrib/army/garrison/korea/korea_standard.rgd.json'
  now=copy.deepcopy(old if os.getenv('KOREA021_BASELINE') else json.loads(p.read_text()));layout=json.loads((D/'OFFICIAL_SHEEP_LAYOUT.json').read_text())
  for variant in ('default','campaign'):
   a=child(now,variant+'/army_bag/starting_units')['value'];o=child(now,variant+'/army_bag/starting_units_spawner/spawn_positions')['value']
   self.assertEqual(len(a),12 if variant=='default' else 11);self.assertEqual(len(o),12 if variant=='default' else 11);self.assertEqual(a[-5:],layout['units']);self.assertEqual(o[-5:],layout['positions']);del a[-5:];del o[-5:]
  self.assertEqual(now,old)
def load_tests(loader,tests,pattern):
 s=unittest.TestSuite()
 for cls,names in ((Routing021,['test_pbg_identity_matches_when_display_name_differs','test_bare_name_matches_known_korean_owner_only','test_other_owner_with_same_basename_is_rejected']),(Start021,['test_voice_start_is_independent_of_unsupported_gameplay_age','test_voice_restore_without_gameplay_enrollment','test_existing_foreign_player_capture_presentation_stays_started']),(Sheep021,['test_exact_five_sheep_and_offsets_preserve_original_army'])):
  s.addTests(cls(n) for n in names)
 return s
if __name__=='__main__':unittest.main()
