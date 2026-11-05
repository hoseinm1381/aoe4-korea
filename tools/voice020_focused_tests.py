"""Current-scope regression suite; historical frozen-release tests remain intact."""
from pathlib import Path
import sys,unittest,json,time
R=Path(__file__).resolve().parents[1];sys.path[:0]=[str(R/'tests'),str(R/'tools')]
names=['test_voices_020','test_native_start','test_barrage_015']
research=['test_original_missing_custom_fields_loses_literature_refund','test_original_dead_actor_loses_payment_current_refunds','test_fee_once_completion_and_observatory_rebate','test_queue_rejection_cancel_and_death_refund_once','test_native_insufficient_and_duplicate_paid_callbacks','test_foreign_allowance_consumes_and_restores_once','test_fallback_catalogue_matches_all_native_variants_and_gold_exception','test_all_research_variants_only_flags_and_presentation_change','test_custom_tooltips_preserve_stock_dictionary_and_match_fees']
names+=['test_research_016.Research016.'+n for n in research]
suite=unittest.TestLoader().loadTestsFromNames(names);ids=[]
def visit(s):
 if isinstance(s,unittest.TestSuite):
  for x in s:visit(x)
 else:ids.append(s.id())
visit(suite);start=time.monotonic();result=unittest.TextTestRunner(verbosity=2).run(suite)
report={'tests':result.testsRun,'successful':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors),'ids':ids,'seconds':time.monotonic()-start,'historical_frozen_release_tests':'Unchanged. Baseline broad run already had 9 failures and 1 error before voice promotion; see baseline-tests.log. This suite checks current presentation/native-start/barrage/payment behavior, not retired version/hold/hash assertions.','native_runtime_proof':False}
(R/'docs/voices020/FOCUSED_TESTS.json').write_text(json.dumps(report,indent=2)+'\n');sys.exit(0 if result.wasSuccessful() else 1)
