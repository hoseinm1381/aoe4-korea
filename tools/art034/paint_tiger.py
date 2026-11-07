"""Paint three 512px Tiger Hunter atlases, preserving donor skin and hair channels."""
import json
from pathlib import Path
import sys
from PIL import Image, ImageDraw

root,stage = map(Path,sys.argv[1:])
catalog = json.loads((root/'authoring/art013/catalog.json').read_text(encoding='utf-8'))
for age in (2,3,4):
    asset = f'kr_tiger_hunter_a{age}'
    row = next(row for row in catalog['sources'] if row['id']==asset)
    sources = {t['name'].split('.')[0]:root/t['file'] for t in row['textures']}
    folder = stage/'authoring'/asset
    folder.mkdir(parents=True,exist_ok=True)
    colors = [(48,54,57),(169,124,63),(145,119,88),(119,90,62),
              (97,110,114),(107,83,59),(114,125,132),(54,46,38)]
    for role in ('albedo','metalness','pattern'):
        image = Image.open(sources[role]).convert('RGBA')
        image = Image.merge('RGBA',tuple(c.resize((384,512),Image.Resampling.LANCZOS) for c in image.split()))
        atlas = Image.new('RGBA',(512,512))
        if role=='pattern':
            image.putalpha(0)
        atlas.paste(image,(0,0))
        draw = ImageDraw.Draw(atlas)
        for tile,rgb in enumerate(colors):
            y = tile*64
            if role=='pattern':
                fill=(222 if tile in (2,5) else 0,0,0,0)
            elif role=='metalness':
                fill=(140,95,0,240) if tile in (0,1,4,6) else (0,150,0,240)
            else:
                fill=(*rgb,255)
            draw.rectangle((384,y,511,y+63),fill=fill)
            if role!='albedo':
                continue
            if tile in (3,4,6):
                light = tuple(min(255,c+24) for c in rgb)
                dark = tuple(c-30 for c in rgb)
                draw.rounded_rectangle((397,y+7,498,y+56),radius=5,fill=rgb,outline=light,width=2)
                draw.line((398,y+49,495,y+49),fill=dark,width=3)
                for x in (407,488):
                    for dy in (13,46):
                        draw.ellipse((x-2,y+dy-2,x+2,y+dy+2),fill=(192,162,105))
            if tile in (2,5):
                for x in range(388,513,19):
                    draw.polygon([(x,y),(x+9,y),(x+17,y+14),(x+9,y+31),
                                  (x+13,y+47),(x+8,y+63),(x+2,y+63),(x+6,y+46),
                                  (x+3,y+28),(x+9,y+14)],fill=tuple(c-32 for c in rgb))
                draw.line((384,y+12,511,y+12),fill=(175,138,83),width=2)
                draw.line((384,y+51,511,y+51),fill=(175,138,83),width=2)
            if tile in (0,1):
                draw.line((387,y+18,509,y+18),fill=tuple(c+21 for c in rgb),width=2)
                draw.line((387,y+47,509,y+47),fill=tuple(c-17 for c in rgb),width=3)
        atlas.save(folder/(role+'.png'))


    Image.new('RGBA',(512,512),(0,128,255,128)).save(folder/'normal.png')
