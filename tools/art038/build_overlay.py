"""Compose, independently read back, and package the Korea 0.3.8 visual update."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from stage_art import FLAGS, UI

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'art013'))
from build import digest, finalize, run
import readback_probe as reader
from runtime import EXT, ROOT, import_table, read_json, rgd, stock_game, write_json
from voice020_release import retained_codex

CORE = EXT / 'bin/core/garrison-core.exe'


def compose_and_verify(stage):
    base = read_json(ROOT / 'docs/BUILD_VERIFICATION.json')
    assert base['version'] == '0.3.7'
    release = ROOT / 'release' / base['zip_name']
    assert digest(release) == base['zip_sha256']
    before = Path(base['assembly_path'])
    source = before / 'korea.sga'
    assert digest(source) == base['archive_sha256']
    old_members = read_json(before / 'report.json')['members']
    overlay = read_json(stage / 'overlay.json')
    names = sorted(read_json(ROOT / 'docs/update_036/landmark-native-readback.json'))
    expected_scope = {f'{UI}/{flag}.rrtex' for flag in FLAGS}
    expected_scope.update(f'art/kr013/static/{name}/model{ext}'
                          for name in names for ext in ('.rgm', '.rrgeom'))
    assert set(overlay) == expected_scope <= set(old_members)
    for member, row in overlay.items():
        path = stage / 'overlay' / member
        assert row['sha256'] == digest(path) and row['bytes'] == path.stat().st_size
        assert old_members[member]['sha256'] != row['sha256']
        assert row['toc'] == old_members[member]['toc']

    assembly = stage / 'assembly'
    assembly.mkdir()
    archive = assembly / 'korea.sga'
    members = stage / 'members.txt'
    members.write_text(''.join(f'{m}={stage/"overlay"/m}\n' for m in sorted(overlay)),
                       encoding='utf-8')
    run([EXT / 'bin/sga-archiver.exe', 'set-members', source, members, archive],
        stage / 'compose.log')
    game = stock_game.current()
    listing = game.archiver.run(['list', str(archive), '--verify'])
    assert listing['archive']['verification']['verified']
    assert listing['archive']['name'] == base['owner'].replace('-', '')
    expected = old_members | overlay
    assert {m['path']: (m['toc'], m['size']) for m in listing['members']} == {
        m: (row['toc'], row['bytes']) for m, row in expected.items()}
    write_json(assembly / 'report.json', dict(archive=str(archive), members=expected))
    print('ARCHIVE_SCOPE_VERIFIED', len(expected_scope), flush=True)
    game.archiver.run(['extract', str(archive), str(assembly / 'readback'), '--filter', ''])
    for member, row in expected.items():
        assert digest(assembly / 'readback' / member) == row['sha256'], member
    print('ALL_MEMBERS_READ_BACK', len(expected), flush=True)

    prefixes = tuple(f'art/kr013/static/{name}/' for name in names)
    indexed = [m for m in listing['members']
               if m['path'].startswith((*prefixes, 'art/kr036/architecture/'))]
    reader.INDEX = stage / 'review.sqlite3'
    reader.create_index(archive, indexed, listing['archive']['name'])
    config = read_json(before.parent / 'review-config.json')
    config['index_path'] = str(reader.INDEX)
    review_config = stage / 'review-config.json'
    write_json(review_config, config)
    report = {}
    for name in names:
        stem = f'art/kr013/static/{name}/model'
        result = subprocess.run(
            [CORE, 'convert', 'decode-static', '--logical-path', stem + '.rgm',
             '--config', review_config, '--index', reader.INDEX,
             '--output-root', stage / 'decoded' / name],
            check=True, capture_output=True, timeout=150)
        model = read_json(json.loads(result.stdout)['manifest_path'])
        old, = (before.parent / 'decoded' / name).glob('*/decoded-static.json')
        original = read_json(old)
        assert not model['blockers'] and not model['missing_textures'], name
        original_groups = original['geometry']['groups']
        healthy = {}
        for group in original_groups:
            palette = group['rig_projection']['lod_palette']['name']
            if palette.startswith('mesh_healthy'):
                level = palette[-1]
                healthy[level] = healthy.get(level, 0) + group['triangle_count']
        assert set(healthy) == {'1', '2', '3'} and healthy['1'] > healthy['3'], name
        retained = [g for g in original_groups if not (
            (palette := g['rig_projection']['lod_palette']['name']).startswith('mesh_healthy')
            and palette[-1] in '23')]
        for old_group, new_group in zip(retained, model['geometry']['groups'], strict=True):
            for key in ('name', 'triangle_count', 'positions', 'triangles', 'normals',
                        'uv_layers', 'skin_indices', 'skin_weights'):
                assert new_group[key] == old_group[key], (name, key)
            assert new_group['rig_projection']['lod_palette']['name'] == \
                old_group['rig_projection']['lod_palette']['name'], name
        report[name] = {'old_healthy_triangles': healthy,
                        'current_healthy_triangles': healthy['1'],
                        'other_state_meshes_preserved': True}
        print('LANDMARK_NATIVE_READBACK', name, healthy, flush=True)

    write_json(stage / 'geometry-verification.json', report)
    write_json(stage / 'policy.json',
               dict(baseline_version='0.3.7', allowed_changed=sorted(overlay),
                    allowed_added=[], allowed_removed=[]))
    (stage / 'baseline-members.json.gz').write_bytes(gzip.compress(
        json.dumps({'members': old_members}, sort_keys=True, separators=(',', ':')).encode(),
        mtime=0))


def package(stage):
    base = read_json(ROOT / 'docs/BUILD_VERIFICATION.json')
    config = read_json(ROOT / 'project.json')
    assert (base['version'], config['version']) == ('0.3.7', '0.3.8')
    assert len(read_json(stage / 'geometry-verification.json')) == 9
    assert digest(ROOT / 'release' / base['zip_name']) == base['zip_sha256']
    assert digest(ROOT / 'source/presentation/cover.png') == digest(stage / 'cover.png')
    native = read_json(ROOT / 'inputs/native-manifest.json')
    recipe = read_json(Path(base['assembly_path']).parent / 'validation-recipe.json')
    assembly = stage / 'assembly'
    members = read_json(assembly / 'report.json')['members']
    overlay = read_json(stage / 'overlay.json')
    expected = {}
    for row in recipe['attributes'] + recipe['members']:
        member = row['member']
        path = Path(row['file'])
        if member in overlay:
            path = ROOT / 'inputs/native' / member
            row['file'] = str(path)
            row['sha256'] = overlay[member]['sha256']
            assert digest(path) == row['sha256'] == native[member]['sha256'], member
        expected[member] = {'toc': row.get('toc', 'attrib'), 'sha256': row['sha256'],
                            'bytes': path.stat().st_size}
    assert set(overlay) <= set(expected)
    recipe_path = stage / 'validation-recipe.json'
    write_json(recipe_path, recipe)
    run([CORE, 'civilization', 'validate', recipe_path], stage / 'validate.log')
    print('NATIVE_VALIDATION_PASS', len(recipe['attributes']), flush=True)

    tables = {row['member']: None for row in recipe['attributes']}
    codex = next(member for member in tables if member.startswith('attrib/codex/'))
    tables[codex] = rgd.read(import_table(read_json(ROOT / 'source/tables' / (codex + '.json'))))
    _, report = retained_codex(tables, config)
    fingerprint = hashlib.sha256(
        json.dumps(expected, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    out = stage / 'package'
    out.mkdir()
    finalize(out, config, expected, native, tables, fingerprint, base, assembly, report)
    receipt = read_json(ROOT / 'docs/BUILD_VERIFICATION.json')
    assert receipt['changed_members'] == sorted(overlay)
    assert not receipt['added_members'] and not receipt['removed_members']
    rollback = ROOT / config['rollback_folder'] / base['zip_sha256'][:12] / base['zip_name']
    assert digest(rollback) == base['zip_sha256']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('verify', 'package'))
    parser.add_argument('stage', type=Path)
    args = parser.parse_args()
    (compose_and_verify if args.action == 'verify' else package)(args.stage)
