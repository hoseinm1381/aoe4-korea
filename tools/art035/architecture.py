"""Paint Korean architecture on the shipped UVs and rebind the native materials."""
import argparse
import hashlib
from io import BytesIO
from pathlib import Path
import sqlite3
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from runtime import read_json, stock_game, write_json
from art016.repair import encode_bc3
from garrison_shared import model_variants as mv, relic_chunky as rc, rrtex_decoder as rr

MOTIF = ((24, 55, 51), (66, 112, 89), (173, 103, 60), (203, 159, 92), (125, 58, 48))


def normalize(path):
    return path.replace('\\', '/').lower()


def paint_finish(image, target, grain=0.50):
    """Retain the original relief and alpha while painting in a new pigment."""
    pixels = np.array(image.convert('RGBA'))
    light = pixels[:, :, :3].astype(np.float32).mean(axis=2)
    center = np.median(light)
    paint = np.array(target)[None, None, :] + (light - center)[:, :, None] * grain
    pixels[:, :, :3] = np.clip(paint, 0, 255).astype(np.uint8)
    return Image.fromarray(pixels)


def panel_pattern(image):
    """A repeated painted floral centre, framing rules, and end diamonds."""
    draw = ImageDraw.Draw(image)
    dark, jade, ochre, gold, rust = MOTIF
    for row in range(8):
        y = row * 64
        draw.rectangle((0, y, 511, y + 4), fill=(*dark, 255))
        draw.rectangle((0, y + 6, 511, y + 8), fill=(*gold, 255))
        draw.rectangle((0, y + 11, 511, y + 15), fill=(*rust, 255))
        draw.rectangle((0, y + 57, 511, y + 59), fill=(*gold, 255))
        draw.rectangle((0, y + 61, 511, y + 63), fill=(*dark, 255))
        for x in range(32, 512, 64):
            cy = y + 36
            draw.polygon([(x - 19, cy), (x, cy - 18), (x + 19, cy), (x, cy + 18)],
                         fill=(*dark, 255), outline=(*jade, 255), width=2)
            for dx, dy in ((-7, 0), (7, 0), (0, -7), (0, 7)):
                draw.ellipse((x + dx - 5, cy + dy - 5, x + dx + 5, cy + dy + 5),
                             fill=(*ochre, 255))
            draw.ellipse((x - 4, cy - 4, x + 4, cy + 4), fill=(*gold, 255))
    return image


def landmark_albedo(base):
    assert base.size == (2048, 2048)
    palette = {
        (0, 0): (46, 83, 64), (1, 0): (127, 89, 47), (2, 0): (51, 99, 75),
        (0, 1): (134, 107, 53), (1, 1): (173, 145, 102), (3, 1): (95, 72, 55),
        (0, 2): (132, 57, 42), (1, 2): (86, 55, 38), (2, 2): (47, 88, 73),
        (3, 2): (154, 121, 72), (0, 3): (112, 107, 92), (1, 3): (92, 106, 105),
        (2, 3): (133, 112, 82), (3, 3): (57, 69, 76),
    }
    result = base.copy()
    for (col, row), color in palette.items():
        x, y = col * 512, row * 512
        tile = paint_finish(base.crop((x, y, x + 512, y + 512)), color, .85)
        if (col, row) == (0, 0):
            tile = panel_pattern(tile)
        if (col, row) == (1, 0):
            tile = Image.blend(tile, base.crop((x, y, x + 512, y + 512)), .23)
        if row == 3 and col in (0, 2):
            draw = ImageDraw.Draw(tile)
            for band in (60, 284):
                draw.rectangle((0, band-4, 511, band-1), fill=(143, 118, 77, 255))
                draw.rectangle((0, band, 511, band+15), fill=(105, 99, 82, 255))
                draw.rectangle((0, band+16, 511, band+19), fill=(66, 63, 53, 255))
        result.paste(tile, (x, y))
    return result


def samples(groups, side, material=None):
    """Estimate area by stratified barycentric samples of the native triangles."""
    columns = []
    steps = 7
    barycentric = [(i / steps, j / steps) for i in range(1, steps)
                   for j in range(1, steps - i)]
    for group in groups:
        positions = np.asarray(group['positions'])
        uv = np.asarray(group['uv_layers']['UVMap'])
        indices = np.asarray(group['triangles'])
        triangle = positions[indices]
        area = np.linalg.norm(np.cross(triangle[:, 1] - triangle[:, 0],
                                       triangle[:, 2] - triangle[:, 0]), axis=1) / 2
        if material is not None and group['material'] != material:
            columns.append((np.zeros(area.size, dtype=int), area, False))
            continue
        for u, v in barycentric:
            sample = np.array([u, v, 1-u-v]) @ uv[indices]
            x = (sample[:, 0] % 1 * side).astype(int).clip(0, side-1)
            y = ((1 - sample[:, 1]) % 1 * side).astype(int).clip(0, side-1)
            columns.append((y * side + x, area / len(barycentric), True))
    return columns


