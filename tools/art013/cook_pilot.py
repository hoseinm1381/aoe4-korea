from pathlib import Path
import sys,re,json,shutil,tempfile,subprocess,hashlib,msvcrt
from check_sources import model_tools
if not model_tools():raise SystemExit('Unsupported model tools: native pilot not launched')
R=Path(__file__).resolve().parents[2];stage=Path(tempfile.gettempdir())/'k13';project=stage/'library/Mods/k013';source=project/'project/source';old='art/scenario/garrison/k013/units/template/body';new='art/kr013/vma1'
body=source/new;body.mkdir(parents=True,exist_ok=True)
for p in (source/old).iterdir():
 if p.is_file():shutil.copy2(p,body/p.name)
export=R/'output/art-current/export/villager_pilot'
for name in ['model.fbx','model.rig']:shutil.copy2(export/name,body/name)
for name in ['model.material','model.rgotemplate']:
 p=body/name;s=p.read_text('utf-8');p.write_text(s.replace(old,new),encoding='utf-8')
burn=source/'_default.burnproj';s=burn.read_text('utf-8');blocks=[b for b in re.findall(r'<BurnRule>.*?</BurnRule>',s,re.S) if old.replace('/','\\') in b];assert len(blocks)==4
if new.replace('/','\\') not in s:s=s.replace('</Rules>','\n'.join(b.replace(old.replace('/','\\'),new.replace('/','\\')) for b in blocks)+'\n\t</Rules>')
burn.write_text(s,encoding='utf-8')
run=stage/'native-pilot';assert not run.exists(),'Preserve prior native diagnostic run';run.mkdir()
editor=Path.home()/'AppData/Local/Garrison/Kit/tools/essence-object-editor/EssenceEditor.exe'
cmd=[str(editor),'-rtm','--safe_settings','--do_not_restore','--quiet_crash_report','--no_source_control','--log_path',str(run/'logs'),'--build_mod',str(project/'project/k013.aoe4mod'),'--no_burn_window','--burn_verbose_log_level','--burn_cache_type','Local','--burn_max_threads','1','--burn_log_path',str(run/'logs/burn.log'),'--build_path',str(run/'output'),'--intermediate_path',str(run/'intermediate')]
log=R/'docs/update_013/pilot-native-cook.log'
with (stage/'native-cook.lock').open('a+b') as lock:
 lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
 try:
  si=subprocess.STARTUPINFO();si.dwFlags|=subprocess.STARTF_USESHOWWINDOW;si.wShowWindow=0
  print('NATIVE_PILOT_STARTED',flush=True)
  with log.open('w',encoding='utf-8') as f:p=subprocess.run(cmd,cwd=editor.parent,stdout=f,stderr=subprocess.STDOUT,timeout=1200,startupinfo=si)
 finally:lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)
archives=list((run/'output').rglob('*.sga'))
report={'exit_code':p.returncode,'archives':[str(x) for x in archives],'project':str(project),'run':str(run),'template_generated_actor_not_for_integration':True,'source_geometry_export':str(export)}
(R/'docs/update_013/pilot-native-cook.json').write_text(json.dumps(report,indent=2)+'\n')
print('NATIVE_PILOT_FINISHED',p.returncode,len(archives),flush=True)
assert p.returncode==0 and len(archives)==1,'Inspect native cook evidence'