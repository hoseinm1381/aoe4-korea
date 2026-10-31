"""Verify and decode a private native model pilot through an isolated archive index."""
import argparse,json,sqlite3,subprocess,hashlib,os
from pathlib import Path
R=Path(__file__).resolve().parents[2]
ORIGINAL_INDEX=Path.home()/'AppData/Local/Garrison/Kit/game-assets.sqlite3'
ORIGINAL_CONFIG=Path.home()/'AppData/Local/Garrison/Kit/game-assets.local.json'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def create_index(archive: Path, members: list[dict], provider_id: str):
    source = sqlite3.connect("file:" + ORIGINAL_INDEX.as_posix() + "?mode=ro", uri=True)
    target = sqlite3.connect(INDEX)
    try:
        for table in ("metadata", "archives", "assets", "resolved_assets", "folders", "object_types"):
            schema = source.execute("select sql from sqlite_master where type=? and name=?",
                                    ("table", table)).fetchone()[0]
            target.execute(schema)
        for key, value in source.execute("select key,value from metadata"):
            if key == "archive_count":
                value = "1"
            elif key in ("asset_count", "resolved_asset_count"):
                value = str(len(members))
            target.execute("insert into metadata(key,value) values(?,?)", (key, value))
        file = archive.stat()
        target.execute("insert into archives values(?,?,?,?,?,?,?,?,?,?,?)",
                       (1, "cardinal", archive.name, str(archive), file.st_size, file.st_mtime_ns,
                        provider_id, "11", "0", 1, len(members)))
        for index, item in enumerate(members, 1):
            path = item["path"]
            if not path.startswith("art/"):
                continue
            folder, name = path.rsplit("/", 1)
            extension = Path(name).suffix.lower()
            template = source.execute("select asset_kind,curated_category,civilization,object_class,object_type "
                                      "from resolved_assets where extension=? limit 1", (extension,)).fetchone()
            if template is None:
                template = ("resource", "Other", "Shared / Neutral", "Resource", "Resource")
            kind, category, civilization, object_class, object_type = template
            raw_name = item["toc"] + ":" + path.replace("/", "\\")
            target.execute("insert into assets(id,archive_id,logical_path,folder,name,extension,asset_kind,"
                           "curated_category,civilization,object_class,object_type,size,raw_name,verification,"
                           "storage,encryption,preview_status,preview_path) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (index, 1, path, folder, name, extension, kind, category, civilization,
                            object_class, object_type, item["size"], raw_name, item["verification"],
                            item["storage"], item["encryption"], "not_generated", None))
            target.execute("insert into resolved_assets(id,logical_path,folder,name,extension,asset_kind,"
                           "curated_category,civilization,object_class,object_type,size,raw_name,preview_status,"
                           "preview_path,product,archive,archive_path,provider_archive_id,archive_version,"
                           "product_version,verified,provider_count) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                           (index, path, folder, name, extension, kind, category, civilization,
                            object_class, object_type, item["size"], raw_name, "not_generated", None,
                            "cardinal", archive.name, str(archive), provider_id, "11", "0", 1, 1))
        target.commit()
    finally:
        source.close()
        target.close()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--archive',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--logical-path',default='art/kr013/vma1/model.rgm');a=p.parse_args()
 EXT=Path(os.environ.get('GARRISON_EXTENSION',Path.home()/'AppData/Roaming/Blender Foundation/Blender/5.2/extensions/raw_githubusercontent_com/garrison'))
 CORE=EXT/'bin/core/garrison-core.exe';ARCH=EXT/'bin/sga-archiver.exe'
 assert not a.output.exists(),'Preserve previous native readback';a.output.mkdir(parents=True)
 INDEX=a.output/'index.sqlite3';CONFIG=a.output/'config.json'
 listing=json.loads(subprocess.check_output([str(ARCH),'list',str(a.archive),'--verify'],text=True))
 assert listing['archive']['verification']['verified']
 names={x['path'] for x in listing['members']};stem=a.logical_path[:-4]
 assert all(stem+s in names for s in ['.rgm','.rgo','.rrgeom','.rrmaterial']),'Fresh archive lacks native model resources'
 create_index(a.archive,listing['members'],listing['archive']['name'])
 config=json.loads(ORIGINAL_CONFIG.read_text('utf-8'));config['index_path']=str(INDEX);CONFIG.write_text(json.dumps(config,indent=2))
 command=[str(CORE),'convert','decode-static','--logical-path',a.logical_path,'--config',str(CONFIG),'--index',str(INDEX),'--output-root',str(a.output/'decoded')]
 result=subprocess.run(command,capture_output=True,text=True,errors='replace',timeout=300)
 (a.output/'decode.log').write_text(result.stdout+'\nSTDERR:\n'+result.stderr,encoding='utf-8')
 assert result.returncode==0,'Native decoder failed; inspect diagnostic log'
 output=json.loads(result.stdout);manifest=Path(output['manifest_path']);assert manifest.is_file() and manifest.resolve().is_relative_to(a.output.resolve())
 decoded=json.loads(manifest.read_text('utf-8'))
 receipt={'schema':'korea.art013-native-model-readback/v1','archive':str(a.archive),'archive_sha256':sha(a.archive),'archive_bytes':a.archive.stat().st_size,'namespace':listing['archive']['name'],'archive_verified':True,'native_model_resources':[{'path':m['path'],'bytes':m['size']} for m in listing['members'] if m['path'] in {stem+s for s in ['.rgm','.rgo','.rrgeom','.rrmaterial']}],'manifest':str(manifest),'manifest_sha256':sha(manifest),'decoded_top_level_fields':list(decoded),'status':'native_decoded_pending_contract_comparison'}
 (a.output/'readback.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
