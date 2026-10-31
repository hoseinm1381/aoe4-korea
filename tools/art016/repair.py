"""Source-only Korean colour/merge-rig repair. Never cook, assemble or package."""
import sys, json, struct, hashlib, gzip, base64, zlib, copy
import re
from functools import lru_cache
from pathlib import Path
R=Path(__file__).resolve().parents[2]
import os
W=Path(os.environ.get('KOREA_ART016_STAGE',str(R/'output/source016')))
sys.path.insert(0,str(R/'tools'))
from runtime import *
from garrison_shared import relic_chunky as rc,model_variants as mv,rrtex_decoder as rr
sys.path.insert(0,str(R/'tools/art013'))
from rig_contract import read_contract
def sha(b):return hashlib.sha256(b).hexdigest()
def one(raw,tag):
 cs=[c for c in rc.walk(rc.parse(raw).roots) if c.tag==tag];assert len(cs)==1,(tag,len(cs));return cs[0]
def skins(payload):
 n=struct.unpack_from('<I',payload)[0];off=4;rows=[]
 for i in range(n):
  name,off=rc.read_lp_string(payload,off);parent=struct.unpack_from('<h',payload,off)[0];off+=2
  rows.append({'name':name,'parent':parent,'bind':payload[off:off+40]});off+=40
 assert off==len(payload)
 return rows
def pack_skins(rows):
 return struct.pack('<I',len(rows))+b''.join(rc.lp_string(b['name'])+struct.pack('<h',b['parent'])+b['bind'] for b in rows)
def rename_model(raw,old,new):
 # Native names are length-prefixed strings, including chunk names. Rewrite
 # only qualified names and verify all large vertex/index buffers unchanged.
 edits={};doc=rc.parse(raw)
 for c in rc.walk(doc.roots):
  payload=c.payload
  if not c.children:
   for suffix in ['', '_lod1','_lod2','_lod3']:
    payload=payload.replace(rc.lp_string(old+suffix),rc.lp_string(new+suffix))
  name=c.name
  if c.decoded_name==old:name=new.encode()+b'\0'
  if name!=c.name:edits[c.offset]=rc.Rename(name,None if c.children else payload)
  elif payload!=c.payload:edits[c.offset]=payload
 return rc.rebuild(doc,lambda c:edits.get(c.offset))
@lru_cache(maxsize=1)
def baseline_records():
 snapshot=R/'docs/update_016/before-native.json.gz'
 return json.loads(gzip.decompress(snapshot.read_bytes())) if snapshot.exists() else {}
def baseline_bytes(path):
 key=path.relative_to(R).as_posix();entries=baseline_records()
 return base64.b64decode(entries[key]) if key in entries else path.read_bytes()
