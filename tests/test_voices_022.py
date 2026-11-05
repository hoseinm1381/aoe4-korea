"""0.2.2 playback configuration and bounded freeze diagnostics.
Real Lua replay is source proof, not a native performance or audible test.
"""
from pathlib import Path
import unittest,json,gzip,sys
from lupa import LuaRuntime
from test_voices_020 import Voice020
R=Path(__file__).resolve().parents[1]
class Voice022(Voice020):
 def test_window_is_bounded_and_completes_at_35_seconds(self):
  self.lua.execute('logs={};function print(s) logs[#logs+1]=s end')
  for quarter in range(1,241):
   self.g.now=quarter/4;self.g.KoreaVoice_Tick()
  logs=[self.g.logs[i] for i in range(1,len(self.g.logs)+1)]
  phases=[s for s in logs if s.startswith('KOREA022_VOICE')]
  self.assertEqual(len(phases),21*5)
  self.assertIn('KOREA022_VOICE t=35 phase=complete',phases)
  self.assertTrue(all(25<=int(s.split('t=')[1].split()[0])<=45 for s in phases))
class Helper022(Voice020):
 def real_endpoint(self,available):
  self.g.KoreaVoice_Stop()
  self.lua.execute('messages={};function capture(blob) messages[#messages+1]=Garrison.decode(blob) end')
  self.g.Garrison_Send=self.g.capture if available else None
  self.lua.execute((R/'source/resources/scar/garrison/garrison.scar').read_text())
  self.lua.execute((R/'source/scar/korea/voices_020.scar').read_text())
  self.g.KoreaVoice_Start(self.lua.table_from({1:'korea'}))
 def test_documented_real_helper_session_pulse_and_clip(self):
  self.real_endpoint(True);self.g.KoreaVoice_Tick()
  messages=[self.g.messages[i] for i in range(1,len(self.g.messages)+1)]
  self.assertEqual(messages[0].m,'audio_session');self.assertEqual(messages[1].kind,'pulse')
  self.assertEqual(messages[2].clip,'VILLAGER_MA1select')
  self.assertTrue(all(m.mod=='korea' and m.v==1 and m.epoch==1 for m in messages))
 def test_matching_helper_reannounces_if_bridge_was_absent_at_start(self):
  self.real_endpoint(False);self.assertEqual(len(self.g.messages),0)
  self.g.Garrison_Send=self.g.capture;self.g.KoreaVoice_Tick()
  self.assertEqual(self.g.messages[1].m,'audio_session');self.assertEqual(self.g.messages[3].clip,'VILLAGER_MA1select')
class Gameplay022(unittest.TestCase):
 def replay(self,source,fail=False):
  lua=LuaRuntime(unpack_returned_tuples=True)
  lua.execute('''
   logs={};calls={};now=0
   KoreaState={active=true,ending=false,traceStart=0,players={[1]={id=1}},order={1}}
   function print(s) logs[#logs+1]=s end
   function World_GetGameTime() return now end
   function Player_IsAlive() return true end
   function mark(name) calls[#calls+1]=tostring(now)..":"..name end
   function KoreaLandmarks_Tick() mark("landmarks") end
   function KoreaEconomy_Tick() if fail and now==35 then error("test economy failure") end;mark("economy") end
   function KoreaEffects_Tick() mark("effects") end
   function KoreaEffects_Timers() mark("timers") end
   function KoreaUI_Update() mark("ui") end
  ''')
  lua.execute(source);g=lua.globals();g.fail=fail
  for second in range(1,61):
   g.now=second
   if fail and second==35:
    with self.assertRaises(Exception):g.KoreaLifecycle_Tick()
    break
   g.KoreaLifecycle_Tick()
  return [g.calls[i] for i in range(1,len(g.calls)+1)],[g.logs[i] for i in range(1,len(g.logs)+1)]
 def test_no_simulation_timing_or_order_change_in_first_minute(self):
  p=R/'source/scar/korea/lifecycle.scar';before=gzip.decompress((R/'docs/update_022/lifecycle.scar.before.gz').read_bytes()).decode()
  old,_=self.replay(before);new,logs=self.replay(p.read_text())
  self.assertEqual(old,new);self.assertEqual(len(new),60*5)
  self.assertEqual(len(logs),21*7)
  self.assertIn('KOREA022_GAMEPLAY t=35 phase=complete',logs)
 def test_trace_identifies_last_entered_subsystem(self):
  _,logs=self.replay((R/'source/scar/korea/lifecycle.scar').read_text(),True)
  self.assertEqual(logs[-1],'KOREA022_GAMEPLAY t=35 phase=economy')
class Config022(unittest.TestCase):
 def test_direct_clips_use_speech_volume_like_berber(self):
  self.assertEqual(json.loads((R/'source/resources/audio/events.json').read_text()),{'volume_bus':'speech','events':{}})
 def test_semantic_undo_restores_complete_original_scripts(self):
  sys.path.insert(0,str(R/'tools'));from release022 import verify
  verify()
def load_tests(loader,tests,pattern):
 return unittest.TestSuite([Helper022('test_documented_real_helper_session_pulse_and_clip'),Helper022('test_matching_helper_reannounces_if_bridge_was_absent_at_start'),Voice022('test_window_is_bounded_and_completes_at_35_seconds'),Gameplay022('test_no_simulation_timing_or_order_change_in_first_minute'),Gameplay022('test_trace_identifies_last_entered_subsystem'),Config022('test_direct_clips_use_speech_volume_like_berber'),Config022('test_semantic_undo_restores_complete_original_scripts')])
if __name__=='__main__':unittest.main()
