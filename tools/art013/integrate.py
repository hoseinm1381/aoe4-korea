"""Prepare Korean-only visual graph; stage first, promote after native proof.

All private PBG identities are allocated by Garrison's native derivation API.
Native stock graphs, gameplay, speakers and lifecycle owners are retained.
"""
from pathlib import Path
import sys,json,hashlib,copy,re,struct,tempfile,subprocess,collections
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));sys.path.insert(0,str(R/'tools/art013'))
from runtime import *
from garrison_shared import relic_chunky as rc,derived_blueprints as derive,mod_content,model_variants as mv
from native_tree import NativeTree
G=stock_game.current();config=read_json(R/'project.json');OWNER=config['owner'].replace('-','')
BASE=R/'output/art-current/integration';BASE.mkdir(parents=True,exist_ok=True)
TABLES=BASE/'tables';NATIVE=BASE/'native'
catalog=read_json(R/'authoring/art013/catalog.json')['sources'];cat={x['id']:x for x in catalog}
plan=read_json(R/'source/art013/integration-plan.json')['assets'];inv=read_json(R/'docs/update_013/ownership-inventory.json')
stocknodes=inv['stock_attachment_lists'];index=G.blueprint_index(Path(tempfile.gettempdir())/'k13/blueprint-cache')
names=collections.defaultdict(list)
for p in index:
 if p.startswith('attachments/attachment_lists/'):names[p.rsplit('/',1)[-1]].append(p)
def norm(p):return p.replace('\\','/').lower().removeprefix('data:').removesuffix('.rgm').removesuffix('.rgo')
def h(raw):return hashlib.sha256(raw).hexdigest()
def put(member,raw):
 p=NATIVE/member;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
def table(member,doc):
 p=TABLES/(member+'.json');p.parent.mkdir(parents=True,exist_ok=True);write_json(p,export_table(rgd.write(doc)))
def resolve(name):
 name=norm(name).split(':',1)[-1].removesuffix('.rgd')
 if name.startswith('attachments/attachment_lists/'):return name if name in index else None
 found=names[name.rsplit('/',1)[-1]];return found[0] if len(found)==1 else None
ordinary=read_json(R/'docs/update_013/ordinary-native.json')['assets'];models={norm(x['stock_model']):x['private_model'] for x in ordinary}
for row in ordinary:
 raw=G.model_files(row['stock_model'],required=('.rrmaterial',))['.rrmaterial'];doc=rc.parse(raw);edits={}
 for c in doc.roots:
  name=c.decoded_name.removesuffix('_collection');mapping=row['material_edits'].get(name)
  if c.tag!=b'GMat' or not mapping:continue
  mapping={k:(v.removeprefix('game:')+'.rrtex' if v.startswith('game:') else v) for k,v in mapping.items()}
  one=rc.pack_document([rc.pack_chunk(c.kind,c.tag,c.payload,version=c.version,name=c.name)])
  edits[c.offset]=rc.parse(mv.rewrite_material(one,mapping,{})).roots[0].payload
 for ext in ['.rgm','.rgo','.rrgeom','.rrmaterial']:
  data=rc.rebuild(doc,lambda c:edits.get(c.offset)) if ext=='.rrmaterial' else (R/'output/art-current/ordinary-native'/row['asset']/('model'+ext)).read_bytes()
  put(row['private_model']+ext,data)

# Only art members from the fresh native cook are admitted, never prototype actors.
static=read_json(R/'docs/update_013/static-cook.json');units=read_json(R/'docs/update_013/unit-native-readbacks.json')
archives=[Path(static['archive']),Path(units['archive'])]
for archive in archives:
 listing=G.archiver.run(['list',str(archive),'--verify']);assert listing['archive']['verification']['verified']
 extraction=Path(tempfile.gettempdir())/'k13'/('integration-art-'+h(archive.read_bytes())[:12])
 if not extraction.exists():G.archiver.run(['extract',str(archive),str(extraction),'--filter','art/kr013/'])
 for p in extraction.rglob('*'):
  if p.is_file() and p.suffix in ['.rgm','.rgo','.rrgeom','.rrmaterial','.rrtex']:put(p.relative_to(extraction).as_posix(),p.read_bytes())

