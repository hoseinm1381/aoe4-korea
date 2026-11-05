"""Current tests without rewriting frozen 0.2.1 or older receipts."""
from pathlib import Path
import sys,unittest,json,time,ast
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tests'),str(R/'tools')]
tree=ast.parse((R/'tools/voice020_focused_tests.py').read_text());research=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','')=='research'))
names=['test_voices_020','test_voices_021','test_voices_022','test_native_start','test_barrage_015']+['test_research_016.Research016.'+n for n in research]
start=time.monotonic();result=unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromNames(names))
report={'tests':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'seconds':time.monotonic()-start,'native_runtime_proof':False,'audible_proof':False,'historical_tests':'Old tests and receipts unchanged; 35-second source replay is not a reproduced native freeze.'}
(R/'docs/update_022/REGRESSIONS.json').write_text(json.dumps(report,indent=2)+'\n');sys.exit(0 if result.wasSuccessful() else 1)
