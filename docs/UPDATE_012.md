# Koreans 0.1.2 — local review and native retest

Owner screenshots of tested 0.1.1 show empty overview lists for the three new
ports, inherited Malian overview technologies for Berbers, missing selector
flags and overlapping or misplaced tech-tree icons. The owner specifically
identified Berber blacksmith research appearing in Age I.

## Changes

- 8 owned unique-unit entries and 10 owned unique-technology entries.
  `source/codex-review.json` owns these reviewed lists. Real blueprint UI supplies
  names, icons and tooltips. Internal markers are not presented as research.
- Seven source-backed bonus explanations, plus the hidden combined lobby
  summary at trait index 0. Active alliance, research and landmark requirements
  are explicit. Existing unit/research mechanics are unchanged.
- Plural display labels, without changing race/bundle/audio keys or UUIDs.
- Clear RaceBP `icon_small`, following the installed Garrison authoring guide;
  the native Codex falls back to its already cooked `icon` flag.
- Build both Codex representations from native construction tabs, spawners and
  research lists. Follow positive current official/private prerequisites;
  ignore negative/self-exclusion requirements when computing admission ages.
  Keep producer availability and landmark construction/production ages separate.
- Use local x pitch 2 and persistent family lanes, reserve producer header rows,
  merge same-name producer variants and report conditional-unit aliases. Bind
  actual unit-tier research through `upgrade_pbg`. Native age rows remain 0–11.
- Stock foreign Villager menus do not import an entire donor civilization's
  construction tree. Such conditional production slots remain untouched in
  gameplay and are recorded in `docs/CODEX_GRAPH.json` for native review.
- Use maximum standard ZIP compression while preserving SDK package member
  bytes. Keep HD loading screens and world textures/geometry unchanged.

## Evidence and limits

`tests/fixtures/codex-before-012.rgd` was extracted from the tested 0.1.1 ZIP and
SHA-256 checked against its original final member manifest. Regressions prove
the previous empty/donor lists and Age-I blacksmith defect, check corrected
research tiers, icon pitch, both native views, selector fields and UI-only scope.
The final assembler verifies native identity, CRC/SHA1, every member's SHA-256,
declaration hashes, exact change allowlist and outer ZIP/SGA integrity.

See `docs/BUILD_VERIFICATION.json`, `docs/FINAL_MEMBER_MANIFEST.json.gz`,
`docs/SOURCE_TESTS.json` and `docs/SIZE_REPORT.json` for current results. This is
typed-native validation/assembly/readback, not a new art cook or Content Editor
burn. No new world art requires cooking. Native appearance, tooltip layout,
audio listening, gameplay, AI, save/load, multiplayer and VRAM/frame-time
remain separate acceptance gates. No runtime performance claim follows from
ZIP or audio size reduction.

Retest the checklist in START-HERE.md. Tested 0.1.1, original masters, native
world assets, credits and stable identity are retained. Nothing is installed
or published. Push requires owner acceptance and a separate manual instruction.

Final ordinary producer headers lead their available age band; units/research follow. The supported one-member native refinement, when needed, is recorded in update_012/HEADER_REVIEW.json. Every untouched member was re-extracted and hash checked. The normal full builder produces this final layout directly.
