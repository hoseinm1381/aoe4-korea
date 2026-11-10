"""Use the stock opaque sRGB unit-albedo texture contract for Korea's landmarks."""
import argparse
import hashlib
from io import BytesIO
from pathlib import Path
import sqlite3
import struct
import sys
import zlib

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from runtime import read_json, stock_game, write_json
from garrison_shared import model_variants as mv, relic_chunky as rc, rrtex_decoder as rr

STOCK_MODEL = ('art/civilizations/chinese/humans/chi_villager_female_age02/'
               'chi_villager_female_age02')
ART_PATH = 'art/kr036/architecture'
NATIVE = ROOT/'inputs/native'


def stock_template():
    game = stock_game.current()
    materials = game.model_files(STOCK_MODEL, required=('.rrmaterial',))
    path = mv.material_slots(materials['.rrmaterial'])['textures']['albedoTexture'].replace('\\','/').lower()
    database = Path.home()/'AppData/Local/Garrison/Kit/game-assets.sqlite3'
    with sqlite3.connect('file:'+database.as_posix()+'?mode=ro', uri=True) as index:
        record = index.execute('SELECT archive_path FROM resolved_assets WHERE logical_path=?',(path,)).fetchone()
    assert record
    return path, game.member(record[0],path)


def encode_srgb_bc1(template, member, image):
    """Mirror the stock TMAN/TDAT v6 layout, including the TSRI marker."""
    document = rc.parse(template)
    tman = next(chunk for chunk in rc.walk(document.roots) if chunk.tag==b'TMAN')
    assert struct.unpack_from('<I',tman.payload,20)==(19,)
    assert sum(chunk.tag==b'TSRI' for chunk in rc.walk(document.roots))==1
    width,height = image.size
    count = max(width,height).bit_length()
    values = np.asarray(image.convert('RGB'),dtype=np.float32)/255
    linear = np.where(values<=.04045,values/12.92,((values+.055)/1.055)**2.4)
    linear_channels = tuple(Image.fromarray(linear[:,:,channel]) for channel in range(3))
    records, blocks = [], []
    for level in reversed(range(count)):
        w,h = max(1,width>>level),max(1,height>>level)
        if level:
            sample=np.stack([np.asarray(channel.resize((w,h),Image.Resampling.BOX))
                             for channel in linear_channels],axis=2)
            encoded=np.where(sample<=.0031308,sample*12.92,1.055*sample**(1/2.4)-.055)
            tile=Image.fromarray(np.clip(np.rint(encoded*255),0,255).astype(np.uint8))
        else:
            tile=image.convert('RGB')
        with BytesIO() as output:
            tile.save(output,format='DDS',pixel_format='DXT1')
            dds=output.getvalue()
        assert dds[:4]==b'DDS ' and dds[84:88]==b'DXT1'
        payload=dds[128:]
        assert len(payload)==((w+3)//4)*((h+3)//4)*8
        mip=struct.pack('<4I',level,w,h,len(payload))+payload
        fragments=[mip[i:i+65536] for i in range(0,len(mip),65536)]
        records.append(len(fragments))
        for part in fragments:
            packed=zlib.compress(part,9)
            if len(packed)>=len(part):
                packed=part
            blocks.append((len(part),packed))
    header=struct.pack('<8IBII',6,width,height,1,2,19,count,2,0,1,count)
    manifest=header+b''.join(struct.pack('<I',n) for n in records)
    manifest+=b''.join(struct.pack('<2I',n,len(data)) for n,data in blocks)
    stream=struct.pack('<I',6)+b''.join(data for _,data in blocks)
    rr._validate_stream_table(manifest,stream)
    name=member.removesuffix('.rrtex').replace('/','\\').encode()+b'\0'
    return rc.rebuild(document,lambda c:manifest if c.tag==b'TMAN'
        else stream if c.tag==b'TDAT' else rc.Rename(name) if c.tag==b'TXTR' else None)


def pagoda_finish(source, mask):
    """Differentiate the dark ledges, warm ashlar and earth-toned courtyard."""
    output=source.copy().convert('RGB')
    pixels=np.asarray(output,dtype=np.uint8).copy()
    owner=np.asarray(mask.getchannel('R').resize(output.size,Image.Resampling.NEAREST))>=128
    palettes={7:(74,55,39),12:(102,82,62),14:(68,76,72)}
    for side in (0,1024):
        for tile,color in palettes.items():
            x,y=side+tile%4*256,tile//4*256
            patch=pixels[y:y+256,x:x+256]
            gray=patch.astype(np.float32).mean(axis=2)
            texture=(gray-np.median(gray))*.82
            rgb=np.clip(np.array(color)+texture[:,:,None],12,143).astype(np.uint8)
            visible=~owner[y:y+256,x:x+256]
            patch[visible]=rgb[visible]
    return Image.fromarray(pixels)


def run(stage):
    overlay=stage/'overlay'
    overlay.mkdir()
    contract=read_json(ROOT/'docs/update_036/landmark-native-readback.json')
    template_path, template=stock_template()
    old_manifest=read_json(ROOT/'inputs/native-manifest.json')
    result={}
    for asset in sorted(contract):
        source=ROOT/'authoring/art036'/(asset+'.png')
        image=Image.open(source).convert('RGB')
        if asset=='stone_pagoda':
            image=pagoda_finish(image,Image.open(ROOT/'authoring/art036/raised-owner.png'))
            image.save(stage/'stone-pagoda-srgb.png',optimize=True)
        member=f'{ART_PATH}/{asset}.rrtex'
        before=NATIVE/member
        assert hashlib.sha256(before.read_bytes()).hexdigest()==old_manifest[member]['sha256']
        output=overlay/member
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_bytes(encode_srgb_bc1(template,member,image))
        dds=stage/(asset+'.dds')
        audit=rr.decode_rrtex(output,output_dds=dds,validate_stream=True)
        assert audit['internal_format']==19 and audit['projection']['format']=='BC1_UNORM_SRGB'
        assert (audit['width'],audit['height'],audit['mip_count'])==(2048,1024,12)
        material=NATIVE/f'art/kr013/static/{asset}/model.rrmaterial'
        rrmat=rc.parse(material.read_bytes())
        for item in rrmat.roots:
            if item.tag!=b'GMat':
                continue
            raw=rc.pack_document([rc.pack_chunk(item.kind,item.tag,item.payload,version=item.version,name=item.name)])
            slots=mv.material_slots(raw)['textures']
            assert slots['albedoTexture'].replace('\\','/').lower()==member
        result[member]={'toc':'data','bytes':output.stat().st_size,
                        'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
                        'origin':'0.3.7 stock-contract BC1 sRGB landmark albedo'}
        print('SRGB_ALBEDO',asset,audit['projection']['format'],flush=True)
    write_json(stage/'art-overlay.json',result)
    write_json(stage/'art-contract.json',{
        'stock_albedo_member':template_path, 'format_before':'BC3_UNORM (22)',
        'format_after':'BC1_UNORM_SRGB (19), TSRI present', 'models':list(contract),
        'mips_per_texture':12, 'standalone_scope':'albedo only',
    })


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',type=Path)
    run(parser.parse_args().stage)
