"""Recolor a stock UV atlas for Korean weapon styling and encode a full DDS mip chain."""
from io import BytesIO
from pathlib import Path
import sys

from PIL import Image

source, master, label, mips = sys.argv[1:]
image = Image.open(source).convert('RGBA')
pixels = []
for r,g,b,a in image.getdata():
    value = (r*3+g*6+b)//10
    if r > b+12 and r > g+5:
        # Dark lacquer, with warm gilding retained on highlights.
        highlight = min(1,max(0,(value-88)/97))
        color = (int(value*(.63+.48*highlight)+8), int(value*(.40+.49*highlight)+4),
                 int(value*(.33+.25*highlight)+3))
    elif label=='bow':
        color = (int(r*.91),int(g*.85),int(b*.76))
    else:
        # Cool forged edges and dark wrap, preserving the source roughness map.
        color = (int(r*.94),int(g*.99),min(255,int(b*1.05+3)))
    pixels.append((*color,a))
image.putdata(pixels)
image.save(master)
output=Path(mips)
output.mkdir(exist_ok=True)
for i in range(max(image.size).bit_length()):
    f=BytesIO()
    level=image.resize(tuple(max(1,x>>i) for x in image.size),Image.Resampling.LANCZOS)
    level.save(f,format='DDS',pixel_format='DXT5')
    data=f.getvalue()
    assert data[84:88]==b'DXT5'
    (output/f'{i}-{level.width}-{level.height}.bin').write_bytes(data[128:])
