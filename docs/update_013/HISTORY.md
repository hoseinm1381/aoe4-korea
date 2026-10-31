# Korean 0.1.3 art integration — native conversion qualified, integration in progress

## Current result: actual native conversion works

The owner requested an actual conversion trial rather than stopping at the
version guard, then updated the installed Blender add-on to Garrison 0.1.9.
A native trial using the ordinary current editor completed but omitted RGM/RGO/
RRGeom. A separate current-editor copy prepared with Garrison's existing exact
ObjectEditor feature-marker patch produced all four native model resources.
The only profile admission change was process-local and pinned to the exact
current editor/Core hashes; no installed SDK or game binary was changed.

The fresh 437,142-byte archive passed CRC/SHA1 and namespace verification.
Its Korean villager model decoded with no blockers, warnings or missing textures:
73 bones, three native LOD palettes and 1,362 / 606 / 250 triangles. All native
vertices matched source positions, UVs and bone influences within the recorded
half-float/8-bit tolerances; hierarchy and triangle counts match. The earlier
1,210 / 505 / 192 figures were polygon counts, not triangle counts.

See `update_013/native-conversion-qualification.json` and
`update_013/native-conversion-comparison.json`. The reusable exact-hash setup is
`tools/art013/prepare_model_tools.py`. It creates/verifies only a task-owned
model-tools copy, preserving the installed game/add-on. A changed editor pair
requires a fresh native qualification. Official UI admission is not altered.

The previous conclusion that a build could not work was too strong: the old
fingerprint table blocked setup, while actual conversion with the unchanged
patch routine succeeds. This qualifies the native conversion path for the
recorded pilot; it does not claim all 152 asset bindings, native animation,
full-mod runtime or the final 0.1.3 player ZIP are complete. Unit/mount batch
exports have resumed. The current playable mod remains 0.1.2 until integration
and strict final archive verification finish.

The older blocker reports below describe the earlier checks, not current
conversion capability.

The owner requested the existing Korean assets from `Temp_before_github_push`
be applied to the standalone Korea repository, with only necessary new editable
inputs and a minimum workable source workspace. No new push, installation, tag
or player release publication was requested.

The complete art source set is now in `authoring/art013/`: 152 Blends, shared
textures, original high-resolution unit texture masters, concise recipes and
native lifecycle/bind evidence. Cold-open comparison against every original
passed after relative paths were corrected. Original sources were not changed.
Large review renders, GLBs, donor decodes, backups and temporary cook work were
not copied. Existing gameplay/native inputs are unchanged and pinned in
`source/art013/baseline-runtime.json`; original editable sources remain indexed.

The next candidate is 0.1.3. The actual project and current player ZIP remain
0.1.2 because no 0.1.3 native art package passed verification. The new sources
are not active in-game yet; copying a Blend does not wire a native model.

## Native blocker and pilot evidence

Installed authoring extension/core: Garrison 0.1.8; Blender 5.2.2. The installed
Garrison model-tools readiness check reports the connected Content Editor as
`unsupported`, with editor fingerprint `df563dcdab31` and core `e2149a216e28`.
It cannot prepare a supported current model-cook overlay. The old overlay is
16.3.11308. Replacing hashes, patching an unknown editor or accepting a fabricated
unit prototype is not part of this integration.

A real supported prototype was obtained through the core CLI, and the Korean
villager was exported with its 73-bone rig and all three authored LOD meshes
(1,210 / 505 / 192 triangles). The generated English template is cook boilerplate
only: its actor, animator and clips must not be integrated. No stock owner was
replaced. The isolated native pilot stalled without a burn log or SGA, and its
exact task-owned editor process was terminated. Its process exit code was zero,
but no archive exists: the pilot is failed, not a successful cook.

Evidence is under `docs/update_013/`: `saved-files.json`, `editor-readiness.json`,
`pilot-native-cook.json`, `unit-export-pilot.log`, `template-export.log`,
`template-source.log` and the captured process command. Transient exports and
cook staging are outside tracked source, under `output/art-current/` and the
short `%TEMP%/k13` diagnostic directory. Nothing depends on a second checkout.

## Follow-up compatibility check

The owner confirmed that only the current installation is available. Blender's
configured official feed was refreshed successfully and offered Garrison 0.1.9.
The 0.1.9 package was verified against its advertised size and SHA-256 and tested
from an isolated temporary tools folder, without replacing the installed add-on.
It reports the same unsupported Content Editor/Core fingerprints as 0.1.8.
At that earlier checkpoint native setup was blocked. See
[the maintainer-ready compatibility report](update_013/MODEL_TOOLS_COMPATIBILITY.md)
for exact hashes, package identity, readiness results and the required fix.
This report has not been sent externally. Art sources and the 0.1.2 package
were not changed during this follow-up.

## Post-restart recheck

The owner restarted the laptop and requested another diagnosis. Fresh-process
checks of both 0.1.8 and verified official 0.1.9 still return `unsupported`.
There was no running editor/game/Blender process before the checks. The official
feed was refreshed and still offers 0.1.9. This is a model-tools preparation
block before asset conversion; the earlier pilot stall has no independently
proven root cause. The exact checked DLL is `Essence.Editor.Core.dll`; the
compatibility report has been corrected. See `update_013/post-restart-check.json`.
The checked binaries and old player ZIP are unchanged. No native cook was
relaunched against a tool pair already refusing compatibility.

## Resume with compatible model tools

1. Use the installed Garrison 0.1.9 and the exact-hash locally qualified model-tools path. The original version-guard-only blocker has been superseded by a real cook/readback.
   Re-run `python -B tools/art013/check_sources.py --check-model-tools`. Exit 2
   means the blocker remains; exit 0 only means source/tool readiness.
2. The native villager pilot cook/readback is now qualified. Continue per-asset checks while batching units. Compare
   exact rest/bind records, skin palettes, all three active LODs, UVs and weights.
   Keep original Chinese/native animators, state graphs and equipment owners.
3. Follow `source/art013/integration-plan.json`. All 152 entries are pending,
   including private age/gender bodies, mounts, weapon/tool sockets, ordinary
   building render owners, native construction/damage/ruins/repair, camp modules
   and unique-building state/LOD bindings. Fourteen inherited trader/monk consumer
   notes are unresolved; do not treat those descriptions as blueprint names.
   The compact native owner/stamp/equipment provenance is beside the plan.
4. Native derive/cook must allocate new private attachment identities. Never
   override a global stock model or guess PBG IDs. Keep all gameplay scalars,
   footprints, production, stable owner/race, voices, music and UI unchanged.
5. After qualified resources exist, register exact consumed native inputs,
   bump the actual candidate to 0.1.3, and create a precise added/changed-member
   allowlist against `docs/update_013/baseline-members.json.gz`. The existing
   0.1.2 builder does not consume these draft art sources and must not be used
   as evidence of a 0.1.3 art build.
6. Build and verify final archive namespace, mounts, CRC/SHA1/SHA256, every
   allowlisted member, unchanged gameplay and the final ZIP. Retain 0.1.2 until
   the new ZIP passes. Measure package contribution and decoded texture/geometry
   costs separately. Import, fresh-match visuals, repairs, save/load, multiplayer
   and performance remain native acceptance gates.

`tools/art013/curate_sources.py` is a one-time source-promotion helper. The pilot
export/template/cook scripts are diagnostics, not a completed batch build route.
The old `cook_pilot.py` entrypoint retains the earlier failed run; do not overwrite
that evidence. Use the qualified preparation path for subsequent cooks. No new
0.1.3 player ZIP has been produced yet.
