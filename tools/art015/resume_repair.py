"""Scoped Korea 0.1.5 repair, preserving the real 0.1.4 baseline."""
import sys, os, json, gzip, hashlib, shutil, zipfile, struct, subprocess
from pathlib import Path

R = Path('F:/aoe_4_temp/New_custom_civilization/aoe4-korea')
W = Path('F:/aoe_4_temp/Temp_aoe4/k15')
os.environ['TEMP'] = str(W)
os.environ['TMP'] = str(W)
sys.dont_write_bytecode = True
sys.path.insert(0, str(R/'tools'))
from runtime import EXT, read_json, write_json, stock_game
from garrison_shared import relic_chunky as rc

CORE = r'''"""Native material-key and lifecycle-condition contracts; no geometry editing."""
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
'''

def sha(raw): return hashlib.sha256(raw).hexdigest()
def file_sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def prepare():
    assert R.is_dir() and not R.is_junction() and not R.is_symlink()
    assert W.parent.is_dir() and not W.parent.is_junction() and not W.parent.is_symlink()
    if '--resume' not in sys.argv:
        W.mkdir()
        D=R/'docs/update_015'; D.mkdir(exist_ok=False)
        T=R/'tools/art015'; T.mkdir(exist_ok=False)
        (T/'contracts.py').write_text(CORE,encoding='utf-8')
        sys.path.insert(0,str(T)); from contracts import geometry_materials, material_keys, repair_material, repair_conditions, lifecycle_terms
        cfg=read_json(R/'project.json'); assert cfg['version']=='0.1.4'
        receipt=read_json(R/'docs/BUILD_VERIFICATION.json'); oldzip=R/'release'/receipt['zip_name']
        assert file_sha(oldzip)==receipt['zip_sha256']
        # Baseline metadata and exact current source; no full source checkout copy.
        before={p.relative_to(R).as_posix():p.read_text('utf-8') for folder in ['source','tools','tests'] for p in (R/folder).rglob('*') if p.is_file() and p.suffix in ['.json','.scar','.py','.md']}
        for name in ['project.json','inputs/native-manifest.json','docs/BUILD_VERIFICATION.json']:
            before[name]=(R/name).read_text('utf-8')
        (D/'before-source.json.gz').write_bytes(gzip.compress(json.dumps(before).encode(),mtime=0))
        baseline_archive=W/'baseline014.sga'
        with zipfile.ZipFile(oldzip) as z:
            assert z.testzip() is None
            entries=[x for x in z.infolist() if x.filename.endswith('.sga')]; assert len(entries)==1
            with z.open(entries[0]) as src, baseline_archive.open('wb') as dst: shutil.copyfileobj(src,dst)
        assert file_sha(baseline_archive)==receipt['archive_sha256']
        G=stock_game.current(); listing=G.archiver.run(['list',str(baseline_archive),'--verify'])
        assert listing['archive']['verification']['verified']
        rb=W/'baseline-readback'; G.archiver.run(['extract',str(baseline_archive),str(rb),'--filter',''])
        baseline={'members':{m['path']:{'toc':m['toc'],'bytes':m['size'],'sha256':file_sha(rb/m['path'])} for m in listing['members']}}
        (D/'baseline-members.json.gz').write_bytes(gzip.compress(json.dumps(baseline).encode(),mtime=0))
        write_json(D/'BASELINE_014.json',receipt)
        # Keep real bad native data as small independently testable regression fixtures.
        fixture=R/'tests/fixtures/art015-before';fixture.mkdir()
        broken=R/'inputs/native/art/kr013/units/kr_villager_male_a1/model'
        (fixture/'villager.rrmaterial').write_bytes(broken.with_suffix('.rrmaterial').read_bytes())
        geom=rc.parse(broken.with_suffix('.rrgeom').read_bytes())
        (fixture/'villager.gohd').write_bytes(next(c.payload for c in rc.walk(geom.roots) if c.tag==b'GOHD'))
        building=R/'inputs/native/art/kr013/static/bulguksa_temple/model.rgm'
        (fixture/'landmark-condition.bin').write_bytes(next(c.payload for c in rc.walk(rc.parse(building.read_bytes()).roots) if c.tag==b'CNBP' and (ts:=lifecycle_terms(c.payload)) and len(ts)>1 and ts[0]['value']=='healthy'))
        (fixture/'effects.scar').write_bytes((R/'source/scar/korea/effects.scar').read_bytes())
        official=[]
        for row in read_json(R/'docs/update_013/ordinary-native.json')['assets']:
            if not any(s in row['asset'].lower() for s in ['archery_range02','stable02']):continue
            raw=G.model_files(row['stock_model'],required=('.rgm',))['.rgm']
            candidates=[c.payload for c in rc.walk(rc.parse(raw).roots) if c.tag==b'CNBP' and (ts:=lifecycle_terms(c.payload)) and len(ts)>1 and all(t['join']==1 for t in ts)]
            assert candidates
            data=min(candidates,key=len);name=row['asset']+'-official-condition.bin';(fixture/name).write_bytes(data)
            official.append({'model':row['stock_model'],'rgm_sha256':sha(raw),'condition':name,'condition_sha256':sha(data),'condition_count':len(lifecycle_terms(data))})
        assert len(official)==2
        write_json(D/'OFFICIAL_CONDITIONS.json',official)
    else:
        D=R/'docs/update_015'; T=R/'tools/art015'
        assert read_json(D/'BASELINE_014.json')['version']=='0.1.4'
        assert read_json(R/'project.json')['version']=='0.1.4'
        (T/'contracts.py').write_text(CORE,encoding='utf-8')
        sys.path.insert(0,str(T))
        from contracts import geometry_materials, material_keys, repair_material, repair_conditions, lifecycle_terms
        official=read_json(D/'OFFICIAL_CONDITIONS.json')
    staged=W/'repaired'; records=[]
    for family in ['units','static']:
        for model in sorted((R/'inputs/native/art/kr013'/family).glob('*/model.rgm')):
            stem=model.relative_to(R/'inputs/native').as_posix()[:-4]
            required=geometry_materials(model.with_suffix('.rrgeom').read_bytes())
            if family=='units':
                p=model.with_suffix('.rrmaterial');raw=p.read_bytes();new=repair_material(raw,required)
                if new!=raw:
                    target=staged/(stem+'.rrmaterial');target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(new)
                    records.append({'member':stem+'.rrmaterial','before':sha(raw),'after':sha(new),'reason':'Match actual geometry material key; preserve official shader/tint LUT/texture payload','before_keys':sorted(material_keys(raw)),'after_keys':sorted(material_keys(new))})
            else:
                for suffix in ['.rgm','.rgo']:
                    p=model.with_suffix(suffix);raw=p.read_bytes();new,count=repair_conditions(raw)
                    if new!=raw:
                        target=staged/(stem+suffix);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(new)
                        records.append({'member':stem+suffix,'before':sha(raw),'after':sha(new),'condition_count':count,'reason':'Native all-OR lifecycle alternatives match two official current building donors'})
    assert sum(x['member'].endswith('.rrmaterial') for x in records)==72
    assert len({x['member'].rsplit('/',1)[0] for x in records if x['member'].startswith('art/kr013/static/')})==36
    scar=(R/'source/scar/korea/effects.scar').read_text('utf-8')
    old='        if Squad_GetActiveCommand(squad) ~= SCMD_Attack then return end'
    assert scar.count(old)==1
    new='''        -- No Squad_GetActiveCommand API exists in the official ScarDoc/runtime.
        -- Respect an interrupted barrage, moving squad or newly accepted order.
        if not Squad_HasActiveCommand(squad) or Squad_IsMoving(squad)
            or Squad_HasAcceptedCommands(squad) then return end'''
    scar=scar.replace(old,new)
    (W/'effects.scar').write_text(scar,encoding='utf-8')
    write_json(D/'STAGED_REPAIR.json',{'native_changes':records,'official_conditions':official,
        'scar_before':file_sha(R/'source/scar/korea/effects.scar'),'scar_after':file_sha(W/'effects.scar'),
        'geometry_rigs_textures_tables_unchanged':True,'native_game_acceptance':'pending',
        'squad_interruption_limit':'A new stationary ground attack cannot be distinguished by the documented APIs; moving/queued/interrupted orders are guarded.'})
    print('STAGED',len(records),'native files; official donor conditions and rollback verified',flush=True)

