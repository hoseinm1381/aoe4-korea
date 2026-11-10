# Rebuild Korea 0.3.8

Clone this repository with Git LFS installed and run `git lfs pull`. Install AoE IV, the Garrison authoring tools and Python 3.13. Verify the native and editable inputs with `python -B tools/inputs.py verify`, then run `BUILD.cmd`. The builder assembles the full mod from the indexed native media, tuning, localization and SCAR. For model, flag and audio editing, retain the indexed masters under `authoring/` and the specific recook inputs linked from the [0.3.8 notes](UPDATE_038.md).

The player ZIP is distributed through [GitHub Releases](https://github.com/hoseinm1381/aoe4-korea/releases/tag/v0.3.8). Scratch outputs and rollback ZIPs are local.

---

# Korea 0.3.0

Korean units now have a five-second reply cooldown per unit and task. A different task can reply as soon as the current line finishes. Rapid orders leave at most one pending reply for the selected squad.

- Import the player ZIP from GitHub Releases using Garrison 0.1.16 or newer. Select Korea in Standard Skirmish with Tuning Pack None and Standard Starting Resources.
- This release carries forward the 0.2.13 Literature prices and refunds, keep barrage changes, stronger unique-building player colours and the larger Gyeongbok Palace.
- The editable source includes the indexed art, audio and native inputs. See the development guide and build verification receipt. Voice timing still needs a fresh in-game listening check.

Earlier entries describe historical builds.

---

# Korea 0.2.11

The standalone Garrison release sets the native standard starting army to 200 food, 200 wood, and 100 gold. Korean unit dialogue and group Scholar Supervise are enabled. Korean upgrades use the stock tooltip layout, including Textiles and Wheelbarrow.

- Play the local `release/Koreans-Garrison-0.2.11.zip` using the separately kept patched Race-only Garrison 0.1.15 loader for AoE IV 17.0.12260.0. Select Korea in Standard Skirmish with Tuning Pack None and Standard Starting Resources.
- Rebuild with `BUILD.cmd --replace-current`. The documented Garrison authoring tools and indexed native and editable inputs are required. The version-specific archive comparison uses `docs/update_0211/expected-members.json.gz`.
- The release archive and starting resource readback passed. Match starting totals, voice playback, tooltip stability, and multiplayer still need runtime validation. See `docs/BUILD_VERIFICATION.json`.

Earlier entries below describe historical builds.

---

# Korea 0.2.4 crash diagnostic - current local candidate

Verified local ZIP: `release/Koreans-Garrison-0.2.4.zip`, 199,761,556 bytes.
SHA256: `b0544f10ac45604968502330c977f99cef735a67b086c976f321cfa98d2eab89`.
The owner supplied a new Korea log and screenshot and reports a random crash at
6:42. This supersedes the previous no-Korea-log status. The current log has no
fatal SCAR stack; root cause is unconfirmed. 0.2.4 adds bounded paired tracing of
45 project functions and selected native boundaries for the owner's next test.
All original SCAR statements recover exactly after removing diagnostic lines.
Models, LOD/equipment, higher-quality audio, native data/gameplay values and five
starting sheep are unchanged. Distant Mounted Hwarang horse legs and extra bow
are recorded with the original screenshot and explicitly deferred by the owner.

56 behavior/diagnostic/stress checks, full Lua/static/MCP checks, native validation
of 527 tables, 10,282 final-member readbacks, namespace/CRC/ZIP/hash and exact
unchanged-member preservation passed. This is not an in-game crash-fix claim.
Exact 0.2.3 rollback: `archives/diagnostic024-baseline/e65c6b0c165b/Koreans-Garrison-0.2.3.zip`.
Read `docs/UPDATE_024_DIAGNOSTIC.md` and `docs/update_024/COMPLETION.json`.
Next: fresh single-player Korean Standard/None; same speed/cheats first; train
Mounted Hwarang, cycle mounted/foot, move/attack, train/lose units near Seowon,
and continue past eight minutes. Preserve warnings.log/scarlog before relaunch.
No installation, live-match execution, push or other-civilization mutation.

Earlier milestone/status entries below are historical.

---

# Korea 0.2.3 higher-quality audio - built 2026-11-02

Current verified local ZIP: `release/Koreans-Garrison-0.2.3.zip` - 199,764,260 bytes
(+53,899,867 versus 0.2.2). SHA256:
`e65c6b0c165bf5887d6e99d23fc4a1401f15023697a3fe719a4b0935a0274187`.
All 7,632 dialogue takes use approved 24 kHz higher-fidelity Vorbis encodes from
lossless masters. Working 0.2.2 routing/helper/speech bus, 827 nonverbal efforts,
five starting sheep, models, animations and gameplay remain unchanged. Exact
owner-tested 0.2.2 is retained at
`archives/quality023-baseline/6175fcef8fff/Koreans-Garrison-0.2.2.zip`.

Native validation/build, all 10,281 member SHA256 readbacks, namespace/CRC,
ZIP/hash checks and four installed-backend silent decode probes passed.
45 retained behavior tests, four lifecycle stress checks and 12 native model/
player-schema contracts passed. Full 0.2.3 native listening remains pending.
Random single-player crashes are **not diagnosed or claimed fixed**: the supplied
log and explicit older fatal-error sessions identify Chagatai; no correlated
Korea crash stack was found. See `docs/update_023/CRASH_AUDIT.json`.
Read `docs/UPDATE_023.md` and `docs/update_023/COMPLETION.json` for exact evidence.
No push, publication, installation or game interruption. Earlier entries below
are historical; the owner reported 0.2.2 voices worked.

---

# Korea 0.2.2 owner-reported working - 2026-11-02



The owner reported "it worked" after the documented Garrison helper/audio-settings

repair, then requested cleanup and a mandatory future packaging rule. This

supersedes the earlier blanket audio-unresolved status below. The exact tested

ZIP remains unchanged: 145,864,393 bytes; SHA256

6175fcef8fffb0b6a59c1e02f3b4524b42dc14b84d36de591b760c42936ca94e.

See docs/update_022/OWNER_ACCEPTANCE.json (update_022 from docs).

The report did not enumerate every voice context or establish the freeze cause,

historical pronunciation, save/load, AI, multiplayer or performance acceptance.

Historical failed-session and as-built evidence below stays preserved. No rebuild,

installation or push follows from this documentation/cleanup update.



---



# Korea 0.2.2 local diagnostic candidate - 2026-11-02



Read docs/UPDATE_022.md (UPDATE_022.md from docs). Current silent Korea/Berber

sessions fail Garrison startup before any audio backend. 0.2.2 adds Berber

speech-bus parity and bounded freeze-phase logs, preserving all recordings,

models, gameplay and five native sheep. It does not claim to fix the shared

client launch failure or establish the freeze cause. Build with release022.py

verify and tools/build.py --replace-current; frozen old verifiers remain unchanged.

No push, installation or client/game changes. Earlier notes below are history.



---



# Korea 0.2.1 local repair - 2026-11-02



Read the current UPDATE_021 handoff and update_021/COMPLETION.json. The five native sheep and Berber-parity voice routing repair are packaged. The observed Garrison launch failure left no audio consumer; successful fresh client launch and audible/native acceptance remain pending. Prior notes below are historical.



---



# Korea 0.2.0 voice workflow



Read UPDATE_020_VOICES.md and voices020/RUN_CHECKPOINT.json. Build from current typed source and indexed native audio with tools/build.py. Regeneration uses the protected external F: workstation and tools/voice020_generate.py, followed by codec finalization, audit and bank mapping. Ordinary rebuilds need no models/network/other-civ checkout. Historical milestones below retain their original scope.



---



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



Documentation-led correction: the 0.2.1 SGA omitted scar/garrison/garrison.scar.

0.2.2 now embeds the unmodified installed 0.1.13 helper, as the current guide

requires for adapted mods. Its complete import closure is empty. Real-helper

MessagePack tests cover session, pulse, direct clip and a bridge that becomes

available after start. This removes reliance on an externally supplied helper;

it does not claim to start the client-owned audio backend. Berber is treated as

unverified; the installed guide/API is the 0.2.2 contract.

