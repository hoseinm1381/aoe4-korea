# Garrison Korean art cook compatibility report

Prepared Korean art integration is blocked at native model cooking.

- Installed authoring: Garrison 0.1.8.
- Official configured feed refreshed through Blender: Garrison 0.1.9 is available.
- Official 0.1.9 archive was hash-verified and tested from an isolated temporary tools folder; the installed add-on was not replaced.
- Both SDK versions return `status: unsupported` from `editor_overlay.inspect_overlay(None, game_root)` against the connected Content Editor.
- The existing old model overlay is 16.3.11308. The pilot using it stalled before creating a burn log or SGA; it is a failed run.

Current editor identities:

- `EssenceEditor.exe`: SHA-256 `df563dcdab31e0b772b9239da2c6058f86aa0063ec2359a0847e5057fae4efab`; 10242872 bytes.
- `Essence.Editor.Core.dll`: SHA-256 `e2149a216e284bd6c33995c542f898af7f34ffa2e071162735ec1b6a74ef88ef`; 3291448 bytes.

Official 0.1.9 package: 53,559,526 bytes; SHA-256 `026d601bd2389a775b41041a2278b741fd2ade621b5d049f99cc015ea81589e0`.

Needed from the tool maintainer: supported model-tools preparation for the exact editor/core pair above. No hash bypass, guessed binary patch or fabricated prototype was used. The ordinary Steam editor is not a substitute for the prepared model-capable editor in this workflow.

Supporting local evidence: `official-update-check.log`, `official-update-package.log`, `editor-readiness.json`, `editor-readiness-019.json`, `pilot-native-cook.json`, and `stalled-pilot-process.json`.

All 152 portable source assets, native binding provenance and 0.1.2 rollback remain available. Next work after compatibility is supplied: qualify native pilot/readback; integrate private body/equipment/building owners and active LODs; build and verify the actual 0.1.3 archive and ZIP. Nothing has been sent to the maintainer or pushed to GitHub.

## Recheck after the owner restarted the laptop

Fresh SDK processes returned the same `unsupported` result for 0.1.8 and 0.1.9. No Essence Editor, Blender or AoE4 process was running before the probes. The configured official feed was refreshed successfully and still offers the same 0.1.9 package. The block is at model-tools preparation, before any Korean model conversion. The earlier pilot’s silent stall has no separately proven root cause.

Correction: the previous report named `Essence.Core.dll`; the actual Garrison gate checks `Essence.Editor.Core.dll`, whose identity is recorded above. This corrects the diagnostic file name, without changing either readiness result.

The checked editor/Core file identities are unchanged by the restart. A compatible Garrison model-cook tool build is still required. See `post-restart-check.json` and `post-restart-feed.log`. The 0.1.2 player ZIP hash remains unchanged; no 0.1.3 package was produced.