def active_visuals(tree):
 root=next(o for o in tree.objects.values() if o['type']=='StampBlueprint' and not o['owner']);a=tree.field(root,root['fields']['m_blueprints']);out=[]
 for i in range(a['count']):
  slot=a['data_address']+8*i;obj=tree.by_offset[slot+struct.unpack('<q',tree.bytes(slot,8))[0]]
  if obj['type']=='VisualStampBlueprint':out.append(obj)
 return out
stamp_cache={};stamp_receipts=[]
def clone_stamp(stem,unique=None):
 stem=norm(stem).removesuffix('.bin');key=(stem,unique)
 if key in stamp_cache:return stamp_cache[key]
 cache=Path(tempfile.gettempdir())/'k13/stamp-cache';cache.mkdir(exist_ok=True);p=cache/(h(stem.encode())[:20]+'.bin')
 if not p.exists():p.write_bytes(G.member('Data.sga',stem+'.bin'))
 tree=NativeTree(p);active=active_visuals(tree);replacements={}
 for obj in active:
  old=norm(tree.field(obj,obj['fields']['m_blueprint'])['text'])
  if old in models:replacements[old]=models[old]
 if unique and '/const_dest/' not in stem:
  candidates=[norm(tree.field(o,o['fields']['m_blueprint'])['text']) for o in active if '/structures/' in norm(tree.field(o,o['fields']['m_blueprint'])['text'])]
  if candidates:replacements={candidates[0]:'art/kr013/static/'+unique+'/model'}
 if not replacements:stamp_cache[key]=None;return None
 target='art/kr013/stamps/s'+h(repr(key).encode())[:16]+'.bin'
 memory=bytearray(tree.memory.payload);objects=bytearray(tree.chunks[b'ROBJ'].payload);creation=bytearray(tree.chunks[b'RNEW'].payload)
 ids={oid:int.from_bytes(hashlib.sha256((OWNER+target+str(oid)).encode()).digest()[:8],'little') for oid in tree.objects};assert len(set(ids.values()))==len(ids)
 changed=[]
 for i,(oid,obj) in enumerate(tree.objects.items()):
  at=8+i*36;old,tid,address,owner,checksum=struct.unpack_from('<QQQQI',objects,at);assert old==oid
  struct.pack_into('<QQQQI',objects,at,ids[oid],tid,address,ids.get(owner,0),checksum)
  for name,f in obj['fields'].items():
   pos=obj['offset']+int(f.get('Offset'))-tree.memory.payload_offset
   if name=='m_objectID':
    previous=struct.unpack_from('<Q',memory,pos)[0]
    if previous in ids:struct.pack_into('<Q',memory,pos,ids[previous])
   if obj['type']=='VisualStampBlueprint' and name=='m_blueprint':
    oldmodel=norm(tree.field(obj,f)['text'])
    if oldmodel not in replacements:continue
    displacement,length=struct.unpack_from('<qQ',memory,pos);new=replacements[oldmodel].replace('/','\\').encode();assert len(new)<=length,(oldmodel,new)
    start=pos+displacement;memory[start:start+length]=new+b'\0'*(length-len(new));struct.pack_into('<Q',memory,pos+8,len(new));changed.append((oldmodel,replacements[oldmodel]))
 for i in range(struct.unpack_from('<Q',creation)[0]):
  at=8+29*i;struct.pack_into('<Q',creation,at,ids[struct.unpack_from('<Q',creation,at)[0]])
 edits={tree.memory.offset:bytes(memory),tree.chunks[b'ROBJ'].offset:bytes(objects),tree.chunks[b'RNEW'].offset:bytes(creation)}
 put(target,rc.rebuild(tree.document,lambda c:edits.get(c.offset)))
 after=NativeTree(NATIVE/target);assert len(after.objects)==len(tree.objects)
 assert len(active_visuals(after))==len(active)
 stamp_receipts.append({'source':stem+'.bin','source_sha256':h(p.read_bytes()),'private':target,'changed_models':changed,'objects':len(tree.objects),'functional_objects_preserved':True})
 stamp_cache[key]=target[:-4];return target[:-4]

unique_cons={c['table']:a['asset'] for a in plan if a['asset'] in ['stone_pagoda','bulguksa_temple','seon_deok_observatory','gate_of_reverence','gyeongbok_palace','hall_of_worthies','seowon_academy','mountain_fortress','hwangnyongsa'] for c in a['consumers']}
families={};equipment=collections.defaultdict(list)
for a in plan:
 family=a.get('family')
 if family and not family.startswith(('mount','trade_cargo')):
  for c in a['consumers']:
   f='villager' if family.startswith('villager') else family
   if 'repeater_crossbowman' in c['table']:f='tiger_hunter'
   families[c['table']]=f
  for e in a.get('equipment_candidates',[]):
   if e not in equipment[family]:equipment[family].append(e)