TESTS = '''"""Real faulty 014 fixtures, official donors and complete preservation checks."""
import sys, unittest, struct, gzip, json, hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R/'tools'),str(R/'tools/art015')]
from runtime import read_json
from contracts import *
F=R/'tests/fixtures/art015-before'

class Repair015(unittest.TestCase):
    def test_real_missing_material_key_is_repaired_without_shader_changes(self):
        geom=rc.pack_document([rc.pack_chunk(b'DATA',b'GOHD',(F/'villager.gohd').read_bytes(),version=2)])
        names=geometry_materials(geom); raw=(F/'villager.rrmaterial').read_bytes()
        self.assertTrue(names-material_keys(raw))
        patched=repair_material(raw,names)
        self.assertEqual(material_keys(patched),names)
        self.assertEqual(rc.parse(patched).roots[0].payload,rc.parse(raw).roots[0].payload)
        self.assertEqual(repair_material(patched,names),patched)

    def test_real_landmark_condition_matches_two_current_official_donors(self):
        raw=(F/'landmark-condition.bin').read_bytes();before=lifecycle_terms(raw)
        self.assertEqual([t['join'] for t in before],[0,1,1])
        doc=rc.pack_document([rc.pack_chunk(b'DATA',b'CNBP',raw,version=4)])
        fixed,count=repair_conditions(doc);self.assertEqual(count,1)
        payload=rc.parse(fixed).roots[0].payload;after=lifecycle_terms(payload)
        self.assertEqual([t['value'] for t in after],[t['value'] for t in before])
        self.assertEqual([t['join'] for t in after],[1,1,1])
        self.assertEqual([i for i,(a,b) in enumerate(zip(raw,payload)) if a!=b],[before[0]['join_offset']])
        for row in read_json(R/'docs/update_015/OFFICIAL_CONDITIONS.json'):
            official=(F/row['condition']).read_bytes()
            self.assertEqual(hashlib.sha256(official).hexdigest(),row['condition_sha256'])
            self.assertTrue(all(t['join']==1 for t in lifecycle_terms(official)))
        self.assertEqual(repair_conditions(fixed),(fixed,0))

    def test_all_108_current_models_pass_actual_material_and_selector_contracts(self):
        self.assertEqual(verify_native(R/'inputs/native')['models'],108)

    def test_real_nil_call_fixture_and_documented_replacement(self):
        old=(F/'effects.scar').read_text('utf-8')
        new=(R/'source/scar/korea/effects.scar').read_text('utf-8')
        self.assertIn('Squad_GetActiveCommand(squad)',old)
        self.assertNotIn('Squad_GetActiveCommand(squad)',new)
        for symbol in ['Squad_HasActiveCommand','Squad_IsMoving','Squad_HasAcceptedCommands']:
            self.assertIn(symbol+'(squad)',new)

    def test_actual_014_baseline_preserves_geometry_textures_rigs_hwacha_and_gameplay(self):
        snap=json.loads(gzip.decompress((R/'docs/update_015/before-source.json.gz').read_bytes()))
        policy=read_json(R/'source/update-015-policy.json')
        old=json.loads(snap['inputs/native-manifest.json']);now=read_json(R/'inputs/native-manifest.json')
        self.assertEqual(set(old),set(now))
        changed={m for m in old if old[m]['sha256']!=now[m]['sha256']}
        self.assertEqual(changed,set(policy['native_changed']))
        self.assertEqual(len(changed),108)
        for m in old:
            if m.endswith(('.rrgeom','.rrtex')) or m.startswith('art/kr014/'):
                self.assertEqual(old[m]['sha256'],now[m]['sha256'],m)
        for name,raw in snap.items():
            if name.startswith('source/tables/') or (name.startswith('source/scar/') and name!='source/scar/korea/effects.scar'):
                self.assertEqual(raw,(R/name).read_text('utf-8'),name)
        from rig_contract import read_contract
        sys.path.insert(0,str(R/'tools/art013'))
        for row in policy['source_changes']:self.assertEqual(row,'scar/korea/effects.scar')
        cfg=read_json(R/'project.json')
        self.assertEqual(cfg['owner'],json.loads(snap['project.json'])['owner'])
        self.assertEqual(cfg['bundle_key'],json.loads(snap['project.json'])['bundle_key'])

if __name__=='__main__':unittest.main()
'''.replace('        from rig_contract import read_contract\n','')

