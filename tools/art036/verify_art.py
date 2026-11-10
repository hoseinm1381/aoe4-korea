"""Read back 0.3.6 landmark masks, LODs, geometry and native materials."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'tools/art013')]
from runtime import EXT, read_json, stock_game, write_json
from landmarks import scale_positions
import readback_probe as reader


def projected_coverage(groups, mask):
    selected, total = 0., 0.
    h,w=mask.shape
    samples=tuple((i/7,j/7,1-(i+j)/7) for i in range(1,7) for j in range(1,7-i))
    for g in groups:
        indices=np.asarray(g['triangles'])
        p=np.asarray(g['positions'])
        tris=p[indices]
        area=np.linalg.norm(np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]),axis=1)/2
        uv=np.asarray(g['uv_layers']['UVMap'])
        assigned=uv[:,0]>.5
        assert (assigned[indices]==assigned[indices[:,0],None]).all()
        if assigned.any():
            assert p[assigned,2].min()>.30
        tri_uv=uv[indices]
        for bary in samples:
            xy=np.array(bary)@tri_uv
            u=(xy[:,0]*w).astype(int).clip(0,w-1)
            v=((1-xy[:,1])*h).astype(int).clip(0,h-1)
            selected+=area[mask[v,u]>=128].sum()
        total+=area.sum()*len(samples)
    return round(float(100*selected/total),2)


def run(stage, previous):
    archive=stage/'assembly/korea.sga'
    contract=read_json(stage/'landmarks.json')
    listing=stock_game.current().archiver.run(['list',str(archive),'--verify'])
    assert listing['archive']['verification']['verified']
    assert listing['archive']['name']=='748d61b94d3e4cf3a506a9ac1f992d1d'
    assets=sorted(contract['coverage'])
    prefixes=tuple(f'art/kr013/static/{name}/' for name in assets)
    indexed=[m for m in listing['members'] if m['path'].startswith((*prefixes,'art/kr036/architecture/'))]
    reader.INDEX=stage/'review.sqlite3'
    reader.create_index(archive,indexed,listing['archive']['name'])
    config=read_json(previous/'isolated-config.json')
    config['index_path']=str(reader.INDEX)
    write_json(stage/'review-config.json',config)
    core=EXT/'bin/core/garrison-core.exe'

    def inspect(asset):
        path=f'art/kr013/static/{asset}/model'
        proc=subprocess.run([core,'convert','decode-static','--logical-path',path+'.rgm',
                             '--config',stage/'review-config.json','--index',reader.INDEX,
                             '--output-root',stage/'decoded'/asset],
                             check=True,capture_output=True,timeout=120)
        model=read_json(json.loads(proc.stdout)['manifest_path'])
        assert not model['blockers'] and not model['missing_textures'],asset
        old,=(previous/'decoded-final'/asset).glob('*/decoded-static.json')
        old_groups=read_json(old)['geometry']['groups']
        groups=model['geometry']['groups']
        textures={t['logical_path']:t for t in model['textures']}
        mask_path='art/kr036/architecture/raised-owner.rrtex'
        assert set(textures)=={mask_path,*[f'art/kr036/architecture/{t}.rrtex'
            for t in (asset,'shared-normal','shared-matte')]}
        for path,t in textures.items():
            assert t['resource']['sha256']==contract['overlay'][path]['sha256']
        mask=np.asarray(Image.open(textures[mask_path]['projection']['path']).convert('RGBA'))
        assert not mask[:,:,1:].any() and not mask[:,:512,0].any()
        levels={key:[] for key in ('1','2','3')}
        for before,after in zip(old_groups,groups,strict=True):
            for k in ('name','triangle_count','triangles','skin_indices','skin_weights','normals'):
                assert before[k]==after[k],(asset,k)
            ref=np.asarray(before['positions'])
            if asset=='stone_pagoda':
                ref=scale_positions(ref)
                assert np.max(abs(np.asarray(after['positions'])-ref))<.012
            else:
                assert before['positions']==after['positions']
            uv0,uv1=(np.asarray(g['uv_layers']['UVMap']) for g in (before,after))
            assert np.array_equal(uv0[:,1],uv1[:,1])
            np.testing.assert_allclose(uv0[:,0],(uv1[:,0]%.5)*2,atol=.001,rtol=0)
            lod=after['rig_projection']['lod_palette']['name']
            if lod.startswith('mesh_healthy'):
                levels[lod[-1]].append(after)
        result={lod:projected_coverage(rows,mask[:,:,0]) for lod,rows in levels.items()}
        assert all(5<=value<=25 for value in result.values()),(asset,result)
        assert all(abs(result[lod]-contract['coverage'][asset][lod])<.35 for lod in levels),(asset,result)
        print('LANDMARK_NATIVE_READBACK',asset,result,flush=True)
        return asset, {'coverage_percent':result,'missing_textures':0,'terrain_mask_samples':0,
                       'triangle_topology_and_skin_preserved':True,
                       'max_healthy_height':max(max(p[2] for p in g['positions']) for g in levels['1'])}

    with ThreadPoolExecutor(max_workers=3) as pool:
        readback=dict(pool.map(inspect,assets))
    write_json(stage/'landmark-native-readback.json',readback)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',type=Path)
    parser.add_argument('previous',type=Path)
    args=parser.parse_args()
    run(args.stage,args.previous)