def prepare():
 import sqlite3
 W.mkdir(parents=True,exist_ok=True);(W/'donors').mkdir(exist_ok=True)
 g=stock_game.current();official=read_json(R/'docs/update_014/OFFICIAL_RIG_CONTRACTS.json')
 cat=read_json(R/'authoring/art013/catalog.json');rows=[a for a in cat['sources'] if '/units/' in a['blend']];assert len(rows)==72
 index=Path.home()/'AppData/Local/Garrison/Kit/game-assets.sqlite3'
 db=sqlite3.connect('file:'+index.as_posix()+'?mode=ro',uri=True)
 receipt=[];before={}
 combined_cache={}
 for row in rows:
  asset=row['id'];dest=W/'donors'/asset;dest.mkdir(exist_ok=True)
  donor=g.model_files(official[asset]['source']);slots=mv.material_slots(donor['.rrmaterial'])['textures'];p=slots.get('patternTex')
  if p and p!='__default':
   p=p.replace('\\','/');ar=db.execute('select archive_path from resolved_assets where logical_path=?',(p,)).fetchone();assert ar,p
   raw=g.member(ar[0],p);(dest/'stock.rrtex').write_bytes(raw);rr.decode_rrtex(dest/'stock.rrtex',output_dds=dest/'stock.dds',validate_stream=True)
  atlas=read_json(R/row['metadata']['atlas_layout.json'])
  rec={'asset':asset,'stem':'art/kr013/units/'+asset+'/model','atlas':atlas,'textures':row['textures'],'stock_pattern':p,'stock_pattern_sha256':sha(raw) if p and p!='__default' else None,'stock_model':official[asset]['source'],'mask_mode':'restore_stock_owner'}
  base=R/'inputs/native/art/kr013/units'/asset/'model'
  for ext in ['.rgm','.rrgeom','.rrmaterial']:
   q=base.with_suffix(ext);before[q.relative_to(R).as_posix()]=base64.b64encode(baseline_bytes(q)).decode()
  raw=baseline_bytes(base.with_suffix('.rgm'))
  cavalry=asset.startswith(('kr_horseman_','kr_lancer_','kr_hwarang_mounted_','kr_mount_horseman_','kr_mount_lancer_','kr_mount_hwarang_'))
  if cavalry:
   source=official[asset]['source'];match=re.search(r'chi_(?:horse|cavalry)_(light|armor)_age(\d+)',source);assert match,source
   name='chi_horse_combined_'+match[1]+'_age'+match[2];combined_stem='art/civilizations/chinese/animals/'+name+'/'+name
   if combined_stem not in combined_cache:combined_cache[combined_stem]=g.model_files(combined_stem)
   combined=combined_cache[combined_stem];combined_rig=one(combined['.rgm'],b'SKLN').payload;reference_parts=[]
   for c in rc.walk(rc.parse(combined['.rgm']).roots):
    if c.tag==b'SKMS':
     sk=next(x for x in c.children if x.tag==b'SKIN');inv=next(x for x in c.children if x.tag==b'SKEL');reference_parts.append((skins(sk.payload),inv.payload))
   old=skins(one(raw,b'SKIN').payload);is_mount=asset.startswith('kr_mount_')
   candidates=[p for p in reference_parts if any(b['name'].startswith('gaia_c_') for b in p[0])==is_mount];assert len(candidates)==1
   ref,inv=candidates[0];index={b['name']:i for i,b in enumerate(ref)};mapping={'metarig_root':'gaia_root'}
   renamed=[mapping.get(b['name'],b['name']) for b in old];assert len(set(renamed))==len(renamed)
   assert set(renamed)-set(index)<= {'gaia_props'},(asset,set(renamed)-set(index))
   old_inv=one(raw,b'SKEL').payload
   new=[];new_inv=[]
   for i,b in enumerate(old):
    name=renamed[i]
    if name not in index:
     assert name=='gaia_props' and b['parent']==0
     new.append(dict(b));new_inv.append(old_inv[i*40:(i+1)*40]);continue
    ri=index[name];rb=ref[ri];parent=rb['parent']
    while parent>=0 and ref[parent]['name'] not in renamed:parent=ref[parent]['parent']
    pi=renamed.index(ref[parent]['name']) if parent>=0 else -1
    assert pi==b['parent'],(asset,name,'hierarchy',pi,b['parent'])
    new.append({'name':name,'parent':pi,'bind':rb['bind']});new_inv.append(inv[ri*40:(ri+1)*40])
   patched=rc.rebuild(rc.parse(raw),lambda c:combined_rig if c.tag==b'SKLN' else pack_skins(new) if c.tag==b'SKIN' else b''.join(new_inv) if c.tag==b'SKEL' else None)
   # Every weighted skin name must now exist in the exact animated owner.
   assert {b['name'] for b in new}<={b['name'] for b in read_contract(patched)['bones']}
   rec['cavalry']={'root_before':old[0]['name'],'root_after':new[0]['name'],'skin_bones':len(new),'owner_bones':len(read_contract(patched)['bones']),'combined_donor':combined_stem,'donor_sha256':sha(combined['.rgm']),'geometry_unchanged':True}
   (dest/'rig.rgm').write_bytes(patched)
  receipt.append(rec)
  print('PREPARED',asset,'cavalry',cavalry,flush=True)
 extras=[{'asset':r['id'].lower(),'stem':'art/kr013/static/'+r['id'].lower()+'/model','pattern':next(t['file'] for t in r['textures'] if 'pattern' in t['name'].lower())} for r in cat['sources'] if r['group']=='Weapons and equipment']
 extras.append({'asset':'kr_hwacha','stem':'art/kr014/hwacha/model','pattern':'authoring/art014/hwacha/pattern.png'})
 for row in extras:
  p=R/'inputs/native'/(row['stem']+'.rrmaterial');before[p.relative_to(R).as_posix()]=base64.b64encode(baseline_bytes(p)).decode()
  receipt.append({'asset':row['asset'],'stem':row['stem'],'textures':[{'name':'pattern.png','file':row['pattern']}],'atlas':{'native_u_scale':1},'mask_mode':'preserve_authored_RGB_native_zero_alpha'})
 (W/'before-native.json.gz').write_bytes(gzip.compress(json.dumps(before).encode(),mtime=0))
 write_json(W/'preparation.json',receipt)
