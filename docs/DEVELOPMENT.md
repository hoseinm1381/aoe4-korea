# Korea 0.1.6 ZIP built - 2026-11-01

The duplicate Gapsa spear is fixed by restoring its left-hand shield. The verified
0.1.6 ZIP also includes the pending colour, cavalry and research payment/UI repairs.
Read [the release handoff](UPDATE_016_RELEASE.md) and `docs/update_016_build`.
The owner explicitly resumed building, superseding the historical hold below for
this release. Native fresh-match acceptance remains pending. No push or install.

---

# Korea 016 source repair, final build held - 2026-10-31

The owner reports 015 gameplay runs, but unit colour and cavalry animation failed.
The current source restores broad dynamic owner masks and combined cavalry skin
bindings. Read docs/UPDATE_016.md and docs/update_016. The release ZIP remains 015.
Do not cook, assemble or package while the owner is playing; project.json enforces
the build hold. Native acceptance of the source repair awaits later packaging
and fresh-match tests. Preserve current originals, releases and rollback inputs.

---

# Korea 0.1.5 repair, 2026-10-31

The owner resumed the latest Korea missing-model/landmark/Hwacha-crash repair.
Read docs/UPDATE_015.md and docs/update_015 receipts. Version 0.1.4 failed native
visual/barrage acceptance; its package checks remain historical. The new local
candidate requires fresh-match testing. Preserve sources, identity, editable art,
native inputs and exact 0.1.3/0.1.4 rollback ZIPs. No push or installation.
Owner requests cleanup of this task's generated E:/F: files after verification.

---

# Korea 0.1.4 current handoff

Read [UPDATE_014.md](UPDATE_014.md). The maintained build consumes indexed current
native inputs and `source/update-014-policy.json`. Full fresh model preview
projection is limited by the installed decoder's animation-discovery timeout;
source, native contract, archive integrity and actual game acceptance are separate.
Earlier development milestones below retain their historical scope.

---

# Korean art 0.1.3

Read [the current art/build handoff](UPDATE_013.md). The maintained build now
consumes the qualified private Korean media and exact 0.1.3 policy.
Older development milestones below retain their historical scope.

---

# Current Korean art preparation, 2026-10-31

Read [UPDATE_013.md](UPDATE_013.md) before art builds. The playable version remains
0.1.2; the new 152-asset source set is prepared for 0.1.3, with native integration
blocked by unsupported model tools. Existing `tools/build.py` rebuilds 0.1.2.
Packed art013 images have been consolidated into local relative shared files.
Older development notes below retain their historical scope.

---

# Current 0.1.1 development update

Read UPDATE_011.md first. Use `python -B tools/build.py --replace-current`
for the one current build/ZIP. The guarded builder replaces only previously
verified staging after preserving the tested player ZIP in archives/.
The active update allowlist is source/update-011-policy.json, compared with
docs/update_011/baseline-members.json.gz. Older allowlists below are history.
New presentation sources and recook entrypoints are documented in UPDATE_011.md.
No push, tag, installation or publication until acceptance and separate manual
instruction. All four projects rebuild from their own repository files.

# Working on Korea

## One repository, one current build

| Path | Authority |
| --- | --- |
| `source/tables/attrib/*.rgd.json` and descendants | Lossless typed native gameplay/core tables |
| `source/scar/` | Maintained civilization scripts and dispatcher |
| `source/locale/en.json` | Editable English localization |
| `source/presentation/` | Original banner and generated PNG surfaces |
| `authoring/` | Indexed editable Blends, rigs, textures, recipes and qualified exports |
| `authoring/attribute-editor/` | Retained original editable XML references |
| `inputs/native/` | Accepted compiled-only/native rebuild resources, including audio where present |
| `tools/` | Environment check, field editor, input verifier, Codex generator and builder |
| `release/` | Exactly one current player ZIP, ignored by Git |
| `output/current/` | Reusable generated staging/readback; not source |

The current build consumes typed tables, not the XML reference copies. This keeps
accepted art/voice/lifecycle fixes that a broad old-project burn can discard.
Typed JSON preserves native keys, hashes, scalar kinds, variants, IDs and opaque
Chunky metadata. It is not a guessed XML decompilation. Existing XML is retained
for authors who need its original inheritance/edit history; editing it alone
does not change the current package.

## Tools and first start

