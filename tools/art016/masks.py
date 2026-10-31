"""Restore donor owner mask in the original-UV region; preserve Korean skin/hair."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageOps,ImageChops,ImageStat,ImageDraw
import os
R=Path(__file__).resolve().parents[2];W=Path(os.environ.get('KOREA_ART016_STAGE',str(R/'output/source016')))
for row in json.loads((W/'preparation.json').read_text()):
 asset=row['asset'];dst=W/'masks'/asset;dst.mkdir(parents=True,exist_ok=True)
 source=R/next(x['file'] for x in row['textures'] if x['name']=='pattern.png');im=Image.open(source).convert('RGBA');r,g,b,a=im.split()
 old=r.copy();size=im.size;scale=row['atlas']['native_u_scale'];width=round(size[0]*scale)
 donor=W/'donors'/asset/'stock.dds'
 if donor.exists() and row['mask_mode']=='restore_stock_owner':
  stock=ImageOps.flip(Image.open(donor).convert('RGBA'))
  # Mask alpha can be zero. RGBA resizing premultiplies and erases those RGB
  # data channels, so filter every independent channel separately.
  stock=Image.merge('RGBA',tuple(c.resize((width,size[1]),Image.Resampling.BILINEAR) for c in stock.split()))
  red=Image.new('L',size);alpha=Image.new('L',size);red.paste(stock.getchannel('R'),(0,0));alpha.paste(stock.getchannel('A'),(0,0))
  r=ImageChops.lighter(r,red)
 else:alpha=Image.new('L',size)
 # A vertex assigned to skin or hair must never also be an owner-colour surface.
 if row['mask_mode']=='restore_stock_owner':
  protected=ImageChops.lighter(g,b).point(lambda v:255 if v>32 else 0)
  r=ImageChops.subtract(r,protected)
 result=Image.merge('RGBA',(r,g,b,alpha));result.save(dst/'pattern.png')
 assert ImageChops.difference(result.getchannel('G'),im.getchannel('G')).getbbox() is None
 assert ImageChops.difference(result.getchannel('B'),im.getchannel('B')).getbbox() is None
 levels=[];mip=ImageOps.flip(result);level=0
 while True:
  file=f'mip{level}.dds';mip.save(dst/file,pixel_format='DXT5');levels.append({'level':level,'width':mip.width,'height':mip.height,'dds':file})
  if mip.size==(1,1):break
  shape=(max(1,mip.width//2),max(1,mip.height//2))
  mip=Image.merge('RGBA',tuple(c.resize(shape,Image.Resampling.BOX) for c in mip.split()));level+=1
 info={'source_sha256':hashlib.sha256((dst/'pattern.png').read_bytes()).hexdigest(),'old_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'native_u_scale':scale,'owner_atlas_mean_before':ImageStat.Stat(old).mean[0],'owner_atlas_mean_after':ImageStat.Stat(r).mean[0],'skin_hair_byte_preserved':True,'stock_alpha_restored':True,'mips':levels}
 (dst/'mask.json').write_text(json.dumps(info,indent=2)+'\n')
 print(asset,round(info['owner_atlas_mean_before'],2),'->',round(info['owner_atlas_mean_after'],2),flush=True)