equipment['villager']=equipment['villager_male']
assets=set(cat);used=set();stockraw={};clones={};clone_reports=[]
bp_cache=Path(tempfile.gettempdir())/'k13/native-blueprint-cache';bp_cache.mkdir(exist_ok=True)
def stock_blueprint(path):
 file=bp_cache/(h(path.encode())+'.rgd');expected=stocknodes.get(path,{}).get('source_sha256')
 if file.exists() and (expected is None or h(file.read_bytes())==expected):return file.read_bytes()
 raw=G.blueprint(path)
 if expected:assert h(raw)==expected,'Official blueprint changed since ownership qualification: '+path
 file.write_bytes(raw);return raw

# The market and monastery inherit these stock consumers. Isolate their unit
# and squad identities without changing the original effective gameplay values.
redirects={};new_docs={};inherited=[]
for symbol,family in [('unit_trade_cart_chi','trader'),('unit_monk_3_chi_ha_01','monk')]:
 ebps=next((p for p in index if p.startswith('ebps/') and p.rsplit('/',1)[-1]==symbol),None)
 sbps=next((p for p in index if p.startswith('sbps/') and p.rsplit('/',1)[-1]==symbol),None)
 assert ebps and sbps,(symbol,ebps,sbps)
 allocated={}
 for path in [ebps,sbps]:
  kind=path.split('/')[0];name='kr013_'+family+'_'+kind
  result,report=derive.build([{'name':name,'family':kind,'source':path,'changes':[]}],{path:stock_blueprint(path)},mod_id=config['owner'],mod_key='korea',pbgid=mod_content.pbgid,owner=OWNER)
  dest,(_,raw)=next(iter(result.items()));doc=rgd.read(raw);member='attrib/'+dest+'.rgd';source='source/tables/'+member+'.json'
  allocated[kind]={'member':member,'source':source,'doc':doc,'reference':OWNER+':'+name};redirects[(kind,symbol)]=OWNER+':'+name
 for _,mapname,name,node in refs(allocated['sbps']['doc'].nodes):
  if mapname=='ebps' and name.split(':')[-1]==symbol:child(node,'$PBGNAME').value=allocated['ebps']['reference']
 for item in allocated.values():new_docs[item['source']]=item['doc'];table(item['member'],item['doc'])
 source=allocated['ebps']['source'];families[source]=family
 inv['source_consumers'].append({'source':source,'roots':[]})
 inherited.append({'symbol':symbol,'family':family,'ebps':allocated['ebps']['member'],'sbps':allocated['sbps']['member'],'native_sdk_allocated':True})
def redirect(doc):
 changes=[]
 for route,mapname,name,node in refs(doc.nodes):
  ref=redirects.get((mapname,name.split(':')[-1]))
  if ref:child(node,'$PBGNAME').value=ref;changes.append((route,name,ref))
 return changes
villager_template=rgd.read(stock_blueprint('attachments/attachment_lists/civilizations/chinese/units/tier1_villager_chi'))
rigid_attachment_template=copy.deepcopy(next(n for p,n in rgd.flatten(villager_template.nodes) if n.key=='animator_sim_attachment'))
def body(family,age,female=False):
 stem=family
 if family=='villager':stem='villager_female' if female else 'villager_male'
 elif female and family in ['scout','trader']:stem=family+'_female'
 options=[(int(re.search(r'_a(\d+)$',x).group(1)),x) for x in assets if x.startswith('kr_'+stem+'_a') and re.search(r'_a\d+$',x)]
 if not options:return None
 prior=[x for x in options if x[0]<=age];asset=max(prior or options)[1];used.add(asset);return 'art/kr013/units/'+asset+'/model'
def mount(family,age):
 stem={'hwarang_mounted':'hwarang','scout':'scout','horseman':'horseman','lancer':'lancer','trader':'trader'}.get(family)
 if stem:return body('mount_'+stem,age)