def apply_stage():
    D=R/'docs/update_015'; T=R/'tools/art015'
    sys.path.insert(0,str(T));from contracts import verify_native
    plan=read_json(D/'STAGED_REPAIR.json');cfg=read_json(R/'project.json')
    assert cfg['version']=='0.1.4'
    # Verify the entire stage and every destination immediately before mutation.
    for row in plan['native_changes']:
        assert file_sha(R/'inputs/native'/row['member'])==row['before']
        assert file_sha(W/'repaired'/row['member'])==row['after']
    p=R/'source/scar/korea/effects.scar';assert file_sha(p)==plan['scar_before']
    assert file_sha(W/'effects.scar')==plan['scar_after']
    native=read_json(R/'inputs/native-manifest.json')
    for row in plan['native_changes']:
        target=R/'inputs/native'/row['member'];shutil.copyfile(W/'repaired'/row['member'],target)
        native[row['member']]={**native[row['member']],'bytes':target.stat().st_size,'sha256':row['after'],'change':row['reason']}
    write_json(R/'inputs/native-manifest.json',native)
    shutil.copyfile(W/'effects.scar',p)
    policy={'schema':'korea.update-015-policy/v1',
        'allowed_changed':sorted([x['member'] for x in plan['native_changes']]+['scar/korea/effects.scar','garrison/civilizations.json']),
        'allowed_added':[],'allowed_removed':[],
        'native_changed':sorted(x['member'] for x in plan['native_changes']),
        'source_changes':['scar/korea/effects.scar'],
        'geometry_textures_skeletons_animation_graphs_gameplay_tables_unchanged':True}
    write_json(R/'source/update-015-policy.json',policy)
    cfg.update(version='0.1.5',update_policy='source/update-015-policy.json',
        baseline_members='docs/update_015/baseline-members.json.gz',build_stage='art015-current',
        rollback_folder='archives/art015-baseline',
        publication='Local 0.1.5 repair candidate; no push, tag, publication or installation authorized')
    write_json(R/'project.json',cfg)
    # Preserve the historical 012 -> 013 test using its actual saved 013 source.
    p=R/'tests/test_update_013_art.py';text=p.read_text('utf-8')
    assert text.count("['version']=='0.1.4'")==2
    p.write_text(text.replace("['version']=='0.1.4'","['version'] in ('0.1.4','0.1.5')"),encoding='utf-8')
    (R/'tests/test_update_015.py').write_text(TESTS,encoding='utf-8')
    p=R/'tools/build.py';text=p.read_text('utf-8')
    anchor="    config=read_json(ROOT/'project.json');verify()"
    assert text.count(anchor)==1
    text=text.replace(anchor,anchor+"\n    if config['version']=='0.1.5':\n        from art015.contracts import verify_native\n        print('NATIVE_MODEL_CONTRACTS',verify_native(ROOT/'inputs/native'),flush=True)")
    old="ROOT/'archives/art013-baseline'/previous['zip_sha256'][:12]/old.name"
    assert text.count(old)==1
    text=text.replace(old,"ROOT/config.get('rollback_folder','archives/art013-baseline')/previous['zip_sha256'][:12]/old.name")
    anchor="    delivery=out/'delivery';delivery.mkdir();package=delivery/(config['name']+'-Garrison-'+config['version']+'.zip')"
    assert text.count(anchor)==1
    text=text.replace(anchor,"    if config['version']=='0.1.5':details['changelog']='0.1.5: repair Korean body material keys and official lifecycle OR selectors; replace the unavailable Hwacha barrage-cleanup API. Geometry, rigs, textures, gameplay and identity preserved. Fresh-match acceptance pending.'\n"+anchor)
    text=text.replace("'world_art_changed':config['version'] in ('0.1.3','0.1.4')", "'world_art_changed':config['version'] in ('0.1.3','0.1.4','0.1.5')")
    p.write_text(text,encoding='utf-8')
    write_json(D/'APPLIED_REPAIR.json',{'native_changes':plan['native_changes'],
        'contracts':verify_native(R/'inputs/native'),'scar_sha256':file_sha(R/'source/scar/korea/effects.scar'),
        'native_content_editor_recook':'not required: geometry and compressed textures unchanged; native material-key and selector corrections only',
        'native_game_acceptance':'pending'})
    # Keep the exact executable recipe in the maintained source.
    shutil.copyfile(Path(__file__),T/'resume_repair.py')
    print('APPLIED_015',len(plan['native_changes']),'native changes; gameplay tables and geometry preserved',flush=True)

