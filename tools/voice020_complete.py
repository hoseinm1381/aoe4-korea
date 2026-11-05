"""Create compact, factual Korea 0.2.0 completion and budget receipts."""
from pathlib import Path
import datetime,gzip,hashlib,json,math,shutil,zipfile
R=Path(__file__).resolve().parents[1];D=R/'docs/voices020';W=Path(r'F:\aoe_4_temp\ai_voice\tts-workstation')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def compact(source,target):
 raw=Path(source).read_bytes();Path(target).write_bytes(gzip.compress(raw,mtime=0))
def main():
 b=read(R/'docs/BUILD_VERIFICATION.json');assert b['version']=='0.2.0' and b['all_member_readback_sha256'] and b['native_crc_sha1'] and b['zip_crc'];package=R/'release'/b['zip_name'];assert sha(package)==b['zip_sha256'] and package.stat().st_size<600000000
 rollback=R/'archives/voices020-baseline/e48869987e4c/Koreans-Garrison-0.1.6.zip';assert rollback.stat().st_size==107644580 and sha(rollback)=='e48869987e4c7159290a911d263e06288b6ddf8da7cd3c34e236eaadf0a3a788'
 with zipfile.ZipFile(package) as z:assert z.testzip() is None
 a=read(D/'AUDIO_AUDIT.json');c=read(D/'BANK_COVERAGE.json');t=read(D/'FOCUSED_TESTS.json');assert a['all_pass'] and t['successful'];language=read(D/'LANGUAGE_SCREENING.json');assert language['flagged_groups']==0
 s=read(D/'SEMANTIC_PRESERVATION.json');assert s['all_typed_non_speech_values_order_and_types_preserved'];assert not read(D/'ATTACHMENT_CLOSURE.json')['unmuted_payloads']
 assembly=Path(b['assembly_path']);current=read(assembly/'report.json')['members'];baseline=json.loads(gzip.decompress((D/'baseline-members.json.gz').read_bytes()))['members'];media=[m for m in baseline if m.startswith(('art/','audio/'))]
 assert all(current[m]==baseline[m] for m in media),'Original media changed';media_bytes=sum(x['bytes'] for m,x in current.items() if m.startswith(('art/','audio/')));assert media_bytes<=300000000
 out=R/'output/current';saved=D/'package';saved.mkdir(exist_ok=True)
 for name in ('build-recipe.json','expected-members.json','verification.json','codex-report.json'):compact(out/name,saved/(name+'.gz'))
 for name in ('validate.log','assembly.log'):shutil.copyfile(out/name,saved/name)
 compact(assembly/'report.json',saved/'assembly-report.json.gz')
 storage=read(D/'STORAGE_ALLOCATION.json');unit=storage['allocation_unit_bytes'];native=read(R/'inputs/native-manifest.json');voice_members=[m for m in native if m.startswith(('audio/korea_020/','audio/korea_020_efforts/'))]
 allocated=sum(math.ceil(native[m]['bytes']/unit)*unit for m in voice_members);masters=list((R/'authoring/voices020/generated').glob('*.wav'));master_allocated=sum(math.ceil(p.stat().st_size/unit)*unit for p in masters)
 old=read(D/'baseline-build.json');budget={'version':'0.2.0','archive_bytes':b['archive_bytes'],'zip_bytes':b['zip_bytes'],'baseline_016_zip_bytes':old['zip_bytes'],'zip_increment_vs_016_bytes':b['zip_bytes']-old['zip_bytes'],'compressed_increment_scope':'Exact ZIP growth for voices, bank/controller and native speaker isolation together; not a fictitious per-OGG ZIP share.','archive_increment_vs_016_bytes':b['archive_bytes']-old['archive_bytes'],'packaged_media_bytes':media_bytes,'media_cap_bytes':300000000,'zip_cap_bytes':600000000,'new_audio_encoded_bytes':a['new_audio_encoded_bytes'],'dialogue_encoded_bytes':a['dialogue_encoded_bytes'],'effort_encoded_bytes':a['effort_encoded_bytes'],'decoded_dialogue_pcm16_bytes':a['decoded_dialogue_pcm16_bytes'],'decoded_dialogue_float32_bytes':a['decoded_dialogue_float32_bytes'],'decoded_effort_pcm16_bytes':a['decoded_effort_pcm16_bytes'],'decoded_effort_float32_bytes':a['decoded_effort_float32_bytes'],'decoded_audio_note':a['decoded_memory_note'],'lossless_dialogue_master_bytes':a['lossless_dialogue_master_bytes'],'filesystem':storage['filesystem'],'allocation_unit_bytes':unit,'cluster_rounded_native_audio_allocation_estimate':allocated,'cluster_rounded_dialogue_master_allocation_estimate':master_allocated,'allocation_note':storage['note'],'preserved_original_media_members':len(media),'original_texture_budget_receipt':read(R/'docs/update_016_build/ASSET_BUDGET.json'),'native_frame_time_vram_audio_residency':'not measured; package bytes are not runtime acceptance'}
 originals=read(R/'authoring/voices020/ORIGINAL_ENCODINGS.json')['files'];budget.update(protected_original_encoding_files=len(originals),protected_original_encoding_bytes=sum(x['bytes'] for x in originals.values()),protected_original_encoding_allocation_estimate=sum(math.ceil(x['bytes']/unit)*unit for x in originals.values()))
 write(D/'ASSET_BUDGET.json',budget);write(R/'docs/SIZE_REPORT.json',budget)
 samples=read(D/'TRANSCRIPTION_SAMPLES.json');encoding=read(D/'ENCODING_FINALIZATION.json');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
 result={'utc':now,'status':'local 0.2.0 candidate built and verified; native/historical acceptance pending','zip_path':str(package),'zip_bytes':b['zip_bytes'],'zip_sha256':b['zip_sha256'],'archive_bytes':b['archive_bytes'],'archive_sha256':b['archive_sha256'],'owner':'748d61b9-4d3e-4cf3-a506-a9ac1f992d1d','archive_namespace':'748d61b94d3e4cf3a506a9ac1f992d1d','race_bundle':'korea','voice_profiles':c['profiles'],'role_age_banks':c['age_banks'],'squad_blueprints':len(c['units']),'dialogue_clips':c['dialogue_clips'],'stock_nonverbal_efforts':c['effort_files'],'semantic_tables':s['tables'],'focused_tests':t['tests'],'audio_full_decode_quality_duplicate_checks':True,'grouped_language_screened_clips':language['clips_screened'],'language_flags':language['flagged_groups'],'representative_transcription':samples,'codec_headroom_fixed_clips':encoding['fixed_count'],'exact_016_rollback':{'path':str(rollback),'bytes':107644580,'sha256':sha(rollback)},'native_crc_full_readback_zip_crc':'pass','original_art_models_animation_and_gameplay_values':'Preserved by original native-member hashes and independent typed voice-only reconstruction. Runtime behavior is a separate gate.','excluded_nonhuman_proxies':c['excluded_proxies'],'context_limits':c['context_limits'],'historical_pronunciation':'Researched original compositions and explicit model/phonetic approximations; no verified Old/Middle Korean pronunciation claim.','pending':['Garrison client import and fresh-match listening','Historical/native-speaker word and pronunciation review; modern ASR disagreements remain','Native age/gender/selection/context/capture/suppression and nonverbal timing','Save/load, AI, multiplayer, repeated matches and performance'],'not_performed':['GitHub push/tag/publication','Game installation or interruption','Changes to other civilizations or trusted AGENTS.md','Broad E:/F: cleanup'],'automation':'Stop the one-time Codex automation after final review; no recurrence','source_and_master_inputs':'Retained; weights and original encodings/masters are protected, not disposable temp'}
 write(D/'COMPLETION.json',result);write(R/'docs/SOURCE_TESTS.json',{'version':'0.2.0','current_scope':t,'preservation':s,'audio_checks':'docs/voices020/AUDIO_AUDIT.json','historical_suite':'Baseline 65 tests had 9 failures +1 error before speech promotion; those frozen/retired-release checks remain unchanged in tests and baseline-tests.log.','native_acceptance':'pending'})
 text=f'''# Korea 0.2.0 local voice candidate - 2026-11-02

Built `{package}`: **{b['zip_bytes']:,} bytes**.
ZIP SHA-256: `{b['zip_sha256']}`.
Packaged SGA SHA-256: `{b['archive_sha256']}`.

The single ordinary Garrison ZIP includes {c['dialogue_clips']:,} original dialogue
recordings, {c['profiles']} fictional role/gender profiles, {c['age_banks']} age banks,
{len(c['units'])} mapped squad blueprints and {c['effort_files']} unchanged stock nonverbal efforts.
Each context has six alternative lines; selection has three independent takes,
movement/combat/work two, and neutral/alert replies one. Six phrases cycle before
the next take. Some early banks are retained authoring extras for later units.

All {s['tables']} staged native tables passed independent typed preservation and
current native schema/reference checks. Main paired SBPS/EBPS and active attachment
speakers are suppressed; the closure has no remaining original speech payloads.
Current art/media, colour/cavalry bindings, Gapsa shield and research values/scripts
are preserved against exact 0.1.6. The three default invisible controller proxies
are excluded from human speech; unsupported HRE/XP3 modes are not claimed.

{t['tests']} current-scope Lua/start/barrage/research regressions passed. Full audio
decode, finite/rate/channel/duration/silence/clipping and PCM duplicate checks pass.
{encoding['fixed_count']} codec-overrun clips were re-encoded with safe headroom from
untouched masters. Grouped modern language detection included every take with zero
non-Korean top-language groups. Representative modern ASR has disagreements on
archaic forms; these remain review evidence, not pronunciation acceptance.

Fresh native assembly, normalized owner namespace, full member readback SHA-256,
archive CRC/SHA1, untouched-media comparison and final ZIP CRC/packaged-SGA hash
passed. Original 0.1.6 rollback is preserved at `{rollback}` with its exact
107,644,580 bytes and SHA-256 e48869987e4c7159290a911d263e06288b6ddf8da7cd3c34e236eaadf0a3a788.

Packaged media: **{media_bytes:,} bytes**, below 300,000,000. ZIP growth versus
0.1.6: **{budget['zip_increment_vs_016_bytes']:,} bytes** for the complete voice update.
New encoded audio: {a['new_audio_encoded_bytes']:,} bytes. See ASSET_BUDGET.json for
archive/ZIP deltas, potential decoded audio, retained texture measurements and
cluster-rounded exFAT storage estimates. No native performance claim is made.

Historical diction follows the civ's Three Kingdoms-to-Joseon design. Earlier
forms are uncertain retrojections; later forms are informed original compositions.
Modern TTS has not recovered validated historical phonology. Meaning, pronunciation
directions, respellings, confidence and primary source locators are retained in
authoring/voices020. [Listen locally](voices020/VOICE_REVIEW.html).

Repair and unqualified religious/ability targets use neutral acknowledgements;
repair-specific recordings are retained for a future qualified target dispatcher.
Import, audible native behavior, historical/native-speaker review, save/load, AI,
multiplayer and measured performance remain pending. Follow START-HERE.md.

The free pinned downloads are complete. Focused Qwen inference is qualified on
the RTX 5050 Laptop 8 GB using one model and bounded batches. The entire optional
multi-engine Suite GUI installer is not qualified. All workstation tools/weights,
lossless masters, scripts, seeds, receipts and required native inputs remain on F:.
No other civ, game installation, GitHub push/tag/publication or broad drive cleanup.
The original historical test files and trusted AGENTS.md remain unchanged.

Key receipts are under docs/voices020: COMPLETION.json, BANK_COVERAGE.json,
SEMANTIC_PRESERVATION.json, ATTACHMENT_CLOSURE.json, AUDIO_AUDIT.json,
LANGUAGE_SCREENING.json, TRANSCRIPTION_SAMPLES.json and package/.
'''
 (R/'docs/UPDATE_020_VOICES.md').write_text(text,encoding='utf-8')
 header='# Korea 0.2.0 local voice candidate - 2026-11-02\n\nRead [the voice/build handoff](docs/UPDATE_020_VOICES.md) and current package receipt. The local ZIP and exact 0.1.6 rollback are verified. Historical/native listening and gameplay acceptance remain separate pending gates; no new publication or installation. Older release notes below are history.\n\n---\n\n'
 p=R/'RELEASES.md';oldtext=p.read_text(encoding='utf-8');p.write_text(header+oldtext,encoding='utf-8')
 p=R/'docs/DEVELOPMENT.md';oldtext=p.read_text(encoding='utf-8');head='# Korea 0.2.0 voice workflow\n\nRead UPDATE_020_VOICES.md and voices020/RUN_CHECKPOINT.json. Build from current typed source and indexed native audio with tools/build.py. Regeneration uses the protected external F: workstation and tools/voice020_generate.py, followed by codec finalization, audit and bank mapping. Ordinary rebuilds need no models/network/other-civ checkout. Historical milestones below retain their original scope.\n\n---\n\n';p.write_text(head+oldtext,encoding='utf-8')
 p=W.parent/'README_VOICE_WORKSTATION.txt';oldtext=p.read_text(encoding='utf-8-sig');p.write_text(oldtext.replace('Korean recording is in progress.','Korean recording and the local 0.2.0 package are complete.').replace('Korean recording is in progress','Korean recording and the local 0.2.0 package are complete'),encoding='utf-8')
 promotion=read(D/'PROMOTION.json');promotion.update(build_completed=True,zip_sha256=b['zip_sha256'],native_game_acceptance=False);write(D/'PROMOTION.json',promotion)
 checkpoint=read(D/'RUN_CHECKPOINT.json');checkpoint.update(utc=now,active_release='0.2.0 local verified candidate',remaining_work=result['pending'],completion_receipt='docs/voices020/COMPLETION.json',next_steps=['Manual native/historical listening using START-HERE.md and VOICE_REVIEW.html.','No further regeneration/build/push/install/cleanup is implied by the completed one-time job.']);write(D/'RUN_CHECKPOINT.json',checkpoint)
 print(json.dumps({k:result[k] for k in ('status','zip_path','zip_bytes','zip_sha256','voice_profiles','role_age_banks','dialogue_clips','focused_tests')},indent=2),flush=True)
if __name__=='__main__':main()
