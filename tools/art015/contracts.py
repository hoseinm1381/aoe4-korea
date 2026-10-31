"""Native material-key and lifecycle-condition contracts; no geometry editing."""
import struct
from garrison_shared import relic_chunky as rc

def geometry_materials(raw):
    names = set()
    for c in rc.walk(rc.parse(raw).roots):
        if c.tag != b'GOHD': continue
        if c.version != 2: raise ValueError('Only qualified native GOHD v2 is supported')
        off = 0; parts = []
        for _ in range(4):
            size = struct.unpack_from('<I', c.payload, off)[0]; off += 4
            parts.append(c.payload[off:off+size].decode('utf-8')); off += size
        if off+1 != len(c.payload): raise ValueError('Unknown geometry header suffix')
        names.add(parts[1])
    if not names or '' in names: raise ValueError('Missing native geometry material keys')
    return names

def material_keys(raw):
    return {c.decoded_name for c in rc.parse(raw).roots if c.tag == b'GMat'}

def repair_material(raw, required):
    doc = rc.parse(raw)
    if not required-material_keys(raw): return raw
    if len(required) != 1: raise ValueError('Multi-material repairs need explicit slot mapping')
    roots = [c for c in doc.roots if c.tag == b'GMat']
    if len(roots) != len(doc.roots) or not roots: raise ValueError('Unknown material container')
    # The 014 repair already supplied the same atlas to every donor LOD slot.
    # Require identical shader/texture/parameter payloads before collapsing them.
    lods = [c for c in roots if c.decoded_name in ('lod1','lod2','lod3')]
    candidates = lods or roots
    if len({c.payload for c in candidates}) != 1: raise ValueError('Active donor LOD materials differ')
    first = candidates[0]
    return rc.pack_document([rc.pack_chunk(first.kind, first.tag, first.payload,
        version=first.version, name=next(iter(required)).encode('utf-8')+b'\0')])

def lifecycle_terms(raw):
    if len(raw) < 4: return None
    count = struct.unpack_from('<I', raw)[0]; off = 4; terms = []
    try:
        for _ in range(count):
            kind, negate, join = struct.unpack_from('<IBI', raw, off); offset = off+5; off += 9
            if kind != 2: return None
            parts = []
            for _ in range(2):
                size = struct.unpack_from('<I', raw, off)[0]; off += 4
                parts.append(raw[off:off+size].decode('utf-8')); off += size
            terms.append({'kind':kind, 'negate':negate, 'join':join,
                'variable':parts[0], 'value':parts[1], 'join_offset':offset})
    except (struct.error, UnicodeDecodeError): return None
    if off != len(raw) or any(t['variable'] != 'life_cycle_state' or t['negate'] for t in terms): return None
    return terms

def repair_conditions(raw):
    edits = {}; count = 0
    for c in rc.walk(rc.parse(raw).roots):
        if c.tag != b'CNBP': continue
        terms = lifecycle_terms(c.payload)
        if terms is None or len(terms) < 2: continue
        joins = [t['join'] for t in terms]
        if all(x == 1 for x in joins): continue
        if joins != [0]+[1]*(len(joins)-1): raise ValueError('Unknown lifecycle expression')
        patched = bytearray(c.payload)
        struct.pack_into('<I', patched, terms[0]['join_offset'], 1)
        edits[c.offset] = bytes(patched); count += 1
    return (rc.rebuild(rc.parse(raw), lambda c:edits.get(c.offset)) if edits else raw), count

def verify_native(root):
    models = 0; selectors = 0
    for family in ['units','static']:
        for p in sorted((root/'art/kr013'/family).glob('*/model.rgm')):
            required = geometry_materials(p.with_suffix('.rrgeom').read_bytes())
            if required-material_keys(p.with_suffix('.rrmaterial').read_bytes()):
                raise ValueError('Missing material key: '+str(p))
            if family == 'static':
                for suffix in ['.rgm','.rgo']:
                    raw = p.with_suffix(suffix).read_bytes()
                    repaired, n = repair_conditions(raw)
                    if repaired != raw: raise ValueError('Malformed lifecycle alternatives: '+str(p))
                    selectors += sum(1 for c in rc.walk(rc.parse(raw).roots)
                        if c.tag == b'CNBP' and (ts:=lifecycle_terms(c.payload)) and len(ts)>1)
            models += 1
    if models != 108: raise ValueError('Expected 72 unit and 36 static models')
    return {'models':models,'multi_state_selectors':selectors,'all_material_keys_resolve':True,
        'lifecycle_alternatives_match_official_or_encoding':True}
