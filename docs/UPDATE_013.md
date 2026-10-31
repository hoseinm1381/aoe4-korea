# Korean art 0.1.3 — local candidate

The owner explicitly resumed this work in the replacement chat on 2026-10-31.
The current source uses version 0.1.3. The final local package receipt is
`docs/BUILD_VERIFICATION.json`; player import and native match acceptance remain
pending. No commit, push, tag, installation or player Release is part of this step.

## Retained and integrated inputs

All 152 curated editable assets remain under `authoring/art013/`, with their
shared/source texture masters. Their original source files in
Temp_before_github_push were not changed. Only required art, native resources,
portable recipes and compact diagnostic receipts were added to this repository.

The integration uses 72 unit/mount models, 46 ordinary-building native models,
25 equipment models, nine unique buildings and two separate camp shelter modules.
The shelters are additional render models from two of the same source assets.
Dormant age/state variants remain available without changing gameplay age rules.

Private native attachment lists/stamps isolate Korea from stock civilizations.
The inherited trader and monk use SDK-derived private entity/squad identities
with preserved effective gameplay values. Existing animation and speech owners
remain. The stock cavalry animation owner lacks rein bones: export copies fold
only those influences to the nearest existing animated ancestor, preserving
editable sources, geometry, UVs and rig hierarchy.

Ordinary-building geometry retains original native topology, UV/index/skin/mask
bytes and lifecycle owners. Unique buildings retain authored construction,
damage and ruins sets. A one-bone static skin stream preserves their RGB player
colour masks. The wonder uses lossless native render partitions; the cooker's
explicit mesh aliases are checked for equivalent lifecycle membership.

## Verification and limits

- 23 source regressions pass, including real before/after gameplay and media checks.
- All 72 units/mounts pass native readback and geometry/UV/hierarchy/weight checks.
- All 36 equipment/unique/camp models pass native readback and cold-source vertex,
  UV, state/LOD triangle and lifecycle-condition/membership comparisons.
- 46 ordinary models preserve native UVs, indices, skin and selector bytes.
- The full source passes supported native civilization validation. Final archive,
  identity, declaration, readback and ZIP results are recorded by the package build.

Stock lower-detail building source previews are not claimed as activated native
LODs. The preserved native structures retain their original behavior; actual
culling/LOD use, animations, repairs, save/load, AI, multiplayer and performance
require fresh native tests. File size is not runtime VRAM/frame-time proof.

## Rebuild and edit

Use Python 3.13 and the installed Garrison SDK/core. The qualified current model
editor pair is pinned by `tools/art013/prepare_model_tools.py`; changed editor
hashes require requalification. The ordinary mod rebuild consumes this repository's
maintained tables, scripts and indexed native media, without the old workspace:

```
python -B tools/inputs.py verify
python -B tools/build.py --replace-current
python -B -m unittest discover -s tests -v
```

The art export/cook/comparison tools under `tools/art013/` are reproducible
qualification recipes. They use curated inputs plus installed tools, preserve
failed diagnostic runs, and never save a user scene. Their first-run staging and
readback paths are generated data, not extra source checkouts. For an intentional
future art edit, regenerate the affected native resources and review/update its
input manifest and exact change policy before rebuilding.

`source/update-013-policy.json` is the exact package member allowlist against
0.1.2. `source-before-promotion.json.gz` preserves the replaced editable table
text and build configuration. The 0.1.2 player ZIP is retained under
`archives/art013-baseline/` after the new ZIP passes. Earlier diagnostic history
is retained in `update_013/HISTORY.md` and the individual logs/receipts.

## Final package receipt

Local ZIP: `release/Koreans-Garrison-0.1.3.zip` — **95,155,560 bytes**.

Native SGA: **234,726,386 bytes**; all 1,572 members
passed readback/integrity and independent namespace/declaration checks.

Additional native art inputs: **219,247,846 bytes**.
The ZIP increase against the preserved 0.1.2 pre-art candidate is
**90,762,491 bytes**. Native texture budgets,
formats and mip counts are in `update_013/ASSET_BUDGET.json`.

All 23 source tests passed. Nothing was pushed, tagged, published or installed.
Native appearance, animation, repairs, LOD switching, multiplayer and performance
remain pending owner tests.
