"""Paint unique Korean structures on a private two-region native atlas.

The left half is the architectural finish. Only selected raised mesh islands
use the neutral right half and native red owner mask. Index and skin streams
are retained verbatim.
"""
import argparse
from io import BytesIO
import hashlib
from pathlib import Path
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'tools/art035')]
from runtime import read_json, write_json
from architecture import Candidate, normalize
from art016.repair import encode_bc3
from garrison_shared import model_variants as mv, relic_chunky as rc, rrtex_decoder as rr

# Roof, beam, bracket, deep ornament, stone, secondary stone, courtyard, screen.
PALETTES = {
    'bulguksa_temple': ((32,39,36),(114,49,37),(45,88,58),(144,87,54),(102,100,82),(125,111,89),(82,73,56),(119,103,66)),
    'gate_of_reverence': ((30,28,26),(119,41,32),(39,78,54),(151,95,49),(82,78,69),(103,91,77),(81,67,55),(95,72,45)),
    'gyeongbok_palace': ((26,32,42),(138,43,33),(35,94,75),(178,114,46),(110,103,94),(127,117,105),(89,79,63),(135,108,66)),
    'hall_of_worthies': ((48,38,29),(120,74,36),(86,95,47),(164,102,49),(101,87,69),(123,106,79),(93,70,47),(145,107,65)),
    'hwangnyongsa': ((37,29,27),(123,51,36),(46,66,77),(162,98,55),(98,90,71),(116,100,74),(89,67,48),(127,97,62)),
    'mountain_fortress': ((28,39,42),(83,48,39),(48,72,69),(129,72,45),(78,84,78),(105,105,90),(70,69,55),(104,85,62)),
    'seon_deok_observatory': ((44,42,32),(88,52,30),(64,76,53),(126,85,46),(111,106,77),(82,81,58),(75,66,43),(130,106,67)),
    'seowon_academy': ((37,35,28),(103,59,42),(63,75,48),(128,86,49),(101,94,79),(115,107,88),(86,74,52),(140,118,79)),
    'stone_pagoda': ((45,38,31),(98,57,35),(69,73,52),(138,91,51),(113,98,75),(97,90,72),(86,74,54),(135,109,74)),
}

ACCENTS = {
    'bulguksa_temple': (2, 8, 0, 10, 11, 9),
    'gate_of_reverence': (2, 0, 10, 8, 11, 9),
    'gyeongbok_palace': (2, 8, 0, 10, 9),
    'hall_of_worthies': (2, 8, 0, 10, 9),
    'hwangnyongsa': (8, 2, 0, 10, 9),
    'mountain_fortress': (2, 0, 8, 10, 9, 11, 13),
    'seon_deok_observatory': (5, 14, 12),
    'seowon_academy': (0, 8, 10, 9, 11),
    'stone_pagoda': (5, 12, 14),
}
STONE = {'stone_pagoda', 'seon_deok_observatory'}


def textured_tile(source, color, tile, seed, ceremony):
    """Use macro patina and brushwork with the existing UV-aligned relief."""
    n = source.width
    original = np.asarray(source.convert('RGB'), dtype=np.float32).mean(axis=2)
    rng = np.random.default_rng(seed)
    field = Image.fromarray(rng.integers(0,255,(12,12),dtype=np.uint8)).resize((n,n),Image.Resampling.BICUBIC)
    weather = (np.asarray(field,dtype=np.float32)-128)*.16
    micro = rng.normal(0, 2.6, (n,n))
    variation = (original-np.median(original))*.67 + weather + micro
    if tile == 15:
        x, y = np.meshgrid(np.arange(n),np.arange(n))
        variation += 8*np.cos(x*2*np.pi/16)-4*(y%32<2)
    rgb = np.clip(np.array(color)[None,None,:] + variation[:,:,None], 4, 226).astype(np.uint8)
    image = Image.fromarray(rgb).convert('RGBA')
    if tile in (0, 2, 10) and ceremony:
        draw = ImageDraw.Draw(image)
        red, green, gold, near_black = (131,48,36), (54,101,67), (162,113,57), (27,37,29)
        for y in range(0,n,32):
            draw.line((0,y+4,n,y+4),fill=near_black,width=3)
            draw.line((0,y+7,n,y+7),fill=gold,width=2)
            draw.line((0,y+28,n,y+28),fill=red,width=3)
            for x in range(16,n,32):
                draw.polygon(((x-9,y+18),(x,y+10),(x+9,y+18),(x,y+26)),fill=near_black,outline=gold)
                draw.ellipse((x-5,y+14,x+5,y+22),fill=green)
                draw.ellipse((x-2,y+16,x+2,y+20),fill=gold)
    return image


