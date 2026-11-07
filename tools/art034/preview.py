from pathlib import Path
import json
import sys

from PIL import Image, ImageDraw, ImageFont
import numpy as np

stage=Path(sys.argv[1])
image=Image.new('RGB',(1200,495),(23,30,36))
title=ImageDraw.Draw(image)
fonts=Path(r'C:\Windows\Fonts')
big=ImageFont.truetype(str(fonts/'segoeuib.ttf'),27)
small=ImageFont.truetype(str(fonts/'segoeui.ttf'),16)
title.text((24,20),'Korea 0.3.4 · Tiger Hunter armor',font=big,fill=(241,233,210))
title.text((25,54),'Cooked LOD1 in rest pose. Blue illustrates the dynamic owner-colour mask.',font=small,fill=(186,197,205))
W,H=390,345
for col,(label,asset) in enumerate((
    ('Feudal', 'kr_tiger_hunter_a2'),
    ('Castle', 'kr_tiger_hunter_a3'),
    ('Imperial', 'kr_tiger_hunter_a4'),
)):
    for row in (0,):
        q=next((stage/'decoded-bound'/asset).glob('*/decoded-static.json'))
        doc=json.loads(q.read_text())
        canvas=np.zeros((H,W,3),dtype=np.uint8)+np.array([39,47,55],dtype=np.uint8)
        depth=np.full((H,W),-1e10)
        textures=stage/'tiger-textures'/asset
        albedo=np.array(Image.open(textures/'albedoTexture.dds').convert('RGB')).astype(float)
        mask=np.array(Image.open(textures/'patternTex.dds').convert('RGB')).astype(float)
        cam=np.array([.70,-.74,.42] if row==0 else [1.0,-.35,.36])
        cam/=np.linalg.norm(cam)
        right=np.cross((0,0,1),cam);right/=np.linalg.norm(right)
        up=np.cross(cam,right)
        light=np.array([.30,-.38,.87]);light/=np.linalg.norm(light)
        for g in doc['geometry']['groups']:
            if not g['rig_projection']['lod_palette']['name'].endswith('_lod1'):continue
            p=np.array(g['positions']);uv=np.array(next(iter(g['uv_layers'].values())))
            cx=p @ right
            cy=(p-np.array([0,0,1.09])) @ up
            xy=np.column_stack((W/2+cx*142,H/2-cy*142))
            z=p @ cam
            normals=np.array(g['normals'])
            for tri in g['triangles']:
                xs,ys=xy[tri].T
                x1,y1=max(0,int(np.floor(xs.min()))),max(0,int(np.floor(ys.min())))
                x2,y2=min(W-1,int(np.ceil(xs.max()))),min(H-1,int(np.ceil(ys.max())))
                if x2<x1 or y2<y1:continue
                X,Y=np.meshgrid(np.arange(x1,x2+1)+.5,np.arange(y1,y2+1)+.5)
                div=(ys[1]-ys[2])*(xs[0]-xs[2])+(xs[2]-xs[1])*(ys[0]-ys[2])
                if abs(div)<1e-6:continue
                a=((ys[1]-ys[2])*(X-xs[2])+(xs[2]-xs[1])*(Y-ys[2]))/div
                b=((ys[2]-ys[0])*(X-xs[2])+(xs[0]-xs[2])*(Y-ys[2]))/div
                c=1-a-b
                weights=np.stack((a,b,c),axis=-1)
                Z=weights @ z[tri]
                patch=depth[y1:y2+1,x1:x2+1]
                selection=(a>=0)&(b>=0)&(c>=0)&(Z>patch)
                if not selection.any():continue
                uvn=weights[selection] @ uv[tri]
                index=(uvn[:,0]*albedo.shape[1]).astype(int).clip(0,albedo.shape[1]-1)
                line=((1-uvn[:,1])*albedo.shape[0]).astype(int).clip(0,albedo.shape[0]-1)
                color=albedo[line,index]
                color_mask=(mask[line,index,0]/255)[:,None]
                blue=np.array([35,117,215])*(color.mean(1)[:,None]/200+.38)
                color=color*(1-color_mask*.75)+blue*color_mask*.75
                shade=np.clip((weights[selection] @ normals[tri]) @ light,.0,1.0)*.54+.56
                canvas[y1:y2+1,x1:x2+1][selection]=np.clip(color*shade[:,None],0,255).astype(np.uint8)
                patch[selection]=Z[selection]
        image.paste(Image.fromarray(canvas),(10+col*398,90+row*218))
    title.text((155+col*398,449),label,font=big,fill=(241,233,210))
image.save(stage/'tiger-readback.png')
