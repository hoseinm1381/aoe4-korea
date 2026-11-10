"""Build the sRGB-only Korean landmark hotfix from the verified 0.3.6 ZIP."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build import digest, finalize
from runtime import EXT, import_table, read_json, rgd, stock_game, write_json
from voice020_release import retained_codex


def stage_archive(stage):
    base=read_json(ROOT/'docs/BUILD_VERIFICATION.json')
    assert base['version']=='0.3.6'
    old=ROOT/'release'/base['zip_name']
    assert digest(old)==base['zip_sha256'] and list(old.parent.iterdir())==[old]
    prior=Path(base['assembly_path'])
    old_members=read_json(prior/'report.json')['members']
    assert len(old_members)==base['members']
    source=stage/'baseline.sga'
    with ZipFile(old) as bundle, bundle.open('korea/korea.sga') as src, source.open('xb') as dest:
        shutil.copyfileobj(src,dest)
    assert digest(source)==base['archive_sha256']
    files=read_json(stage/'art-overlay.json')
    assert len(files)==9 and set(files)<=set(old_members)
    overlay={key:{'toc':v['toc'],'bytes':v['bytes'],'sha256':v['sha256']} for key,v in files.items()}
    assert all(digest(stage/'overlay'/name)==row['sha256'] for name,row in overlay.items())
    expected=old_members|overlay
    members=stage/'members.txt'
    members.write_text(''.join(f'{m}={stage/"overlay"/m}\n' for m in sorted(files)),encoding='utf-8')
    assembly=stage/'assembly'
    assembly.mkdir()
    archive=assembly/'korea.sga'
    with (stage/'compose.log').open('w',encoding='utf-8') as log:
        subprocess.run([EXT/'bin/sga-archiver.exe','set-members',source,members,archive],
                       check=True,stdout=log,stderr=subprocess.STDOUT)
    game=stock_game.current()
    listing=game.archiver.run(['list',str(archive),'--verify'])
    assert listing['archive']['verification']['verified']
    assert listing['archive']['name']==base['owner'].replace('-','')
    assert {m['path']:(m['toc'],m['size']) for m in listing['members']}=={
        p:(m['toc'],m['bytes']) for p,m in expected.items()}
    write_json(assembly/'report.json',dict(archive=str(archive),members=expected))
    (stage/'baseline-members.json.gz').write_bytes(gzip.compress(
        json.dumps({'members':old_members},sort_keys=True,separators=(',',':')).encode(),mtime=0))
    write_json(stage/'policy.json',dict(baseline_version='0.3.6',allowed_changed=sorted(overlay),
                                      allowed_added=[],allowed_removed=[]))
    print('ART_ARCHIVE_READY',archive,flush=True)
    game.archiver.run(['extract',str(archive),str(assembly/'readback'),'--filter',''])
    print('READBACK_READY',len(expected),flush=True)


def package(stage):
    base=read_json(ROOT/'docs/BUILD_VERIFICATION.json')
    config=read_json(ROOT/'project.json')
    assert (base['version'],config['version'])==('0.3.6','0.3.7')
    old=ROOT/'release'/base['zip_name']
    assert list(old.parent.iterdir())==[old] and digest(old)==base['zip_sha256']
    prior=Path(base['assembly_path']).parent
    recipe=read_json(prior/'validation-recipe.json')
    assembly=stage/'assembly'
    members=read_json(assembly/'report.json')['members']
    assert (assembly/'readback/garrison/civilizations.json').is_file()
    allowed=set(read_json(stage/'policy.json')['allowed_changed'])
    expected={}
    for row in recipe['attributes']+recipe['members']:
        member=row['member']
        path=Path(row['file'])
        if member in allowed:
            path=ROOT/'inputs/native'/member
            row['file']=str(path)
            row['sha256']=members[member]['sha256']
        expected[member]={'toc':row.get('toc','attrib'),'sha256':row['sha256'],'bytes':path.stat().st_size}
    write_json(stage/'validation-recipe.json',recipe)
    with (stage/'validate.log').open('w',encoding='utf-8') as log:
        subprocess.run([EXT/'bin/core/garrison-core.exe','civilization','validate',
                        stage/'validation-recipe.json'],check=True,stdout=log,stderr=subprocess.STDOUT)
    print('NATIVE_VALIDATION_PASS',flush=True)
    tables={row['member']:None for row in recipe['attributes']}
    codex=next(member for member in tables if member.startswith('attrib/codex/'))
    tables[codex]=rgd.read(import_table(read_json(ROOT/'source/tables'/(codex+'.json'))))
    _,report=retained_codex(tables,config)
    fingerprint=hashlib.sha256(json.dumps(expected,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    out=stage/'package'
    out.mkdir()
    finalize(out,config,expected,read_json(ROOT/'inputs/native-manifest.json'),tables,
             fingerprint,base,assembly,report)
    receipt=read_json(ROOT/'docs/BUILD_VERIFICATION.json')
    assert receipt['changed_members']==read_json(stage/'policy.json')['allowed_changed']
    assert not receipt['added_members'] and not receipt['removed_members']
    rollback=ROOT/config['rollback_folder']/base['zip_sha256'][:12]/base['zip_name']
    assert digest(rollback)==base['zip_sha256']
    print('VERIFIED_037',receipt['zip_name'],receipt['zip_sha256'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('stage','package'))
    parser.add_argument('stage',type=Path)
    args=parser.parse_args()
    (stage_archive if args.action=='stage' else package)(args.stage)