def architecture_paint(name, source, mask):
    roof, beam, green, gold, granite, other, ground, lattice = PALETTES[name]
    colors = (green,gold,green,roof,gold,ground,roof,ground,beam,beam,green,lattice,
              granite,other,other,roof)
    base = Image.new('RGBA',(1024,1024))
    for i,color in enumerate(colors):
        x,y=i%4*256,i//4*256
        src=source.crop((x*2,y*2,(x+256)*2,(y+256)*2)).resize((256,256),Image.Resampling.LANCZOS)
        ceremony=name not in STONE|{'seowon_academy','mountain_fortress'}
        base.paste(textured_tile(src,color,i,153+i,ceremony),(x,y))
    neutral = np.asarray(base.convert('L'),dtype=np.float32)
    # Keep owner texels chromatically neutral. The engine applies the actual
    # player colour via patternTex rather than mixing with baked pigments.
    neutral = Image.fromarray(np.clip(neutral*.64+20,28,118).astype(np.uint8)).convert('RGBA')
    trim = mask.getchannel('R').crop((512,0,1024,512)).resize(base.size,Image.Resampling.NEAREST)
    return duplicate_atlas(base, Image.composite(neutral,base,trim))


def duplicate_atlas(left, right):
    atlas=Image.new('RGBA',(2*left.width,left.height))
    atlas.paste(left,(0,0))
    atlas.paste(right,(left.width,0))
    return atlas


def encode(candidate, name, template, image, pattern=False):
    # Pillow premultiplies RGBA when resizing. Preserve the pattern RGB first,
    # then restore the native unused zero-alpha channel for each mip.
    if not pattern:
        return candidate.encode(name,template,image,art_version='036')[0]
    master=candidate.output/'authoring/art036'/(name+'.png')
    master.parent.mkdir(parents=True,exist_ok=True)
    image.save(master,optimize=True)
    candidate.masters['files'].append({
        'path':master.relative_to(candidate.output/'authoring').as_posix(),
        'bytes':master.stat().st_size,
        'sha256':hashlib.sha256(master.read_bytes()).hexdigest(),
        'role':'0.3.6 shared dynamic owner mask with native zero alpha',
    })
    levels=[]
    rgb=image.convert('RGB')
    for i in range(max(image.size).bit_length()):
        size=tuple(max(1,d>>i) for d in image.size)
        layer=rgb.resize(size,Image.Resampling.BOX).convert('RGBA')
        layer.putalpha(0)
        with BytesIO() as out:
            layer.save(out,format='DDS',pixel_format='DXT5')
            encoded=out.getvalue()
        assert encoded[84:88]==b'DXT5'
        levels.append((*size,encoded[128:]))
    member=f'art/kr036/architecture/{name}'
    candidate.put(member+'.rrtex',encode_bc3(template,member,levels))
    candidate.textures[name] = {
        'width': image.width, 'height': image.height, 'mips': len(levels),
        'rgba8_decoded_bytes': sum(4*w*h for w,h,_ in levels),
        'bc3_bytes': sum(len(blocks) for _,_,blocks in levels),
    }
    source=candidate.output/'inputs/native'/(member+'.rrtex')
    rr.decode_rrtex(source,output_dds=candidate.stage/'owner-readback.dds',validate_stream=True)
    assert Image.open(candidate.stage/'owner-readback.dds').convert('RGBA').getchannel('A').getextrema()==(0,0)
    return member+'.rrtex'


def classify(group, mask, scale=False):
    p=np.asarray(group['positions'])
    if scale:
        p=scale_positions(p)
    u=np.asarray(group['uv_layers']['UVMap'])
    t=np.asarray(group['triangles'])
    points=p[t]
    cross=np.cross(points[:,1]-points[:,0],points[:,2]-points[:,0])
    area=np.linalg.norm(cross,axis=1)*.5
    uv=u[t].mean(axis=1)
    tile=np.minimum(3,(uv[:,0]*4).astype(int))+4*np.minimum(3,((1-uv[:,1])*4).astype(int))
    graph=coo_matrix((np.ones(t.size,dtype=bool),(t.ravel(),np.roll(t,1,axis=1).ravel())),
                     shape=(len(p),len(p))).tocsr()
    count, labels=connected_components(graph,directed=False)
    island=labels[t[:,0]]
    assert (labels[t]==island[:,None]).all()
    total=np.bincount(island,weights=area,minlength=count)
    vertical=np.bincount(island,weights=area*(abs(cross[:,2])<1.4*area),minlength=count)
    low=np.full(count,np.inf)
    high=np.full(count,-np.inf)
    np.minimum.at(low,labels,p[:,2])
    np.maximum.at(high,labels,p[:,2])
    zones=np.bincount(island*16+tile,weights=area,minlength=count*16).reshape(-1,16)
    effective=np.zeros(count)
    grid=tuple((i/7,j/7,1-(i+j)/7) for i in range(1,7) for j in range(1,7-i))
    tri_uv=u[t]
    for bary in grid:
        sample=np.array(bary)@tri_uv
        x=(sample[:,0]*512).astype(int).clip(0,511)
        y=((1-sample[:,1])*512).astype(int).clip(0,511)
        effective+=np.bincount(island,weights=area*(mask[y,x]>=128)/len(grid),minlength=count)
    return p,t,labels,island,area,total,vertical,low,high,zones,effective


