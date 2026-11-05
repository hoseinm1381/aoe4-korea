"""Rebuild one complete independent civilization and one playable import ZIP.

Requires Python 3.13, installed Garrison authoring/core and Content Editor.
Korea 0.2.1 was built with the installed 0.1.13 native SDK.
No combined checkout, separate sound download, GitHub token or live Blender needed.
"""
import argparse,hashlib,json,os,shutil,subprocess,zipfile,gzip,tempfile,copy
from pathlib import Path
from runtime import ROOT,EXT,read_json,write_json,import_table,rgd,stock_game,mod_bundle
from codex import build as build_codex
from inputs import verify

def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args,log):
    with Path(log).open('w',encoding='utf-8') as stream:
        p=subprocess.run([str(x) for x in args],stdout=stream,stderr=subprocess.STDOUT)
    if p.returncode:raise RuntimeError('Command failed; inspect '+str(log))
def safe_output_cleanup(out,owner):
    expected=(ROOT/'output/current').resolve()
    if out.resolve()!=expected or not out.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Only this repository output/current can be reused')
    if out.is_symlink() or out.is_junction():raise ValueError('Linked output is protected')
    receipt=read_json(out/'verification.json')
    if receipt.get('owner')!=owner or not receipt.get('all_member_readback_sha256'):raise ValueError('Only a verified previous build may be replaced')
    for directory,dirs,files in os.walk(out,followlinks=False):
        for name in dirs+files:
            p=Path(directory)/name
            if p.is_symlink() or p.is_junction() or not p.resolve().is_relative_to(expected):raise ValueError('Linked/escaped output is protected')
    shutil.rmtree(out)