Install Python 3.13, Garrison authoring/core and AoE4 Content Editor normally.
Run `START_DEVELOPMENT.cmd`, or `python -B tools/check_environment.py`.
Set `GARRISON_PYTHON` to another Python 3.13 executable if needed; set
`GARRISON_EXTENSION` when the extension is not under Blender 5.2's usual folder.
Builds need these installed tools, not the former combined mod, another civ repo
or a separately downloaded media pack. No AI/provider environment is required
to keep or edit the existing shipped audio.

## Edit gameplay and text

```text
python -B tools/tables.py find villager
python -B tools/tables.py show <printed-table-path> health_max
python -B tools/tables.py set <printed-table-path> <exact/printed/field/path> <JSON-value>
```

Use both default and campaign variants where applicable. Preserve keys/hashes,
scalar types and PBG identities. New instances/IDs come from supported native
derive/cook or Attribute Editor operations. Do not invent IDs or change the owner.
Edit SCAR and localization directly in `source/`. The builder regenerates both
Codex views from actual engineer construction menus, spawners and upgrade lists;
adjust `tools/codex.py` for a deliberate Codex-layout change. Dynamic Korean
foreign-tech offers remain described by their actual information panel.

## Edit art or audio

Open indexed Blends under `authoring/`. External image/library paths are relative
to this repository; packed images remain packed. Original path/hash metadata in
`source/master-index.json` is provenance, not an external download dependency.
Export and cook a deliberate art change through Garrison, then update its actual
consumed native resources under `inputs/native/`. A saved Blend alone does not
activate an in-game model. Keep construction, ruins/repair, selection, markers,
team-colour masks, equipment, all variants and active LODs intact.

After a reviewed intentional change, record only the changed input:

```text
python -B tools/inputs.py record master <path-relative-to-authoring> --reason "Describe the edit"
python -B tools/inputs.py record native <native/member/path> --toc data --reason "Describe the cook"
```

Register new masters and provenance in `source/master-index.json` first. Vietnam's
10,529 shipped Ogg clips live once in `inputs/native/audio/`; these are the available
editable current audio in the accepted combined repository. Original WAVs and
voice-generation environments were not in that snapshot and are not claimed here.
Persia/Korea retain their installed native speech banks. Do not regenerate voices
or fetch paid services as part of an ordinary build.

## Verify and rebuild

```text
python -B tools/inputs.py verify
python -B tools/build.py --prepare-only --output output/preflight
python -B tools/build.py --replace-current
python -B -m unittest discover -s tests -v
```

Optional Lua regression dependency: `python -m pip install -r requirements-tests.txt`.
Builds themselves do not require Lupa. `--replace-current` reuses only a verified
successful `output/current` and replaces only the previously recorded local player
ZIP after the new ZIP passes. Unknown files and failed output are protected.
Keep useful failed-build diagnostics; successful staging/readbacks can be removed
after verification. Never delete native inputs, editable masters or Git objects.

An ordinary build checks input hashes, compiles typed tables, validates the full
private recipe, uses supported civilization assembly, reads back every final
member by TOC/SHA-256, checks native CRC/SHA1 and declaration/header identity,
then verifies the sole playable ZIP. This is local repository-contained rebuild
proof, not a remote clean-clone, in-game or performance result.

The repository's large-file rules, if any, refer to files in this same repository.
Use a complete Git/Git LFS checkout when such rules are present. Make whole-file
changes normally; do not replace the source with one frequently uploaded ZIP.

## Native acceptance

Test import, dropdown/selection, match load, all-age production and landmarks,
mechanics/voices, repeated matches, mixed independent civilizations and stock
opponents. Save/load, AI, Nomad, later-age starts, multiplayer and frame-time/VRAM
need their own qualification. A cook, small ZIP or source test does not prove them.
Do not push, tag, publish or install until the owner authorizes that action.

## Retained art recipe limits

The current package builder consumes only repository inputs plus installed tools.
Original art scripts/recipes are preserved as authoring provenance and can contain
old absolute workspace paths. Review and adapt those paths before running them.
Use the portable indexed Blends and the current Garrison project for new exports.
Full fresh recooking of every retained art master was not performed for this split.
The portable-master receipts check image/library closure; package rebuilds preserve
accepted native art and audio bytes.

`source/authoring-profile.json` records initial carrier generation. Later
reviewed typed tables own the final start, resources and schema; `tools/build.py`
is the current rebuild entrypoint. Rerunning the initial profile alone would
not reproduce later changes, including Korea's stock scout and allowances.