def choose_tint(rows, name, height, target):
    """Assign whole mesh islands, prioritizing architecture above the plinth."""
    total=sum(row[4].sum() for row in rows)
    selected=[np.zeros(len(row[5]),dtype=bool) for row in rows]
    candidates=[]
    for j,row in enumerate(rows):
        _,_,_,_,_,weights,vertical,low,high,zones,effective=row
        safe=np.where((effective>0)&(low>max(.30,height*.086))
                       &(vertical>=weights*(.70 if name in STONE else .15)))[0]
        tile=zones.argmax(axis=1)
        for i in safe:
            if tile[i] not in ACCENTS[name]:
                continue
            order=ACCENTS[name].index(tile[i])
            if name in STONE:
                # Favor the upper tower register, leaving lower ashlar and
                # paving in their natural granite palette.
                order=(order, -int(8*(low[i]+high[i])/(2*height)))
            else:
                order=(order,0)
            candidates.append((order,-effective[i],j,i))
    area=0.
    for _,negative,j,i in sorted(candidates):
        weight=-negative
        if area+weight>target*total:
            continue
        selected[j][i]=True
        area+=weight
        if area>=.995*target*total:
            break
    return selected, round(float(area/total*100),2)


def scale_positions(points):
    result=points.copy()
    # Keep contact with the plinth. The extra vertical lift starts at the
    # first tower course above the courtyard and applies to every visual state.
    result *= 1.30
    result[:,2] += np.maximum(0, points[:,2]-.56)*.15
    return result


def native_scale(positions):
    blender=np.column_stack((-positions[:,0],-positions[:,2],positions[:,1]))
    new=scale_positions(blender)
    return np.column_stack((-new[:,0],new[:,2],-new[:,1]))


def scale_rgm(raw):
    document=rc.parse(raw)
    def scale(chunk):
        payload=bytearray(chunk.payload)
        if chunk.tag==b'LGEO':
            count,=struct.unpack_from('<I',payload)
            coords=np.ndarray((count,4),dtype='<f2',buffer=payload,offset=4)
            assert np.isfinite(coords).all() and np.all(coords[:,3]==0)
            coords[:,:3]=native_scale(coords[:,:3].astype(float))
            return bytes(payload)
        if chunk.tag==b'RFBD':
            assert len(payload)==28 and payload[:4]==b'\1\0\0\0'
            points=np.array(struct.unpack_from('<6f',payload,4)).reshape(2,3)
            struct.pack_into('<6f',payload,4,*scale_positions(points).ravel())
            return bytes(payload)
        return None
    return rc.rebuild(document,scale)


def repaint_geometry(candidate, previous, name, mask):
    path=f'art/kr013/static/{name}/model'
    prior,=(previous/'decoded-final'/name).glob('*/decoded-static.json')
    groups=read_json(prior)['geometry']['groups']
    payload=rc.parse((ROOT/'inputs/native'/(path+'.rrgeom')).read_bytes())
    chunks=[c for c in rc.walk(payload.roots) if c.tag==b'GEOB']
    assert len(chunks)==2*len(groups)
    by_state={}
    for i,g in enumerate(groups):
        lod=g['rig_projection']['lod_palette']['name']
        state=('healthy' if lod.startswith('mesh_healthy') else g['name'].split('_part')[0],lod[-1])
        by_state.setdefault(state,[]).append(i)
    height=max(max(v[2] for v in g['positions']) for g in groups)
    if name=='stone_pagoda':
        height=height*1.30+max(0,height-.56)*.15
    edits={}
    measure={}
    previews=[]
    for state,indices in by_state.items():
        rows=[classify(groups[i],mask,name=='stone_pagoda') for i in indices]
        target=.067 if name in STONE else .095
        masks,coverage=choose_tint(rows,name,height,target)
        if state[0]=='healthy':
            assert 5<=coverage<=25,(name,state,coverage)
            measure[state[1]]=coverage
        for index,row,selected in zip(indices,rows,masks,strict=True):
            g=groups[index]
            chunk=chunks[index*2]
            data=bytearray(chunk.payload)
            count,_,stride,_=struct.unpack_from('<4I',data)
            assert count==g['vertex_count'] and stride==28 and len(data)==16+count*stride
            pos=np.ndarray((count,4),dtype='<f2',buffer=data,offset=16,strides=(stride,2))
            uv=np.ndarray((count,2),dtype='<f2',buffer=data,offset=28,strides=(stride,2))
            prior_uv=np.asarray(g['uv_layers']['UVMap'])
            assert np.array_equal(uv[:,0],prior_uv[:,0])
            assert np.array_equal(1-uv[:,1].astype(float),prior_uv[:,1])
            assert (uv[:,0]>0.006).all() and (uv[:,0]<.994).all()
            masked=selected[row[2]]
            uv[:,0]=uv[:,0]*.5 + .5*masked
            assert np.array_equal(uv[:,0]>.5,masked)
            assert not masked.any() or np.min(row[0][masked,2])>max(.30,height*.086)
            if name=='stone_pagoda':
                assert np.all(pos[:,3]==1)
                pos[:,:3]=native_scale(pos[:,:3].astype(float))
            edits[chunk.offset]=bytes(data)
            if state==('healthy','1'):
                previews.append({'name':g['name'],'positions':row[0].tolist() if name=='stone_pagoda' else g['positions'],
                                 'triangles':g['triangles'],'uv_layers':{'UVMap':np.column_stack((uv[:,0],prior_uv[:,1])).tolist()}})
    assert set(measure)=={'1','2','3'}
    candidate.put(path+'.rrgeom',rc.rebuild(payload,lambda c:edits.get(c.offset)))
    if name=='stone_pagoda':
        candidate.put(path+'.rgm',scale_rgm((ROOT/'inputs/native'/(path+'.rgm')).read_bytes()))
    write_json(candidate.stage/'preview-geometry'/(name+'.json'),previews)
    return measure


