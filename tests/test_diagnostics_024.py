"""Execute actual diagnostic module/voice/conversion paths; no native crash claim."""
from pathlib import Path
import re,unittest
from lupa import LuaRuntime,LuaError
from test_voices_020 import Voice020
R=Path(__file__).resolve().parents[1]
TEXT=(R/'source/scar/korea/diagnostics_024.scar').read_text()
NAMES=re.findall(r'"(Korea\w+)"',TEXT.split('local names={')[1].split('for _,name')[0])
def install(lua):
 for name in NAMES:
  if lua.globals()[name] is None:lua.execute('function '+name+'(...) return ... end')
 lua.execute(TEXT)

class Diagnostics024(unittest.TestCase):
 def engine(self):
  lua=LuaRuntime(unpack_returned_tuples=True)
  lua.execute('now=402;logs={};function World_GetGameTime() return now end;function print(s) logs[#logs+1]=s end')
  return lua
 def test_return_nil_holes_and_nested_order_are_preserved(self):
  lua=self.engine();lua.execute('function KoreaUI_Update(...) return ... end;function KoreaUI_Toggle(...) return KoreaUI_Update(...) end');install(lua)
  self.assertEqual(lua.eval('KoreaUI_Toggle')(1,None,3),(1,None,3))
  self.assertEqual(lua.eval('#KoreaDiag024State.stack'),0)
  logs='\n'.join(lua.globals().logs.values());self.assertEqual(logs.count('kind=ENTER'),2);self.assertEqual(logs.count('kind=EXIT'),2);self.assertIn('t=402.000',logs)
 def test_error_propagates_and_retains_last_entered_frame(self):
  lua=self.engine();lua.execute('function KoreaUI_Update() error("actual fault") end');install(lua)
  with self.assertRaisesRegex(LuaError,'actual fault'):lua.globals().KoreaUI_Update()
  logs='\n'.join(lua.globals().logs.values());self.assertIn('kind=ENTER',logs);self.assertNotIn('kind=EXIT',logs);self.assertEqual(lua.eval('#KoreaDiag024State.stack'),1)
 def test_trace_is_capped_and_does_not_dereference_native_data(self):
  lua=self.engine();install(lua);lua.execute('KoreaDiag024State.maxLines=3;bad=setmetatable({},{__tostring=function() error("unsafe tostring") end});for i=1,10 do KoreaDiag024_Mark("test",bad) end')
  self.assertEqual(lua.globals().KoreaDiag024State.lines,3);self.assertTrue(lua.globals().KoreaDiag024State.limited)
  logs='\n'.join(lua.globals().logs.values());self.assertEqual(logs.count('TRACE_LIMIT'),1);self.assertIn('detail=<table>',logs)
 def test_twenty_minute_limit_and_repeated_install_are_bounded(self):
  lua=self.engine();install(lua);count=len(lua.globals().logs);lua.globals().KoreaDiag024_Install();self.assertEqual(len(lua.globals().logs),count)
  lua.execute('now=1201;KoreaUI_Toggle();assert(KoreaDiag024State.limited)')
  self.assertEqual(lua.eval('#KoreaDiag024State.stack'),0)
 def transform_engine(self,fail=False):
  lua=self.engine();lua.execute('''
   order={};unit={bp="unit_horseman_2_ayy",health=.5};squad={};player={id=1}
   function Korea_Alive(e) return e==unit end
   function Korea_BP(c,n) return n end
   function Entity_GetBlueprint(e) return e.bp end
   function Entity_GetHealthPercentage(e) return e.health end
   function Entity_GetSquad(e) return squad end
   function Entity_ConvertBlueprint(e,bp) order[#order+1]="entity";e.bp=bp;if fail then error("native conversion fault") end end
   function Squad_ConvertBlueprint(s,bp) order[#order+1]="squad";s.bp=bp end
   function Entity_SetHealth(e,h) order[#order+1]="health";e.health=h end
  ''');lua.globals().fail=fail;lua.execute((R/'source/scar/korea/effects.scar').read_text());install(lua);return lua
 def test_actual_hwarang_conversion_keeps_native_order_and_health(self):
  lua=self.transform_engine();lua.execute('KoreaEffects_Transform({executer=unit},player,true);KoreaEffects_Transform({executer=unit},player,false)')
  self.assertEqual(list(lua.globals().order.values()),['entity','squad','health']*2);self.assertEqual(lua.globals().unit.health,.5)
  logs='\n'.join(lua.globals().logs.values());self.assertEqual(logs.count('transform.entity_convert.before'),2);self.assertEqual(logs.count('transform.set_health.after'),2)
 def test_injected_conversion_fault_reports_exact_native_boundary(self):
  lua=self.transform_engine(True)
  with self.assertRaisesRegex(LuaError,'native conversion fault'):lua.execute('KoreaEffects_Transform({executer=unit},player,true)')
  logs='\n'.join(lua.globals().logs.values());self.assertIn('transform.entity_convert.before',logs);self.assertNotIn('transform.entity_convert.after',logs);self.assertNotIn('kind=EXIT',logs)

class VoiceDiagnostics024(Voice020):
 def test_actual_voice_callbacks_at_402_seconds_use_paired_registered_identity(self):
  self.g.KoreaVoice_Stop();self.lua.execute('logs={};function print(s) logs[#logs+1]=s end;registered={};function Rule_AddSquadEvent(f,s,e,r) registered[e]=f end;function Rule_RemoveSquadEvent(f,s) assert(f==registered[1] or f==registered[2]) end')
  install(self.lua);self.lua.execute('now=402;KoreaVoice_Start({[1]="korea"});KoreaVoice_Tick();KoreaVoice_Stop()')
  logs='\n'.join(self.g.logs.values());self.assertIn('t=402.000',logs);self.assertIn('site=KoreaVoice_Tick',logs);self.assertIn('voice.selection.after',logs);self.assertEqual(self.lua.eval('#KoreaDiag024State.stack'),0)

def load_tests(loader,tests,pattern):
 return unittest.TestSuite([loader.loadTestsFromTestCase(Diagnostics024),VoiceDiagnostics024('test_actual_voice_callbacks_at_402_seconds_use_paired_registered_identity')])
if __name__=='__main__':unittest.main()
