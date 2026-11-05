# Korea 0.2.1: starting sheep and voice routing

The owner reported no audible Korean voices and no five starting sheep in 0.2.0.
This local repair retains the recordings and all art/research values.

Game logs show audio.korea transport=none and 37 no_consumer batches; the client
first reported native startup/readiness failure. Both Korea and Berber are
recognized by its census as carrying audio. No backend started in that session.
This is evidence of missing client playback, not a codec failure. A successful
fresh normal Garrison launch is required; this mod cannot start a missing client
process. No live game/client file or process was altered.

The controller now follows Berber's compiled PBG-ID-first mapping, with a known
owner fallback for bare names; foreign namespaces remain rejected. Local voice
presentation starts independently of unsupported gameplay starts. Bounded
STARTED/BOUND/QUEUED/SEND_FAILED diagnostics distinguish submitted cues from
backend playback: QUEUED never establishes audible success.

The native ArmyBP now includes exactly five stock sheep and official standard
offsets: two white, one black and two brown. Existing default six Villagers plus
one Scout and campaign six Villagers stay unchanged. No dynamic sheep spawning.
Typed semantic undo removes only these appended entries and recovers the entire
original army. The campaign's original six-unit roster was inspected separately.

All 7,632 dialogue and 827 effort encodings, 9,734 native inputs and 9,612 editable
inputs, colour/cavalry/Gapsa and research fixes are retained. Updated installed
authoring/client is 0.1.13. Package results and exact rollback hashes will be
recorded in update_021/COMPLETION.json.

Seven new regressions fail in five places against preserved 0.2.0 source and must
pass after repair. Historical tests and 0.2.0 receipts remain unchanged. Import,
audible voice and five-sheep native materialization, AI, save/load, multiplayer
and performance remain separate acceptance gates. No push, tag or installation.

Built local ZIP: F:\aoe_4_temp\New_custom_civilization\aoe4-korea\release\Koreans-Garrison-0.2.1.zip

Bytes: 145,866,303; SHA-256: 275dd0ae0ab008b19c3155560393bccaf018167186402e3bff4ddb6d282f2011.
Packaged SGA SHA-256: eff3b6199cf4f22159684253c7d08346f62b47b50f97e55fbc94e422f79bc526.
All 39 current regressions, 527 native tables and 10279 full member readbacks passed. Exact 0.2.0 and 0.1.6 rollback ZIPs are preserved. Media remains 298,524,568 bytes. See update_021/COMPLETION.json and ASSET_BUDGET.json.

Post-cleanup ZIP CRC/SHA-256, packaged SGA SHA-256, exact 0.2.0/0.1.6 rollback hashes and input-index digests passed. Verified reproducible staging retired: 2,055,557,553 logical bytes. Required inputs, recordings/weights and compact evidence remain. The live game/client were not altered.
