"""Verify delivery/rollback and retain compact budget and rebuild receipts before cleanup."""
import sys,zipfile,json,hashlib,collections,concurrent.futures
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from common import *
from garrison_shared import rrtex_decoder as rr
receipt=read_json(R/'docs/BUILD_VERIFICATION.json');assert receipt['version']=='0.1.4'
package=R/'release'/receipt['zip_name'];assert sha(package.read_bytes())==receipt['zip_sha256']
with zipfile.ZipFile(package) as z:
 assert z.testzip() is None
 manifest=next(n for n in z.namelist() if Path(n).name=='garrison.json');m=json.loads(z.read(manifest));assert m['members'][0]['role']=='civilization';prefix=manifest[:-len('garrison.json')]
 with z.open(prefix+m['members'][0]['path']) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==receipt['archive_sha256']
old=read_json(D/'BASELINE_013.json');rollback=R/'archives/art013-baseline'/old['zip_sha256'][:12]/old['zip_name'];assert sha(rollback.read_bytes())==old['zip_sha256']
master=read_json(R/'source/master-index.json');known={r['path'] for r in master['files']}
for p in sorted((R/'authoring/art014').rglob('*')):
 if p.is_file() and p.suffix!='.blend1':
  rel=p.relative_to(R/'authoring').as_posix()
  if rel not in known:master['files'].append({'path':rel,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes()),'provenance':'Korea 014 editable Hwacha native donor geometry and rig'})
write_json(R/'source/master-index.json',master);receipt['editable_master_index_sha256']=sha((R/'source/master-index.json').read_bytes());write_json(R/'docs/BUILD_VERIFICATION.json',receipt)
native=read_json(R/'inputs/native-manifest.json');members=[m for m in native if m.startswith(('art/kr013/','art/kr014/'))]
def texture(m):
 p=R/'inputs/native'/m;d=rr.decode_rrtex(p,validate_stream=True)
 return {'member':m,'sha256':native[m]['sha256'],'file_bytes':p.stat().st_size,'width':d['width'],'height':d['height'],'mips':d['mip_count'],'format':d['projection']['format'],'native_mip_block_bytes':sum(x['size'] for x in d['mips']),'rgba8_mip_bytes':sum(x['width']*x['height']*4*max(1,d['depth']) for x in d['mips'])}
textures=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for row in pool.map(texture,[m for m in members if m.endswith('.rrtex')]):textures.append(row)
unique={row['sha256']:row for row in textures};budget={'version':'0.1.4','zip_bytes':receipt['zip_bytes'],'zip_sha256':receipt['zip_sha256'],'archive_bytes':receipt['archive_bytes'],'archive_sha256':receipt['archive_sha256'],'zip_increase_vs_013':receipt['zip_bytes']-old['zip_bytes'],'zip_increase_vs_accepted_011':receipt['zip_bytes']-next((R/'archives/tested_0.1.1').glob('*.zip')).stat().st_size,'packaged_additional_art_input_bytes':sum(native[m]['bytes'] for m in members),'texture_mip_block_bytes_logical_paths':sum(t['native_mip_block_bytes'] for t in textures),'texture_rgba8_mip_bytes_logical_paths':sum(t['rgba8_mip_bytes'] for t in textures),'texture_unique_content_mip_block_bytes':sum(t['native_mip_block_bytes'] for t in unique.values()),'texture_unique_content_rgba8_mip_bytes':sum(t['rgba8_mip_bytes'] for t in unique.values()),'texture_formats':dict(collections.Counter(t['format'] for t in textures)),'texture_count':len(textures),'textures_with_mips':sum(t['mips']>1 for t in textures),'zip_budget_600000000_passed':receipt['zip_bytes']<600000000,'additional_art_budget_300000000_passed':sum(native[m]['bytes'] for m in members)<=300000000,'runtime_texture_residency_frame_time_lod_switching':'not measured; encoded mip/geometry byte counts are not live VRAM or performance proof'}
assert budget['zip_budget_600000000_passed'] and budget['additional_art_budget_300000000_passed']
write_json(D/'ASSET_BUDGET.json',budget);write_json(D/'TEXTURE_BUDGET.json',{'textures':textures})
write_json(D/'COMPLETION.json',{'version':'0.1.4','owner':receipt['owner'],'source_tests':29,'real_before_source_tables_checked':494,'exact_official_unit_skeleton_payloads':72,'qualified_static_geometry_retained':36,'shader_bound_RGB_masks_checked':108,'fresh_native_unit_static_cook_models':108,'fresh_hwacha_native_cook':True,'archive_member_byte_readback_count':receipt['members'],'archive_and_zip_integrity_passed':True,'rollback_013_verified':True,'zip_name':receipt['zip_name'],'zip_bytes':receipt['zip_bytes'],'zip_sha256':receipt['zip_sha256'],'full_fresh_model_projection':'not completed: installed 0.1.9 decoder stalls at optional animation_discovery after texture/geometry decode. Exact native skeletons and retained qualified geometry checked separately; timeout evidence retained.','native_game_appearance_animations_lifecycle':'pending owner test','ai_save_load_multiplayer_performance':'not qualified','github_push_tag_publication_installation':'not performed'})
print('FINAL_014_DELIVERY_VERIFIED',json.dumps({k:budget[k] for k in ['zip_bytes','zip_increase_vs_013','packaged_additional_art_input_bytes','texture_mip_block_bytes_logical_paths','texture_rgba8_mip_bytes_logical_paths']}),flush=True)
