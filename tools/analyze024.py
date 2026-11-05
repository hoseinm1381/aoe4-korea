"""Read a Korea 0.2.4 warnings/scar log; summarize the latest diagnostic run."""
from pathlib import Path
import re,json,argparse
ROW=re.compile(r'KOREA024 seq=(\d+) t=([0-9.]+) kind=(ENTER|EXIT|STEP) call=(\d+) parent=(\d+) depth=(\d+) site=(\S+) detail=(.*)')
def analyze(text):
 text=text.rsplit('KOREA024 DIAGNOSTIC_READY',1)[-1]
 active={};rows=[];max_depth=0
 for line in text.splitlines():
  m=ROW.search(line)
  if not m:continue
  seq,now,kind,call,parent,depth,site,detail=m.groups();row={'sequence':int(seq),'game_seconds':float(now),'kind':kind,'call':int(call),'parent':int(parent),'depth':int(depth),'site':site,'detail':detail}
  rows.append(row);max_depth=max(max_depth,row['depth'])
  if kind=='ENTER':active[row['call']]=row
  elif kind=='EXIT':active.pop(row['call'],None)
 return {'diagnostic_rows':len(rows),'trace_limit_reached':'KOREA024 TRACE_LIMIT' in text,'last_game_seconds':rows[-1]['game_seconds'] if rows else None,'maximum_observed_nesting':max_depth,'open_callbacks':sorted(active.values(),key=lambda x:x['call']),'last_native_or_phase_step':next((x for x in reversed(rows) if x['kind']=='STEP'),None),'last_30_rows':rows[-30:],'interpretation':'No 0.2.4 diagnostic trace present; this cannot localize the crash.' if not rows else 'Open ENTERs/last STEP narrow the interrupted path; they do not establish causation. Buffered log loss and native/asynchronous crashes remain possible. TRACE_LIMIT makes later silence inconclusive.','crash_cause_confirmed':False}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('log',type=Path);p.add_argument('--out',type=Path);a=p.parse_args();report=analyze(a.log.read_text(encoding='utf-8',errors='replace'));report['log_path']=str(a.log.resolve());raw=json.dumps(report,indent=2,ensure_ascii=False)+'\n'
 if a.out:a.out.write_text(raw,encoding='utf-8')
 print(raw)
if __name__=='__main__':main()