def rigid(old,family,age):
 # Gapsa shields are left-hand defense meshes, never a fallback spear.
 if family=='gapsa' and '/weapons/defense/' in old:return None
 available=equipment.get(family,[]);suffix=None
 for e in available:
  key='Korea_'+e
  if key not in cat:continue
  recipe=read_json(R/cat[key]['metadata']['recipe.json'])
  if norm(recipe.get('donor',''))==old:suffix=e;break
 if suffix is None:
  if 'torch' in old:suffix='shared_torch'
  else:
   primary={'archer':'gakgung_archer','tiger_hunter':'gakgung_tiger_hunter','crossbowman':'crossbow','handcannoneer':'hand_chongtong','spearman':'jangchang_plain' if age<3 else 'jangchang_tassel','gapsa':'gapsa_heavy_spear','horseman':'cavalry_spear','lancer':'lancer_lance','hwarang_mounted':'gakgung_hwarang' if any(t in old for t in ['bow','archer']) else 'hwarang_sword','hwarang_dismounted':'gakgung_hwarang' if 'bow' in old else 'hwarang_sword','seonbi':'seonbi_book','monk':'monk_staff','righteous_army_monk':'righteous_monk_sword'}
   if '/weapons/' in old or '/tools/' in old:suffix=primary.get(family)
 if suffix and 'Korea_'+suffix in cat:used.add('Korea_'+suffix);return 'art/kr013/static/korea_'+suffix+'/model'
 return None
def private_list(path,context,stack=()):
 key=(path,context);family,age,unique=context
 # Use the native tier's actual visual age wherever one exists.
 match=re.search(r'(?:^|/)tier([1-4])_',path)
 if match:age=int(match.group(1));context=(family,age,unique);key=(path,context)
 if key in clones:return clones[key]
 if path in stack:return None
 if path not in stockraw:stockraw[path]=stock_blueprint(path)
 original=stockraw[path];doc=rgd.read(original);changed=[]
 def walk(nodes,route=''):
  for n in nodes:
   p=route+'/'+str(n.key)
   if isinstance(n.value,list):
    fields={x.key:x for x in n.value}
    if '$PBGNAME' in fields and fields['$PBGNAME'].value:
     target=resolve(fields['$PBGNAME'].value)
     if target:
      ref=private_list(target,context,stack+(path,))
      if ref:changed.append((p,fields['$PBGNAME'].value,ref));fields['$PBGNAME'].value=ref
    if n.key=='meshes' and '/animator_merge_mesh_attachment/' in p and family:
     art=[x for x in n.value if x.kind=='CString' and norm(x.value).startswith('art/')]
     if art and any('/humans/' in norm(x.value) or '/animals/' in norm(x.value) for x in art):
      old=norm(art[0].value);female='female' in old;new=mount(family,age) if '/animals/' in old and 'combined' not in old else body(family,age,female)
      if new:
       before=copy.deepcopy(n.value);n.value=[copy.deepcopy(art[0])];n.value[0].value=new.replace('/','\\')
       if '/animals/' in old and 'combined' in old and mount(family,age):
        second=copy.deepcopy(n.value[0]);second.key='animator1';second.hash=rgd.dictionary_hash(second.key);second.value=mount(family,age).replace('/','\\');n.value.append(second)
        if family=='trader':
         cargo=body('trade_cargo',age)
         if cargo:
          third=copy.deepcopy(n.value[0]);third.key='animator2';third.hash=rgd.dictionary_hash(third.key);third.value=cargo.replace('/','\\');n.value.append(third)
       changed.append((p,[x.value for x in before],[x.value for x in n.value]))
    if family in ['camp_lumber','camp_mining'] and re.search(r'/tier[1-4]_econ_(wood|mining)',path) and n.key=='attachment_list' and any(x.key=='stamp_attachment' and any(y.key=='stamp' and norm(y.value).startswith('art/stamps/') and '/const_dest/' not in norm(y.value) for y in x.value) for x in n.value):
     shelter='Korea_lumber_camp01' if family=='camp_lumber' else 'Korea_mining_camp01'
     attach=copy.deepcopy(rigid_attachment_template);at(attach,'attach_data/marker_name_parent').value='';child(attach,'animator').value=('art/kr013/static/'+shelter.lower()+'/model').replace('/','\\');n.value.append(attach);used.add(shelter);changed.append((p,'native camp machinery retained','Added root-attached Korean shelter with native pathfinding disabled'))
    walk(n.value,p)
   elif n.kind=='CString' and n.value and norm(n.value).startswith('art/'):
    old=norm(n.value);new=None
    if n.key=='parent_animator' or '/animation_attachment/' in p:continue
    if n.key=='stamp':new=clone_stamp(n.value,unique)
    elif old in models:new=models[old]
    elif family and n.key in ['animator','animator0']:new=rigid(old,family,age)
    elif unique and '/structures/' in old and n.key=='animator':new='art/kr013/static/'+unique+'/model'
    if new and norm(new)!=old:changed.append((p,n.value,new));n.value=new.replace('/','\\')
 walk(doc.nodes)
 if not changed:clones[key]=None;return None
 name='kr013_v'+h(repr(key).encode())[:15]
 generated,report=derive.build([{'name':name,'family':'attachments/attachment_lists','source':path,'changes':[]}],{path:original},mod_id=config['owner'],mod_key='korea',pbgid=mod_content.pbgid,owner=OWNER)
 assert len(generated)==1
 dest,(_,raw)=next(iter(generated.items()));owned=rgd.read(raw)
 # The SDK supplies new identities; use the fully audited original payload and
 # substitute only its SDK-generated IDs after the visual/reference edits.
 for variant in doc.nodes:
  if not isinstance(variant.value,list):continue
  try:child(variant,'pbgid').value=at(owned,variant.key+'/pbgid').value
  except StopIteration:pass
 table('attrib/'+dest+'.rgd',doc);reference=OWNER+':'+name;clones[key]=reference
 clone_reports.append({'stock':path,'private':'attrib/'+dest+'.rgd','context':context,'sdk_identity':report,'visual_changes':changed})
 return reference