LUA_TESTS = '''"""Execute the real barrage script against an explicit stub engine boundary."""
import unittest
from pathlib import Path
from lupa import LuaRuntime, LuaError
R=Path(__file__).resolve().parents[1]
ENGINE="""
now=0; calls={applied=0,removed=0,stops=0,groups=0,destroyed=0,attacks=0}
player={id=1}; unit={id=11,owner=1,alive=true,command=17,squad={active=true,moving=false,accepted=false}}
KoreaState={debuffs={},barrages={}}
MAT_Weapon=1;MUT_Multiplication=2;CMD_AttackForced=17;CMD_Stop=18;SCMD_Attack=27;SCMD_Stop=28
function Korea_Alive(e) return e~=nil and e.alive end
function Korea_Entity(id) if id==unit.id then return unit end end
function Entity_GetPlayerOwner(e) return e.owner end
function Entity_GetID(e) return e.id end
function Entity_GetSquad(e) return e.squad end
function Entity_GetActiveCommand(e) return e.command end
function Korea_Functioning(e) return e.alive and not e.ruined end
function Korea_BP(kind,name) return name end
function World_GetGameTime() return now end
function Modifier_Create(...) return {} end
function Modifier_ApplyToEntity(...) calls.applied=calls.applied+1;return calls.applied end
function Korea_RemoveModifier(h) calls.removed=calls.removed+1 end
function SGroup_CreateUnique() calls.groups=calls.groups+1;return {} end
EGroup_CreateUnique=SGroup_CreateUnique
function SGroup_Add(g,e) g[1]=e end
EGroup_Add=SGroup_Add
function SGroup_Destroy(g) calls.destroyed=calls.destroyed+1 end
EGroup_Destroy=SGroup_Destroy
function LocalCommand_SquadPos(...) calls.attacks=calls.attacks+1 end
LocalCommand_EntityPos=LocalCommand_SquadPos
function LocalCommand_Squad(...) calls.stops=calls.stops+1 end
LocalCommand_Entity=LocalCommand_Squad
function Squad_HasActiveCommand(s) return s.active end
function Squad_IsMoving(s) return s.moving end
function Squad_HasAcceptedCommands(s) return s.accepted end
"""
class Barrage015(unittest.TestCase):
    def engine(self,old=False,keep=False):
        lua=LuaRuntime(unpack_returned_tuples=True);lua.execute(ENGINE)
        p=R/('tests/fixtures/art015-before/effects.scar' if old else 'source/scar/korea/effects.scar')
        lua.execute(p.read_text('utf-8'))
        lua.execute('KoreaEffects_Barrage({executer=unit,target={x=1,y=0,z=2}},player,'+str(keep).lower()+')')
        return lua
    def test_actual_old_fixture_reproduces_reported_nil_call(self):
        lua=self.engine(old=True)
        with self.assertRaisesRegex(LuaError,'Squad_GetActiveCommand'):
            lua.execute('now=7;KoreaEffects_Timers(now)')
    def test_completion_stops_once_removes_modifiers_and_destroys_groups(self):
        lua=self.engine();lua.execute('now=7;KoreaEffects_Timers(now);KoreaEffects_Timers(now)')
        c=lua.globals().calls
        self.assertEqual((c.stops,c.applied,c.removed,c.groups,c.destroyed),(1,2,2,2,2))
        self.assertTrue(lua.eval('next(KoreaState.barrages)==nil'))
    def test_move_newly_accepted_order_and_stop_are_respected(self):
        for interruption in ['unit.squad.moving=true','unit.squad.accepted=true','unit.squad.active=false']:
            lua=self.engine();lua.execute(interruption+';now=7;KoreaEffects_Timers(now)')
            c=lua.globals().calls;self.assertEqual(c.stops,0);self.assertEqual(c.removed,2)
    def test_death_and_capture_cleanup_without_old_owner_command(self):
        for loss in ['unit.alive=false','unit.owner=2']:
            lua=self.engine();lua.execute(loss+';now=2;KoreaEffects_Timers(now)')
            c=lua.globals().calls;self.assertEqual(c.stops,0);self.assertEqual(c.removed,2)
            self.assertTrue(lua.eval('next(KoreaState.barrages)==nil'))
    def test_repeated_barrage_and_keep_branch_remain_operable(self):
        lua=self.engine();lua.execute('now=7;KoreaEffects_Timers(now);now=8;KoreaEffects_Barrage({executer=unit,target={x=1}},player,false);now=15;KoreaEffects_Timers(now)')
        self.assertEqual(lua.globals().calls.stops,2);self.assertEqual(lua.globals().calls.removed,4)
        lua=self.engine(keep=True);lua.execute('now=6;KoreaEffects_Timers(now);now=7;KoreaEffects_Timers(now)')
        self.assertEqual(lua.globals().calls.stops,1);self.assertEqual(lua.globals().calls.removed,2)
if __name__=='__main__':unittest.main()
'''

