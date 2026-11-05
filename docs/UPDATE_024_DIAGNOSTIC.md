# Korea 0.2.4 - local crash localization build

The owner supplied a Korea 0.2.3 log and screenshot, reporting a random crash at
game clock 6:42. Mounted Hwarang distant horse legs and an extra bow are visible
issues recorded for later; the owner explicitly prioritizes crash localization.
No model, LOD, equipment, audio, blueprint or gameplay-value change is included.

## Evidence and hypotheses

The preserved supplied log is update_024/warnings-023-korea.txt.gz, with its source
hash and screenshot provenance in BASELINE.json. It identifies native Standard,
Korea startup, complete first-45-second phases, Mounted Hwarang creation, movement,
combat and conversion to foot form at 23:25:25.871. Its last record at 23:28:26.326
is a temporary 1775 ms hang-detection extension. It contains no fatal Lua/SCAR
stack or explicit engine crash fault. A hang message does not identify its cause.
CheatTurbo and instant-build/resource cheats were used; preserve those conditions
for the first comparison. Do not turn this observation into a confirmed cheat bug.

All 15 original authored SCAR files, generated data banks and the packaged current
Garrison helper were included in the inventory/review. The new diagnostic module
makes 16 authored files. Static/Lua/MCP evidence is distinct from game execution.
The audit includes every scheduled callback, global/squad event, native command,
group owner, modifier and UI/voice state boundary. See SCAR_INVENTORY.json and
SCAR_AUDIT.json. There is no unique 402-second one-shot trigger. Recurring work
includes 6-second Hangul, 15-second academy, 30-second water, 20-second guards,
5-second patrol and 10-second kill income, relative to player initialization.

High-priority paths to localize, not proven defects:

- Mounted/foot conversion changes entity blueprint, squad blueprint and health
  in sequence; the voice tracker then observes a changed blueprint on a retained
  squad identity. Official chatcheats.scar uses the same entity-then-squad order,
  so it is not replaced by an invented conversion workflow. Instrument each
  operation and voice callback retirement/re-registration instead.
- Global death, construction and research events can interleave with rewards,
  production, refunds and automatic follow-up research. Paired callback markers
  expose incomplete or deeply re-entered calls without suppressing exceptions.
- Recurring landmark/economy entity and squad snapshots touch native handles;
  Seowon neutral scans, academy resolution, state writes and supervision reads
  get finer markers. Retained loops/timings and native groups remain unchanged.
- Timed buff/debuff/barrage expiry removes native modifiers and may issue Stop;
  markers bracket application, removal, ownership resolution and commands.
- Local selection, voice reactions, squad event registration/removal and UI
  publication are traced separately from simulation work. Native model/render
  issues remain possible if the tail closes all SCAR callbacks before the crash.

## What changed

`korea/diagnostics_024.scar` imports after the existing modules. It wraps only an
explicit list of this project's public Lua functions, before their interval/event
registration. Paired ENTER/EXIT IDs carry parent and nesting depth; STEP lines
bracket selected native operations. It patches no engine or Garrison globals,
adds no rule, suppresses no exception, changes no arguments/return values, makes
no retry and dereferences no native object merely to format a log. Original
callbacks retain identical registered/removal identities after wrapping.

Logging starts immediately and continues beyond the previous 45-second window.
It is bounded at 20 game minutes or 100,000 trace lines, with explicit TRACE_LIMIT.
Logging adds overhead. This candidate is temporary and not a performance release.
Removing the marked lines restores every changed original SCAR file byte-for-byte.
The native and editable master indexes, all models/audio, bank scripts, research
prices/refunds and five native sheep remain identical to 0.2.3. Exact 0.2.3 is
moved to diagnostic024-baseline only after the verified diagnostic ZIP is copied.

## Owner reproduction

Import the 0.2.4 ZIP normally; enable only this Korea candidate for the first
comparison, select Koreans / native Standard / Tuning Pack None / single player.
Start fresh. Reproduce the previous sequence and continue past eight game minutes.
Train Mounted Hwarang, change mounted -> foot -> mounted several times, move and
attack, and train/lose units near a Seowon. First keep the same speed/cheats as
the failure. A second fresh match with no Hwarang conversion separates that path
from recurring economy/voice work; normal-speed comparison is a later useful axis.

After crash/freeze, preserve Documents/My Games/Age of Empires IV/warnings.log
and that session's scarlog before restarting the game. The first trace line must
include KOREA024 DIAGNOSTIC_READY. Analyze with:

```text
python -B tools/analyze024.py warnings.log --out docs/update_024/NEXT_RUN_ANALYSIS.json
```

Return the whole log if possible. The latest unmatched ENTER and STEP identify
where to investigate next, but are not sufficient alone to declare root cause.
If the trace limit was reached or the log was buffered/truncated, repeat with a
narrower trace. Do not call a passing mock, source scan or package a crash fix.

Build with Python 3.13 and TEMP/TMP on F:/aoe_4_temp/Temp_aoe4/k20:
`tools/release024.py`, `tools/check024.py`, `tools/build.py --replace-current`.
No installation, live match execution, push, other-civ change or broad cleanup.

Verified local package: F:\aoe_4_temp\New_custom_civilization\aoe4-korea\release\Koreans-Garrison-0.2.4.zip

ZIP: 199,761,556 bytes; SHA256 b0544f10ac45604968502330c977f99cef735a67b086c976f321cfa98d2eab89.
SGA: 374,155,769 bytes; SHA256 66dc7db60170f35801d72f6ad2878590e494c506f2f6f93534032b39a387af35.
All 10,282 member SHA256 readbacks, namespace/CRC/ZIP checks and exact unchanged-member preservation passed.
Exact 0.2.3 rollback: F:\aoe_4_temp\New_custom_civilization\aoe4-korea\archives\diagnostic024-baseline\e65c6b0c165b\Koreans-Garrison-0.2.3.zip.

Scoped cleanup removed 2,453,875,069 bytes of regenerable build/readback/staging and byte-verified duplicate metadata. Current and exact 0.2.3 rollback ZIP hashes were verified afterward. Inputs, all art/audio masters, models, weights, sources, diagnostic logs and compact receipts remain.