changed_consumers=[]
for i,entry in enumerate(inv['source_consumers'],1):
 source=entry['source'];family=families.get(source);unique=unique_cons.get(source)
 if '/kr_building_econ_wood_' in source:family='camp_lumber'
 elif '/kr_building_econ_mining_camp' in source:family='camp_mining'
 # Existing ordinary buildings and other unit render owners may reference a
 # Korean-modified model through a shared official list; isolate every consumer.
 p=R/source;original=rgd.write(new_docs[source]) if source in new_docs else import_table(read_json(p));doc=rgd.read(original);changed=redirect(doc)
 age=int(re.search(r'_([1-4])_',p.stem).group(1)) if re.search(r'_([1-4])_',p.stem) else 1
 for route,mapname,name,node in list(refs(doc.nodes)):
  if not name or 'attachments/attachment_lists' not in mapname:continue
  target=resolve(name)
  if not target:continue
  ref=private_list(target,(family,age,unique))
  if ref:
   before=child(node,'$PBGNAME').value;child(node,'$PBGNAME').value=ref;changed.append((route,before,ref))
 if changed:
  before=[(p,n.kind,n.value) for p,n in rgd.flatten(rgd.read(original).nodes) if n.kind not in ['List','List2','CString']]
  after=[(p,n.kind,n.value) for p,n in rgd.flatten(doc.nodes) if n.kind not in ['List','List2','CString']];assert before==after
  member=Path(source).relative_to('source/tables').as_posix()[:-5];table(member,doc);changed_consumers.append({'source':source,'changes':changed,'nonstring_gameplay_byte_values_preserved':True})
 if i%10==0:print('VISUAL_GRAPH',i,len(inv['source_consumers']),'private_lists',len(clone_reports),'stamps',len(stamp_receipts),flush=True)
for p in (R/'source/tables').rglob('*.rgd.json'):
 source=p.relative_to(R).as_posix()
 if any(x['source']==source for x in inv['source_consumers']):continue
 doc=rgd.read(import_table(read_json(p)));changed=redirect(doc)
 if changed:table(p.relative_to(R/'source/tables').as_posix()[:-5],doc);changed_consumers.append({'source':source,'changes':changed,'nonstring_gameplay_byte_values_preserved':True})
write_json(R/'docs/update_013/visual-integration.json',{'owner':OWNER,'private_lists':clone_reports,'private_stamps':stamp_receipts,'consumers':changed_consumers,'inherited_consumers':inherited,'assets_selected':sorted(used),'source_assets_available':len(cat),'source_gameplay_numeric_values_preserved':True,'state_graphs_and_speech_owners':'unchanged','runtime_animation_and_lifecycle':'pending','promotion':'staged only'})
print('VISUAL_GRAPH_STAGED',len(clone_reports),len(stamp_receipts),len(changed_consumers),len(used),flush=True)
