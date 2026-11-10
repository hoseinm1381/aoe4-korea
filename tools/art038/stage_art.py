"""Stage Korea's 0.3.8 flag and highest-detail building resources."""
import argparse
from io import BytesIO
from pathlib import Path
import struct
import subprocess
import sys
import zlib

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import digest
from runtime import ROOT, read_json, write_json
from garrison_shared import relic_chunky as rc, rrtex_decoder as rr

UI = 'ui/images/garrison/korea/presentation_011'
PRESENTATION = ROOT / 'source/presentation'
FLAGS = ('flag_list', 'flag_list_small', 'flag_secondary',
         'flag_secondary_small', 'flag_fade', 'flag_tile')
SINGLE = struct.pack('<I', 1)


def cloth(image):
    """Warp the approved emblem and light the resulting diagonal cloth folds."""
    width, height = image.size
    x, y = np.meshgrid(np.linspace(0, 1, width, dtype=np.float32),
                       np.linspace(0, 1, height, dtype=np.float32))
    phase = 2 * np.pi * (2.35 * x - 1.17 * y + 0.10 * np.sin(2 * np.pi * y))
    horizontal = x + 0.017 * np.sin(phase) * np.sin(np.pi * x)
    vertical = y + 0.035 * np.sin(phase + 0.45) * np.sin(np.pi * y)
    uv = np.stack((horizontal * (width - 1), vertical * (height - 1)), axis=-1)
    uv = np.clip(uv, 0, [width - 1, height - 1])
    lower = np.floor(uv).astype(np.int32)
    upper = np.minimum(lower + 1, [width - 1, height - 1])
    fraction = uv - lower
    left, top = lower[:, :, 0], lower[:, :, 1]
    right, bottom = upper[:, :, 0], upper[:, :, 1]
    fx, fy = fraction[:, :, 0, None], fraction[:, :, 1, None]
    rgba = np.asarray(image.convert('RGBA'), dtype=np.float32)
    color = ((rgba[top, left] * (1 - fx) + rgba[top, right] * fx) * (1 - fy)
             + (rgba[bottom, left] * (1 - fx) + rgba[bottom, right] * fx) * fy)
    fold = 0.18 * np.sin(phase + 0.66) - 0.23 * np.maximum(0, np.cos(phase)) ** 5
    fold += 0.10 * np.maximum(0, np.sin(phase + 0.80)) ** 6
    shade = 0.99 + fold - 0.20 * ((2 * x - 1) ** 4 + (2 * y - 1) ** 4)
    color[:, :, :3] *= shade[:, :, None]
    # Fine weave remains visible on the full-size card and averages out in the picker.
    grain = 1.0 + 0.010 * np.sin(1.27 * x * width) * np.sin(1.19 * y * height)
    color[:, :, :3] *= grain[:, :, None]
    return Image.fromarray(np.clip(np.rint(color), 0, 255).astype(np.uint8))


