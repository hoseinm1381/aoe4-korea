"""Compose cavalry visual resources with exact donor merge palettes."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(os.environ.get('KOREA_ROOT', Path(__file__).resolve().parents[2]))
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'tools/art013')]
from art016.repair import one, rename_model, skins
from rig_contract import read_contract
from runtime import EXT, read_json, write_json
from garrison_shared import model_variants as mv, relic_chunky as rc, rrtex_decoder as rr


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def arch(*args):
    return json.loads(subprocess.check_output([EXT/'bin/sga-archiver.exe', *map(str, args)]))


def exact_native_rig(cooked, stock, mount):
    parts = [c for c in rc.walk(rc.parse(stock).roots)
             if c.tag == b'SKMS' and c.decoded_name.startswith('chi_horse_') == mount]
    assert len(parts) == 1
    donor_skin, inverse = [next(c.payload for c in parts[0].children if c.tag == tag)
                           for tag in (b'SKIN', b'SKEL')]
    cooked_skin = skins(one(cooked,b'SKIN').payload)
    donor_names = [(x['name'],x['parent']) for x in skins(donor_skin)]
    assert [(x['name'],x['parent']) for x in cooked_skin] == donor_names, donor_names
    assert read_contract(cooked)['bones'] == read_contract(stock)['bones']
    # No vertex/index buffer or LOD palette index is remapped. The verified
    # order lets us restore exact stock local and inverse bind matrices.
    bind = {b'SKLN': one(stock,b'SKLN').payload, b'SKIN': donor_skin, b'SKEL': inverse}
    out = rc.rebuild(rc.parse(cooked), lambda c: bind.get(c.tag))
    assert all(one(out,tag).payload == data for tag,data in bind.items())
    return out, len(donor_names)


def prepare(stage, old):
    candidate = stage/'candidate'
    baseline = read_json(old/'assembly/report.json')
    prior = baseline['members']
    source = Path(baseline['archive'])
    assert digest(source) == baseline['sha256'] == read_json(ROOT/'docs/BUILD_VERIFICATION.json')['archive_sha256']
    assert baseline['race'] == 'korea' and len(prior) == 10282
    manifest = read_json(ROOT/'inputs/native-manifest.json')
    master = read_json(ROOT/'source/master-index.json')
    specs = read_json(stage/'assets.json')
    assert len(specs) == 16
    overlay = {}
    receipts = []
    for spec in specs:
        asset, tier = spec['asset'], spec['tier']
        logical = f'art/kr013/units/{asset}/model'
        source_path = stage/'refined-extract'/logical
        donor_file = next((stage/'donors'/tier).glob('*/source/art/civilizations/chinese/animals/*combined*/*.rgm'))
        stock = donor_file.read_bytes()
        cooked = source_path.with_suffix('.rgm').read_bytes()
        bound, skin_count = exact_native_rig(cooked, stock, spec['part']=='horse')
        mesh = asset+'_mesh'
        old_mat = (ROOT/'inputs/native'/logical).with_suffix('.rrmaterial').read_bytes()
        old_slots = mv.material_slots(old_mat)['textures']
        cooked_slots = mv.material_slots(source_path.with_suffix('.rrmaterial').read_bytes())['textures']
        payloads = {
            logical+'.rgm': rename_model(bound, 'unit_mesh', mesh),
            logical+'.rrgeom': rename_model(source_path.with_suffix('.rrgeom').read_bytes(), 'unit_mesh', mesh),
        }
        assert source_path.with_suffix('.rgo').read_bytes() == (ROOT/'inputs/native'/logical).with_suffix('.rgo').read_bytes()
        replacements = {}
        for slot in ('albedoTexture','normalMap','metalTex','patternTex'):
            member = cooked_slots[slot].replace(chr(92),'/')
            tex = stage/'refined-extract'/member
            assert tex.parent == source_path.parent
            rr.decode_rrtex(tex, output_dds=stage/'textures-refined'/asset/(slot+'.dds'), validate_stream=True)
            payloads[member] = tex.read_bytes()
            replacements[slot] = cooked_slots[slot]
        material = mv.rewrite_material(old_mat,replacements,{})
        assert mv.material_slots(material)['textures'] == old_slots | replacements
        payloads[logical+'.rrmaterial'] = material
        for member,data in payloads.items():
            path = candidate/'inputs/native'/member
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(data)
            overlay[member] = path
            row = {'toc':'data','bytes':len(data),'sha256':digest(path),'origin':'0.3.3 cavalry CLI cook'}
            manifest[member] = row
        folder = stage/'authoring'/asset
        for path in sorted(folder.iterdir()):
            assert path.suffix in {'.blend','.png'}
            rel = f'art033/{asset}/{path.name}'
            p = candidate/'authoring'/rel
            p.parent.mkdir(parents=True,exist_ok=True)
            p.write_bytes(path.read_bytes())
            master['files'].append({'path':rel,'bytes':p.stat().st_size,'sha256':digest(p),
                                    'role':'editable rebuilt cavalry model or shader atlas'})
        receipts.append({k:spec[k] for k in ('asset','family','age','part','tier')} |
                        {'rig_sha256':hashlib.sha256(stock).hexdigest(),'skin_bones':skin_count,
                         'model_sha256':digest(overlay[logical+'.rgm']),
                         'exact_stock_skin_and_owner_binds':True})
        print('STAGED',asset,skin_count,flush=True)
    overwritten_textures = {m for m in overlay if m in prior and m.endswith('.rrtex')}
    for p in (ROOT/'inputs/native/art').rglob('*.rrmaterial'):
        member = p.relative_to(ROOT/'inputs/native').as_posix()
        if member in overlay:
            continue
        raw = p.read_bytes()
        assert not any(m.replace('/',chr(92)).encode() in raw for m in overwritten_textures), member
    write_json(candidate/'inputs/native-manifest.json',manifest)
    write_json(candidate/'source/master-index.json',master)
    write_json(stage/'models.json',receipts)
    write_json(stage/'overlay.json',{m:str(p) for m,p in overlay.items()})
    policy = {'allowed_changed':sorted(set(overlay)&set(prior)),'allowed_added':sorted(set(overlay)-set(prior)),'allowed_removed':[]}
    assert len(policy['allowed_changed']) == 96 and len(policy['allowed_added']) == 16, policy
    write_json(candidate/'source/update-033-policy.json',policy)
    assembly = stage/'assembly-refined'
    assembly.mkdir(exist_ok=True)
    archive = assembly/'korea.sga'
    lines = stage/'archive-overlay.txt'
    lines.write_text(''.join(f'{m}={p.as_posix()}\n' for m,p in overlay.items()),encoding='utf-8')
    arch('set-members',source,lines,archive,'--alias','data')
    fields = {m:{k:manifest[m][k] for k in ('toc','sha256','bytes')} for m in overlay}
    report = baseline | {'archive':str(archive),'sha256':digest(archive),'members':prior | fields}
    write_json(assembly/'report.json',report)
    expected = read_json(old/'expected-members.json') | fields
    write_json(stage/'expected-members.json',expected)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',type=Path)
    p.add_argument('previous_stage',type=Path)
    a = p.parse_args()
    prepare(a.stage,a.previous_stage)
