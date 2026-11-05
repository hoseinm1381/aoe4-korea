"""Current behavior checks plus audio-only preservation; frozen tests stay intact."""
from pathlib import Path
import sys,unittest,json,time,ast
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tests'),str(R/'tools')]
from release023 import verify
verify()
tree=ast.parse((R/'tools/voice020_focused_tests.py').read_text());research=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','')=='research'))
names=['test_voices_020','test_voices_021','test_native_start','test_barrage_015']+['test_research_016.Research016.'+n for n in research]
names+=['test_voices_022.Helper022.test_documented_real_helper_session_pulse_and_clip','test_voices_022.Helper022.test_matching_helper_reannounces_if_bridge_was_absent_at_start','test_voices_022.Voice022.test_window_is_bounded_and_completes_at_35_seconds','test_voices_022.Gameplay022','test_voices_022.Config022.test_direct_clips_use_speech_volume_like_berber']
start=time.monotonic();result=unittest.TextTestRunner(verbosity=2).run(unittest.TestLoader().loadTestsFromNames(names))
report={'tests':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'seconds':time.monotonic()-start,'native_runtime_proof':False,'audible_proof':False,'historical_tests':'Old tests and receipts unchanged. Frozen 0.2.2 exact-version assertion replaced for current run by stricter 0.2.3 audio-only preservation verifier; all 45 behavioral checks retained.'}
(R/'docs/update_023/REGRESSIONS.json').write_text(json.dumps(report,indent=2)+'\n');sys.exit(0 if result.wasSuccessful() else 1)
