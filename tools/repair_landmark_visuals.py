"""Restore the native visual lifecycle on Korea's six landmark models."""
import hashlib
import struct
import sys
from pathlib import Path

def graft(source, donor, rc):
    original, official = (rc.parse(raw) for raw in (source, donor))
    def chunk(doc, tag):
        matches = [c for c in rc.walk(doc.roots) if c.tag == tag]
        assert len(matches) == 1, tag
        return matches[0]
    def lp(raw, offset):
        return rc.read_lp_string(raw, offset)
    def default_fields(raw):
        assert raw[:4] == bytes(4)
        offset = 8
        enums, floats = {}, {}
        for _ in range(struct.unpack_from('<I', raw, 4)[0]):
            start = offset
            name, offset = lp(raw, offset)
            count, = struct.unpack_from('<I', raw, offset)
            offset += 4
            for _ in range(count):
                _, offset = lp(raw, offset)
            _, offset = lp(raw, offset)
            enums[name] = raw[start:offset]
        count, = struct.unpack_from('<I', raw, offset)
        offset += 4
        for _ in range(count):
            start = offset
            name, offset = lp(raw, offset)
            offset += 12
            floats[name] = raw[start:offset]
        return enums, floats, raw[offset:]
    def pack(c):
        return rc.pack_chunk(c.kind, c.tag, c.payload, version=c.version, name=c.name)
    dtbp = chunk(original, b'DTBP')
    enums, floats, tail = default_fields(dtbp.payload)
    official_enums, official_floats, _ = default_fields(chunk(official,b'DTBP').payload)
    assert set(enums) == {'life_cycle_state'} and not floats
    assert enums['life_cycle_state'] == official_enums['life_cycle_state']
    defaults = (struct.pack('<II',0,3) + enums['life_cycle_state']
        + official_enums['life_cycle_state_previous'] + official_enums['preview']
        + struct.pack('<I',2) + official_floats['health'] + official_floats['build'] + tail)
    triggers = {}
    for variant in chunk(official,b'BBPC').children:
        cond, action = variant.children
        assert (cond.tag,action.tag)==(b'CNBP',b'BBPD')
        name, _ = lp(action.payload,0)
        if name.startswith('set_lifecycle_'):
            assert name not in triggers
            triggers[name] = variant
    actions = {a.decoded_name:a for a in chunk(official,b'ACTC').children if a.decoded_name in triggers}
    assert set(actions)==set(triggers) and len(actions)==29
    for name, action in actions.items():
        count, = struct.unpack_from('<I',action.payload)
        assert count==(1 if "construct_" in name else 2)
        offset=4
        for key in ('life_cycle_state','life_cycle_state_previous')[:count]:
            opcode,offset=lp(action.payload,offset)
            assert opcode=='setstate'
            assert struct.unpack_from('<I',action.payload,offset)[0]==2
            offset+=4
            attr,offset=lp(action.payload,offset)
            var,offset=lp(action.payload,offset)
            assert (attr,var)==('StateMachine',key)
            attr,offset=lp(action.payload,offset)
            state,offset=lp(action.payload,offset)
            assert attr=='State' and state in (
                ['healthy','ruins','preview','targeting']
                + [f'construct_{i:02}' for i in range(0,100,5)]
                + [f'damage_{i}' for i in range(1,6)])
            offset+=4
        assert offset==len(action.payload)
    bbpc, actc = chunk(original,b'BBPC'), chunk(original,b'ACTC')
    assert not bbpc.children and not actc.children
    patches = {dtbp.offset:defaults, bbpc.offset:b''.join(map(pack,triggers.values())),
               actc.offset:b''.join(map(pack,actions.values()))}
    output = rc.rebuild(original, lambda c: patches.get(c.offset))
    verified = rc.parse(output)
    assert len(chunk(verified,b'BBPC').children)==29 and len(chunk(verified,b'ACTC').children)==29
    assert all(chunk(verified,tag).payload == chunk(original,tag).payload
               for tag in (b'INFO',b'EVCT',b'STRT',b'CUAT'))
    return output

def main():
    root, stage = map(Path,sys.argv[1:])
    sys.path.insert(0,str(root/'tools'))
    from runtime import read_json,write_json,stock_game
    from garrison_shared import relic_chunky as rc
    stock = stock_game.current()
    donor_path = ('art/civilizations/chinese/structures/wonder_forbidden_palace/'
                  'chi_wonder_forbidden_palace_control_age04/chi_wonder_forbidden_palace_control_age04')
    donor = stock.model_files(donor_path, required=('.rgo',))['.rgo']
    manifest_path = stage/'candidate/inputs/native-manifest.json'
    manifest = read_json(manifest_path)
    policy_path = stage/'candidate/source/update-031-policy.json'
    policy = read_json(policy_path)
    records = []
    for asset in ('bulguksa_temple','gate_of_reverence','gyeongbok_palace',
                  'hall_of_worthies','seon_deok_observatory','stone_pagoda'):
        member = f'art/kr013/static/{asset}/model.rgo'
        before = (root/'inputs/native'/member).read_bytes()
        after = graft(before, donor, rc)
        target = stage/'candidate/inputs/native'/member
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(after)
        sha = hashlib.sha256(after).hexdigest()
        manifest[member].update(bytes=len(after),sha256=sha,change='Add stock visual lifecycle actions and variables')
        if member not in policy['allowed_changed']:policy['allowed_changed'].append(member)
        records.append({'member':member,'before':hashlib.sha256(before).hexdigest(),'after':sha,
                        'native_lifecycle_actions':29,'geometry_untouched':True})
    write_json(manifest_path,manifest)
    write_json(policy_path,policy)
    write_json(stage/'candidate/docs/update_031/landmark-models.json',
               {'donor':donor_path+'.rgo','donor_sha256':hashlib.sha256(donor).hexdigest(),'models':records})
    print('NATIVE_LIFECYCLE_REPAIRED',len(records), 'models')

if __name__=='__main__':main()