def encode_bc3(template,name,levels):
 # Native stream v6: a smallest-first list of mip records, each split into
 # independent <=64KiB zlib members. TMAN stores member counts and byte sizes.
 counts=[];sizes=[];data=struct.pack('<I',6)
 for level,(w,h,blocks) in reversed(list(enumerate(levels))):
  assert len(blocks)==max(1,(w+3)//4)*max(1,(h+3)//4)*16
  record=struct.pack('<4I',level,w,h,len(blocks))+blocks
  chunks=[record[i:i+65536] for i in range(0,len(record),65536)];counts.append(len(chunks))
  for block in chunks:
   packed=zlib.compress(block,9)
   if len(packed)>=len(block):packed=block
   sizes.append((len(block),len(packed)));data+=packed
 w,h,_=levels[0]
 manifest=struct.pack('<8IBII',6,w,h,1,2,22,len(levels),2,0,1,len(levels))+b''.join(struct.pack('<I',n) for n in counts)+b''.join(struct.pack('<2I',*s) for s in sizes)
 rr._validate_stream_table(manifest,data)
 _,decoded=rr._decode_mips(data);assert {x.level:x.data for x in decoded}=={i:x[2] for i,x in enumerate(levels)}
 return rc.rebuild(rc.parse(template),lambda c:manifest if c.tag==b'TMAN' else data if c.tag==b'TDAT' else rc.Rename(name.replace('/','\\').encode()+b'\0') if c.tag==b'TXTR' else None)
def stage():
 native=W/'native';native.mkdir(exist_ok=True);changes=[]
 for row in read_json(W/'preparation.json'):
  asset=row['asset'];base=R/'inputs/native'/row['stem'];dest=native/row['stem'];dest.parent.mkdir(parents=True,exist_ok=True)
  mat=baseline_bytes(base.with_suffix('.rrmaterial'));oldname=next(c.decoded_name for c in rc.parse(mat).roots if c.tag==b'GMat');newname=asset+'_atlas'
  unit=row['mask_mode']=='restore_stock_owner'
  if unit:
   raw=(W/'donors'/asset/'rig.rgm').read_bytes() if row.get('cavalry') else baseline_bytes(base.with_suffix('.rgm'))
   raw=rename_model(rename_model(raw,'unit_mesh',asset+'_mesh'),oldname,newname)
   geo=rename_model(rename_model(baseline_bytes(base.with_suffix('.rrgeom')),'unit_mesh',asset+'_mesh'),oldname,newname)
  mask=read_json(W/'masks'/asset/'mask.json');logical='art/kr016/patterns/'+mask['source_sha256'];levels=[]
  for level in mask['mips']:
   dds=(W/'masks'/asset/level['dds']).read_bytes();assert dds[:4]==b'DDS ' and dds[84:88]==b'DXT5';levels.append((level['width'],level['height'],dds[128:]))
  pattern_path=mv.material_slots(baseline_bytes(base.with_suffix('.rrmaterial')))['textures']['patternTex'].replace('\\','/')
  tex=encode_bc3((R/'inputs/native'/pattern_path).read_bytes(),logical,levels)
  t=native/(logical+'.rrtex');t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes(tex)
  mat=mv.rewrite_material(mat,{'patternTex':logical.replace('/','\\')+'.rrtex'},{})
  if unit:mat=rc.rebuild(rc.parse(mat),lambda c:rc.Rename(newname.encode()+b'\0') if c.tag==b'GMat' else None)
  files=[('.rgm',raw),('.rrgeom',geo),('.rrmaterial',mat)] if unit else [('.rrmaterial',mat)]
  for suffix,b in files:dest.with_suffix(suffix).write_bytes(b)
  changes.append({'asset':asset,'stem':row['stem'],'unit':unit,'material_name':newname if unit else oldname,'mesh_name':asset+'_mesh' if unit else None,'pattern':logical+'.rrtex','mask':mask,'cavalry':row.get('cavalry')})
  print('STAGED',asset,flush=True)
 write_json(W/'changes.json',changes)
if __name__=='__main__':
 {'prepare':prepare,'stage':stage}[sys.argv[1]]()
