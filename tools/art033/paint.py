"""Paint the cavalry atlas with stock skin channels and Korean trim swatches."""
from pathlib import Path
import json
import sys

from PIL import Image, ImageDraw
import numpy as np

stage = Path(sys.argv[1])
specs = []
for family, tiers in [('horseman', (2, 3, 4)), ('lancer', (3, 4)), ('hwarang', (2, 3, 4))]:
    for age in tiers:
        tier = f'{"armor" if family == "lancer" else "light"}_age{age:02}'
        manifest = next((stage / 'donors' / tier).glob('*/decoded-static.json'))
        donor = json.loads(manifest.read_text())
        for part in ('rider', 'horse'):
            asset = f'kr_{"mount_" if part == "horse" else ""}{family}{"_mounted" if family == "hwarang" and part == "rider" else ""}_a{age}'
            folder = stage / 'authoring' / asset
            folder.mkdir(parents=True, exist_ok=True)
            spec = dict(asset=asset, part=part, family=family, age=age, tier=tier, manifest=str(manifest))
            specs.append(spec)
            textures = {t['name']: t for m in donor['material']['materials']
                        if m['name'] == part + '_lod1' for t in m['textures'] if t['projection_path']}
            for role, slot, default in (
                ('albedo', 'albedoTexture', (100, 82, 61, 255)),
                ('pattern', 'patternTex', (0, 0, 0, 0)),
                ('normal', 'normalMap', (0, 128, 255, 128)),
                ('metalness', 'metalTex', (0, 0, 0, 255)),
            ):
                source = textures.get(slot)
                base = (Image.open(source['projection_path']).convert('RGBA') if source
                        else Image.new('RGBA', (256, 256), default))
                # Preserve donor UV layout in the left three quarters, including skin/hair masks.
                base = Image.merge('RGBA', tuple(c.resize((384, 512), Image.Resampling.LANCZOS) for c in base.split()))
                if role == 'albedo':
                    a = np.array(base).astype(float)
                    rgb = a[:, :, :3]
                    if part == 'horse':
                        coat = {'horseman': (1.12, .93, .78), 'lancer': (.86, .90, .96), 'hwarang': (.99, 1.00, 1.10)}
                        rgb *= np.array(coat[family])
                        if family == 'hwarang':
                            value = rgb @ np.array((.27, .55, .18))
                            bright = 34 + value * 1.38
                            rgb[:] = bright[:, :, None] * np.array((1.03, 1.00, .95)) + (rgb-value[:,:,None])*.24
                    else:
                        pattern = Image.open(textures['patternTex']['projection_path']).convert('RGB').resize((384, 512))
                        non_skin = (np.array(pattern)[:, :, 1:].max(2) < 35)[:, :, None]
                        cloth = {'horseman': (.92, .98, 1.02), 'lancer': (.86, .90, .96), 'hwarang': (1.03, .91, .79)}
                        rgb[:] = np.where(non_skin, rgb * np.array(cloth[family]), rgb)
                    base = Image.fromarray(a.clip(0, 255).astype('uint8'))
                if role == 'pattern':
                    base.putalpha(0)
                atlas = Image.new('RGBA', (512, 512), default)
                atlas.paste(base, (0, 0))
                draw = ImageDraw.Draw(atlas)
                colors = [
                    (37, 35, 30), (158, 115, 65), (90, 89, 75),
                    (183, 166, 125), (85, 72, 60), (111, 60, 47),
                    (88, 83, 76), (65, 55, 42)
                ]
                for tile, rgb in enumerate(colors):
                    top = tile * 64
                    fill = {'albedo': (*rgb, 255), 'pattern': (235 if tile in {2, 5} else 0, 0, 0, 0),
                            'normal': default, 'metalness': (160, 114, 0, 230) if tile in {1, 6} else (0, 155, 0, 245)}[role]
                    draw.rectangle((384, top, 511, top + 63), fill=fill)
                    if role == 'albedo':
                        if tile in {2, 3, 5}:
                            for y in range(top + 3, top + 64, 4):
                                v = 9 if y % 8 == 3 else -6
                                draw.line((384, y, 511, y), fill=tuple(x+v for x in rgb)+(255,))
                        if tile in {4, 6}:
                            for y in range(top + 5, top + 60, 11):
                                for x in range(385 + (y % 2) * 6, 511, 12):
                                    draw.rectangle((x, y, min(x+10, 511), y+8), fill=tuple(x+13 for x in rgb)+(255,))
                                    draw.point((x+3, y+3), fill=(171, 139, 91, 255))
                atlas.save(folder / f'{role}.png')
(stage / 'assets.json').write_text(json.dumps(specs, indent=2))
