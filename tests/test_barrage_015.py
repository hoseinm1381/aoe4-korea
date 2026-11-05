"""Execute the real barrage script against an explicit stub engine boundary."""
import unittest
from pathlib import Path
from lupa import LuaRuntime, LuaError
R=Path(__file__).resolve().parents[1]
ENGINE="""
now=0; calls={applied=0,removed=0,stops=0,groups=0,destroyed=0,attacks=0}
player={id=1}; unit={id=11,owner=1,alive=true,command=17,squad={active=true,moving=false,accepted=false}}
KoreaState={debuffs={},barrages={}}
MAT_Weapon=1;MUT_Multiplication=2;CMD_AttackForced=17;CMD_Stop=18;SCMD_Attack=27;SCMD_Stop=28
function Korea_Alive(e) return e~=nil and e.alive end
function Korea_Entity(id) if id==unit.id then return unit end end
function Entity_GetPlayerOwner(e) return e.owner end
function Entity_GetID(e) return e.id end
function Entity_GetSquad(e) return e.squad end
function Entity_GetActiveCommand(e)
    if e.command == nil then error('Entity does not have an active state') end
    return e.command
end
function Entity_ActiveCommandIs(e, command) return e.command == command end
function Korea_Functioning(e) return e.alive and not e.ruined end
function Korea_BP(kind,name) return name end
function World_GetGameTime() return now end
function Modifier_Create(...) return {} end
function Modifier_ApplyToEntity(...) calls.applied=calls.applied+1;return calls.applied end
function Korea_RemoveModifier(h) calls.removed=calls.removed+1 end
function SGroup_CreateUnique() calls.groups=calls.groups+1;return {} end
EGroup_CreateUnique=SGroup_CreateUnique
function SGroup_Add(g,e) g[1]=e end
EGroup_Add=SGroup_Add
function SGroup_Destroy(g) calls.destroyed=calls.destroyed+1 end
EGroup_Destroy=SGroup_Destroy
function LocalCommand_SquadPos(...) calls.attacks=calls.attacks+1 end
LocalCommand_EntityPos=LocalCommand_SquadPos
function LocalCommand_Squad(...) calls.stops=calls.stops+1 end
LocalCommand_Entity=LocalCommand_Squad
function Squad_HasActiveCommand(s) return s.active end
function Squad_IsMoving(s) return s.moving end
function Squad_HasAcceptedCommands(s) return s.accepted end
"""
class Barrage015(unittest.TestCase):
    def engine(self,old=False,keep=False):
        lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(ENGINE)
        p=R/('tests/fixtures/art015-before/effects.scar' if old else 'source/scar/korea/effects.scar')
        lua.execute(p.read_text('utf-8'))
        lua.execute('KoreaEffects_Barrage({executer=unit,target={x=1,y=0,z=2}},player,'+str(keep).lower()+')')
        return lua
    def test_actual_old_fixture_reproduces_reported_nil_call(self):
        lua=self.engine(old=True)
        with self.assertRaisesRegex(LuaError,'Squad_GetActiveCommand'):
            lua.execute('now=7;KoreaEffects_Timers(now)')
    def test_completion_stops_once_removes_modifiers_and_destroys_groups(self):
        lua=self.engine();lua.execute('now=7;KoreaEffects_Timers(now);KoreaEffects_Timers(now)')
        c=lua.globals().calls
        self.assertEqual((c.stops,c.applied,c.removed,c.groups,c.destroyed),(1,2,2,2,2))
        self.assertTrue(lua.eval('next(KoreaState.barrages)==nil'))
    def test_move_newly_accepted_order_and_stop_are_respected(self):
        for interruption in ['unit.squad.moving=true','unit.squad.accepted=true','unit.squad.active=false']:
            lua=self.engine();lua.execute(interruption+';now=7;KoreaEffects_Timers(now)')
            c=lua.globals().calls;self.assertEqual(c.stops,0);self.assertEqual(c.removed,2)
    def test_death_and_capture_cleanup_without_old_owner_command(self):
        for loss in ['unit.alive=false','unit.owner=2']:
            lua=self.engine();lua.execute(loss+';now=2;KoreaEffects_Timers(now)')
            c=lua.globals().calls;self.assertEqual(c.stops,0);self.assertEqual(c.removed,2)
            self.assertTrue(lua.eval('next(KoreaState.barrages)==nil'))
    def test_repeated_barrage_and_keep_branch_remain_operable(self):
        lua=self.engine();lua.execute('now=7;KoreaEffects_Timers(now);now=8;KoreaEffects_Barrage({executer=unit,target={x=1}},player,false);now=15;KoreaEffects_Timers(now)')
        self.assertEqual(lua.globals().calls.stops,2);self.assertEqual(lua.globals().calls.removed,4)
        lua=self.engine(keep=True);lua.execute('now=6;KoreaEffects_Timers(now);now=7;KoreaEffects_Timers(now)')
        self.assertEqual(lua.globals().calls.stops,1);self.assertEqual(lua.globals().calls.removed,2)
    def test_keep_cleanup_after_native_active_state_ended(self):
        lua=self.engine(keep=True)
        lua.execute('unit.command=nil;now=6;KoreaEffects_Timers(now);now=7;KoreaEffects_Timers(now)')
        c=lua.globals().calls
        self.assertEqual((c.stops,c.removed,c.groups,c.destroyed),(0,2,1,1))
        self.assertTrue(lua.eval('next(KoreaState.barrages)==nil'))
if __name__=='__main__':unittest.main()
