"""Verify required whole-file inputs. No downloads or source-pack extraction."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def check(p,row):
    if not p.is_file() or p.stat().st_size!=row['bytes']:raise ValueError('Missing, changed or LFS-pointer input: '+str(p))
    with p.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
    if actual!=row['sha256']:raise ValueError('Changed input; review and update its manifest: '+str(p))
def verify():
    for relative,row in read(ROOT/'inputs/native-manifest.json').items():check(ROOT/'inputs/native'/relative,row)
    path=ROOT/'source/master-index.json'
    if not path.exists():raise ValueError('Editable master inventory is incomplete')
    overrides=ROOT/'source/portable-masters.json';changed=read(overrides).get('files',{}) if overrides.exists() else {}
    master=read(path)['files']
    for row in master:check(ROOT/'authoring'/row['path'],changed.get(row['path'],row))
    print('INPUTS_VERIFIED native='+str(len(read(ROOT/'inputs/native-manifest.json')))+' editable='+str(len(master)))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True);sub.add_parser('verify')
    record=sub.add_parser('record',help='Explicitly accept an intentional edited master or newly cooked native file')
    record.add_argument('kind',choices=['master','native']);record.add_argument('path');record.add_argument('--reason',required=True);record.add_argument('--toc',choices=['data','info','locale'],default='data')
    a=p.parse_args()
    if a.action=='verify':verify()
    else:
        base=(ROOT/('authoring' if a.kind=='master' else 'inputs/native')).resolve();target=(base/a.path).resolve()
        if not target.is_relative_to(base) or not target.is_file():raise ValueError('Expected a file inside '+str(base))
        relative=target.relative_to(base).as_posix()
        with target.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
        row={'bytes':target.stat().st_size,'sha256':digest,'change':a.reason}
        if a.kind=='native':
            path=ROOT/'inputs/native-manifest.json';manifest=read(path);previous=manifest.get(relative,{});manifest[relative]={**previous,**row,'toc':a.toc}
        else:
            path=ROOT/'source/portable-masters.json';manifest=read(path) if path.exists() else {'schema':'garrison.portable-masters/v1','files':{}}
            indexed={x['path'] for x in read(ROOT/'source/master-index.json')['files']}
            if relative not in indexed:raise ValueError('Register the new master and its provenance in source/master-index.json first')
            manifest['files'][relative]=row
        path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');print('RECORDED',a.kind,relative)
