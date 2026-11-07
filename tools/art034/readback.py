"""Read back the candidate's Tiger Hunters and weapon props through Garrison."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import subprocess
import sys

root,stage=map(Path,sys.argv[1:])
sys.path[:0]=[str(root/'tools'),str(root/'tools/art013')]
from runtime import EXT, read_json, write_json
import readback_probe as reader

report=read_json(stage/'assembly-bound/report.json')
archive=Path(report['archive'])
arch=EXT/'bin/sga-archiver.exe'
core=EXT/'bin/core/garrison-core.exe'
listing=json.loads(subprocess.check_output([arch,'list',archive,'--verify']))
assert listing['archive']['verification']['verified']
assert listing['archive']['name']=='748d61b94d3e4cf3a506a9ac1f992d1d'
specs = [(f'kr_tiger_hunter_a{age}',f'art/kr013/units/kr_tiger_hunter_a{age}/model',True) for age in (2,3,4)]
for row in read_json(stage/'weapons.json')['models']:
    key=row['private'].split('/')[-2]
    specs.append((key,row['private'],False))
dirs={stem.rsplit('/',1)[0] for _,stem,_ in specs}
items=[m for m in listing['members'] if any(m['path'].startswith(folder+'/') for folder in dirs)]
reader.INDEX=stage/'bound.sqlite3'
if not reader.INDEX.exists():
    reader.create_index(archive,items,listing['archive']['name'])
config=read_json(reader.ORIGINAL_CONFIG)
(stage/'isolated-no-game/cardinal/archives').mkdir(parents=True,exist_ok=True)
config.update(index_path=str(reader.INDEX),game_root=str(stage/'isolated-no-game'))
write_json(stage/'isolated.json',config)
expected={}
for line in (stage/'export.log').read_text(errors='replace').splitlines():
    if line.startswith('TIGER_EXPORT'):
        _,asset,counts=line.split(maxsplit=2)
        expected[asset]=json.loads(counts)

def verify(spec):
    asset,path,tiger=spec
    process=subprocess.run([core,'convert','decode-static','--logical-path',path+'.rgm',
          '--config',stage/'isolated.json','--index',reader.INDEX,
          '--output-root',stage/'decoded-bound'/asset],capture_output=True,text=True,errors='replace',timeout=120)
    assert process.returncode==0, (asset,process.stderr,process.stdout)
    manifest=Path(json.loads(process.stdout)['manifest_path'])
    decoded=read_json(manifest)
    assert not decoded['blockers'], (asset,decoded['blockers'])
    groups=decoded['geometry']['groups']
    if tiger:
        assert decoded['skeleton']['bone_count']==48
        assert decoded['completeness']['unresolved_rig_groups']==0
        lods=[[],[],[]]
        for g in groups:
            idx=int(g['rig_projection']['lod_palette']['name'][-1])-1
            lods[idx].append(g)
        counts=[sum(g['triangle_count'] for g in tier) for tier in lods]
        assert counts==expected[asset],(asset,counts,expected[asset])
        assert all(t.endswith('chi_skin_tinting_lut.rrtex') for t in decoded['missing_textures'])
    else:
        counts=[g['triangle_count'] for g in groups]
        assert len(counts)==3 and all(counts),asset
        assert all(not t.startswith('art/kr034') for t in decoded['missing_textures'])
    print('DECODED',asset,counts,flush=True)
    return dict(asset=asset,triangles=counts,manifest=str(manifest.resolve().relative_to(stage.resolve())),bone_count=decoded['skeleton'].get('bone_count',0))

with ThreadPoolExecutor(max_workers=3) as pool:
    result=list(pool.map(verify,specs))
write_json(stage/'readback.json',result)
