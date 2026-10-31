# Korea 0.1.4 local repair candidate

The owner resumed all reported Korea fixes, approved the temporary E: editor
tools, and explicitly confirmed application of this staged patch in the replacement
chat on 2026-10-31. No commit, push, tag, publication or installation is included.
The current player ZIP is `release/Koreans-Garrison-0.1.4.zip`; exact final hashes
and sizes are in `BUILD_VERIFICATION.json` and `update_014/ASSET_BUDGET.json`.

## Changes and evidence

- K01: clear only the capital's inherited
  `nomad_mode_town_center_complete\ZXL\spawn_official_master` completion action.
  Native starting ArmyBP remains six Villagers and one Scout. Scholar production
  and academy mechanics remain unchanged. No cleanup/spawn script was added.
- K02: bind the actual native RGB pattern texture, rather than its red-only
  automatically packed derivative. Preserve dynamic owner, skin and hair channels
  and the official unit shader's skin-tint LUT. All 108 model material bindings
  were checked; no team colour was baked into albedo.
- K03: the Pagoda's custom main model now has an independent root-attached native
  animator, instead of merging its one-root mesh into the foreign Acre Tower rig.
  Nine unique buildings/wonder retain their private stamp/model resources and
  authored lifecycle geometry. The unit shader requires a valid one-root skin
  stream for rigid geometry: all 36 prior qualified static geometry, UV, SKMS and
  lifecycle sets were retained after the unskinned trial failed projection.
- K04-K10: all 72 unit/mount models retain the exact current official SKLN payload,
  including bone order, reference transforms, named partitions, animation groups
  and LOD bone domains. Actual 0.1.3 Archer and mount fixtures demonstrate the
  malformed LOD counts and missing animation groups. The already-valid Lancer
  rider is retained as a control. Native graphs and clips are unchanged.
- K11: new editable Hwacha, its atlas/mask, source recipe and donor geometry/rig
  are in `authoring/art014/hwacha`. The rectangular 100-rocket rack uses 3,081
  highest-LOD triangles and three encoded LODs. Its five-bone official siege
  skeleton, native animation owner, crew, weapons and projectiles are preserved.
  One private attachment identity was allocated through the native SDK.

All 494 original tables were compared against the actual saved 0.1.3 source.
Only the three existing tables listed in the change policy differ; one private
Hwacha visual table was added. Unrelated gameplay, source art, voices, UI and
stable civilization identity are preserved. The 29 source regressions pass
(the affected six 0.1.4 checks were rerun after correcting the control expectation).

## Build and validation boundaries

The fresh 108-model native conversion and separate Hwacha cook completed with
real native burn logs. The final supported civilization assembly passed identity,
dependency/prematch validation, stored CRC/SHA1, all 1,734 member byte readbacks,
declaration checks and player ZIP CRC/SGA-digest verification. These are package
checks, not an in-game rendering or motion pass.

The installed 0.1.9 preview decoder stalls at its optional `animation_discovery`
stage for models with a skeleton, including one-root rigid models. Isolated and
merged-stock-index attempts timed out; their diagnostic receipts are retained.
Full fresh model projection is therefore **unverified**. Exact native skeleton
payload checks, current shader/texture checks, and byte-identical retained static
geometry/lifecycle evidence are reported separately, without promoting the
timeouts to a pass.

Follow `START-HERE.md` for fresh-match tests of the starting army, two owner
colours, every reported infantry/cavalry family and state, unique-building
construction/damage/ruins/repair, and Hwacha movement/aim/fire/reload/death.
LOD switching, save/load, AI, multiplayer and matching-settings frame-time/VRAM
remain separate unqualified gates. No performance claim follows from file size.

## Rebuild and editable inputs

Use Python 3.13 and the installed Garrison SDK. A normal mod rebuild consumes
the indexed repository files only; it does not require retired temporary cooks:

```
python -B tools/inputs.py verify
python -B tools/build.py --replace-current
python -B -m unittest discover -s tests -v
```

Use a task-local TEMP/TMP on owner-approved storage. `tools/art014` retains the
export/cook/repair recipes and real regression fixtures. The unsupported unskinned
static trial is diagnostic provenance, not the maintained static layout. Art edits
need a fresh export/cook and explicit update of the consumed native inputs; a
normal package rebuild does not export Blender changes.

The Hwacha recipe starts from `authoring/art014/hwacha/donor_geometry.blend`.
Its museum/reference provenance is recorded in that folder's `recipe.json`.
The master uses a packed authored albedo and relative local image path. All
existing 152 curated art sources remain unchanged.

The owner requested retiring generated F: work and the approved E: tool copy after
verification. `update_014/CLEANUP.json` records the result. Editable inputs,
current native resources, scripts, compact failure evidence, Git and the exact
0.1.3 rollback are retained.
