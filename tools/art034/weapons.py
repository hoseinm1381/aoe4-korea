"""Restore cavalry shields and dress the existing native weapon attachment slots."""
import copy
import re
import sqlite3
import struct
import subprocess
import sys
from pathlib import Path

from runtime import EXT, child, at, export_table, import_table, read_json, refs, rgd, stock_game, write_json
from art016.repair import encode_bc3
from garrison_shared import derived_blueprints as derive, mod_content, model_variants as mv, relic_chunky as rc, rrtex_decoder as rr

def weapon_model(stage, game, db, stock, style, pil, put, digest):
    resource = stock.rsplit('/',1)[-1]
    logical = f'art/kr034/weapons/{style}_{resource}/model'
    folder = stage/'authoring'/'weapons'/f'{style}_{resource}'
    folder.mkdir(parents=True,exist_ok=True)
    work = stage/'weapon-readback'/f'{style}_{resource}'
    work.mkdir(parents=True,exist_ok=True)
    files = game.model_files(stock,required=('.rgm','.rrgeom','.rrmaterial'))
    model=rc.parse(files['.rgm'])
    owner=next(c for c in rc.walk(model.roots) if c.tag==b'BANA')
    prior_path, end=rc.read_lp_string(owner.payload,0)
    assert prior_path.replace('\\','/').lower() == stock and end==len(owner.payload), (stock,prior_path)
    private_path=logical.replace('/','\\')
    replaced=rc.rebuild(model,lambda c:rc.lp_string(private_path) if c.tag==b'BANA' else None)
    assert [c.payload for c in rc.walk(model.roots) if c.tag in (b'MRKS',b'SKLN',b'SKIN',b'SKEL')] == [
        c.payload for c in rc.walk(rc.parse(replaced).roots) if c.tag in (b'MRKS',b'SKLN',b'SKIN',b'SKEL')]
    put(logical+'.rgm',replaced,'native donor weapon and exact anchors')
    if '.rgo' in files:
        put(logical+'.rgo',files['.rgo'],'native weapon state controller')

    # Preserve the hand grip, end markers, vertex normals, UVs, and skinning.
    # Remodel the blade shoulders around their native anchor so contact and
    # the charge-break animation still use the donor frames.
    geometry=rc.parse(files['.rrgeom'])
    chunks=[c for c in rc.walk(geometry.roots) if c.tag==b'GEOB']
    assert len(chunks)==6
    edited={}
    vertex_counts=[]
    for c in chunks[::2]:
        data=bytearray(c.payload)
        count,_,stride,_=struct.unpack_from('<4I',data)
        assert stride==28 and len(data)==16+count*stride
        vertices=[struct.unpack_from('<4e',data,16+i*stride) for i in range(count)]
        end_y=max(v[1] for v in vertices)
        changes=0
        for i,(x,y,z,w) in enumerate(vertices):
            assert w==1
            if style=='bow':
                # Only the mid-limb volume changes. Tips, grip, and string tracks stay aligned.
                t=abs(y)/end_y
                rim=max(0,1-abs(t-.56)/.24)
                xx,zz=x,z*(1+.10*rim)
            else:
                # Keep impact length fixed. Profile the shoulders like the
                # existing Korean leaf spear, lacquered lance, and sabre.
                center,width,amount={
                    'fight_spear':(.91,.08,.29), 'charge_spear':(.91,.08,.43),
                    'fight_sabre':(.65,.30,.17), 'charge_lance':(.71,.27,.31),
                    'fight_polearm':(.80,.18,.17), 'charge_polearm':(.80,.18,.31),
                }[style]
                factor=max(0,1-abs(y/end_y-center)/width)
                xx,zz=x*(1+amount*factor),z
            if (xx,zz)!=(x,z):
                struct.pack_into('<3e',data,16+i*stride,xx,y,zz)
                changes+=1
        assert changes,(stock,style)
        edited[c.offset]=bytes(data)
        vertex_counts.append(changes)
    private=rc.rebuild(geometry,lambda c:edited.get(c.offset))
    after=[c for c in rc.walk(rc.parse(private).roots) if c.tag==b'GEOB']
    assert [c.payload for c in chunks[1::2]]==[c.payload for c in after[1::2]]
    for a,b in zip(chunks[::2],after[::2],strict=True):
        assert a.payload[:16]==b.payload[:16]
        assert all(a.payload[i+6:i+28]==b.payload[i+6:i+28] for i in range(16,len(a.payload),28))
    put(logical+'.rrgeom',private,'reprofiled weapon geometry with donor weights and sockets')

    mat=files['.rrmaterial']
    slots=mv.material_slots(mat)['textures']
    albedo=slots['albedoTexture'].replace('\\','/')
    archive=db.execute('select archive_path from resolved_assets where logical_path=?',(albedo,)).fetchone()
    assert archive, albedo
    template=game.member(archive[0],albedo)
    donor=work/'stock.rrtex'
    donor.write_bytes(template)
    dds=work/'stock.dds'
    rr.decode_rrtex(donor,output_dds=dds,validate_stream=True)
    subprocess.run([pil,Path(__file__).with_name('paint_weapon.py'),dds,folder/'albedo.png',style,work/'mips'],
                   check=True)
    levels=[]
    for p in sorted((work/'mips').glob('*.bin'),key=lambda p:int(p.stem.split('-')[0])):
        i,w,h=map(int,p.stem.split('-'))
        assert i==len(levels)
        levels.append((w,h,p.read_bytes()))
    tex=f'{logical}/albedo'
    put(tex+'.rrtex',encode_bc3(template,tex,levels),'Korean lacquer and metal weapon atlas')
    material=mv.rewrite_material(mat,{'albedoTexture':tex.replace('/','\\')+'.rrtex'},{})
    assert mv.material_slots(material)['textures']==slots|{'albedoTexture':tex.replace('/','\\')+'.rrtex'}
    put(logical+'.rrmaterial',material,'weapon material with stock normals and metalness')
    receipt=dict(donor=stock,private=logical,style=style,donor_hashes={k:digest(v) for k,v in files.items()},
                 painted_atlas_source=albedo,painted_atlas_source_hash=digest(template),
                 reprofiled_vertices=vertex_counts,exact_native_marker_skin_and_controller=True)
    write_json(folder/'recipe.json',receipt)
    return receipt


