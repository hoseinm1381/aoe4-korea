"""Check the final 0.3.5 playable ZIP and decode its decorated buildings."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from zipfile import ZipFile

from PIL import Image

from architecture import ROOT, coverage, samples
from runtime import EXT, read_json, stock_game, write_json

sys.path.insert(0, str(ROOT / 'tools/art013'))
import readback_probe as reader


def digest(file):
    with file.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def verify(stage):
    receipt = read_json(ROOT / 'docs/BUILD_VERIFICATION.json')
    policy = read_json(ROOT / 'source/update-035-policy.json')
    contract = read_json(ROOT / 'docs/update_035/architecture.json')
    assert receipt['version'] == '0.3.5'
    for mode in ('changed', 'added', 'removed'):
        assert receipt[mode+'_members'] == policy['allowed_'+mode], mode
    package = ROOT / 'release' / receipt['zip_name']
    assert digest(package) == receipt['zip_sha256']
    archive = stage / 'final-from-zip.sga'
    with ZipFile(package) as bundle:
        assert bundle.testzip() is None
        with bundle.open('korea/korea.sga') as source, archive.open('xb') as target:
            shutil.copyfileobj(source, target)
    assert digest(archive) == receipt['archive_sha256']
    game = stock_game.current()
    listing = game.archiver.run(['list', str(archive), '--verify'])
    assert listing['archive']['verification']['verified']
    assert listing['archive']['name'] == receipt['owner'].replace('-', '')
    assert len(listing['members']) == receipt['members']
    names = set(contract['landmarks']) | set(contract['shelters'])
    model_folders = tuple(f'art/kr013/static/{name}/' for name in sorted(names))
    indexed = [m for m in listing['members'] if m['path'].startswith(
        (*model_folders, 'art/kr035/architecture/', 'art/kr014/patterns/', 'art/kr014/shared/'))]
    reader.INDEX = stage / 'final.sqlite3'
    reader.create_index(archive, indexed, listing['archive']['name'])
    config = read_json(stage / 'isolated-config.json')
    config['index_path'] = str(reader.INDEX)
    write_json(stage / 'final-config.json', config)

    def model(name):
        stem = f'art/kr013/static/{name}/model'
        core = EXT / 'bin/core/garrison-core.exe'
        process = subprocess.run(
            [core, 'convert', 'decode-static', '--logical-path', stem+'.rgm',
             '--config', stage/'final-config.json', '--index', reader.INDEX,
             '--output-root', stage/'decoded-final'/name],
            capture_output=True, check=True, timeout=120)
        decoded = read_json(json.loads(process.stdout)['manifest_path'])
        assert not decoded['blockers'] and not decoded['missing_textures'], name
        before, = (stage/'decoded-isolated/static'/name).glob('*/decoded-static.json')
        groups = decoded['geometry']['groups']
        assert groups == read_json(before)['geometry']['groups'], name
        row = contract['landmarks'].get(name) or contract['shelters'][name]
        mask = next(t for t in decoded['textures'] if t['logical_path'] == row['mask'])
        image = Image.open(mask['projection']['path']).convert('RGBA')
        assert mask['resource']['sha256'] == contract['overlay'][row['mask']]['sha256']
        assert image.getchannel('G').getextrema() == (0, 0)
        assert image.getchannel('B').getextrema() == (0, 0)
        if name in contract['landmarks']:
            actual = [coverage(image, samples([
                g for g in groups if g['name'].startswith('mesh_healthy') and
                g['rig_projection']['lod_palette']['name'].endswith(f'lod{lod}')
            ], image.width)) for lod in (1, 2, 3)]
        else:
            healthy = [g for g in groups if g['name'] == 'mesh_healthy']
            points = samples(healthy, image.width, 'korea_camp_weathered_timber')
            base, = (stage/'decoded-isolated/ordinary'/name).glob('*/decoded-static.json')
            base_points = samples(read_json(base)['geometry']['groups'], image.width, 'no_owner_accent')
            actual = coverage(image, points + base_points)
        assert actual == row['final_percent'], (name, actual, row['final_percent'])
        print('FINAL_DECODE', name, actual, flush=True)
        return name, {'player_colour_percent': actual, 'geometry_identical': True,
                      'missing_texture_references': 0, 'mask_mips': mask['mip_count']}

    with ThreadPoolExecutor(max_workers=3) as pool:
        models = dict(pool.map(model, sorted(names)))
    write_json(ROOT/'docs/update_035/final-readback.json', {
        'archive_sha256': receipt['archive_sha256'], 'zip_sha256': receipt['zip_sha256'],
        'models': models, 'preserved_members': receipt['preserved_baseline_members'],
        'native_match': 'pending',
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', type=Path)
    verify(parser.parse_args().stage)
