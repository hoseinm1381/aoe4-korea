"""Apply reviewed 014 model/material repairs and narrowly scoped native blueprint edits."""
import sys,json,copy,gzip,shutil,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import *
from garrison_shared import relic_chunky as rc,derived_blueprints as derive,mod_content
config=read_json(R/'project.json');assert config['version']=='0.1.3'
PREVIEW='--preview' in sys.argv
OUT=W/'source-preview014' if PREVIEW else R
if PREVIEW:assert not OUT.exists(),'Preserve the staged preview';OUT.mkdir()
def output(p):return OUT/p.relative_to(R)
before=json.loads(gzip.decompress((D/'before-source.json.gz').read_bytes()))
G=stock_game.current();owner=config['owner'].replace('-','');changed=[]
def save(p,doc,reason):
 old=p.read_bytes();target=output(p);write_json(target,export_table(rgd.write(doc)));changed.append({'file':p.relative_to(R).as_posix(),'reason':reason,'before_sha256':sha(old),'after_sha256':sha(target.read_bytes())})
# K01: only remove Zhu Xi's free-Official completion action; retain all other construction callbacks.
p=R/'source/tables/attrib/ebps/korea/kr_building_town_center_capital_chi_ha_01.rgd.json';doc=rgd.read(import_table(read_json(p)));hits=[]
for route,n in rgd.flatten(doc.nodes):
 if n.kind=='CString' and n.value.lower().replace('\\','/').endswith('nomad_mode_town_center_complete/zxl/spawn_official_master'):
  hits.append(route);n.value=''
assert hits==['default/construction_ext/on_construction_complete_state_tree_refs/on_construction_complete_entity_state_tree_ref'],hits
save(p,doc,'Remove the inherited free Imperial Official construction-complete state only')
# K03: rigid unique buildings must use a root-attached rigid animator, not inherit a foreign skin palette.
template=rgd.read(G.blueprint('attachments/attachment_lists/civilizations/chinese/units/tier1_villager_chi'))
sim=copy.deepcopy(next(n for _,n in rgd.flatten(template.nodes) if n.key=='animator_sim_attachment'))
at(sim,'attach_data/marker_name_parent').value='';at(sim,'attach_data/game_object_attachment_type').value=0
rigid=[]
for p in (R/'source/tables/attrib/attachments').rglob('*.rgd.json'):
 doc=rgd.read(import_table(read_json(p)));edits=[]
 def walk(nodes,route=''):
  for i,n in enumerate(nodes):
   path=route+'/'+str(n.key)
   if n.key=='animator_skin_attachment' and at(n,'animator').value.replace('\\','/').startswith('art/kr013/static/'):
    new=copy.deepcopy(sim);at(new,'animator').value=at(n,'animator').value;at(new,'is_selectable').value=at(n,'is_selectable').value
    nodes[i]=new;edits.append(path)
   elif isinstance(n.value,list):walk(n.value,path)
 walk(doc.nodes)
 if edits:save(p,doc,'Replace foreign skinned building attachment with native root rigid attachment');rigid.append({'file':p.relative_to(R).as_posix(),'paths':edits})
# K11: native SDK derives the isolated tier list and its PBG identity; only its skin resource changes.
path='attachments/attachment_lists/civilizations/chinese/team_weapons/tier4_nest_of_bees_chi'
idx=G.blueprint_index(W/'stock-blueprint-index');matches=[k for k in idx if k.startswith('attachments/attachment_lists/') and k.endswith('/tier4_nest_of_bees_chi')];assert len(matches)==1;path=matches[0]
raw=G.blueprint(path);generated,report=derive.build([{'name':'kr014_hwacha_visual','family':'attachments/attachment_lists','source':path,'changes':[]}],{path:raw},mod_id=config['owner'],mod_key='korea',pbgid=mod_content.pbgid,owner=owner)
dest,(_,newraw)=next(iter(generated.items()));doc=rgd.read(newraw);count=0
for route,n in rgd.flatten(doc.nodes):
 if n.kind=='CString' and n.key=='animator' and 'chi_nest_of_bees' in n.value:
  n.value='art\\kr014\\hwacha\\model';count+=1
