"""Compose a 0.3.6 candidate over the exact verified 0.3.5 player archive."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
from runtime import EXT, import_table, read_json, stock_game, write_json


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def snapshot(stage, previous):
    baseline = read_json(ROOT/'docs/BUILD_VERIFICATION.json')
    config = read_json(ROOT/'project.json')
    assert baseline['version']=='0.3.5' and config['version']=='0.3.5'
    source = previous/'final-from-zip.sga'
    assert digest(source)==baseline['archive_sha256']
    old = read_json(Path(baseline['assembly_path'])/'report.json')['members']
    assert len(old)==baseline['members']
    recipe = read_json(previous/'build/build-recipe.json')
    art = read_json(stage/'landmarks.json')['overlay']
    overlay = {member: stage/'candidate/inputs/native'/member for member in art}
    assert all(digest(path)==art[member]['sha256'] for member,path in overlay.items())
    for p in read_json(stage/'gameplay.json')['changed_tables']:
        member=p.removeprefix('source/tables/').removesuffix('.json')
        path=stage/'compiled'/member
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(import_table(read_json(ROOT/p)))
        overlay[member]=path
    overlay['scar/korea/effects.scar']=ROOT/'source/scar/korea/effects.scar'
    records={}
    for member,path in overlay.items():
        records[member]={'toc':old.get(member,{}).get('toc','data'),
                         'sha256':digest(path),'bytes':path.stat().st_size}
    changed=set(overlay)&set(old)
    added=set(overlay)-set(old)
    assert len(changed)==23 and len(added)==12, (len(changed),len(added))
    assert all(records[m]!=old[m] for m in changed)
    for family in ('attributes','members'):
        for entry in recipe[family]:
            member=entry['member']
            if member in changed:
                entry['file']=str(overlay[member])
                entry['sha256']=records[member]['sha256']
    for member in sorted(added):
        recipe['members'].append(dict(member=member,file=str(overlay[member]),
                                      sha256=records[member]['sha256'],toc='data'))
    write_json(stage/'validation-recipe.json',recipe)
    expected=old|records
    write_json(stage/'expected-members.json',expected)
    write_json(stage/'policy.json',dict(baseline_version='0.3.5',
               allowed_changed=sorted(changed),allowed_added=sorted(added),allowed_removed=[]))
    (stage/'baseline-members.json.gz').write_bytes(gzip.compress(
        json.dumps({'members':old},sort_keys=True,separators=(',',':')).encode(),mtime=0))
    files=stage/'overlay.txt'
    files.write_text(''.join(f'{member}={path}\n' for member,path in sorted(overlay.items())),
                     encoding='utf-8')
    return source, files


def run(stage, previous):
    source, files = snapshot(stage, previous)
    archiver = EXT/'bin/sga-archiver.exe'
    core = EXT/'bin/core/garrison-core.exe'
    output = stage/'assembly'
    output.mkdir()
    archive=output/'korea.sga'
    with (stage/'overlay.log').open('w',encoding='utf-8') as log:
        subprocess.run([archiver,'set-members',source,files,archive,'--alias','data'],
                       stdout=log,stderr=subprocess.STDOUT,check=True)
    print('CANDIDATE_SGA',archive,archive.stat().st_size,flush=True)
    expected=read_json(stage/'expected-members.json')
    listing=stock_game.current().archiver.run(['list',str(archive),'--verify'])
    assert listing['archive']['verification']['verified']
    assert listing['archive']['name']=='748d61b94d3e4cf3a506a9ac1f992d1d'
    assert {m['path']:(m['toc'],m['size']) for m in listing['members']}=={
        p:(m['toc'],m['bytes']) for p,m in expected.items()}
    # The ordinary full-build finalizer uses this complete extraction for its
    # separate per-member SHA-256 and declaration checks.
    readback=output/'readback'
    stock_game.current().archiver.run(['extract',str(archive),str(readback),'--filter',''])
    assert (readback/'garrison/civilizations.json').is_file()
    write_json(output/'report.json',dict(archive=str(archive),members=expected))
    print('FULL_SGA_READBACK_READY',len(expected),flush=True)
    with (stage/'validate.log').open('w',encoding='utf-8') as log:
        subprocess.run([core,'civilization','validate',stage/'validation-recipe.json'],
                       stdout=log,stderr=subprocess.STDOUT,check=True)
    print('NATIVE_VALIDATION_PASS',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',type=Path)
    parser.add_argument('previous',type=Path)
    options=parser.parse_args()
    run(options.stage,options.previous)
