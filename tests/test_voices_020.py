"""Exercise the actual Korean voice controller through a Lua engine boundary.
These are presentation contracts, not an audible native-game test.
"""
from pathlib import Path
import unittest
from lupa import LuaRuntime
R=Path(__file__).resolve().parents[1]
class Voice020(unittest.TestCase):
 def setUp(self):
  self.lua=LuaRuntime(unpack_returned_tuples=True);self.g=self.lua.globals()
  self.lua.execute('''
  function import() end
  now=0; age=1; clips={}; removed=0; destroyed=0
  player={id=1}; other={id=2};PLAYERS={{id=player,index=1}}
  actor={id=10,bp="748d61b94d3e4cf3a506a9ac1f992d1d:voice_test",owner=player,alive=true,female=false,hp=100,resource="",moving=false}
  actors={[10]=actor};squads={actor};selected={actor}
  function World_GetGameTime() return now end
  function Game_GetLocalPlayer() return player end
  function Player_GetID(p) return p.id end
  function Player_HasUpgrade(p,bp) return (bp=="feudal_age" and age>=2) or (bp=="castle_age" and age>=3) or (bp=="imperial_age" and age>=4) end
  function BP_GetUpgradeBlueprint(n) return n end
  function BP_GetName(n) return n end
  function Squad_IsValid(id) return actors[id]~=nil end
  function Squad_FromID(id) return actors[id] end
  function Squad_IsAlive(s) return s.alive end
  function World_OwnsSquad() return false end
  function Squad_GetPlayerOwner(s) if not s.alive then error("dead owner dereference") end;return s.owner end
  function Squad_GetBlueprint(s) return s.bp end
  function Squad_GetID(s) return s.id end
  function Squad_IsFemale(s) return s.female end
  function Squad_GetPosition() return {x=0,z=0} end
  function Squad_GetHealth(s) return s.hp end
  function Camera_GetCurrentTargetPos() return {x=0,z=0} end
  function Player_GetSquads() return squads end
  function SGroup_CreateUnique() return {owned=true} end
  function SGroup_CountSpawned(g) return #g end
  function SGroup_GetSpawnedSquadAt(g,i) return g[i] end
  function Misc_GetSelectedSquads(g) for i=#g,1,-1 do g[i]=nil end;for i,s in ipairs(selected) do g[i]=s end end
  function SGroup_Destroy(g) assert(g.owned,"borrowed group destroyed");destroyed=destroyed+1 end
  function Rule_AddSquadEvent() end
  function Rule_RemoveSquadEvent() removed=removed+1 end
  function Rule_AddInterval() end
  function Rule_Remove() end
  function Rule_AddGlobalEvent() end
  function Rule_RemoveGlobalEvent() end
  function Squad_IsConstructing() return false end
  function Squad_IsGatheringResourceType(s,t) return s.resource==t end
  function Squad_IsAttacking() return false end
  function Squad_IsMoving(s) return s.moving end
  RT_Wood="wood";RT_Gold="gold";RT_Stone="stone";RT_Food="food"
  SCMD_Move=1;SCMD_Patrol=2;SCMD_Attack=3;SCMD_StationaryAttack=4;SCMD_AttackMove=5;SCMD_Stop=6;SCMD_HoldPosition=7;SCMD_BuildStructure=8;SCMD_Gather=9;SCMD_Trade=10;SCMD_Load=11;SCMD_Unload=12;SCMD_Retreat=13;SCMD_DefaultAction=14;SCMD_Ability=15;SCMD_BuildSquad=16;SCMD_InstantLoad=17;SCMD_UnloadSquads=18
  GE_SquadCommandIssued=1;GE_SquadKilled=2;GE_LocalPlayerChanged=3
  Garrison={audio={forMod=function(key) assert(key=="korea");return {
    play=function(path) clips[#clips+1]=path;return true end,
    pulse=function() end, session=function() end,stop=function() end} end}}
  local function ageBank(prefix)
   local events={};local ack={{prefix.."ack1",.5},{prefix.."ack2",.5}}
   for _,e in ipairs({"select","move","attack","wood","food","build"}) do events[e]={{prefix..e,.5}} end
   events.stop=ack;events.hold=ack;events.unload=ack;events.garrison=ack;events.acknowledge=ack;return events
  end
  KoreaVoiceBank={complete=true,units={[actor.bp]={role="VILLAGER_M",female_role="VILLAGER_F",private=true,stock_speaker="male",stock_female_speaker="female"}},clips={},stock_efforts={male={death={{"death",.5}},pain_light={{"pain",.2}},pain_heavy={{"pain",.2}}}}}
  for _,role in ipairs({"VILLAGER_M","VILLAGER_F"}) do
   KoreaVoiceBank.clips[role]={};for a=1,4 do KoreaVoiceBank.clips[role]["A"..a]=ageBank(role.."A"..a) end
  end
  ''')
  path=R/'source/scar/korea/voices_020.scar'
  if not path.exists():path=R/'output/voices020/scar/korea/voices_020.scar'
  self.lua.execute(path.read_text(encoding='utf-8'));self.g.KoreaVoice_Start(self.lua.table_from({1:'korea'}));self.g.KoreaVoice_Tick()
 def command(self,c):self.g.KoreaVoice_OnCommand(self.lua.table_from({'squad':self.g.actor,'player':self.g.player,'command':c}),self.g.KoreaVoiceState.actors[10])
 def test_local_selection_and_female_mapping(self):
  self.assertEqual(self.g.clips[1],'VILLAGER_MA1select');self.g.actor.female=True;self.g.now=20;self.g.KoreaVoice_Tick();self.assertEqual(self.g.KoreaVoiceState.actors[10].role,'VILLAGER_F')
 def test_age_refresh_at_playback(self):
  self.g.age=4;self.g.now=20;self.command(self.g.SCMD_Move);self.assertEqual(self.g.clips[2],'VILLAGER_MA4move')
 def test_aliases_do_not_repeat_same_clip(self):
  self.g.now=20;self.command(self.g.SCMD_Stop);self.g.now=40;self.command(self.g.SCMD_HoldPosition);self.assertEqual(self.g.clips[2],'VILLAGER_MA1ack1');self.assertEqual(self.g.clips[3],'VILLAGER_MA1ack2')
 def test_gather_waits_for_actual_resource(self):
  self.g.now=20;before=len(self.g.clips);self.command(self.g.SCMD_Gather);self.assertEqual(len(self.g.clips),before);self.g.actor.resource='wood';self.g.KoreaVoice_Tick();self.assertEqual(self.g.clips[len(self.g.clips)],'VILLAGER_MA1wood')
 def test_foreign_owner_not_tracked(self):
  self.g.actor.owner=self.g.other;self.g.now=20;self.g.KoreaVoice_Tick();self.assertIsNone(self.g.KoreaVoiceState.actors[10])
 def test_death_does_not_dereference_dead_owner(self):
  record=self.g.KoreaVoiceState.actors[10];self.g.actor.alive=False;self.g.actors[10]=None;self.g.now=20;self.g.KoreaVoice_OnKilled(self.lua.table(),record);self.assertEqual(self.g.clips[len(self.g.clips)],'death')
 def test_stop_destroys_only_owned_group_and_can_restart(self):
  self.g.KoreaVoice_Stop();self.g.KoreaVoice_Stop();self.assertEqual(self.g.destroyed,1);self.assertFalse(self.g.KoreaVoiceState.running);self.g.KoreaVoice_Start(self.lua.table());self.assertTrue(self.g.KoreaVoiceState.running)
 def test_each_task_has_its_own_five_second_cooldown(self):
  self.g.now=1
  self.command(self.g.SCMD_Move)
  self.g.now=2
  self.command(self.g.SCMD_Attack)
  self.assertEqual(self.g.clips[3], 'VILLAGER_MA1attack')
  self.g.now=5.99
  self.command(self.g.SCMD_Move)
  self.assertEqual(len(self.g.clips), 3)
  self.g.now=6
  self.command(self.g.SCMD_Move)
  self.assertEqual(self.g.clips[4], 'VILLAGER_MA1move')

 def test_build_replies_after_active_movement_line_without_echo(self):
  self.g.now=1
  self.command(self.g.SCMD_Move)
  self.g.now=1.1
  self.command(self.g.SCMD_BuildStructure)
  self.assertEqual(len(self.g.clips), 2)
  self.g.now=1.75
  self.g.KoreaVoice_Tick()
  self.assertEqual(self.g.clips[3], 'VILLAGER_MA1build')
  self.lua.execute('function Squad_IsConstructing(s) return s.building==true end')
  self.g.actor.building=True
  self.g.now=8
  self.g.KoreaVoice_Tick()
  self.assertEqual(len(self.g.clips), 3)

 def test_latest_order_replaces_pending_reply(self):
  self.g.now=0.1
  self.command(self.g.SCMD_Move)
  self.g.now=0.2
  self.command(self.g.SCMD_Attack)
  self.g.now=0.75
  self.g.KoreaVoice_Tick()
  self.assertEqual(self.g.clips[2], 'VILLAGER_MA1attack')
  self.g.now=2
  self.g.KoreaVoice_Tick()
  self.assertEqual(len(self.g.clips), 2)

 def test_deselection_drops_pending_reply(self):
  self.g.now=0.1
  self.command(self.g.SCMD_Move)
  self.g.selected=self.lua.table()
  self.g.now=0.25
  self.g.KoreaVoice_Tick()
  self.g.now=1
  self.g.KoreaVoice_Tick()
  self.assertEqual(len(self.g.clips), 1)
 def test_unarmed_mixed_attack_order_uses_neutral_reply(self):
  self.lua.execute('KoreaVoiceBank.clips.SCHOLAR=KoreaVoiceBank.clips.VILLAGER_M;KoreaVoiceBank.units[actor.bp].role="SCHOLAR"')
  self.g.now=20;self.g.KoreaVoice_Tick();self.command(self.g.SCMD_AttackMove);self.assertEqual(self.g.clips[len(self.g.clips)],'VILLAGER_MA1ack1')
 def test_siege_build_command_and_unload_all(self):
  self.g.now=20;self.command(self.g.SCMD_BuildSquad);self.assertEqual(self.g.clips[len(self.g.clips)],'VILLAGER_MA1build');self.g.now=40;self.command(self.g.SCMD_UnloadSquads);self.assertEqual(self.g.clips[len(self.g.clips)],'VILLAGER_MA1ack1')
 def test_unknown_command_is_quiet(self):
  count=len(self.g.clips);self.g.now=20;self.g.KoreaVoice_OnCommand(self.lua.table_from({'squad':self.g.actor,'player':self.g.player}),self.g.KoreaVoiceState.actors[10]);self.assertEqual(len(self.g.clips),count)
 def test_incomplete_bank_cannot_start(self):
  self.g.KoreaVoice_Stop();self.g.KoreaVoiceBank.complete=False;self.g.KoreaVoice_Start(self.lua.table());self.assertFalse(self.g.KoreaVoiceState.running)
if __name__=='__main__':unittest.main()