assert count>0
p=R/'source/tables/attrib'/Path(dest+'.rgd.json');write_json(output(p),export_table(rgd.write(doc)));changed.append({'file':p.relative_to(R).as_posix(),'reason':'SDK-derived private Hwacha visual tier','added':True})
p=R/'source/tables/attrib/ebps/korea/kr_unit_nest_of_bees_4_chi_ha_01.rgd.json';doc=rgd.read(import_table(read_json(p)));count=0
for route,mapname,name,n in refs(doc.nodes):
 if mapname=='attachments/attachment_lists' and name=='tier4_nest_of_bees_chi':child(n,'$PBGNAME').value=owner+':kr014_hwacha_visual';count+=1
assert count>0;save(p,doc,'Wire only the Hwacha body tier; keep its animation graph, crew, weapons and projectiles')
native=read_json(R/'inputs/native-manifest.json');oldnative=copy.deepcopy(native);native_changes=[]
for stage in [W/'repaired-native',Path(read_json(D/'HWACHA_NATIVE_COOK.json')['native_stage'])]:
 assert stage.is_dir()
 for source in sorted(stage.rglob('*')):
  if not source.is_file():continue
  member=source.relative_to(stage).as_posix();assert member.startswith(('art/kr013/','art/kr014/'))
  h=sha(source.read_bytes())
  if native.get(member,{}).get('sha256')==h:continue
  target=source if PREVIEW else R/'inputs/native'/member
  if not PREVIEW:target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
  native[member]={'bytes':target.stat().st_size,'sha256':h,'toc':'data','change':'Korea 014 native rig/material/rigid/Hwacha repair'};native_changes.append(member)
write_json(output(R/'inputs/native-manifest.json'),native)
master=read_json(R/'source/master-index.json');indexed={r['path'] for r in master['files']}
for p in sorted((R/'authoring/art014').rglob('*')):
 if p.is_file() and p.suffix!='.blend1':
  path=p.relative_to(R/'authoring').as_posix();assert path not in indexed
  master['files'].append({'path':path,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes()),'provenance':'Korea 0.1.4 editable Hwacha and original textures'})
write_json(output(R/'source/master-index.json'),master)
# Exact prior package/member inventory is the baseline for the final supported assembly.
listing=G.archiver.run(['list',str(W/'baseline013.sga'),'--verify']);assert listing['archive']['verification']['verified']
prior=W/'baseline013-readback'
if not prior.exists():G.archiver.run(['extract',str(W/'baseline013.sga'),str(prior),'--filter',''])
baseline={'members':{m['path']:{'toc':m['toc'],'sha256':sha((prior/m['path']).read_bytes()),'bytes':m['size']} for m in listing['members']}}
bp=output(D/'baseline-members.json.gz');bp.parent.mkdir(parents=True,exist_ok=True);bp.write_bytes(gzip.compress(json.dumps(baseline).encode(),mtime=0))
table_members=[r['file'].removeprefix('source/tables/').removesuffix('.json') for r in changed]
added_native=sorted(set(native)-set(oldnative));added_tables=[r['file'].removeprefix('source/tables/').removesuffix('.json') for r in changed if r.get('added')]
policy={'schema':'korea.update-014-policy/v1','allowed_changed':sorted(set(native_changes+table_members+['garrison/civilizations.json'])),'allowed_added':sorted(added_native+added_tables),'allowed_removed':[],'native_changed':sorted(m for m in native_changes if m in oldnative),'native_added':added_native,'source_changes':changed,'starting_official_removed_paths':hits,'rigid_attachment_repairs':rigid,'hwacha_sdk_identity':report,'native_animation_graphs_changed':False}
write_json(output(R/'source/update-014-policy.json'),policy);write_json(output(D/'INTEGRATION.json'),policy)
config.update(version='0.1.4',update_policy='source/update-014-policy.json',baseline_members='docs/update_014/baseline-members.json.gz',build_stage='art014-current',publication='Local 0.1.4 repair candidate; no push, tag, installation or publication authorized')
write_json(output(R/'project.json'),config)
print('014_PREVIEW_STAGED' if PREVIEW else '014_INTEGRATED',len(changed),'tables',len(native_changes),'native changes',flush=True)