def slot_style(actor, source, weapon):
    if source.startswith('wpn_melee_horseman_'):
        return 'charge_spear' if source.endswith('_charge') else 'fight_spear'
    if source.startswith('wpn_melee_knight_'):
        return 'charge_lance' if '_charge_' in source else 'fight_sabre'
    if source=='wpn_melee_onna_bugeisha_jpn' and 'knight_' in actor:
        return 'charge_polearm' if '_charge_' in weapon else 'fight_polearm'
    if source.startswith('wpn_range_horsearcher_') and actor.endswith('_ayy'):
        return 'bow'
    return None


def attachments(root, stage, pil, put, put_table, digest):
    game = stock_game.current()
    index = game.blueprint_index(stage/'blueprints')
    owner=read_json(root/'project.json')['owner']
    namespace=owner.replace('-','')
    wanted=('horseman','lancer','hwarang_mounted')
    removals=[]
    actor_slots=[]
    derive_cache={}
    model_cache={}
    index_path=Path.home()/'AppData/Local/Garrison/Kit/game-assets.sqlite3'
    with sqlite3.connect('file:'+index_path.as_posix()+'?mode=ro',uri=True) as db:
        for row in read_json(root/'docs/update_013/visual-integration.json')['private_lists']:
            if row['context'][0] not in wanted:
                continue
            source=rgd.read(game.blueprint(row['stock']))
            current=rgd.read(import_table(read_json(root/'source/tables'/(row['private']+'.json'))))
            before={key:n.value for key,n in rgd.flatten(source.nodes) if n.key=='animator'}
            fixes=[]
            for key,n in rgd.flatten(current.nodes):
                if n.key!='animator' or not n.value.startswith('art\\kr013\\static\\korea_'):
                    continue
                assert n.value.split('\\')[-2] in ('korea_cavalry_spear','korea_lancer_lance','korea_hwarang_sword')
                restore=before[key]
                assert 'shield' in restore, (row['stock'],key,restore)
                fixes.append(dict(slot=key,from_asset=n.value,to_shield=restore))
                n.value=restore
            if fixes:
                put_table(row['private'],current)
                removals.append(dict(member=row['private'],stock=row['stock'],fixes=fixes))
        for path in sorted((root/'source/tables/attrib/ebps/korea').glob('*.json')):
            actor=path.name.removesuffix('.rgd.json')
            if not actor.startswith(('kr_unit_horseman_','kr_unit_knight_')):
                continue
            doc=rgd.read(import_table(read_json(path)))
            changes=[]
            for route,node in rgd.flatten(doc.nodes):
                if node.key!='non_entity_weapon_wrapper' or '/combat_ext/' not in route:
                    continue
                children={n.key:n for n in node.value}
                if 'animator_attachments' not in children or 'non_entity_weapon_wrapper_pbg' not in children:
                    continue
                ref=child(children['animator_attachments'],'$PBGNAME')
                weapon=child(children['non_entity_weapon_wrapper_pbg'],'$PBGNAME').value
                style=slot_style(actor,ref.value,weapon)
                if style is None:
                    continue
                stock_symbol=ref.value
                cache_key=(stock_symbol,style)
                if cache_key not in derive_cache:
                    sources=[n for n in index if n.startswith('attachments/attachment_lists/') and n.rsplit('/',1)[-1]==stock_symbol]
                    source,=sources
                    data=game.blueprint(source)
                    name=f'kr034_{style}_{stock_symbol.removeprefix("wpn_")}'
                    derived,_=derive.build([dict(name=name,family='attachments/attachment_lists',source=source,changes=[])],
                                          {source:data},mod_id=owner,mod_key='korea',pbgid=mod_content.pbgid,owner=namespace)
                    (member,(_,raw)),=derived.items()
                    identity=rgd.read(raw)
                    old=rgd.read(data)
                    d=copy.deepcopy(old)
                    for variant in d.nodes:
                        if not isinstance(variant.value,list):
                            continue
                        child(variant,'pbgid').value=at(identity,variant.key+'/pbgid').value
                        ref_node=at(variant,'attachment_lists/parent_animator')
                        stock_model=ref_node.value.replace('\\','/').lower()
                        assert stock_model==at(old,variant.key+'/attachment_lists/parent_animator').value.replace('\\','/').lower()
                        model_key=(stock_model,style)
                        if model_key not in model_cache:
                            model_cache[model_key]=weapon_model(stage,game,db,stock_model,style,pil,put,digest)
                        ref_node.value=model_cache[model_key]['private'].replace('/','\\')
                        assert {k:v for k,_,v,_ in refs(variant.value)}=={
                            k:v for k,_,v,_ in refs(child(old,variant.key).value)}
                    put_table('attrib/'+member+'.rgd',d)
                    derive_cache[cache_key]=namespace+':'+name
                ref.value=derive_cache[cache_key]
                changes.append(dict(route=route,gameplay_weapon=weapon,stock_attachment=stock_symbol,
                                    private_attachment=ref.value,role=style))
            assert changes,actor
            put_table(path.relative_to(root/'source/tables').as_posix().removesuffix('.json'),doc)
            actor_slots.append(dict(actor=actor,slots=changes))
    assert len(removals)==6 and len(actor_slots)==8 and len(model_cache)==10,(len(removals),len(actor_slots),len(model_cache))
    return dict(restored_shields=removals,weapon_slots=actor_slots,models=list(model_cache.values()))
