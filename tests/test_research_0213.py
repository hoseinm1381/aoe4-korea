import json,re,unittest
from pathlib import Path
from lupa import LuaRuntime
root=Path.cwd()
scar=root/'source/scar/korea'
engine=r'''
RT_Food=1;RT_Wood=2;RT_Gold=3;RT_Stone=4;RT_Merc_Byz=5;RT_Action=6
MAT_Upgrade=1;MUT_Multiplication=1;ITEM_REMOVED=0;ITEM_DEFAULT=1;PITEM_Upgrade=1
now=1; oil=400; completed=false; accept=true; queued=0
ability='paid';upgrade='upgrade'; availability={}
actor={id=22};player={id=1,observatoryActive=false}
KoreaState={order={1},players={player}}
KoreaResearchCatalog={{ability=ability,upgrade=upgrade,foreign=true,costs={merc_byz=150,action=1}}}
function BP_GetName(x) return x end
BP_GetAbilityBlueprint=BP_GetName
function Korea_BP(k,v) return v end
function Korea_Alive(e) return e ~= nil end
function Entity_GetID(e) return e.id end
function Player_SetAbilityAvailability(p,a,state) availability[a]=state end
Player_SetUpgradeAvailability=Player_SetAbilityAvailability
function Korea_PlayerModifier(...) end
function Player_GetAbilityBPCost(...) return {merc_byz=0} end
function Player_AddResource(p,r,v) if r==RT_Merc_Byz then oil=oil+v end end
function Player_SetResource(p,r,v) if r==RT_Merc_Byz then oil=v end end
function Player_HasUpgrade(p,u) return completed end
function Entity_QueueProductionItemByPBG(...) queued=queued+1;return accept end
function Table_GetRandomItem(l) return l[1] end
function World_GetGameTime() return now end
function Korea_EventPlayer(c) return player end
function KoreaLandmarks_Snapshot(p) end
function KoreaEffects_Upgrade(...) end
function KoreaLandmarks_Research(...) end
ctx={executer=actor,ability=ability,upgrade=upgrade}
function cast()
    if oil<150 then return false end
    oil=oil-150
    return KoreaResearch_Ability(ctx,player)
end
'''
class Research(unittest.TestCase):
    def lua(self):
        lua=LuaRuntime(unpack_returned_tuples=True)
        lua.execute(engine)
        for script in ('research_core.scar','research.scar'):
            lua.execute((scar/script).read_text(encoding='utf-8'))
        lua.execute('KoreaResearch_Init(player)')
        return lua

    def test_instant_cancel_then_complete_keeps_charge(self):
        lua=self.lua()
        lua.execute('cast();KoreaResearch_Canceled(ctx);KoreaResearch_Tick(player,now);completed=true;KoreaResearch_Completed(ctx);now=2;KoreaResearch_Tick(player,now)')
        self.assertEqual(lua.eval('oil'),250)
        self.assertEqual(lua.eval('player.research.allowances'),1)

    def test_cancel_retry_and_single_refund(self):
        lua=self.lua()
        lua.execute('cast();KoreaResearch_Canceled(ctx);KoreaResearch_EntityLost(actor.id);KoreaResearch_Tick(player,now)')
        self.assertEqual(lua.eval('oil'),250)
        lua.execute('now=2;KoreaResearch_Tick(player,now);KoreaResearch_Tick(player,now)')
        self.assertEqual(lua.eval('oil'),400)
        self.assertEqual(lua.eval('availability[upgrade]'),0)
        self.assertEqual(lua.eval('availability[ability]'),1)
        self.assertEqual(lua.eval('player.research.allowances'),2)
        lua.execute('cast()')
        self.assertEqual(lua.eval('oil'),250)
        self.assertEqual(lua.eval('queued'),2)

    def test_completion_first_refunds_only_observatory_rebate(self):
        lua=self.lua()
        lua.execute('player.observatoryActive=true;cast();completed=true;KoreaResearch_Completed(ctx);KoreaResearch_Canceled(ctx);now=2;KoreaResearch_Tick(player,now)')
        self.assertEqual(lua.eval('oil'),272.5)

    def test_rejected_queue_and_insufficient_literature(self):
        lua=self.lua()
        lua.execute('accept=false;cast()')
        self.assertEqual(lua.eval('oil'),400)
        self.assertEqual(lua.eval('player.research.allowances'),2)
        lua.execute('oil=149;accept=true;cast()')
        self.assertEqual(lua.eval('oil'),149)
        self.assertEqual(lua.eval('queued'),1)

    def test_all_ability_prices_match_visible_tooltips(self):
        catalog=(scar/'catalog.scar').read_text(encoding='utf-8')
        matches=re.findall(r'\["ability"\]="[^"]+:([^"]+)",\["costs"\]=\{[^}]+?\["merc_byz"\]=([0-9.]+)\}',catalog)
        self.assertEqual(len(matches),91)
        strings=json.loads((root/'source/locale/en.json').read_text(encoding='utf-8'))
        def node(nodes,key):
            return next(n['value'] for n in nodes if n['key']==key)
        count=0
        for name,price in matches:
            price=int(float(price))
            p=root/'source/tables/attrib/abilities/korea'/f'{name}.rgd.json'
            for variant in json.loads(p.read_text())['nodes']:
                if not isinstance(variant['value'],list):
                    continue
                bag=node(variant['value'],'ability_bag')
                self.assertEqual(node(node(bag,'cost_to_player'),'merc_byz'),price)
                ui=node(bag,'ui_info')
                self.assertEqual(node(ui,'tooltip_data_template'),'BuildingUpgradeDataTemplate')
                if variant['key']=='default':
                    self.assertTrue(any(strings.get(id,'').startswith(f'Cost: {price:,} Literature') for id in re.findall(r'\$[a-f0-9]+:(\d+)',json.dumps(ui))),name)
                count+=1
        self.assertEqual(count,195)

if __name__=='__main__':
    unittest.main()

