"""Read exact official shared Korean production consumers; no gameplay changes."""
import sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from runtime import stock_game,rgd,refs,write_json,read_json
G=stock_game.current();cache=R/'output/voices020/stock-index';cache.mkdir(parents=True,exist_ok=True)
index=G.blueprint_index(cache)
syms=['unit_scout_1_chi','unit_scout_1_chi_ha_01','unit_villager_free_chi_ha_01','unit_naval_transport_ship_2_chi_ha_01','unit_naval_combat_ship_2_chi_ha_01','unit_naval_combat_warship_4_chi_ha_01','unit_naval_war_galley_3_chi_ha_01','unit_naval_trade_ship_3_chi_ha_01','unit_springald_3_chi_ha_01','unit_bombard_4_chi_ha_01']
rows=[]
for symbol in syms:
 matches=[p for p in index if p.startswith('sbps/') and p.rsplit('/',1)[-1]==symbol]
 if len(matches)!=1:raise ValueError((symbol,matches))
 path=matches[0];raw=G.blueprint(path);doc=rgd.read(raw)
 references=[{'path':p,'category':c,'name':n} for p,c,n,_ in refs(doc.nodes)]
 speech=[{'path':p,'kind':n.kind,'value':n.value} for p,n in rgd.flatten(doc.nodes) if n.key in ('squad_speaker_code','attachment_speaker_code','squad_race_code')]
 rows.append({'symbol':symbol,'official_path':path,'sha256':hashlib.sha256(raw).hexdigest(),'references':references,'speech':speech})
 print('OFFICIAL_SHARED_SQUAD',symbol,flush=True)
write_json(R/'docs/voices020/SHARED_PRODUCTION_CONSUMERS.json',{'schema':'korea.voice-shared-consumers/v1','scope':'Verified shared Scout, free Villager, naval and siege production references. No native mutation.','squads':rows})