def build(out,prepare_only=False,replace_current=False):
    config=read_json(ROOT/'project.json')
    if config.get('build_hold'):raise ValueError(config['build_hold'])
    verify()
    if config.get("excluded_tables") and config.get("research_tooltips") != "stock":
        from research016_ui import verify as verify_research_tooltips
        verify_research_tooltips()
    if config['version'] in ('0.2.4','0.2.5'):
        if config['version']=='0.2.5':
            from release025 import verify as verify025
            verify025()
        else:
            from release024 import verify as verify024
            verify024()
    elif config['version']=='0.2.3':
        from release023 import verify as verify023
        verify023()
    elif config['version']=='0.2.2':
        from release022 import verify as verify022
        verify022()
    elif config['version']=='0.2.1':
        from release021 import verify as verify021
        verify021()
    elif config['version']=='0.2.0':
        from voice020_release import verify_source as verify_voice020_source
        verify_voice020_source()
    if config['version']=='0.1.6':
        from release016 import verify_source
        verify_source()
    if config['version']=='0.1.5':
        from art015.contracts import verify_native
        print('NATIVE_MODEL_CONTRACTS',verify_native(ROOT/'inputs/native'),flush=True)
    release=ROOT/'release';previous=None
    if release.exists() and any(release.iterdir()) and not prepare_only:
        if not replace_current:raise ValueError('Use --replace-current to replace the verified local player ZIP after the new build passes')
        previous=read_json(ROOT/'docs/BUILD_VERIFICATION.json')
        old=release/previous['zip_name']
        if previous.get('owner')!=config['owner'] or list(release.iterdir())!=[old] or digest(old)!=previous['zip_sha256']:raise ValueError('Unknown or changed release files are protected')
    if out.exists() and replace_current and not prepare_only:safe_output_cleanup(out,config['owner'])
    if out.exists():raise ValueError('Build folder already exists; preserve previous evidence: '+str(out))
    out.mkdir(parents=True)
    recipe={k:config[k] for k in ('schema','owner','race','dispatcher','shared_entities')};recipe.update(attributes=[],members=[])
    expected={};prepared=out/'prepared'
    def add(member,p,toc):
        p=p.resolve();rawhash=digest(p)
        row={'member':member,'file':str(p),'sha256':rawhash}
        if toc=='attrib':recipe['attributes'].append(row)
        else:row['toc']=toc;recipe['members'].append(row)
        expected[member]={'toc':toc,'sha256':rawhash,'bytes':p.stat().st_size}
    native=read_json(ROOT/'inputs/native-manifest.json')
    baseline_tocs=read_json(ROOT/'source/baseline-members.json') if (ROOT/'source/baseline-members.json').exists() else {}
    for member,row in sorted(native.items()):add(member,ROOT/'inputs/native'/member,row.get('toc',baseline_tocs.get(member,{}).get('toc','data')))
    for p in sorted((ROOT/'source/resources').rglob('*')):
        if p.is_file():
            member=p.relative_to(ROOT/'source/resources').as_posix()
            add(member,p,baseline_tocs.get(member,{}).get('toc','data'))
    tables={}
    for p in sorted((ROOT/'source/tables').rglob('*.rgd.json')):
        member=p.relative_to(ROOT/'source/tables').as_posix()[:-5]
        exclusion=config.get('excluded_tables',{}).get(member)
        if exclusion:
            if digest(p)!=exclusion['sha256']:raise ValueError('Reviewed excluded table changed: '+member)
            continue
        tables[member]=rgd.read(import_table(read_json(p)))
    if config['version'] in ('0.2.0','0.2.1','0.2.2','0.2.3','0.2.4','0.2.5','0.2.11','0.2.12','0.2.13','0.3.0'):
        from voice020_release import retained_codex
        _,codex_report=retained_codex(tables,config)
    else:_,codex_report=build_codex(tables,config)
    write_json(out/'codex-report.json',codex_report)
    roots=[(m,d) for m,d in tables.items() if m.count('/')==1]
    if len(roots)!=1:raise ValueError('Expected sole native attribute root')
    flags=[n for _,n in rgd.flatten(roots[0][1].nodes) if n.key=='override_instances']
    if len(flags)!=1 or flags[0].kind!='Boolean' or flags[0].value is not False:raise ValueError('Root must be additive native Boolean false')
    for member,doc in sorted(tables.items()):
        p=prepared/member;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(rgd.write(doc));add(member,p,'attrib')
    for p in sorted((ROOT/'source/scar').rglob('*.scar')):add('scar/'+p.relative_to(ROOT/'source/scar').as_posix(),p,'data')
    if (ROOT/'source/locale/en.json').exists():
        locale=read_json(ROOT/'source/locale/en.json')
        text=''.join(str(k)+'\t'+str(v)+'\r\n' for k,v in sorted(locale.items(),key=lambda row:int(row[0])))
        p=prepared/'en/en.ucs';p.parent.mkdir(parents=True);p.write_bytes(text.encode('utf-16'));add('en/en.ucs',p,'locale')
    if expected['mod.bin']['toc']!='info' or expected['mod.rrtex']['toc']!='info':raise ValueError('Native metadata has wrong TOC')
    write_json(out/'build-recipe.json',recipe);write_json(out/'expected-members.json',expected)
    source_fingerprint=hashlib.sha256(json.dumps(expected,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    core=EXT/'bin/core/garrison-core.exe'
    print('NATIVE_VALIDATION',config['race'],len(tables),'tables',flush=True)
    run([core,'civilization','validate',out/'build-recipe.json'],out/'validate.log')
    if prepare_only:
        print('PREPARED_AND_VALIDATED',config['race'],len(tables),'tables',len(expected),'members',flush=True)
        return
    assembly=Path(tempfile.gettempdir())/'garrison-independent-builds'/config['owner']/config.get('build_stage','current')
    if assembly.exists():raise ValueError('Previous native assembly diagnostics are protected: '+str(assembly))
    assembly.parent.mkdir(parents=True,exist_ok=True)
    print('NATIVE_ASSEMBLY',config['race'],str(assembly),flush=True)
    run([core,'civilization','build',out/'build-recipe.json','--output',assembly],out/'assembly.log')
    return finalize(out,config,expected,native,tables,source_fingerprint,previous,assembly,codex_report)

def finalize(out,config,expected,native,tables,source_fingerprint,previous,assembly,codex_report,reuse_package=False):
    release=ROOT/'release'
    report=read_json(assembly/'report.json');archive=Path(report['archive']);game=stock_game.current()
    listing=game.archiver.run(['list',str(archive),'--verify'])
    if listing['archive']['name']!=config['owner'].replace('-','') or not listing['archive']['verification']['verified']:raise ValueError('Final native identity/CRC/SHA1 differs')
    actual={m['path']:m for m in listing['members']}
    if set(actual)!=set(report['members']):raise ValueError('Final member inventory differs')
    # Reuse the supported assembler's full readback if retained, otherwise make
    # one fresh readback. Never infer member bytes from basenames alone.
    candidates=[p for p in (assembly).rglob('civilizations.json') if p.parent.name=='garrison']
    readback=None
    for candidate in candidates:
        base=candidate.parent.parent
        if all((base/m).is_file() for m in actual):readback=base;break
    if readback is None:
        readback=out/'readback';game.archiver.run(['extract',str(archive),str(readback),'--filter',''])
    for member,row in report['members'].items():
        if actual[member]['toc']!=row['toc'] or digest(readback/member)!=row['sha256']:raise ValueError('Final readback differs: '+member)
    for member,row in expected.items():
        if member==config['dispatcher']:
            if not (readback/member).read_bytes().endswith((ROOT/'source/scar'/member[5:]).read_bytes()):raise ValueError('Dispatcher body changed')
        elif report['members'][member]!=row:raise ValueError('Unexpected source/native transformation: '+member)
    declaration=read_json(readback/'garrison/civilizations.json')
    for row in [declaration['attribute_root']]+declaration['races']+declaration['scripts']:
        if digest(readback/row['member'])!=row['sha256']:raise ValueError('Declaration digest differs')
    policy=read_json(ROOT/config.get('update_policy','source/update-012-policy.json'))
    baseline=json.loads(gzip.decompress((ROOT/config.get('baseline_members','docs/update_012/baseline-members.json.gz')).read_bytes()))['members']
    changed=sorted(m for m in baseline if m in report['members'] and baseline[m]!=report['members'][m])
    added=sorted(set(report['members'])-set(baseline));removed=sorted(set(baseline)-set(report['members']))
    if set(removed)!=set(policy['allowed_removed']) or set(changed)-set(policy['allowed_changed']) or set(added)!=set(policy['allowed_added']):
        raise ValueError('Update escaped its explicit source/art allowlist: '+str((changed,added,removed)))
    if config['version'] in ('0.2.0','0.2.1','0.2.2'):
        media_bytes=sum(row['bytes'] for m,row in report['members'].items() if m.startswith(('art/','audio/')))
        if media_bytes>300000000:raise ValueError('Korea media budget exceeded: '+str(media_bytes))
    if config['version']=='0.2.3':
        from release023 import verify as verify023
        verify023()
        scope=read_json(ROOT/'docs/update_023/SCOPE_VERIFICATION.json')
        media_bytes=sum(row['bytes'] for m,row in report['members'].items() if m.startswith(('art/','audio/')))
        if media_bytes!=scope['media_bytes'] or media_bytes>=400000000:raise ValueError('Approved audio-only quality budget differs')
    if config['version'] in ('0.2.4','0.2.5'):
        if config['version']=='0.2.5':
            from release025 import verify as verify025
            verify025()
        else:
            from release024 import verify as verify024
            verify024()
        media_bytes=sum(row['bytes'] for m,row in report['members'].items() if m.startswith(('art/','audio/')))
        if media_bytes!=read_json(ROOT/('docs/update_025/baseline-build.json' if config['version']=='0.2.5' else 'docs/update_024/baseline-build.json'))['media_bytes']:raise ValueError('Diagnostic release must preserve exact accepted higher-quality media budget')
    card=read_json(ROOT/'source/client-card.json')
    details={'id':config['race'],'name':config['name'],'version':config['version'],
      'summary':config['name']+' independent civilization.',
      'description':'Select '+config['name']+' with native Standard and Tuning Pack=None.',
      'author':'hosein81 and chilly5','updated':'2026-11-02' if config['version'] in ('0.2.0','0.2.1','0.2.2') else '2026-11-01','min_garrison':'0.1.9',
      'content_types':['civilization'],'cover':'cover.png',
      'changelog':'Local standalone candidate from accepted combined 1.1.0. Independent native dropdown, preserved gameplay/art/audio and editable whole-file source.'}
    details.update(card)
    details['changelog']='0.1.2: populated unique units and technologies, detailed bonuses, correct research ages, spaced tech trees, plural civilization labels and selector flags. Berber music/voice compression from retained masters. World gameplay, identities and loading/art quality preserved.'
    if config['version']=='0.1.3':details['changelog']='0.1.3: Korean unit, mount, equipment, ordinary-building and unique-building art; private native visual bindings and isolated trader/monk consumers. Gameplay values and independent identity preserved. Native match acceptance pending.'
    if config['version']=='0.1.4':details['changelog']='0.1.4: remove inherited free Imperial Official; repair official unit skeleton/LOD and RGB mask bindings; correct rigid unique-building attachment; add editable Korean Hwacha with native siege animation ownership. Native match acceptance pending.'
    if config['version']=='0.1.5':details['changelog']='0.1.5: repair Korean body material keys and official lifecycle OR selectors; replace the unavailable Hwacha barrage-cleanup API. Geometry, rigs, textures, gameplay and identity preserved. Fresh-match acceptance pending.'
    if config['version']=='0.1.6':details['changelog']='0.1.6: restore extensive dynamic player colour and cavalry skin bindings; fix Gapsa duplicate spear by restoring its shield; correct Korean research prices, book tooltips and refunds. Native match acceptance pending.'
    if config['version']=='0.2.0':details['changelog']='0.2.0: Korean unit speech with original role/gender voices, four age-specific dialogue banks, multiple lines/takes and private native speech suppression. Researched historical diction uses documented pronunciation approximations; expert/native listening remains pending. Existing art, animations, research and identity preserved.'
    if config['version']=='0.2.1':details.update(min_garrison='0.1.13',changelog='0.2.1: restore five native starting sheep; match Korean voices by compiled PBG ID and known owner names like Berber; initialize local voice presentation independently of gameplay enrollment. Original audio, models, research and identity preserved. A successful normal Garrison launch is required for its audio backend.')
    if config['version']=='0.2.2':details.update(min_garrison='0.1.13',changelog='0.2.2: include matching documented Garrison runtime helper and speech-volume bus; bounded 25-45 second phase diagnostics. Existing voice controller, all recordings, five starting sheep, models and gameplay preserved. Current client startup/no-consumer failure remains an external playback blocker; no audible fix is claimed by packaging.')
    if config['version']=='0.2.3':details.update(updated='2026-11-02',min_garrison='0.1.13',changelog='0.2.3: all 7632 Korean dialogue takes rebuilt from lossless masters at 24 kHz with higher-fidelity Vorbis encoding. Same voices, lines, routing, speech bus, five starting sheep, models and gameplay as owner-tested 0.2.2. Historical pronunciation remains approximate. Full 0.2.3 native listening pending.')
    if config['version']=='0.2.4':details.update(updated='2026-11-02',min_garrison='0.1.13',changelog='0.2.4 diagnostic: bounded paired callback/subsystem and native-operation logging for the reported random 6:42 crash. All original gameplay statements, models, higher-quality voices and five starting sheep retained. No crash fix or Mounted Hwarang visual repair claimed; reproduce in a fresh single-player match and retain warnings.log.')
    if config['version']=='0.2.5':details.update(updated='2026-11-04',min_garrison='0.1.13',changelog='0.2.5 diagnostic: Korean voice controller disabled at startup. All voice scripts, helper and audio files remain packaged unchanged except the startup guard. Gameplay, art, tuning and 0.2.4 tracing retained. Crash isolation test; no crash fix claimed.')
    if config['version']=='0.2.11':details.update(updated='2026-11-05',min_garrison='0.1.13',changelog='Korea starts with 200 food, 200 wood and 100 gold. Includes Korean dialogue, stock research tooltips and group Scholar Supervise.')
    if config['version']=='0.2.12':details.update(updated='2026-11-05',min_garrison='0.1.13',changelog='Fix Fortress barrage cleanup and Korean research payment/cancellation. Stock green research buttons, 50% larger fortress visuals, expanded dynamic player colour, and Korean voice controller enabled.')
    if config['version']=='0.2.13':details.update(updated='2026-11-05',min_garrison='0.1.13',changelog='Native Literature prices and tooltips for Korean research, corrected completion and refund order, wider close-range keep barrage coverage, stronger unique building player colours, and a 50% larger Gyeongbok Palace model.')
    if config['version']=='0.3.0':details.update(updated='2026-11-06',min_garrison='0.1.16',changelog='Korean orders repeat their own voice reply at most every five seconds per unit. A different task can reply right away, or after the current line finishes.')
    delivery=out/'delivery';package=delivery/(config['name']+'-Garrison-'+config['version']+'.zip')
    if not reuse_package:
        delivery.mkdir()
        mod_bundle.write_package(delivery/'package',package,bundle_key=config['bundle_key'],details=details,
          archives=[(config['race'],'civilization',archive)],start_here=(ROOT/'START-HERE.md').read_text(encoding='utf-8'),cover=ROOT/'source/presentation/cover.png')
        # Maximum standard ZIP compression; preserve every SDK-generated member byte.
        optimized=package.with_suffix('.optimized.zip')
        with zipfile.ZipFile(package) as original,zipfile.ZipFile(optimized,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as target:
            for info in original.infolist():
                compressed=copy.copy(info);compressed.compress_type=zipfile.ZIP_DEFLATED;compressed._compresslevel=9
                with original.open(info) as source,target.open(compressed,'w',force_zip64=info.file_size>=2**31) as dest:
                    shutil.copyfileobj(source,dest,1024*1024)
        if optimized.stat().st_size<package.stat().st_size:os.replace(optimized,package)
        else:optimized.unlink()
    with zipfile.ZipFile(package) as z:
        if z.testzip() is not None:raise ValueError('ZIP CRC failure')
        names=[n for n in z.namelist() if Path(n).name=='garrison.json']
        if len(names)!=1:raise ValueError('Expected one Garrison manifest')
        manifest=json.loads(z.read(names[0]));members=manifest['members']
        if manifest['bundle_key']!=config['bundle_key'] or manifest['details']['version']!=config['version']:raise ValueError('Packaged identity/version differs')
        if manifest['details']!=details:raise ValueError('Packaged release metadata differs')
        if len(members)!=1 or members[0]['role']!='civilization':raise ValueError('Expected one playable civilization archive')
        prefix=names[0][:-len('garrison.json')]
        with z.open(prefix+members[0]['path']) as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=digest(archive):raise ValueError('Packaged SGA hash differs')
    if package.stat().st_size>=600000000:raise ValueError('Import ZIP exceeds 600000000-byte cap')
    receipt={'race':config['race'],'version':config['version'],'owner':config['owner'],
      'source_fingerprint':source_fingerprint,'tables':len(tables),'members':len(actual),
      'archive_bytes':archive.stat().st_size,'archive_sha256':digest(archive),
      'zip_name':package.name,'zip_bytes':package.stat().st_size,'zip_sha256':digest(package),
      'all_member_readback_sha256':True,'native_crc_sha1':True,'zip_crc':True,
      'preserved_native_media_members':sum(1 for m in native if m.startswith(('art/','audio/'))),
      'native_game_test':'pending','multiplayer_save_ai_performance':'not qualified',
      'publication':'not performed','changed_members':changed,'added_members':added,
      'preserved_baseline_members':len(baseline)-len(changed)-len(removed),'native_codex_retest':'pending','removed_members':removed,'assembly_path':str(assembly),'baseline_zip_bytes':previous['zip_bytes'] if previous else None,'audio_full_decode_verified':bool(config['race']=='berbers'),'world_art_changed':config['version'] in ('0.1.3','0.1.4','0.1.5','0.1.6'),'native_input_manifest_sha256':digest(ROOT/'inputs/native-manifest.json'),'editable_master_index_sha256':digest(ROOT/'source/master-index.json')}
    if config['version'] in ('0.2.0','0.2.1','0.2.2','0.2.3','0.2.4','0.2.5'):
        coverage=read_json(ROOT/'docs/voices020/BANK_COVERAGE.json')
        receipt.update(audio_full_decode_verified=True,voice_profiles=coverage['profiles'],voice_age_banks=coverage['age_banks'],dialogue_clips=coverage['dialogue_clips'],voice_squad_blueprints=len(coverage['units']),media_bytes=media_bytes,zip_increment_vs_016=package.stat().st_size-read_json(ROOT/'docs/voices020/baseline-build.json')['zip_bytes'],historical_pronunciation_qualified=False)
    if config['version']=='0.2.1':receipt.update(zip_increment_vs_020=package.stat().st_size-read_json(ROOT/'docs/update_021/baseline-build.json')['zip_bytes'],native_starting_sheep=5,normal_client_audio_launch_required=True)
    if config['version']=='0.2.2':receipt.update(zip_increment_vs_021=package.stat().st_size-read_json(ROOT/'docs/update_022/baseline-BUILD_VERIFICATION.json')['zip_bytes'],native_starting_sheep=5,normal_client_audio_launch_required=True,audible_playback_qualified=False,freeze_cause_qualified=False)
    if config['version']=='0.2.3':
        audio=read_json(ROOT/'docs/update_023/AUDIO_AUDIT.json')
        receipt.update(audio_full_decode_verified=audio['all_clips_decoded'],dialogue_sample_rate=24000,dialogue_vorbis_compression_level=.35,dialogue_bytes=audio['dialogue_bytes'],decoded_dialogue_float32_bank_bytes=audio['decoded_float32_bank_bytes'],zip_increment_vs_022=package.stat().st_size-read_json(ROOT/'docs/update_023/baseline-build.json')['zip_bytes'],native_starting_sheep=5,audible_playback_qualified=False,freeze_cause_qualified=False,media_budget_exception='0.2.3 only: owner-approved higher-quality audio, unchanged art; 400000000-byte media and 600000000-byte ZIP caps')
    if config['version'] in ('0.2.4','0.2.5'):
        base=read_json(ROOT/'docs/update_024/baseline-build.json')
        receipt.update(dialogue_sample_rate=24000,dialogue_vorbis_compression_level=.35,dialogue_bytes=base['dialogue_bytes'],decoded_dialogue_float32_bank_bytes=base['decoded_dialogue_float32_bank_bytes'],native_starting_sheep=5,diagnostic_only=True,crash_cause_qualified=False,hwarang_model_fix_deferred=True,zip_increment_vs_023=package.stat().st_size-base['zip_bytes'],media_budget_exception='Exact same 354433993-byte higher-quality media as 0.2.3; no media change permitted in diagnostic release')
    if config['version']=='0.2.5':receipt.update(voice_controller_enabled=False,all_voice_files_retained=True,previous_release_retained_in_place=True,crash_cause_qualified=False)
    write_json(out/'verification.json',receipt)
    release.mkdir(exist_ok=True)
    staged=release/'.verified-new.zip'
    if staged.exists():raise ValueError('Previous staged ZIP protected')
    shutil.copyfile(package,staged)
    if digest(staged)!=receipt['zip_sha256']:raise ValueError('Player ZIP copy differs')
    os.replace(staged,release/package.name)
    if previous and previous['zip_name']!=package.name and not config.get('preserve_previous_release',False):
        old=release/previous['zip_name']
        if digest(old)!=previous['zip_sha256']:raise ValueError('Old local ZIP changed during build')
        rollback=ROOT/config.get('rollback_folder','archives/art013-baseline')/previous['zip_sha256'][:12]/old.name
        if rollback.exists():raise ValueError('Previous player ZIP rollback already exists; preserve it')
        rollback.parent.mkdir(parents=True,exist_ok=True)
        shutil.move(str(old),str(rollback))
    write_json(ROOT/'docs/BUILD_VERIFICATION.json',receipt)
    write_json(ROOT/'docs/CODEX_GRAPH.json',codex_report)
    print(json.dumps(receipt,indent=2),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'output/current');p.add_argument('--prepare-only',action='store_true');p.add_argument('--replace-current',action='store_true');a=p.parse_args();build(a.output.resolve(),a.prepare_only,a.replace_current)
