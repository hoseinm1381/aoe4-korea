# Korea 0.1.6 local test ZIP, 2026-11-01

The owner authorized the duplicate-spear fix and resumed the ZIP build. The
verified package is `release/Koreans-Garrison-0.1.6.zip` (107,644,580 bytes).
Its SHA-256 is `e48869987e4c7159290a911d263e06288b6ddf8da7cd3c34e236eaadf0a3a788`. The exact 0.1.5 ZIP is retained at
`archives/art016-baseline/d97df7034df3/Koreans-Garrison-0.1.5.zip`. No installation or publication occurred.

## Gapsa duplicate spear

The original art mapper treated a left-hand shield as an ordinary weapon and
replaced it with `korea_gapsa_heavy_spear`. The Gapsa's normal combat hardpoint
still supplied a right-hand spear, producing two differently coloured spears.
Restore the current official metal-wicker shield for age III and gold-wicker
shield for age IV: 12 paths across male/female and default/campaign/xp3 attachment
variants. Keep their left-palm sockets, custom Korean bodies, right-hand weapons
and all gameplay. The mapper now excludes Gapsa defense meshes from that fallback.
`SPEAR_REPAIR.json` records exact old/new paths and official member hashes.

## Included repairs and evidence

This ZIP includes the pending broad dynamic player masks, restored native mask
alpha, combined cavalry skin bindings, unique mesh/material names, 104 corrected
non-default research prices, book-cost templates and guarded refunds. See
`UPDATE_016.md` and `UPDATE_016_RESEARCH.md` for their original source evidence.
Their build-held status is historical; this request explicitly resumed building.

34 applicable regressions pass, including the actual previous shield-to-spear
mapper failure, exact native reversal checks, prices/refunds, masks, cavalry,
barrage, native start and player schema. Earlier phase-specific hold/equality
assertions were left unchanged and were not represented as current-suite passes;
`release016-tests.json` lists the selected checks and each excluded historical gate.

The supported Garrison validator passed 494 tables. Fresh native assembly passed
all 1,785 member readback hashes, TOCs, CRC/SHA1, independent archive owner,
declaration digests, strict 0.1.5 member allowlist and packaged SGA SHA-256. ZIP
CRC, one civilization-role manifest, stable bundle key and version were checked.
No new geometry Content Editor cook was required. Compact build/assembly/member
receipts and original-source fixtures are retained in `update_016_build`.

`ASSET_BUDGET.json` records archive bytes, incremental ZIP contribution, packaged
art bytes and decoded/block mip totals. These totals do not establish live VRAM,
LOD transitions, frame time or smoothness. Native appearance, animation, payment,
Byzantine coexistence, import, save/load, AI and multiplayer remain separate tests.

Import the ZIP through Garrison and select Koreans with native Standard and
Tuning Pack None. Test the Gapsa before/after its spear upgrade and age upgrade,
two player colours, cavalry idle/movement/attack/charge/death, research hover and
deduction, insufficient funds, cancellation/death and Observatory rebates.

Generated build staging has been retired after package/input checks: 1,605,759,447 logical bytes reclaimed. The known E: task-temp directory is absent and F: task temp is empty. Compact recipes, reports, original sources, masters, native inputs, the current ZIP and exact rollbacks remain. See `update_016_build/CLEANUP.json`.
