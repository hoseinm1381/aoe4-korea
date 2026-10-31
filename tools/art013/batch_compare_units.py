import bpy,json,runpy,sys,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[2]
rows=json.loads((R/'docs/update_013/unit-native-readbacks.json').read_text())['assets'];reports=R/'docs/update_013/unit-source-comparisons';reports.mkdir(exist_ok=True);results=[]
for i,row in enumerate(rows,1):
 name=row['asset'];path=reports/(name+'.json');sys.argv=['blender','--','--manifest',row['manifest'],'--asset',name,'--report',str(path)]
 try:
  runpy.run_path(str(R/'tools/art013/compare_probe.py'),run_name='__main__');result={'asset':name,'passed':True,'report':path.relative_to(R).as_posix()}
 except Exception as error:
  traceback.print_exc();result={'asset':name,'passed':False,'error':str(error)}
 results.append(result);print('NATIVE_SOURCE_COMPARISON',i,len(rows),name,result['passed'],flush=True)
 (R/'docs/update_013/unit-source-comparisons.json').write_text(json.dumps({'completed':len(results),'expected':72,'results':results},indent=2)+'\n')
assert len(results)==72 and all(a['passed'] for a in results),'Some source/native comparisons failed; inspect receipt'
print('ALL_72_NATIVE_SOURCE_COMPARISONS_PASSED',flush=True)
