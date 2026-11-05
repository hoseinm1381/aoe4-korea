"""Stress actual voice lifecycle at a strict mock engine boundary, not native proof."""
import unittest
from test_voices_020 import Voice020

class Safety023(Voice020):
 def test_two_hundred_actors_age_change_and_roster_retirement(self):
  self.lua.execute('''
   squads={};actors={};selected={}
   for i=1,200 do
    local s={id=100+i,bp=actor.bp,owner=player,alive=true,female=false,hp=100,resource="",moving=false}
    squads[i]=s;actors[s.id]=s
   end
   selected={squads[1]};now=20;age=2;KoreaVoice_Tick()
   local n=0;for _ in pairs(KoreaVoiceState.actors) do n=n+1 end;assert(n==200)
   age=4;now=40;KoreaVoice_OnCommand({squad=squads[1],player=player,command=SCMD_Move},KoreaVoiceState.actors[101])
  ''')
  self.assertEqual(self.g.clips[len(self.g.clips)],'VILLAGER_MA4move')
  self.lua.execute('squads={};selected={};now=60;KoreaVoice_Tick();assert(next(KoreaVoiceState.actors)==nil)')
  # The original destroyed ID is absent from the world, so its engine-owned
  # callbacks cannot be removed through an invalid handle. Each of the 200
  # still-valid retired actors unregisters exactly its two callbacks.
  self.assertEqual(self.g.removed,400)

 def test_recycled_squad_id_rejects_delayed_old_kill_callback(self):
  self.lua.execute('''
   oldRecord=KoreaVoiceState.actors[10]
   actor.alive=false
   replacement={id=10,bp=actor.bp,owner=player,alive=true,female=false,hp=100,resource="",moving=false}
   actors[10]=replacement;squads={replacement};selected={replacement};now=20
   KoreaVoice_Tick();before=#clips
   KoreaVoice_OnKilled({},oldRecord)
   assert(#clips==before and KoreaVoiceState.actors[10].squad==replacement)
  ''')

 def test_world_or_destroyed_roster_actor_has_no_owner_dereference(self):
  self.lua.execute('''
   function World_OwnsSquad(s) return s.world==true end
   function Squad_GetPlayerOwner(s) assert(not s.world and s.alive,"invalid owner dereference");return s.owner end
   actor.world=true;now=20;KoreaVoice_Tick();assert(KoreaVoiceState.actors[10]==nil)
   actor.world=false;actor.alive=false;now=22;KoreaVoice_Tick();assert(KoreaVoiceState.actors[10]==nil)
  ''')

 def test_duplicate_start_keeps_single_interval_and_balanced_stop(self):
  self.g.KoreaVoice_Stop()
  self.lua.execute('''
   activeRules={};eventRules={}
   function Rule_AddInterval(f,t) assert(not activeRules[f],"duplicate rule");activeRules[f]=t end
   function Rule_Remove(f) activeRules[f]=nil end
   function Rule_AddGlobalEvent(f,e) assert(not eventRules[f],"duplicate event");eventRules[f]=e end
   function Rule_RemoveGlobalEvent(f) eventRules[f]=nil end
   KoreaVoice_Start({[1]="korea"});KoreaVoice_Start({[1]="korea"})
   assert(activeRules[KoreaVoice_Tick]==.25)
   KoreaVoice_Stop();KoreaVoice_Stop();assert(next(activeRules)==nil and next(eventRules)==nil)
  ''')

def load_tests(loader,tests,pattern):
 names=[n for n in Safety023.__dict__ if n.startswith('test_')]
 return unittest.TestSuite(Safety023(n) for n in names)
if __name__=='__main__':unittest.main()