def update_notes():
    D=R/'docs/update_015'
    p=R/'tests/test_update_012.py';text=p.read_text('utf-8')
    text=text.replace("['version'] in ('0.1.3','0.1.4')", "['version'] in ('0.1.3','0.1.4','0.1.5')")
    text=text.replace("['version']=='0.1.4'", "['version'] in ('0.1.4','0.1.5')")
    p.write_text(text,encoding='utf-8')
    (R/'tests/test_barrage_015.py').write_text(LUA_TESTS,encoding='utf-8')
    handoff='''# Korea 0.1.5 local repair candidate

This resumes the interrupted Korea work from “Fix Berber release 3 issues new”.
The owner reported green MISSING ABP cubes on Villagers, Spearmen and Gapsa,
absent landmark main models, and a Hwacha barrage crash in 0.1.4.

- The 72 custom body/mount models requested their exported atlas material key,
  while 014 supplied donor keys such as lod1/lod2/lod3. Bind the unchanged
  official shader/parameters/RGB textures/tint LUT under the actual geometry key.
  Unused cargo object materials are excluded; active donor LOD payloads match.
- The 36 custom rigid models encoded multi-state lifecycle alternatives with
  first connective 0 then 1. Current stock Chinese range and stable both use 1
  for every alternative. Match those exact native records, changing only the
  first connective word. Preserve single-state conditions and all state names.
- The game log reports effects.scar:134 calling unavailable
  Squad_GetActiveCommand. Use documented Squad_HasActiveCommand,
  Squad_IsMoving and Squad_HasAcceptedCommands before the existing timed Stop.
  Keep death, capture, modifier cleanup and temporary-group lifetimes intact.

No geometry, UV, texture, skeleton, motion clip/graph, gameplay table, identity,
voice or UI is changed. One-root skeleton LOD sharing also exists in retained
Vietnamese/Persian resources; its presence alone was not a proven defect and it
is preserved. The starting Scout uses a stock model and was not custom-rig proof.

The Lua regressions execute the actual old script to reproduce the nil call,
then test the corrected script for completion, move/queue/Stop, death/capture,
repeated use and the keep branch. This is a stubbed engine boundary, not a match.
A new stationary ground-attack order cannot be distinguished by these documented
APIs; retest cancellation/retargeting in game.

Read update_015/APPLIED_REPAIR.json, OFFICIAL_CONDITIONS.json,
BUILD_VERIFICATION.json and update_015/COMPLETION.json for final evidence.
Native material and condition serialization is corrected directly. Geometry and
compressed textures were not recooked; the final civilization archive is freshly
assembled/read back. Earlier 014 cook logs remain historical evidence.

Fresh-match appearance, animations, lifecycle, save/load, multiplayer, AI and
VRAM/frame time remain pending. No push, tag, publication or installation.
The owner requested removal of task-generated E:/F: temporary files after final
ZIP/rollback/input verification; keep editable inputs and compact diagnostics.
'''
    (R/'docs/UPDATE_015.md').write_text(handoff,encoding='utf-8')
    player='''# Koreans — Garrison 0.1.5 local test candidate

Import Koreans-Garrison-0.1.5.zip through Garrison 0.1.9 or newer. Enable Koreans,
disable older Korean packages and the combined pack, select Koreans directly,
and use native Standard with Tuning Pack None. Start a fresh Dark Age match.
This ZIP includes the civilization, art and existing audio.

0.1.5 corrects the custom body atlas-material names, landmark/equipment lifecycle
alternatives and the Hwacha barrage cleanup call that crashed 0.1.4. Existing
geometry, textures, rigs, motion graphs, voices, gameplay and identity remain.

Native acceptance is pending. Retest six starting Villagers/one Scout/no Official;
male/female Villagers, Spearmen, Gapsa and every other unit at all ages; movement,
attacks/tools/torch/death; two player colours; every landmark's preview,
construction, healthy/damage, targeting, ruins and repair; Hwacha ability expiry,
move/Stop/retarget/cancel, repeated use, death and capture. Check close/far LODs.
The starting Scout is stock; train custom Scout tiers too.

Save/load, multiplayer, AI, repeated matches and measured frame time/VRAM are
separate unverified gates. No installation or publication was performed.
Credits: hosein81 and chilly5.
'''
    (R/'START-HERE.md').write_text(player,encoding='utf-8')
    p=R/'README.md';text=p.read_text('utf-8');idx=text.index('0.1.2 populates')
    p.write_text('''# Koreans — independent Garrison civilization

Current local repair candidate: **0.1.5**, `release/Koreans-Garrison-0.1.5.zip`.
Corrects Korean body material keys, lifecycle alternatives on custom rigid
models, and the unavailable Hwacha cleanup API. Existing editable geometry,
textures, rigs, voices, gameplay and stable identity are preserved.
Read [the repair handoff](docs/UPDATE_015.md) and [player instructions](START-HERE.md).
Fresh native appearance/animation and barrage retesting remain pending.
No new commit, push, tag, publication or installation is authorized.

'''+text[idx:],encoding='utf-8')
    for name in ['AGENTS.md','docs/DEVELOPMENT.md','docs/KOREA_KNOWN_ISSUES.md']:
        p=R/name;old=p.read_text('utf-8')
        notice='''# Korea 0.1.5 repair, 2026-10-31

The owner resumed the latest Korea missing-model/landmark/Hwacha-crash repair.
Read docs/UPDATE_015.md and docs/update_015 receipts. Version 0.1.4 failed native
visual/barrage acceptance; its package checks remain historical. The new local
candidate requires fresh-match testing. Preserve sources, identity, editable art,
native inputs and exact 0.1.3/0.1.4 rollback ZIPs. No push or installation.
Owner requests cleanup of this task's generated E:/F: files after verification.

---

'''
        p.write_text(notice+old,encoding='utf-8')
    # Retain both the failed setup run and its diagnosis before the final run.
    old=D/'source-tests.log'
    if old.exists():shutil.copyfile(old,D/'initial-test-setup-failure.log')
    shutil.copyfile(Path(__file__),R/'tools/art015/resume_repair.py')
    print('CURRENT_NOTES_AND_REAL_LUA_REGRESSIONS_READY',flush=True)

