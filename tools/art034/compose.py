"""Stage and validate the 0.3.4 Korea visual overlay before promoting source."""
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT, STAGE, PIL = Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3])
sys.path[:0] = [str(ROOT/'tools'),str(ROOT/'tools/art013')]
from runtime import export_table, read_json, rgd, write_json
from art016.repair import rename_model
from rig_contract import read_contract
from garrison_shared import model_variants as mv, rrtex_decoder as rr
from weapons import attachments
from tiger_bind import bind_tiger

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

candidate=STAGE/'candidate'
baseline=read_json(ROOT/'docs/BUILD_VERIFICATION.json')
assert baseline['version']=='0.3.3'
manifest=read_json(ROOT/'inputs/native-manifest.json')
master=read_json(ROOT/'source/master-index.json')
native_overlay={}
table_overlay={}

def put(member, data, origin):
    path=candidate/'inputs/native'/member
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    manifest[member]={'toc':'data','bytes':len(data),'sha256':digest(data),'origin':'0.3.4 '+origin}
    native_overlay[member]=str(path)

def put_table(member, doc):
    data=rgd.write(doc)
    path=candidate/'source/tables'/(member+'.json')
    write_json(path,export_table(data))
    table_overlay[member]=str(path)

receipt=attachments(ROOT,STAGE,PIL,put,put_table,digest)
write_json(STAGE/'weapons.json',receipt)
for age in (2,3,4):
    asset=f'kr_tiger_hunter_a{age}'
    logical=f'art/kr013/units/{asset}/model'
    old=ROOT/'inputs/native'/logical
    new=STAGE/'tiger-extract'/logical
    raw, stock=new.with_suffix('.rgm').read_bytes(),old.with_suffix('.rgm').read_bytes()
    model=bind_tiger(ROOT,asset,raw,stock)
    name=asset+'_mesh'
    put(logical+'.rgm',rename_model(model,'unit_mesh',name),'Tiger Hunter geometry owner')
    put(logical+'.rrgeom',rename_model(new.with_suffix('.rrgeom').read_bytes(),'unit_mesh',name),'Tiger Hunter sculpted geometry')
    assert new.with_suffix('.rgo').read_bytes()==old.with_suffix('.rgo').read_bytes()
    old_material=old.with_suffix('.rrmaterial').read_bytes()
    new_slots=mv.material_slots(new.with_suffix('.rrmaterial').read_bytes())['textures']
    changes={}
    for slot in ('albedoTexture','normalMap','metalTex','patternTex'):
        path=new_slots[slot].replace('\\','/')
        tex=STAGE/'tiger-extract'/path
        assert tex.parent==new.parent
        rr.decode_rrtex(tex,output_dds=STAGE/'tiger-textures'/asset/(slot+'.dds'),validate_stream=True)
        put(path,tex.read_bytes(),'Tiger Hunter shader atlas')
        changes[slot]=new_slots[slot]
    material=mv.rewrite_material(old_material,changes,{})
    assert mv.material_slots(material)['textures']==mv.material_slots(old_material)['textures']|changes
    put(logical+'.rrmaterial',material,'Tiger Hunter native shader bindings')

for src in sorted((STAGE/'authoring').rglob('*')):
    if not src.is_file():
        continue
    rel=Path('art034')/src.relative_to(STAGE/'authoring')
    dst=candidate/'authoring'/rel
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dst)
    master['files'].append({'path':rel.as_posix(),'bytes':dst.stat().st_size,'sha256':digest(dst.read_bytes()),
                            'role':'editable 0.3.4 Tiger Hunter or cavalry weapon visual'})
write_json(candidate/'inputs/native-manifest.json',manifest)
write_json(candidate/'source/master-index.json',master)
write_json(STAGE/'overlay.json',dict(native=native_overlay,tables=table_overlay))
print('OVERLAY',len(native_overlay),'native',len(table_overlay),'typed tables')
