from pathlib import Path
import hashlib,json,os,sys
from garrison_shared import relic_chunky as rc, stock_game
stage=Path(__file__).parent
prior=Path(os.environ['OLD_STAGE'])
repos=Path('F:/aoe_4_temp/New_custom_civilization')
def readback(civ):
    branch='retry/' if civ=='korea' else ''
    return next((prior/civ).glob(branch+'garrison-independent-builds/*/*/readback'))
def put(civ,member,data):
    target=stage/civ/'overlay'/member
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(data)
def build_berber():
    current=readback('berbers')
    baseline=prior/'berbers/older'
    rows=json.loads((repos/'aoe4-berbers/docs/update_013/converted-buildings.json').read_text())
    checked=[]
    for row in rows:
        stem=row['model']
        if not any(key in stem for key in ('berber_tent_age','ribat_lod0','fez_lod0','funduq_lod0','grand_keep_lod0','koutoubia_lod0')):
            continue
        for suffix in ('.rgm','.rrgeom','.rrmaterial'):
            name=stem+suffix
            original=(baseline/name).read_bytes()
            assert original!=(current/name).read_bytes()
            assert b'object_collection' in original
            put('berbers',name,original)
        assert (baseline/(stem+'.rgo')).read_bytes()==(current/(stem+'.rgo')).read_bytes()
        checked.append(stem)
    assert len(checked)==9
    print('Restored nine original model, geometry and material sets',flush=True)
def build_korea():
    sys.path.insert(0,str(repos/'aoe4-korea/tools'))
    from repair_landmark_visuals import graft
    current=readback('korea')
    donor=('art/civilizations/chinese/structures/wonder_forbidden_palace/'
           'chi_wonder_forbidden_palace_control_age04/chi_wonder_forbidden_palace_control_age04')
    native=stock_game.current().model_files(donor,required=('.rgo',))['.rgo']
    names=json.loads((repos/'aoe4-korea/docs/update_036/landmark-native-readback.json').read_text())
    for name in names:
        member=f'art/kr013/static/{name}/model.rgo'
        put('korea',member,graft((current/member).read_bytes(),native,rc))
    print('Restored construction, damage and ruin controller actions for nine Korean buildings',flush=True)
if __name__=='__main__':
    build_berber()
    build_korea()
