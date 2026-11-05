"""Resume the receipt-stage 0.2.0 failure, rechecking source and every package member.
No recook, source edits, verification bypass or deletion of failure evidence.
"""
from pathlib import Path
import hashlib,json,os,tempfile
from runtime import ROOT,read_json,rgd,import_table
from inputs import verify
from voice020_release import verify_source,retained_codex
from build import finalize,digest

def main():
 config=read_json(ROOT/'project.json');assert config['version']=='0.2.0' and config['owner']=='748d61b9-4d3e-4cf3-a506-a9ac1f992d1d' and not config.get('build_hold')
 out=ROOT/'output/current';assert out.is_dir() and not out.is_symlink() and not out.is_junction()
 verify();verify_source()
 from research016_ui import verify as verify_tooltips
 verify_tooltips()
 recipe=read_json(out/'build-recipe.json');expected=read_json(out/'expected-members.json');native=read_json(ROOT/'inputs/native-manifest.json')
 assert all(recipe[k]==config[k] for k in ('schema','owner','race','dispatcher','shared_entities'))
 tables={}
 for p in sorted((ROOT/'source/tables').rglob('*.rgd.json')):
  m=p.relative_to(ROOT/'source/tables').as_posix()[:-5]
  exclusion=config.get('excluded_tables',{}).get(m)
  if exclusion:assert digest(p)==exclusion['sha256'];continue
  tables[m]=rgd.read(import_table(read_json(p)))
 _,codex_report=retained_codex(tables,config)
 assert codex_report==read_json(out/'codex-report.json')
 rows=recipe['attributes']+recipe['members'];assert len(rows)==len(expected) and len({x['member'] for x in rows})==len(rows)
 for row in rows:
  member=row['member'];p=Path(row['file']);assert p.resolve().is_relative_to(ROOT.resolve()) and p.is_file() and not p.is_symlink() and not p.is_junction()
  assert digest(p)==row['sha256']==expected[member]['sha256'] and p.stat().st_size==expected[member]['bytes']
  if member in tables:
   assert p==out/'prepared'/member and p.read_bytes()==rgd.write(tables[member]) and expected[member]['toc']=='attrib'
  elif member in native:
   assert p==ROOT/'inputs/native'/member and row['sha256']==native[member]['sha256']
  elif member.startswith('scar/'):
   assert p==ROOT/'source/scar'/member[5:]
  elif member=='en/en.ucs':
   locale=read_json(ROOT/'source/locale/en.json');text=''.join(str(k)+'\t'+str(v)+'\r\n' for k,v in sorted(locale.items(),key=lambda row:int(row[0])))
   assert p.read_bytes()==text.encode('utf-16')
  else:assert p==ROOT/'source/resources'/member
 assert set(tables)=={x['member'] for x in recipe['attributes']}
 if (out/'verification.json').exists():
  checkpoint=read_json(out/'verification.json');assert checkpoint['version']=='0.2.0' and checkpoint['owner']==config['owner'] and checkpoint['all_member_readback_sha256'] and checkpoint['zip_crc']
 previous=read_json(ROOT/'docs/BUILD_VERIFICATION.json');assert previous['version']=='0.1.6'
 old=ROOT/'release'/previous['zip_name'];assert list((ROOT/'release').iterdir())==[old] and old.stat().st_size==107644580 and digest(old)=='e48869987e4c7159290a911d263e06288b6ddf8da7cd3c34e236eaadf0a3a788'
 assembly=Path(tempfile.gettempdir())/'garrison-independent-builds'/config['owner']/config['build_stage'];assert assembly.resolve().is_relative_to(Path(r'F:\aoe_4_temp\Temp_aoe4\k20').resolve()) and not assembly.is_symlink() and not assembly.is_junction()
 source_fingerprint=hashlib.sha256(json.dumps(expected,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 print('RESUME_RECHECKED',len(tables),'typed tables',len(rows),'source/native members; all original failed-run evidence retained',flush=True)
 finalize(out,config,expected,native,tables,source_fingerprint,previous,assembly,codex_report,reuse_package=True)
if __name__=='__main__':main()