class LandmarkCandidate(Candidate):
    def __init__(self, stage):
        self.stage=stage
        self.native=ROOT/'inputs/native'
        self.output=stage/'candidate'
        self.output.mkdir()
        self.manifest=read_json(ROOT/'inputs/native-manifest.json')
        self.masters=read_json(ROOT/'source/master-index.json')
        self.changed={}
        self.textures={}
        self.stock=None

    def put(self, member, data):
        super().put(member,data)
        self.changed[member]['origin']='0.3.6 landmark-specific paint, native UV routing or visual geometry'

def main(stage, previous):
    candidate=LandmarkCandidate(stage)
    raw=(candidate.native/'art/kr013/static/stone_pagoda/model.rrmaterial').read_bytes()
    slots=mv.material_slots(raw)['textures']
    old={key:candidate.image(normalize(slots[key])) for key in ('albedoTexture','normalMap','metalTex','patternTex')}
    base_albedo=old['albedoTexture'][1]
    normal=old['normalMap'][1].resize((1024,1024),Image.Resampling.BOX)
    rough=np.array(old['metalTex'][1].resize((1024,1024),Image.Resampling.BOX))
    rough[:,:,0]=0
    rough[:,:,3]=np.clip(rough[:,:,3].astype(float)*.35+150,190,225).astype(np.uint8)
    material=Image.fromarray(rough)
    pattern=Image.new('RGBA',(1024,512),(0,0,0,0))
    decoration=ImageDraw.Draw(pattern)
    for col in range(4):
        for row in range(4):
            x,y=512+128*col,128*row
            for left,top,right,bottom in ((11,9,34,118),(94,9,117,118),(34,19,94,37),(34,88,94,106)):
                decoration.rectangle((x+left,y+top,x+right,y+bottom),fill=(255,0,0,0))
    replacement={
        'normalMap':encode(candidate,'shared-normal',old['normalMap'][0],duplicate_atlas(normal,normal)),
        'metalTex':encode(candidate,'shared-matte',old['metalTex'][0],duplicate_atlas(material,material)),
        'patternTex':encode(candidate,'raised-owner',old['patternTex'][0],pattern,pattern=True),
    }
    decoded_mask=Image.open(stage/'owner-readback.dds').convert('RGBA')
    right_mask=np.asarray(decoded_mask.getchannel('R'))[:,512:]
    assert right_mask.max()==255 and not np.asarray(decoded_mask.getchannel('R'))[:,:512].any()
    coverage={}
    for name in PALETTES:
        albedo=encode(candidate,name,old['albedoTexture'][0],architecture_paint(name,base_albedo,decoded_mask))
        assert candidate.model('static',name,lambda _,__:replacement|{'albedoTexture':albedo})
        coverage[name]=repaint_geometry(candidate,previous,name,right_mask)
        print(name,coverage[name],flush=True)
    write_json(candidate.output/'inputs/native-manifest.json',candidate.manifest)
    write_json(candidate.output/'source/master-index.json',candidate.masters)
    write_json(stage/'landmarks.json',dict(coverage=coverage,overlay=candidate.changed,
               textures=candidate.textures,zero_owner_colour_on_ground_islands=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',type=Path)
    parser.add_argument('previous',type=Path)
    args=parser.parse_args()
    main(args.stage,args.previous)