def run_checks_and_build():
    assert read_json(R/'project.json')['version']=='0.1.5'
    D=R/'docs/update_015';W.mkdir(exist_ok=True)
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    env['PYTHONPATH']=str(W/'testdeps')
    for args,log in [(['-B','-m','unittest','discover','-s','tests','-v'],'source-tests.log'),
                     (['-B','tools/build.py','--replace-current'],'build.log')]:
        print('RUNNING',args,flush=True)
        with (D/log).open('w',encoding='utf-8') as f:
            proc=subprocess.run([sys.executable,*args],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
        if proc.returncode:raise RuntimeError('Inspect '+str(D/log))
        print('PASSED',log,flush=True)

def finalize():
    import re
    D=R/'docs/update_015';v=read_json(R/'docs/BUILD_VERIFICATION.json')
    assert v['version']=='0.1.5' and v['all_member_readback_sha256'] and v['native_crc_sha1'] and v['zip_crc']
    z=R/'release'/v['zip_name']; assert file_sha(z)==v['zip_sha256'] and z.stat().st_size==v['zip_bytes']
    with zipfile.ZipFile(z) as f:
        assert f.testzip() is None
        sgas=[x for x in f.infolist() if x.filename.endswith('.sga')];assert len(sgas)==1
        with f.open(sgas[0]) as s:assert hashlib.file_digest(s,'sha256').hexdigest()==v['archive_sha256']
        starts=[n for n in f.namelist() if n.lower().endswith(('start-here.md','start-here.txt'))]
        assert len(starts)==1 and f.read(starts[0]).decode('utf-8').replace('\r\n','\n')==(R/'START-HERE.md').read_text('utf-8')
    baseline=read_json(D/'BASELINE_014.json')
    rollback=R/'archives/art015-baseline'/baseline['zip_sha256'][:12]/baseline['zip_name']
    assert file_sha(rollback)==baseline['zip_sha256']
    old013=read_json(R/'docs/update_014/BASELINE_013.json')
    roll013=R/'archives/art013-baseline'/old013['zip_sha256'][:12]/old013['zip_name']
    assert file_sha(roll013)==old013['zip_sha256']
    snap=json.loads(gzip.decompress((D/'before-source.json.gz').read_bytes()))
    previous_native=json.loads(snap['inputs/native-manifest.json']);native=read_json(R/'inputs/native-manifest.json')
    for m in native:
        if m.endswith(('.rrtex','.rrgeom')):assert native[m]['sha256']==previous_native[m]['sha256']
    budget=read_json(R/'docs/update_014/ASSET_BUDGET.json')
    art=sum(row['bytes'] for name,row in native.items() if name.startswith(('art/kr013/','art/kr014/')))
    budget.update(version='0.1.5',zip_bytes=v['zip_bytes'],zip_sha256=v['zip_sha256'],
        archive_bytes=v['archive_bytes'],archive_sha256=v['archive_sha256'],
        zip_increase_vs_014=v['zip_bytes']-baseline['zip_bytes'],
        zip_increase_vs_013=v['zip_bytes']-old013['zip_bytes'],
        zip_increase_vs_accepted_011=v['zip_bytes']-next((R/'archives/tested_0.1.1').glob('*.zip')).stat().st_size,
        packaged_additional_art_input_bytes=art,
        texture_accounting='Exact 014 compressed textures and dimensions unchanged; all current whole-file hashes verified by builder',
        archive_delta_vs_014=v['archive_bytes']-baseline['archive_bytes'])
    assert art<=300000000 and v['zip_bytes']<600000000
    write_json(D/'ASSET_BUDGET.json',budget)
    text=(D/'source-tests.log').read_text('utf-8')
    count=int(re.search(r'Ran (\d+) tests',text).group(1));assert count==39 and text.rstrip().endswith('OK')
    write_json(R/'docs/SOURCE_TESTS.json',{'version':'0.1.5','passed':True,'tests':count,
        'command':'PYTHONPATH=<temporary lupa 2.6 wheel target>; Python 3.13 -B -m unittest discover -s tests -v',
        'log':'docs/update_015/source-tests.log','actual_lua_barrage_regressions':5,
        'native_gameplay':'not established by stubbed or static tests'})
    (R/'tools/art015/requirements-test.txt').write_text('lupa==2.6\n',encoding='utf-8')
    current=R/'output/current'
    for name in ['validate.log','assembly.log','verification.json','codex-report.json']:
        shutil.copyfile(current/name,D/name)
    for name in ['expected-members.json','build-recipe.json']:
        (D/(name+'.gz')).write_bytes(gzip.compress((current/name).read_bytes(),mtime=0))
    write_json(D/'COMPLETION.json',{'version':'0.1.5','tests':count,'actual_lua_barrage_regressions':5,
        'native_model_material_contracts':108,'unit_material_key_repairs':72,'rigid_model_selector_repairs':36,
        'native_archive_member_readbacks':v['members'],'changed_members':len(v['changed_members']),
        'baseline_members_preserved':v['preserved_baseline_members'],'added_members':v['added_members'],
        'removed_members':v['removed_members'],'zip_name':v['zip_name'],'zip_bytes':v['zip_bytes'],
        'zip_sha256':v['zip_sha256'],'rollback_014_verified':str(rollback),'rollback_013_verified':str(roll013),
        'native_burn':'No new geometry/texture Content Editor cook; existing resource bytes corrected and fresh supported civilization assembly verified',
        'MCP_check_code':{'unknown_calls':0,'missing_locdb_ids':0,'unchanged_low_confidence_api':'Player_GetAbilityBPCost; official ScarDoc entry, not edited'},
        'native_game_appearance_animation_barrage_lifecycle':'pending owner fresh-match test',
        'save_load_multiplayer_ai_performance':'not qualified','push_tag_publication_installation':'not performed',
        'cleanup':'pending'})
    # Measure only explicit task-owned generated directories, rejecting every link.
    targets=[W,current];inventory=[]
    for target in targets:
        resolved=target.resolve()
        assert resolved==target and target.is_dir() and not target.is_junction() and not target.is_symlink()
        assert resolved in [Path('F:/aoe_4_temp/Temp_aoe4/k15'),R/'output/current']
        files=0;size=0
        for root,dirs,names in os.walk(target,followlinks=False):
            for name in dirs+names:
                path=Path(root)/name
                assert not path.is_symlink() and not path.is_junction()
                assert path.resolve().is_relative_to(resolved)
                if path.is_file():files+=1;size+=path.stat().st_size
        inventory.append({'path':str(resolved),'files':files,'logical_bytes':size})
    # E: tools from the earlier milestone were already retired; do not recreate
    # them or interpret unrelated mod folders as this task's temporary data.
    e=Path('E:/aoe4_korea_014_model_tools');assert not e.exists()
    write_json(D/'CLEANUP_PLAN.json',{'targets':inventory,'E_task_model_tools_already_absent':str(e),
        'preserved':['release ZIP','0.1.3/0.1.4 rollback ZIPs','source/tables','source/scar','authoring','inputs/native','Git','compact diagnostics'],
        'critical_files':{str(p):file_sha(p) for p in [z,rollback,roll013,R/'inputs/native-manifest.json',R/'source/master-index.json']}})
    shutil.copyfile(Path(__file__),R/'tools/art015/resume_repair.py')
    print('FINAL_015_PACKAGE_VERIFIED',v['zip_bytes'],'bytes; cleanup inventory',inventory,flush=True)

def cleanup():
    D=R/'docs/update_015';plan=read_json(D/'CLEANUP_PLAN.json')
    for name,digest in plan['critical_files'].items():assert file_sha(Path(name))==digest,name
    # Compact useful generated diagnostics before removing disposable copies.
    diagnostic=D/'generated-diagnostics.zip';assert not diagnostic.exists()
    with zipfile.ZipFile(diagnostic,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for row in plan['targets']:
            target=Path(row['path'])
            for root,dirs,files in os.walk(target,followlinks=False):
                assert all(not (Path(root)/name).is_symlink() and not (Path(root)/name).is_junction() for name in dirs+files)
                for name in files:
                    p=Path(root)/name
                    if p.suffix.lower() in ['.log','.json'] and p.stat().st_size<10_000_000 and 'testdeps' not in p.parts:
                        z.write(p,target.name+'/'+p.relative_to(target).as_posix())
    with zipfile.ZipFile(diagnostic) as z:assert z.testzip() is None
    before=shutil.disk_usage('F:/').free;removed=[]
    for row in plan['targets']:
        target=Path(row['path']);resolved=target.resolve()
        assert resolved in [Path('F:/aoe_4_temp/Temp_aoe4/k15'),R/'output/current']
        assert resolved==target and not target.is_junction() and not target.is_symlink()
        assert (R/'release/Koreans-Garrison-0.1.5.zip').is_file()
        # One filesystem implementation end to end; absolute targets were checked.
        shutil.rmtree(target)
        assert not target.exists();removed.append(row)
    for name,digest in plan['critical_files'].items():assert file_sha(Path(name))==digest,name
    from inputs import verify
    verify()
    with zipfile.ZipFile(R/'release/Koreans-Garrison-0.1.5.zip') as z:assert z.testzip() is None
    e=Path(plan['E_task_model_tools_already_absent']);assert not e.exists()
    result={'removed':removed,'logical_bytes_removed':sum(x['logical_bytes'] for x in removed),
        'files_removed':sum(x['files'] for x in removed),'observed_F_free_space_increase':shutil.disk_usage('F:/').free-before,
        'E_task_model_tools_absent':str(e),'E_deleted_bytes_this_run':0,
        'F_task_temp_root_empty':not any(W.parent.iterdir()),
        'protected_input_hashes_reverified':True,'release_and_rollback_hashes_reverified':True,
        'generated_diagnostics_zip_sha256':file_sha(diagnostic)}
    write_json(D/'CLEANUP.json',result)
    v=read_json(D/'COMPLETION.json');v['cleanup']='complete; see CLEANUP.json';write_json(D/'COMPLETION.json',v)
    shutil.copyfile(Path(__file__),R/'tools/art015/resume_repair.py')
    print('CLEANUP_COMPLETE',json.dumps(result),flush=True)

def cleanup_python_caches():
    D=R/'docs/update_015';result=read_json(D/'CLEANUP.json');plan=read_json(D/'CLEANUP_PLAN.json')
    for name,digest in plan['critical_files'].items():assert file_sha(Path(name))==digest
    removed=[]
    for target in [R/'tools/__pycache__',R/'tools/art013/__pycache__',R/'tools/art014/__pycache__']:
        if not target.exists():continue
        assert target.resolve()==target and target.name=='__pycache__'
        assert target.resolve().is_relative_to((R/'tools').resolve())
        assert not target.is_junction() and not target.is_symlink()
        files=list(target.iterdir());assert all(p.is_file() and p.suffix=='.pyc' and not p.is_symlink() for p in files)
        row={'path':str(target),'files':len(files),'logical_bytes':sum(p.stat().st_size for p in files)}
        shutil.rmtree(target);assert not target.exists();removed.append(row)
    result['removed'].extend(removed)
    result['logical_bytes_removed']+=sum(x['logical_bytes'] for x in removed)
    result['files_removed']+=sum(x['files'] for x in removed)
    result['python_generated_caches_removed']=True
    for name,digest in plan['critical_files'].items():assert file_sha(Path(name))==digest
    write_json(D/'CLEANUP.json',result)
    shutil.copyfile(Path(__file__),R/'tools/art015/resume_repair.py')
    print('GENERATED_PYTHON_CACHES_REMOVED',removed,flush=True)

if __name__=='__main__':
    if '--apply-stage' in sys.argv:apply_stage()
    elif '--update-notes' in sys.argv:update_notes()
    elif '--finalize' in sys.argv:finalize()
    elif '--cleanup' in sys.argv:cleanup()
    elif '--cleanup-python-caches' in sys.argv:cleanup_python_caches()
    elif '--checks-build' in sys.argv:run_checks_and_build()
    else:prepare()