def coverage(mask, projected):
    red = np.asarray(mask.convert('RGBA'))[:, :, 0].ravel()
    selected = sum(weight[red[indices] >= 128].sum() for indices, weight, use in projected if use)
    area = sum(weight.sum() for _, weight, _ in projected)
    return round(float(100 * selected / area), 2)


def landmark_mask(source):
    """Keep the previous accents and add paint to ornamental friezes."""
    result = source.copy()
    draw = ImageDraw.Draw(result)
    for y in range(28, 512, 64):
        for x in range(32, 512, 64):
            draw.polygon([(x - 14, y+8), (x, y-6), (x+14, y+8), (x, y+22)],
                         fill=(255, 0, 0, 255))
    for x in (0, 1024):
        for y in (1596, 1820):
            draw.rectangle((x+16, y, x+495, y+15), fill=(255, 0, 0, 255))
    return result


def camp_mask(width):
    image = Image.new('RGBA', (512, 512), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    for center in (96, 352):
        draw.rectangle((0, center - width, 511, center + width - 1), fill=(255, 0, 0, 255))
    return image


def texture_slots(raw, choose):
    document = rc.parse(raw)
    edits = {}
    edited_slots = {}
    for chunk in document.roots:
        if chunk.tag != b'GMat':
            continue
        material = rc.pack_document([rc.pack_chunk(chunk.kind, chunk.tag, chunk.payload,
                                                    version=chunk.version, name=chunk.name)])
        before = mv.material_slots(material)
        changes = choose(chunk.decoded_name, before['textures'])
        if not changes:
            continue
        changes = {k: v.replace('/', '\\') for k, v in changes.items()}
        result = mv.rewrite_material(material, changes, {})
        after = mv.material_slots(result)
        assert after['textures'] == before['textures'] | changes
        assert after['parameters'] == before['parameters']
        edits[chunk.offset] = rc.parse(result).roots[0].payload
        edited_slots[chunk.decoded_name] = changes
    return rc.rebuild(document, lambda chunk: edits.get(chunk.offset)), edited_slots


class Candidate:
    def __init__(self, stage):
        self.stage = stage
        self.output = stage / 'candidate'
        self.native = stage / 'baseline-members'
        if not self.native.is_dir():
            raise FileNotFoundError(f'Extract the 0.3.4 player SGA to {self.native}')
        self.output.mkdir()
        self.manifest = read_json(ROOT / 'inputs/native-manifest.json')
        self.masters = read_json(ROOT / 'source/master-index.json')
        self.masters['files'] = [row for row in self.masters['files']
                                 if not row['path'].startswith('art035/')]
        self.changed = {}
        self.textures = {}
        self.stock = None

    def put(self, member, data):
        path = self.output / 'inputs/native' / member
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self.changed[member] = {'toc': 'data', 'bytes': len(data),
                                'sha256': hashlib.sha256(data).hexdigest(),
                                'origin': '0.3.5 Korean architecture finish and owner colour'}
        self.manifest[member] = self.changed[member]

    def image(self, member):
        path = self.native / member
        if not path.is_file():
            if self.stock is None:
                self.stock = stock_game.current()
                self.db = sqlite3.connect('file:' + (Path.home() / 'AppData/Local/Garrison/Kit/game-assets.sqlite3').as_posix() + '?mode=ro', uri=True)
            found = self.db.execute('SELECT archive_path FROM resolved_assets WHERE logical_path=?',
                                    (member,)).fetchone()
            assert found, member
            raw = self.stock.member(found[0], member)
        else:
            raw = path.read_bytes()
        work = self.stage / 'texture-source'
        work.mkdir(exist_ok=True)
        key = hashlib.sha256(raw).hexdigest()
        source, dds = work / (key+'.rrtex'), work / (key+'.dds')
        if not dds.exists():
            source.write_bytes(raw)
            rr.decode_rrtex(source, output_dds=dds, validate_stream=True)
        with Image.open(dds) as image:
            return raw, image.convert('RGBA')

    def encode(self, label, template, image, *, art_version='035'):
        master = self.output / f'authoring/art{art_version}' / (label + '.png')
        master.parent.mkdir(parents=True, exist_ok=True)
        image.save(master, optimize=True)
        self.masters['files'].append({
            'path': master.relative_to(self.output / 'authoring').as_posix(),
            'bytes': master.stat().st_size, 'sha256': hashlib.sha256(master.read_bytes()).hexdigest(),
            'role': 'editable Korean building paint or dynamic owner mask',
        })
        path = f'art/kr{art_version}/architecture/{label}'
        levels = []
        for i in range(max(image.size).bit_length()):
            size = tuple(max(1, dim >> i) for dim in image.size)
            level = image.resize(size, Image.Resampling.BOX)
            with BytesIO() as stream:
                level.save(stream, format='DDS', pixel_format='DXT5')
                data = stream.getvalue()
            assert data[84:88] == b'DXT5'
            levels.append((*size, data[128:]))
        self.put(path+'.rrtex', encode_bc3(template, path, levels))
        source = self.output / 'inputs/native' / (path+'.rrtex')
        dds = self.stage / (label + '-readback.dds')
        rr.decode_rrtex(source, output_dds=dds, validate_stream=True)
        with Image.open(dds) as decoded:
            assert decoded.size == image.size
        self.textures[label] = {'width': image.width, 'height': image.height, 'mips': len(levels),
                                'rgba8_decoded_bytes': sum(4*w*h for w,h,_ in levels),
                                'bc3_bytes': sum(len(blocks) for _,_,blocks in levels)}
        return path+'.rrtex', dds

    def model(self, category, name, choose):
        member = f'art/kr013/{category}/{name}/model.rrmaterial'
        raw = (self.native / member).read_bytes()
        after, slots = texture_slots(raw, choose)
        if slots:
            assert after != raw
            self.put(member, after)
        return slots

    def decoded(self, name):
        path, = (self.stage / 'decoded-isolated/static' / name).glob('*/decoded-static.json')
        decoded = read_json(path)
        assert not decoded['blockers'] and not decoded['missing_textures'], name
        return decoded['geometry']['groups']


def update_landmarks(candidate):
    catalog = read_json(ROOT / 'authoring/art013/catalog.json')['sources']
    names = sorted(row['id'].lower() for row in catalog if row['group'] == 'Landmarks and unique buildings')
    raw = (candidate.native / f'art/kr013/static/{names[0]}/model.rrmaterial').read_bytes()
    slots = mv.material_slots(raw)['textures']
    color_template, before = candidate.image(normalize(slots['albedoTexture']))
    mask_template, old_mask = candidate.image(normalize(slots['patternTex']))
    albedo, _ = candidate.encode('landmark-albedo', color_template, landmark_albedo(before))
    mask, dds = candidate.encode('landmark-owner', mask_template, landmark_mask(old_mask))
    after = Image.open(dds).convert('RGBA')
    receipts = {}
    for name in names:
        lods = {n: [] for n in (1, 2, 3)}
        for group in candidate.decoded(name):
            lod = group['rig_projection']['lod_palette']['name']
            if lod.startswith('mesh_healthy'):
                lods[int(lod[-1])].append(group)
        assert all(lods.values()), name
        projected = [samples(groups, after.width) for groups in lods.values()]
        coverage_before = [coverage(old_mask, points) for points in projected]
        coverage_after = [coverage(after, points) for points in projected]
        owner = mask
        if any(not 5 <= v <= 25 for v in coverage_after):
            # Some gates repeat the same UV islands on many panels. Use their
            # original stripe mask if the additional medallions overfill them.
            assert all(5 <= v <= 25 for v in coverage_before), (name, coverage_before, coverage_after)
            owner, coverage_after = normalize(slots['patternTex']), coverage_before
        changed = candidate.model('static', name, lambda _, textures: {
            'albedoTexture': albedo, **({'patternTex': owner} if normalize(textures['patternTex']) != owner else {})
        })
        assert changed
        receipts[name] = {'baseline_percent': coverage_before, 'final_percent': coverage_after,
                          'mask': owner, 'materials': len(changed)}
        print('LANDMARK', name, coverage_before, '->', coverage_after, flush=True)
    return receipts


def update_shelters(candidate):
    names = ('korea_lumber_camp01', 'korea_mining_camp01')
    materials = ('korea_camp_rough_granite', 'korea_camp_weathered_timber', 'korea_camp_reed_thatch')
    raw = (candidate.native / f'art/kr013/static/{names[0]}/model.rrmaterial').read_bytes()
    slots = mv.material_slots(raw)['textures']
    color_template, before = candidate.image(normalize(slots['albedoTexture']))
    mask_template, old_mask = candidate.image(normalize(slots['patternTex']))
    assert old_mask.getchannel('R').getextrema() == (0, 0)
    finishes = {}
    for material, color in zip(materials, ((113, 106, 90), (103, 68, 42), (130, 106, 63)), strict=True):
        finish = paint_finish(before, color, .85)
        if material == materials[1]:
            draw = ImageDraw.Draw(finish)
            for y in (96, 352):
                draw.rectangle((0, y-36, 511, y+35), fill=(60, 97, 76, 255))
                for dy in (-39, 38):
                    draw.rectangle((0, y+dy-2, 511, y+dy+2), fill=(161, 117, 63, 255))
        if material == materials[2]:
            pixels = np.array(finish)
            for x in range(512):
                pixels[:, x, :3] = np.clip(pixels[:, x, :3].astype(float) * (1 + .13 * np.cos(2*np.pi*x/8)), 0, 255)
            finish = Image.fromarray(pixels)
        finishes[material], _ = candidate.encode(material.removeprefix('korea_camp_'), color_template, finish)
    mask, dds = candidate.encode('shelter-owner', mask_template, camp_mask(118))
    after = Image.open(dds).convert('RGBA')
    result = {}
    for name in names:
        groups = [g for g in candidate.decoded(name) if g['name'] == 'mesh_healthy']
        points = samples(groups, after.width, materials[1])
        shelter_percent = coverage(after, points)
        base, = (candidate.stage / 'decoded-isolated/ordinary' / name).glob('*/decoded-static.json')
        all_base_states = read_json(base)['geometry']['groups']
        # Counting every native machinery group, including construction-only
        # pieces, is conservative for the lower bound on the finished building.
        base_points = samples(all_base_states, after.width, material='no_owner_accent')
        percent = coverage(after, points + base_points)
        assert 5 <= percent <= 25, (name, percent)
        changes = candidate.model('static', name, lambda material, _: {
            'albedoTexture': finishes[material], **({'patternTex': mask} if material == materials[1] else {})
        })
        assert set(changes) == set(materials)
        result[name] = {'baseline_percent': 0, 'final_percent': percent, 'shelter_only_percent': shelter_percent, 'mask': mask, 'materials': changes}
        print('SHELTER', name, '0 ->', percent, flush=True)
    return result


def update_ordinary(candidate):
    """Warm pale stock plaster and stone using the existing layered shader."""
    replacements = {}
    models = {}
    for path in sorted((candidate.native / 'art/kr013/ordinary').glob('*/model.rrmaterial')):
        def choose(_, slots):
            changes = {}
            for slot, tex in slots.items():
                if not slot.startswith('albedoTex') or slot.endswith('Charred'):
                    continue
                member = normalize(tex)
                parts = member.split('/')
                if len(parts) < 2 or parts[-2] not in ('plaster', 'stone'):
                    continue
                if member not in replacements:
                    raw, base = candidate.image(member)
                    color = np.array(base.resize((64, 64)).convert('RGB')).mean(axis=(0, 1))
                    if color.mean() < 145 or color.max() - color.min() > 36:
                        replacements[member] = None
                    else:
                        category = parts[-2]
                        target = (162, 138, 106) if category == 'plaster' else (124, 114, 96)
                        if color.mean() < 171:
                            target = tuple(v-15 for v in target)
                        label = category + '-' + parts[-1].removesuffix('_packed.rrtex')
                        replacements[member], _ = candidate.encode(label, raw, paint_finish(base, target, .82))
                if replacements[member]:
                    changes[slot] = replacements[member]
            return changes
        model = path.parent.name
        changed = candidate.model('ordinary', model, choose)
        if changed:
            models[model] = changed
    print('ORDINARY', len(models), 'models', sum(bool(value) for value in replacements.values()), 'shared finishes', flush=True)
    return models


def main(stage):
    candidate = Candidate(stage)
    landmarks = update_landmarks(candidate)
    shelters = update_shelters(candidate)
    ordinary = update_ordinary(candidate)
    write_json(candidate.output / 'inputs/native-manifest.json', candidate.manifest)
    write_json(candidate.output / 'source/master-index.json', candidate.masters)
    write_json(stage / 'architecture.json', {
        'landmarks': landmarks, 'shelters': shelters, 'ordinary': ordinary,
        'textures': candidate.textures, 'overlay': candidate.changed,
        'coverage_method': 'Native decoded BC3 red >= 128, stratified UV samples weighted by triangle area. Landmark entries list LODs 1-3. Work-camp coverage includes the attached shelter and all native machinery geometry groups; excludes incidental stamp props.',
    })


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', type=Path)
    main(parser.parse_args().stage)
