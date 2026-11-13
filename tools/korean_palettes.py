"""Paint the nine Korean landmark palettes on their existing UVs."""
import argparse
from pathlib import Path
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from art037.srgb_landmarks import encode_srgb_bc1
from runtime import read_json, write_json
from garrison_shared import rrtex_decoder as rr

# Roof, beam, brackets, ornament, granite, secondary stone, ground, screen.
PALETTES = {
    'gyeongbok_palace': ((52, 70, 91), (163, 49, 34), (53, 102, 82), (174, 119, 57), (135, 132, 122), (157, 149, 134), (105, 91, 71), (126, 81, 43)),
    'bulguksa_temple': ((48, 89, 73), (124, 77, 49), (57, 126, 98), (142, 106, 64), (125, 110, 94), (153, 131, 101), (103, 88, 62), (121, 90, 56)),
    'stone_pagoda': ((85, 130, 111), (122, 150, 125), (107, 147, 124), (134, 151, 127), (167, 169, 144), (145, 160, 135), (119, 107, 83), (133, 153, 125)),
    'seon_deok_observatory': ((86, 86, 82), (119, 96, 68), (111, 104, 83), (141, 113, 65), (127, 130, 128), (151, 146, 132), (111, 102, 87), (142, 118, 73)),
    'gate_of_reverence': ((39, 41, 41), (137, 89, 45), (144, 105, 51), (170, 124, 52), (95, 87, 78), (127, 113, 89), (101, 85, 61), (157, 115, 62)),
    'hall_of_worthies': ((39, 84, 91), (129, 65, 40), (46, 113, 110), (161, 116, 64), (119, 117, 101), (143, 125, 99), (101, 81, 60), (147, 91, 54)),
    'seowon_academy': ((94, 68, 49), (132, 99, 66), (81, 96, 70), (159, 135, 86), (151, 139, 113), (176, 154, 118), (114, 98, 76), (141, 116, 78)),
    'mountain_fortress': ((62, 71, 79), (79, 65, 56), (83, 101, 101), (107, 98, 77), (95, 105, 112), (127, 134, 135), (98, 94, 83), (95, 88, 72)),
    'hwangnyongsa': ((83, 52, 51), (142, 66, 49), (55, 101, 102), (177, 132, 72), (132, 111, 94), (155, 128, 101), (112, 91, 70), (150, 108, 65)),
}


def paint(source, mask, palette):
    roof, beam, bracket, ornament, stone, other, ground, screen = palette
    finishes = (bracket, ornament, bracket, roof, ornament, ground, roof, ground,
                beam, beam, bracket, screen, stone, other, other, roof)
    pixels = np.asarray(source.convert('RGB'), dtype=np.float32)
    height, width, _ = pixels.shape
    assert (width, height) == (2048, 1024)
    untouched = np.asarray(mask.getchannel('R').resize(source.size, Image.Resampling.NEAREST)) > 0
    half = width // 2
    finish = pixels[:, :half].copy()
    for index, target in enumerate(finishes):
        y, x = divmod(index, 4)
        region = finish[y*256:(y+1)*256, x*256:(x+1)*256]
        original = region.copy()
        median = np.median(original.reshape(-1, 3), axis=0)
        region[:] = np.clip(np.asarray(target) + original - median, 4, 240)
    output = np.concatenate([finish, finish], axis=1)
    output[untouched] = pixels[untouched]
    return Image.fromarray(np.rint(output).astype(np.uint8))


def run(stage):
    art = ROOT / 'authoring/art036'
    native = ROOT / 'inputs/native'
    mask = Image.open(art / 'raised-owner.png').convert('RGBA')
    masters = stage / 'masters'
    masters.mkdir(parents=True)
    metrics = {}
    for asset, palette in PALETTES.items():
        member = f'art/kr036/architecture/{asset}.rrtex'
        before = native / member
        source = Image.open(art / f'{asset}.png')
        image = paint(source, mask, palette)
        image.save(masters / f'{asset}.png', optimize=True)
        output = stage / 'overlay' / member
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(encode_srgb_bc1(before.read_bytes(), member, image))
        audit = rr.decode_rrtex(output, stage / f'{asset}.dds', validate_stream=True)
        assert audit['projection']['format'] == 'BC1_UNORM_SRGB'
        assert (audit['width'], audit['height'], audit['mip_count']) == (2048, 1024, 12)
        assert before.read_bytes() != output.read_bytes()
        metrics[member] = {'palette': palette, 'mips': 12, 'bytes': output.stat().st_size,
                           'decoded_rgba8_bytes': sum(4*max(1, 2048>>i)*max(1, 1024>>i) for i in range(12))}
    write_json(stage / 'palette-verification.json', metrics)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', type=Path)
    run(parser.parse_args().stage)

