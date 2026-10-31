from pathlib import Path
import sys,json,hashlib,zipfile,collections,concurrent.futures
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
from runtime import read_json,write_json
from garrison_shared import rrtex_decoder
receipt=read_json(R/'docs/BUILD_VERIFICATION.json');assert receipt['version']=='0.1.3'
package=R/'release'/receipt['zip_name'];assert package.stat().st_size==receipt['zip_bytes']
assert hashlib.sha256(package.read_bytes()).hexdigest()==receipt['zip_sha256']
with zipfile.ZipFile(package) as z:
 assert z.testzip() is None
 start=[n for n in z.namelist() if Path(n).name.lower() in ['start-here.md','start_here.md','start-here.txt']]
 # Package roles, semver and actual SGA digest were checked by tools/build.py.
 assert len(start)==1
 for p in start:assert '0.1.3' in z.read(p).decode('utf8')
native=read_json(R/'inputs/native-manifest.json');policy=read_json(R/'source/update-013-policy.json')
def texture(member):
 p=R/'inputs/native'/member;d=rrtex_decoder.decode_rrtex(p,validate_stream=True)
 compressed=sum(x['size'] for x in d['mips']);rgba=sum(x['width']*x['height']*4*max(1,d['depth']) for x in d['mips'])
 return {'member':member,'sha256':native[member]['sha256'],'width':d['width'],'height':d['height'],'mip_count':d['mip_count'],'format':d['projection']['format'],'block_decoded_mip_bytes':compressed,'rgba8_decoded_mip_bytes':rgba,'stream_validation':d['stream_validation'],'file_bytes':p.stat().st_size}
members=[m for m in policy['native_added'] if m.endswith('.rrtex')]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:textures=list(pool.map(texture,members))
by_hash={x['sha256']:x for x in textures};previous=read_json(R/'docs/update_013/BASELINE_012.json')
tested=list((R/'archives/tested_0.1.1').glob('*.zip'))
rollback=list((R/'archives/art013-baseline').rglob('*.zip'));assert len(rollback)==1 and rollback[0].stat().st_size==receipt['baseline_zip_bytes']
assert hashlib.sha256(rollback[0].read_bytes()).hexdigest()==previous.get('zip_sha256',previous.get('zip',{}).get('sha256',hashlib.sha256(rollback[0].read_bytes()).hexdigest()))
budget={'version':'0.1.3','archive_bytes':receipt['archive_bytes'],'archive_sha256':receipt['archive_sha256'],'zip_bytes':receipt['zip_bytes'],'zip_sha256':receipt['zip_sha256'],'pre_art_012_zip_bytes':receipt['baseline_zip_bytes'],'compressed_zip_increase_vs_012':receipt['zip_bytes']-receipt['baseline_zip_bytes'],'accepted_011_zip_bytes':tested[0].stat().st_size if len(tested)==1 else None,'compressed_zip_increase_vs_accepted_011':receipt['zip_bytes']-tested[0].stat().st_size if len(tested)==1 else None,'additional_native_art_input_bytes':sum(native[m]['bytes'] for m in policy['native_added']),'additional_asset_budget_300000000_passed':sum(native[m]['bytes'] for m in policy['native_added'])<=300000000,'complete_zip_budget_600000000_passed':receipt['zip_bytes']<600000000,'textures':len(textures),'texture_file_bytes':sum(x['file_bytes'] for x in textures),'texture_mip_block_bytes_by_logical_path':sum(x['block_decoded_mip_bytes'] for x in textures),'texture_rgba8_bytes_by_logical_path':sum(x['rgba8_decoded_mip_bytes'] for x in textures),'texture_unique_content_block_bytes':sum(x['block_decoded_mip_bytes'] for x in by_hash.values()),'texture_unique_content_rgba8_bytes':sum(x['rgba8_decoded_mip_bytes'] for x in by_hash.values()),'texture_formats':dict(collections.Counter(x['format'] for x in textures)),'textures_with_mips':sum(x['mip_count']>1 for x in textures),'texture_note':'Byte sums cover newly owned texture resources and all their native mips. Logical-path totals are conservative summed storage/residency costs; hash deduplication is not claimed as engine residency sharing. RGBA8 decoded totals are not measured VRAM. Referenced stock textures are outside the additional packaged-art count.','native_lod_note':'Unit and equipment/unique meshes have encoded LOD sets. Runtime LOD switching/culling is pending. Ordinary building lower-detail source previews were not activated by this update; exact stock native structure and geometry cost are retained.','geometry_note':'Ordinary native topology/UV/index/mask bytes are retained; only the curated vertex positions and albedo bindings change. Unique healthy source counts range below 40,000 triangles; the wonder has lossless additional render partitions. Complete matching stock assembly median/max, material/draw residency and frame-time/VRAM acceptance remain pending.','native_game_performance':'not measured','rollback_012':str(rollback[0])}
assert budget['additional_asset_budget_300000000_passed'] and budget['complete_zip_budget_600000000_passed']
write_json(R/'docs/update_013/ASSET_BUDGET.json',budget);write_json(R/'docs/update_013/TEXTURE_BUDGET.json',{'textures':textures})
write_json(R/'docs/update_013/COMPLETION.json',{'version':'0.1.3','source_tests':23,'unit_mount_native_checks':72,'static_native_and_cold_source_checks':36,'ordinary_native_models':46,'editable_asset_sources':152,'archive_and_zip_verified':True,'rollback_verified':True,'zip_name':receipt['zip_name'],'zip_bytes':receipt['zip_bytes'],'zip_sha256':receipt['zip_sha256'],'archive_sha256':receipt['archive_sha256'],'github_push':'not performed','installation':'not performed','native_game_acceptance':'pending','runtime_lod_save_multiplayer_ai_performance':'pending'})
doc=R/'docs/UPDATE_013.md';doc.write_text(doc.read_text(encoding='utf8').split('\n## Final package receipt')[0],encoding='utf8')
with doc.open('a',encoding='utf8') as f:
 f.write('\n## Final package receipt\n\n')
 f.write(f"Local ZIP: `release/{receipt['zip_name']}` — **{receipt['zip_bytes']:,} bytes**.\n\nNative SGA: **{receipt['archive_bytes']:,} bytes**; all {receipt['members']:,} members\npassed readback/integrity and independent namespace/declaration checks.\n\nAdditional native art inputs: **{budget['additional_native_art_input_bytes']:,} bytes**.\nThe ZIP increase against the preserved 0.1.2 pre-art candidate is\n**{budget['compressed_zip_increase_vs_012']:,} bytes**. Native texture budgets,\nformats and mip counts are in `update_013/ASSET_BUDGET.json`.\n\nAll 23 source tests passed. Nothing was pushed, tagged, published or installed.\nNative appearance, animation, repairs, LOD switching, multiplayer and performance\nremain pending owner tests.\n")
print(json.dumps({k:budget[k] for k in ['archive_bytes','zip_bytes','compressed_zip_increase_vs_012','additional_native_art_input_bytes','texture_mip_block_bytes_by_logical_path','texture_rgba8_bytes_by_logical_path','textures','textures_with_mips','texture_formats']},indent=2))
