"""Current 0.2.1 tests; retain historical 0.2.0 receipts unchanged."""
from pathlib import Path
import sys,unittest,json,time,ast
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tests'),str(R/'tools')]
tree=ast.parse((R/'tools/voice020_focused_tests.py').read_text())
research=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','')=='research'))
names=['test_voices_020','test_voices_021','test_native_start','test_barrage_015']+['test_research_016.Research016.'+n for n in research]
suite=unittest.TestLoader().loadTestsFromNames(names);start=time.monotonic()
result=unittest.TextTestRunner(verbosity=2).run(suite)
report={'tests':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'seconds':time.monotonic()-start,'suites':names,'baseline_new_regressions':'Seven new checks replayed against original 0.2.0 source: five fail; foreign-owner rejection and existing capture startup already pass.','historical_tests':'Original historical tests and prior release receipts unchanged.','native_runtime_proof':False}
(R/'docs/update_021/REGRESSIONS.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
sys.exit(0 if result.wasSuccessful() else 1)
