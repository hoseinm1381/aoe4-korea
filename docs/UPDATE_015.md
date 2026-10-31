# Korea 0.1.5 local repair candidate

This resumes the interrupted Korea work from “Fix Berber release 3 issues new”.
The owner reported green MISSING ABP cubes on Villagers, Spearmen and Gapsa,
absent landmark main models, and a Hwacha barrage crash in 0.1.4.

- The 72 custom body/mount models requested their exported atlas material key,
  while 014 supplied donor keys such as lod1/lod2/lod3. Bind the unchanged
  official shader/parameters/RGB textures/tint LUT under the actual geometry key.
  Unused cargo object materials are excluded; active donor LOD payloads match.
- The 36 custom rigid models encoded multi-state lifecycle alternatives with
  first connective 0 then 1. Current stock Chinese range and stable both use 1
  for every alternative. Match those exact native records, changing only the
  first connective word. Preserve single-state conditions and all state names.
- The game log reports effects.scar:134 calling unavailable
  Squad_GetActiveCommand. Use documented Squad_HasActiveCommand,
  Squad_IsMoving and Squad_HasAcceptedCommands before the existing timed Stop.
  Keep death, capture, modifier cleanup and temporary-group lifetimes intact.

No geometry, UV, texture, skeleton, motion clip/graph, gameplay table, identity,
voice or UI is changed. One-root skeleton LOD sharing also exists in retained
Vietnamese/Persian resources; its presence alone was not a proven defect and it
is preserved. The starting Scout uses a stock model and was not custom-rig proof.

The Lua regressions execute the actual old script to reproduce the nil call,
then test the corrected script for completion, move/queue/Stop, death/capture,
repeated use and the keep branch. This is a stubbed engine boundary, not a match.
A new stationary ground-attack order cannot be distinguished by these documented
APIs; retest cancellation/retargeting in game.

Read update_015/APPLIED_REPAIR.json, OFFICIAL_CONDITIONS.json,
BUILD_VERIFICATION.json and update_015/COMPLETION.json for final evidence.
Native material and condition serialization is corrected directly. Geometry and
compressed textures were not recooked; the final civilization archive is freshly
assembled/read back. Earlier 014 cook logs remain historical evidence.

Fresh-match appearance, animations, lifecycle, save/load, multiplayer, AI and
VRAM/frame time remain pending. No push, tag, publication or installation.
The owner requested removal of task-generated E:/F: temporary files after final
ZIP/rollback/input verification; keep editable inputs and compact diagnostics.
