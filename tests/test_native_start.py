"""Execute actual standalone entry scripts against a stubbed engine boundary.

Checks new direct-start enrollment/lifecycle behavior; not native gameplay proof.
"""
import json,unittest
from pathlib import Path
from lupa import LuaRuntime
ROOT=Path(__file__).resolve().parents[1]
CONFIG=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
CIV=CONFIG['race'];TITLE=CIV.title();MODULE=TITLE+'Independent'

def native_starters():
    data=json.loads(next((ROOT/'source/tables/attrib/army').rglob('*.json')).read_text(encoding='utf-8'))
    def child(nodes,key):return next(n for n in nodes if n['key']==key)['value']
    army=child(child(data['nodes'],'default'),'army_bag')
    units=[child(n['value'],'$PBGNAME') for n in child(army,'starting_units')]
    record=child(army,'starting_buildings')[0]['value']
    building=child(child(record,'building'),'$PBGNAME')
    return building,units

class DirectNativeStart(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute('''
          calls={groups=0,destroyed=0,starts=0,stops=0,voice=0,presentation=0}
          player={id={race=""},index=1,isHuman=true}; PLAYERS={player};KoreaState={ending=false}
          function import() end
          function Core_RegisterModule() end
          function print() end
          function Player_GetRaceName(p) return p.race end
          function Player_IsAlive() return not defeated end
          function Player_HasUpgrade() return advanced_age == true end
          function BP_GetUpgradeBlueprint(n) return n end
          function BP_GetEntityBlueprint(n) return n end
          function BP_GetSquadBlueprint(n) return n end
          function BP_GetAbilityBlueprint(n) return n end
          function BP_GetName(n) return n:match("[^:]+$") end
          function EGroup_CreateUnique() calls.groups=calls.groups+1;return {} end
          function Player_GetEntitiesEGroup(p,g) if not missing_capital then g[1]=capital end end
          function EGroup_CountSpawned(g) return #g end
          function EGroup_GetSpawnedEntityAt(g,i) return g[i] end
          function EGroup_Destroy() calls.destroyed=calls.destroyed+1 end
          function Entity_GetBlueprint(e) return e end
          function Player_GetSquads() return squads end
          function SGroup_CountSpawned(g) return #g end
          function SGroup_GetSpawnedSquadAt(g,i) return g[i] end
          function Squad_GetBlueprint(s) return s end
          function Squad_GetFirstEntity(s) return s end
          function Entity_SetStateModelBool() end
          function Entity_HasAbility() return true end
          function Entity_AddAbility() end
          function Rule_AddInterval() end
          function Rule_Remove() end
          function Player_AddResource() error("duplicate resource grant") end
          function Player_SetResource() error("duplicate resource write") end
          function Entity_ConvertBlueprint() error("legacy conversion") end
          function Squad_ConvertBlueprint() error("legacy conversion") end
          function Squad_CreateAndSpawnToward() error("duplicate starting spawn") end
          function SGroup_Destroy() error("borrowed engine group destroyed") end
        ''')
        g=self.lua.globals();capital,units=native_starters();g.capital=capital;g.squads=self.lua.table_from(units)
        g.player.id.race=CONFIG['owner'].replace('-','')+':'+CIV
        self.lua.execute((ROOT/'source/scar'/CIV/'initialization.scar').read_text(encoding='utf-8'))
        self.lua.execute(f'''function {TITLE}Lifecycle_Start(map) if map[1]=="{CIV}" then calls.starts=calls.starts+1 end end
          function {TITLE}Lifecycle_Cleanup() calls.stops=calls.stops+1;KoreaState.ending=true end
          function VietnamPresentation_Start() calls.presentation=calls.presentation+1 end
          function VietnamPresentation_Cleanup() end
          function VietnamPresentation_Restore() end
          function VietnamPresentation_Update() end
          function VietnamPresentation_UpdateCounter() end
          function VietnamVoice_Start() calls.voice=calls.voice+1 end
          function VietnamVoice_Stop() end
          function VietnamPaddyWood_RestoreUI() end''')
        self.lua.execute((ROOT/'source/scar/garrison'/CIV/'dispatcher.scar').read_text(encoding='utf-8'))
        g[MODULE+'_OnGameSetup']()
    def test_direct_start_and_duplicate_start(self):
        g=self.lua.globals();g[MODULE+'_Start']();g[MODULE+'_Start']()
        self.assertEqual(g.calls.starts,1);self.assertEqual(g.calls.groups,g.calls.destroyed)
    def test_foreign_race_is_not_enrolled(self):
        g=self.lua.globals();g.player.id.race='chinese';g[MODULE+'_Start']();self.assertEqual(g.calls.starts,0)
        self.assertEqual(g.calls.voice,0);self.assertEqual(g.calls.presentation,0)
    def test_ai_retains_excluded_scope(self):
        g=self.lua.globals();g.player.isHuman=False;g[MODULE+'_Start']();self.assertEqual(g.calls.starts,0)
        self.assertEqual(g.calls.voice,0);self.assertEqual(g.calls.presentation,0)
    def test_unsupported_start_is_rejected_without_partial_grant(self):
        g=self.lua.globals();g.missing_capital=True;g[MODULE+'_Start']();self.assertEqual(g.calls.starts,0);self.assertEqual(g.calls.groups,g.calls.destroyed)
    def test_later_age_is_rejected(self):
        g=self.lua.globals();g.advanced_age=True;g[MODULE+'_Start']();self.assertEqual(g.calls.starts,0)
    def test_cleanup_once_and_second_match(self):
        g=self.lua.globals();g[MODULE+'_Start']();g[MODULE+'_OnGameOver']();g[MODULE+'_OnGameOver']()
        self.assertEqual(g.calls.stops,1)
        g[MODULE+'_OnGameSetup']();self.assertFalse(g.KoreaState.ending if CIV=='korea' else False)
        g[MODULE+'_Start']();self.assertEqual(g.calls.starts,2)
if __name__=='__main__':unittest.main()