def single_mip_bc7(template, dds, size):
    """Preserve the installed game's BC7 UI container and logical texture name."""
    width, height = size
    assert dds[:4] == b'DDS ' and dds[84:88] == b'DX10'
    assert struct.unpack_from('<I', dds, 128) == (98,)
    blocks = dds[148:]
    assert len(blocks) == ((width + 3) // 4) * ((height + 3) // 4) * 16
    document = rc.parse(template)
    tman, = (c for c in rc.walk(document.roots) if c.tag == b'TMAN')
    tdat, = (c for c in rc.walk(document.roots) if c.tag == b'TDAT')
    assert struct.unpack_from('<8I', tman.payload) == (6, width, height, 1, 2, 28, 1, 2)
    mip = struct.pack('<4I', 0, width, height, len(blocks)) + blocks
    chunks = [mip[i:i + 65536] for i in range(0, len(mip), 65536)]
    compressed = [zlib.compress(part, 9) for part in chunks]
    stored = [min(part, packed, key=len) for part, packed in zip(chunks, compressed, strict=True)]
    manifest = tman.payload[:41] + struct.pack('<I', len(chunks))
    manifest += b''.join(struct.pack('<II', len(part), len(packed))
                         for part, packed in zip(chunks, stored, strict=True))
    stream = struct.pack('<I', 6) + b''.join(stored)
    rr._validate_stream_table(manifest, stream)
    decoded, = rr._decode_mips(stream)[1]
    assert (decoded.width, decoded.height, decoded.data) == (width, height, blocks)
    return rc.rebuild(document, lambda c: {tman.offset: manifest, tdat.offset: stream}.get(c.offset))


def highest_rgm(raw):
    document = rc.parse(raw)
    mesh, = (c for c in rc.walk(document.roots)
             if c.tag == b'SKMS' and c.decoded_name.startswith('mesh_healthy'))
    folder, = (c for c in mesh.children if c.tag == b'LODs')
    count, *palettes = folder.children
    assert count.tag == b'LODC' and count.payload == struct.pack('<I', 3)
    assert len(palettes) == 3 and all(c.tag == b'\0LOD' for c in palettes)
    assert [rc.read_lp_string(c.payload, 4)[0] for c in palettes] == [
        f'{mesh.decoded_name}_lod{level}' for level in (1, 2, 3)]
    distance, = (c for c in mesh.children if c.tag == b'LODD')
    assert struct.unpack('<I3f', distance.payload) == (3, 30.0, 60.0, 90.0)
    remove = {c.offset for c in palettes[1:]}
    for tag, child_tag in ((b'\0GEO', b'LGEO'), (b'MISC', b'RFBD')):
        parent, = (c for c in mesh.children if c.tag == tag)
        records = [c for c in parent.children if c.tag == child_tag]
        assert len(records) == 3
        remove.update(c.offset for c in records[1:])

    def edit(c):
        if c.offset in remove:
            return rc.REMOVE
        if c.offset == count.offset:
            return SINGLE
        if c.offset == distance.offset:
            return SINGLE + distance.payload[12:16]
        return None

    return rc.rebuild(document, edit)


def highest_geometry(raw):
    document = rc.parse(raw)
    meshes = [c for c in rc.walk(document.roots) if c.tag == b'MESH']
    assert len(meshes) == 9
    lod_lists = [[c for c in mesh.children if c.tag == b'LOD '] for mesh in meshes]
    assert [len(lods) for lods in lod_lists] == [1] * 8 + [3]
    assert all(rc.read_lp_string(c.payload, 0)[0].startswith('mesh_healthy')
               for c in rc.walk(lod_lists[-1]) if c.tag == b'GOHD')
    count, = (c for c in meshes[-1].children if c.tag == b'NBLO')
    assert count.payload == struct.pack('<I', 3)
    remove = {c.offset for c in lod_lists[-1][1:]}
    result = rc.rebuild(document, lambda c: rc.REMOVE if c.offset in remove
                        else SINGLE if c.offset == count.offset else None)
    result_meshes = [c for c in rc.walk(rc.parse(result).roots) if c.tag == b'MESH']
    assert [c.payload for c in result_meshes[:-1]] == [c.payload for c in meshes[:-1]]
    assert result_meshes[-1].children[1].payload == lod_lists[-1][0].payload
    return result


def stage_art(stage, previous, texconv):
    baseline = previous / 'assembly/readback'
    names = sorted(read_json(ROOT / 'docs/update_036/landmark-native-readback.json'))
    assert len(names) == 9
    overlay = stage / 'overlay'
    overlay.mkdir()
    rows = {}

    def put(member, data):
        path = overlay / member
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        rows[member] = dict(toc='data', bytes=len(data), sha256=digest(path))

    for name in names:
        stem = f'art/kr013/static/{name}/model'
        for suffix, transform in (('.rgm', highest_rgm), ('.rrgeom', highest_geometry)):
            member = stem + suffix
            put(member, transform((baseline / member).read_bytes()))
        print('HIGHEST_DETAIL', name, flush=True)

    renders = stage / 'flag-renders'
    renders.mkdir()
    for name in FLAGS:
        flat = Image.open(PRESENTATION / 'derived_011' / (name + '.png'))
        image = cloth(flat)
        png = renders / (name + '.png')
        image.save(png)
        subprocess.run([texconv, '-nologo', '-nogpu', '--single-proc', '-m', '1',
                        '-f', 'BC7_UNORM', '-o', renders, png], check=True)
        dds = png.with_suffix('.dds').read_bytes()
        decoded = Image.open(BytesIO(dds)).convert('RGBA')
        error = np.abs(np.asarray(decoded, dtype=np.int16) - np.asarray(image, dtype=np.int16))
        assert decoded.size == image.size and error.mean() < 4.0, (name, error.mean())
        decoded.save(renders / (name + '-readback.png'))
        member = f'{UI}/{name}.rrtex'
        put(member, single_mip_bc7((baseline / member).read_bytes(), dds, image.size))
        print('WAVY_FLAG_BC7', name, image.size, round(error.mean(), 3), flush=True)

    cover = cloth(Image.open(PRESENTATION / 'derived_011/cover.png'))
    cover.save(stage / 'cover.png', optimize=True)
    assert (stage / 'cover.png').stat().st_size < 4 * 1024 * 1024
    write_json(stage / 'overlay.json', rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', type=Path)
    parser.add_argument('previous', type=Path)
    parser.add_argument('texconv', type=Path)
    args = parser.parse_args()
    stage_art(args.stage, args.previous, args.texconv)
