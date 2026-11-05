"""Developer-only silent codec probe using a dummy PID; never attaches to AoE4.
This is not a launcher or a player dependency. Uses installed backend unmodified.
"""
from pathlib import Path
import ctypes,ctypes.wintypes as w,subprocess,os,json,time,re,hashlib
R=Path(__file__).resolve().parents[1];D=R/'docs/update_022'
B=Path.home()/'AppData/Local/Garrison/current/garrison-audio-backend.exe'
A=Path.home()/'AppData/Local/Garrison/library/korea/korea.sga'
def main():
 assert A.is_file() and B.is_file()
 text=(R/'source/scar/korea/voice_bank_020.scar').read_text(encoding='utf-8')
 clips=list(dict.fromkeys(re.findall(r'"(audio/[^" ]+\.ogg)"',text)))
 assert len(clips)==8459
 k=ctypes.WinDLL('kernel32',use_last_error=True)
 k.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,w.LPVOID,w.DWORD,w.DWORD,w.HANDLE];k.CreateFileW.restype=w.HANDLE
 k.WriteFile.argtypes=[w.HANDLE,w.LPCVOID,w.DWORD,ctypes.POINTER(w.DWORD),w.LPVOID];k.WriteFile.restype=w.BOOL
 k.CloseHandle.argtypes=[w.HANDLE];k.CloseHandle.restype=w.BOOL
 path='\\\\.\\pipe\\garrison-'+str(os.getpid())+'-audio.korea'
 log=D/'backend-codec-probe.log';h=None
 with log.open('wb') as stream:
  p=subprocess.Popen([str(B),'--sga',str(A),'--game-pid',str(os.getpid()),'--mod-key','korea'],stdout=stream,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
  try:
   for attempt in range(120):
    h=k.CreateFileW(path,0x40000000,0,None,3,0,None)
    if h!=w.HANDLE(-1).value:break
    assert p.poll() is None,log.read_text(errors='replace')
    time.sleep(.1)
   assert h!=w.HANDLE(-1).value,('pipe unavailable',path,ctypes.get_last_error())
   seq=0
   def send(message):
    nonlocal seq
    seq+=1;message.update(v=1,mod='korea',epoch=1,seq=seq,match=1,t=float(seq))
    raw=(json.dumps(message,separators=(',',':'))+'\n').encode();n=w.DWORD()
    assert k.WriteFile(h,raw,len(raw),ctypes.byref(n),None) and n.value==len(raw)
   send(dict(m='audio_session'))
   # One first and one last dialogue plus two nonverbal efforts. Gain zero
   # verifies decoding/admission without playing over the owner's test game.
   samples=[clips[0],clips[100],clips[-2],clips[-1]]
   for clip in samples:
    send(dict(m='audio',clip=clip,gain=0,x=0,z=0));time.sleep(1)
   time.sleep(1)
   send(dict(m='audio',stop=True));time.sleep(.3)
  finally:
   if h and h!=w.HANDLE(-1).value:k.CloseHandle(h)
   if p.poll() is None:p.terminate()
   p.wait(timeout=10)
 text=log.read_text(errors='replace')
 result={'backend':str(B),'backend_sha256':hashlib.sha256(B.read_bytes()).hexdigest(),'archive_sha256':hashlib.sha256(A.read_bytes()).hexdigest(),'dummy_process_id':os.getpid(),'game_attached':False,'gain':0,'sample_paths':samples,'played_log_count':text.count('played '),'audible_qualified':False,'all_samples_decoded':all('played '+c in text for c in samples),'notes':'Installed normal backend with documented pipe protocol; own diagnostic PID only. No game/client/library edits. Does not qualify normal client backend startup.'}
 (D/'BACKEND_CODEC_PROBE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2),flush=True)
 assert result['all_samples_decoded'],text
if __name__=='__main__':main()
