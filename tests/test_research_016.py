"""Execute maintained research against explicit native-payment stubs; no build."""
import unittest,json,gzip,hashlib,re,sys
from pathlib import Path
from lupa import LuaRuntime
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from runtime import *
D=R/'docs/update_016_research'
BEFORE=json.loads(gzip.decompress((D/'before-source.json.gz').read_bytes()))
CHANGES=read_json(D/'changes.json')
ENGINE='''
RT_Food=1;RT_Wood=2;RT_Gold=3;RT_Stone=4;RT_Merc_Byz=5;RT_Action=6
MAT_Upgrade=7;MUT_Multiplication=8;ITEM_REMOVED=9;ITEM_DEFAULT=10;PITEM_Upgrade=11
bank={[1]=10000,[2]=10000,[3]=10000,[4]=10000,[5]=10000,[6]=2}
enums={food=1,wood=2,gold=3,stone=4,merc_byz=5,action=6}
actor={id=23,alive=true};player={id=1};KoreaState={order={1},players={player}}
modifiers={};availability={};completed={};queues=0;queueOK=true;commonOnly=false
function BP_GetName(bp) return string.match(bp,':(.+)$') or bp end
function BP_GetAbilityBlueprint(name) return name end
function Korea_BP(kind,name) return name end
function Korea_Alive(e) return e~=nil and e.alive end
function Entity_GetID(e) return e.id end
function Player_AddResource(p,r,n) bank[r]=bank[r]+n end
function Player_SetResource(p,r,n) bank[r]=n end
function Player_SetAbilityAvailability(p,bp,v) availability[bp]=v end
function Player_SetUpgradeAvailability(...) end
function Player_HasUpgrade(p,bp) return completed[bp] or false end
function Korea_PlayerModifier(p,mat,name,op,n,bp)
 assert(mat==MAT_Upgrade and op==MUT_Multiplication and n==0)
 modifiers[bp]=modifiers[bp] or {};modifiers[bp][name]=n
end
function Table_GetRandomItem(items) return items[1] end
function Player_GetAbilityBPCost(p,bp)
 local out={};for k,v in pairs(KoreaResearchRoutes[BP_GetName(bp)].costs) do
  if not commonOnly or k=='food' or k=='wood' or k=='gold' or k=='stone' then out[k]=v end
 end;return out
end
function Entity_QueueProductionItemByPBG(e,kind,bp)
 assert(kind==PITEM_Upgrade)
 for _,r in ipairs({'food','wood','gold','stone','merc_byz'}) do
  assert(modifiers[bp]['upgrade_cost_'..r..'_modifier']==0)
 end
 queues=queues+1;return queueOK
end
function Execute(name,ignoreAvailability)
 local bp='748d61b94d3e4cf3a506a9ac1f992d1d:'..name
 local route=KoreaResearchRoutes[BP_GetName(bp)]
 if not ignoreAvailability and availability[bp]==ITEM_REMOVED then return false end
 -- This is the stub boundary: native ability charges once before the callback.
 for k,r in pairs(enums) do if bank[r]<(route.costs[k] or 0) then return false end end
 for k,r in pairs(enums) do bank[r]=bank[r]-(route.costs[k] or 0) end
 return KoreaResearch_Ability({ability=bp,executer=actor},player)
end
'''
class Research016(unittest.TestCase):
 def engine(self,old=False):
  lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(ENGINE)
  for name in ['catalog','research_core','research']:
   rel=f'source/scar/korea/{name}.scar'
   lua.execute(BEFORE[rel] if old and rel in BEFORE else (R/rel).read_text('utf-8'))
  lua.execute('KoreaResearch_Init(player)');return lua
 def test_original_missing_custom_fields_loses_literature_refund(self):
  for old,expected in [(True,8500),(False,10000)]:
   lua=self.engine(old);lua.execute("commonOnly=true;Execute('kr_university_biology');KoreaResearch_Settle(player,'upgrade_tech_university_biology',false)")
   self.assertEqual(lua.eval('bank[RT_Merc_Byz]'),expected)
 def test_original_dead_actor_loses_payment_current_refunds(self):
  for old,expected in [(True,8500),(False,10000)]:
   lua=self.engine(old);lua.execute("actor.alive=false;Execute('kr_university_biology')")
   self.assertEqual(lua.eval('bank[RT_Merc_Byz]'),expected);self.assertEqual(lua.eval('queues'),0)
 def test_fee_once_completion_and_observatory_rebate(self):
  for observatory,expected in [(False,8500),(True,8725)]:
   lua=self.engine();lua.execute(f'player.observatoryActive={str(observatory).lower()}')
   lua.execute("Execute('kr_university_biology');KoreaResearch_Settle(player,'upgrade_tech_university_biology',true);KoreaResearch_Settle(player,'upgrade_tech_university_biology',true)")
   self.assertEqual(lua.eval('bank[RT_Merc_Byz]'),expected);self.assertEqual(lua.eval('queues'),1)
 def test_queue_rejection_cancel_and_death_refund_once(self):
  for end in ["queueOK=false;Execute('kr_university_biology')", "Execute('kr_university_biology');KoreaResearch_Settle(player,'upgrade_tech_university_biology',false)","Execute('kr_university_biology');KoreaResearch_EntityLost(23)"]:
   lua=self.engine();lua.execute(end+";KoreaResearch_EntityLost(23);KoreaResearch_Settle(player,'upgrade_tech_university_biology',false)")
   self.assertEqual(lua.eval('bank[RT_Merc_Byz]'),10000)
   self.assertTrue(lua.eval('next(player.research.pending)==nil'))
 def test_native_insufficient_and_duplicate_paid_callbacks(self):
  lua=self.engine();lua.execute("bank[RT_Merc_Byz]=1499;Execute('kr_university_biology')")
  self.assertEqual(lua.eval('bank[RT_Merc_Byz]'),1499);self.assertEqual(lua.eval('queues'),0)
  lua=self.engine();lua.execute("Execute('kr_university_biology');Execute('kr_university_biology',true)")
  self.assertEqual(lua.eval('bank[RT_Merc_Byz]'),8500);self.assertEqual(lua.eval('queues'),1)
 def test_foreign_allowance_consumes_and_restores_once(self):
  lua=self.engine();lua.execute('''
foreign=nil;for _,route in ipairs(KoreaResearchCatalog) do if route.foreign and player.research.offered[route.ability] then foreign=route;break end end
assert(foreign~=nil);before=bank[RT_Merc_Byz];short=BP_GetName(foreign.ability)
Execute(short);assert(player.research.allowances==1 and bank[RT_Action]==1)
assert(bank[RT_Merc_Byz]==before-foreign.costs.merc_byz)
KoreaResearch_Settle(player,foreign.key,false);KoreaResearch_EntityLost(23)
assert(player.research.allowances==2 and bank[RT_Action]==2 and bank[RT_Merc_Byz]==before)
''')
 def test_fallback_catalogue_matches_all_native_variants_and_gold_exception(self):
  lua=self.engine()
  costs={lua.eval('BP_GetName')(row.ability):dict(row.costs.items()) for row in lua.globals().KoreaResearchCatalog.values()}
  for row in CHANGES['variants']:
   name=Path(row['table']).name.removesuffix('.rgd.json')
   self.assertEqual(costs[name],row['costs'],(name,row['variant']))
  lua.execute("Execute('kr_siege_ram_upgrade');assert(bank[RT_Gold]==9300 and bank[RT_Merc_Byz]==10000);KoreaResearch_Settle(player,'upgrade_ram_scaling',false);assert(bank[RT_Gold]==10000)")
 def test_all_research_variants_only_flags_and_presentation_change(self):
  allowed={'ability_bag/validate_actions','ability_bag/ui_info/tooltip_data_template'}
  tables={row['table'] for row in CHANGES['variants']}
  for rel in tables:
   old=rgd.read(import_table(json.loads(BEFORE[rel])));new=rgd.read(import_table(read_json(R/rel)))
   a={p:(n.kind,n.value) for p,n in rgd.flatten(old.nodes) if not isinstance(n.value,list)}
   b={p:(n.kind,n.value) for p,n in rgd.flatten(new.nodes) if not isinstance(n.value,list)}
   self.assertEqual(set(a),set(b))
   for path in a:
    if a[path]!=b[path]:
     relative=path.split('/',1)[1]
     self.assertTrue(relative in allowed or relative.startswith('ability_bag/cost_to_player/'),(rel,path))
     if relative.startswith('ability_bag/cost_to_player/'):
      self.assertNotEqual(path.split('/',1)[0],'default')
      self.assertEqual(b[path],a['default/'+relative],(rel,path))
   # Reverse these leaves; native roundtrip must match the exact original.
   for path in a:
    if a[path]!=b[path]:at(new,path).value=a[path][1]
   self.assertEqual(rgd.write(old),rgd.write(new),rel)
  for row in CHANGES['variants']:
   doc=rgd.read(import_table(read_json(R/row['table'])));bag=at(doc,row['variant']+'/ability_bag')
   self.assertIs(at(bag,'validate_actions').value,False)
   self.assertEqual({n.key:n.value for n in at(bag,'cost_to_player').value},row['costs'])
  self.assertEqual(len(CHANGES['variant_cost_corrections']),104)
 def test_additive_build_omits_only_reviewed_shared_descriptor(self):
  config=read_json(R/'project.json');excluded=config['excluded_tables']
  self.assertEqual(set(excluded),{'attrib/resource_type_info/merc_byz.rgd'})
  for member,row in excluded.items():self.assertEqual(hashlib.sha256((R/'source/tables'/(member+'.json')).read_bytes()).hexdigest(),row['sha256'])
  self.assertIn("config.get('excluded_tables',{})",(R/'tools/build.py').read_text())
  root=rgd.read(import_table(read_json(R/'source/tables/attrib/korea.rgd.json')))
  self.assertIs(next(n.value for _,n in rgd.flatten(root.nodes) if n.key=='override_instances'),False)
  self.assertTrue(config['build_hold']);self.assertEqual(config['version'],'0.1.5')
 def test_custom_tooltips_preserve_stock_dictionary_and_match_fees(self):
  import xml.etree.ElementTree as ET
  original=gzip.decompress((D/'official-issuabletooltip.xaml.gz').read_bytes()).decode('utf-8-sig')
  text=(R/'source/resources/ui/hud/controls/issuabletooltip.xaml').read_bytes().decode('utf-8')
  cut=text.index('\n    <!-- Korea research templates only;')
  self.assertEqual(text[:cut]+'</ResourceDictionary>'+text[text.rindex('</ResourceDictionary>')+len('</ResourceDictionary>'):],original)
  node=ET.fromstring(text);ns='{http://schemas.microsoft.com/winfx/2006/xaml/presentation}';key='{http://schemas.microsoft.com/winfx/2006/xaml}Key'
  keyed={n.get(key):n for n in node if n.get(key)}
  for name,fee in CHANGES['custom_tooltip_templates'].items():
   self.assertIn(name,keyed);style=keyed[name+'Style']
   self.assertFalse(any(n.get('ItemsSource')=='{Binding Resources}' for n in style.iter()))
   self.assertTrue(any(n.get('Source')=='/WPFGUI;component/icons/korea/bookicon.png' for n in style.iter()))
   self.assertTrue(any(n.get('Text')==f'{fee["literature"]:g} Literature' for n in style.iter()))
   self.assertEqual(any(n.get('Text')=='1 foreign research choice' for n in style.iter()),bool(fee['allowance']))
  for row in CHANGES['variants']:
   if row['costs']['merc_byz']:
    fee=CHANGES['custom_tooltip_templates'][row['tooltip']]
    self.assertEqual(fee,{'literature':row['costs']['merc_byz'],'allowance':row['costs']['action']})
   else:self.assertEqual(row['tooltip'],'UniqueAbilityDataTemplate')
  self.assertTrue((R/'inputs/native/ui/icons/korea/bookicon.rrtex').is_file())
 def test_art_masters_native_inputs_and_release_unchanged(self):
  protected=read_json(D/'protected-before.json');changed=read_json(D/'changed-files.json')
  for rel,sha in protected.items():
   if rel in changed:continue
   self.assertEqual(hashlib.sha256((R/rel).read_bytes()).hexdigest(),sha,rel)
  self.assertTrue(all(not p.startswith(('inputs/','authoring/','release/')) for p in changed))
 def test_original_art_only_source_gate_is_preserved_before_cost_repair(self):
  protected=read_json(R/'docs/update_016/PROTECTED_BEFORE.json')
  for rel,sha in protected.items():
   if rel.startswith(('source/tables/','source/scar/')):
    raw=BEFORE[rel].encode('utf-8') if rel in BEFORE else (R/rel).read_bytes()
    # The original textual snapshot used universal-newline reading. Restore
    # CRLF only when its exact original digest proves that was the source form.
    candidates=[raw,raw.replace(b'\n',b'\r\n')] if rel in BEFORE and b'\r\n' not in raw else [raw]
    self.assertIn(sha,[hashlib.sha256(data).hexdigest() for data in candidates],rel)
if __name__=='__main__':unittest.main()
