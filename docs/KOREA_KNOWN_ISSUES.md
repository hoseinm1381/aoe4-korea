# Current report: 0.2.3 random crash and Mounted Hwarang visual defects

Owner supplied warnings.log in this standalone root and a screenshot at game 6:07.
Crash reported at 6:42. Diagnosis prioritized; Mounted Hwarang distant horse-leg
omission and apparent extra bow are deferred by owner. Their exact LOD/attachment
owners still need investigation; do not remove gear or remodel by guesswork.
0.2.4 is a logging-only diagnostic candidate. See UPDATE_024_DIAGNOSTIC.md and
update_024/SCAR_AUDIT.json. The earlier statement that no Korea-specific log was
available is superseded by this new evidence; root cause remains unconfirmed.

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



# Korea 0.1.6 ZIP built - 2026-11-01



The duplicate Gapsa spear is fixed by restoring its left-hand shield. The verified

0.1.6 ZIP also includes the pending colour, cavalry and research payment/UI repairs.

Read [the release handoff](UPDATE_016_RELEASE.md) and `docs/update_016_build`.

The owner explicitly resumed building, superseding the historical hold below for

this release. Native fresh-match acceptance remains pending. No push or install.



---



# Korea research payment/UI repair - source only, 2026-11-01



The owner also reported duplicate olive-oil costs and incorrect research charges.

The source now corrects 104 free non-default ability variants, gives Korean

research book-cost tooltips and repairs refund handling. Read

[UPDATE_016_RESEARCH.md](UPDATE_016_RESEARCH.md) and its validation receipts.

The colour/cavalry repair is preserved. The build hold remains; the current player

ZIP is still 0.1.5. Native payment, tooltip and appearance acceptance is pending.

Earlier source-preservation statements apply to their original art-only phase.



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



# Current repair candidate: Korea 0.1.4



The owner explicitly authorized implementation and the local build. Source/native

contract repairs and Hwacha are delivered in the 0.1.4 local test ZIP. Read

[UPDATE_014.md](UPDATE_014.md) for actual scope, evidence and decoder limits.

All K01-K11 native appearance/animation/lifecycle acceptance checks remain pending

the owner's fresh-match test. The report below preserves the real 0.1.3 failures.



---



# Korea 0.1.3: owner-reported native issues



Reported 2026-10-31 with three in-game screenshots. Current ZIP is a known-issues

candidate. Previous source/cook/readback/package checks passed; the owner's game

test now establishes failed visual/animation acceptance. Those checks did not

qualify native rendering or motion. No fixes or replacement build are authorized

in this cleanup turn: list and plan only; wait for the next instruction.



| ID | Reported issue | Work required after approval |

| --- | --- | --- |

| K01 | Korea starts with an Imperial Official. | Trace the native starting ArmyBP and Standard/startup callbacks. Remove only the unwanted starting Official, check default/campaign/start-age variants, and verify fresh-match starting units. Do not remove intended trainable Scholars. |

| K02 | Units are white and lack intended colour/team colour. | Trace each consumed native model/material/texture path and UV assignment. Compare with working Berber/Persian/Vietnamese and official unit materials. Restore authored albedo and native RGB owner/skin/hair masks; validate compression, colour spaces and two distinct owner colours in-game. Do not bake player colour into albedo. |

| K03 | Unique buildings have no visible main model; donor yards/decoration can remain. | Trace every active EBPS, private attachment list, stamp and model resource. Check actual material/resource resolution, attachment origin, native mesh groups, lifecycle selectors and model flags. Restore all intended unique buildings/wonder, including preview/construction/healthy/damage/ruins and repair. Identify the cause with one native building probe before batching. |

| K04 | Knight/Lancer model has no animation. | Compare working donor mount/rider animator owners, bind matrices, bone order, skeleton palettes, skin weights, model flags and attachment sockets. Keep the correct native animation graph and verify idle/walk/run/turn/attack/charge/death at each relevant tier. |

| K05 | Horseman model has no animation. | Qualify its own rider/mount skeleton and native owner; do not assume Knight fixes cover Horsemen or transformed Hwarang. Test movement, combat, transitions and both forms where applicable. |

| K06 | Archer animation is broken. | Compare its actual stock animator/attachment graph and bind-pose/skin contract; repair native model integration and weapon socket alignment. Test idle, movement, firing/reload, torch and death. |

| K07 | Crossbowman animation is broken. | Qualify the actual crossbow receiver and all weapon states; correct skeleton/bind/palette/material integration and test fire/reload/weapon grip independently. |

| K08 | Tiger Hunter animation is broken. | Trace its actual donor animator and distinct weapon/ability states; repair their consumed body/equipment contracts and verify complete firing/ability transitions. |

| K09 | Spearman animation is broken. | Match the correct native spear receiver, binds, weights and equipment; test idle/move/attack/brace/charge response/torch/death. |

| K10 | Gapsa animation is broken. | Resolve its own infantry donor and all tiers rather than reuse an assumed generic rig; check armour, weapon/shield sockets, transforms and full native motion set. |

| K11 | Hwacha needs a distinct unique model. | Inspect the existing Hwacha's gameplay/visual owner and proven stock/other-civ siege assemblies. Author an editable Korean rocket-cart silhouette using a compatible native siege skeleton/graph; preserve wheel motion, crew where required, aiming, deploy/fire/reload, projectiles/muzzles, team colour and gameplay. Qualify one complete native unit before widening scope. |



For animation, geometry/UV/bone-name equality alone is insufficient: verify

inverse binds, receiver bone indices/palettes, animator ownership, native model

flags and state-specific attachments. Preserve native animation owners where

possible. Do not replace working motion with frozen static exports or add custom

clips merely to hide a bad model binding.



Suggested order: diagnose one broken infantry unit, one cavalry assembly and one

unique building against working native controls; then apply the proven fixes by

family; create Hwacha after the integration path is proven. Keep the current

ZIP/rollback and editable masters. Test actual appearance and all motion/lifecycle

states in a fresh game before calling the next version accepted. Performance,

LOD switching, save/load and multiplayer remain separate gates.



Cleanup preserved current source/native inputs/ZIPs. New build temp should go on

F: via a task-local TEMP/TMP environment, be verified, and be retired after the

current delivery is saved. Do not globally change Windows temp settings.



Documentation-led correction: the 0.2.1 SGA omitted scar/garrison/garrison.scar.

0.2.2 now embeds the unmodified installed 0.1.13 helper, as the current guide

requires for adapted mods. Its complete import closure is empty. Real-helper

MessagePack tests cover session, pulse, direct clip and a bridge that becomes

available after start. This removes reliance on an externally supplied helper;

it does not claim to start the client-owned audio backend. Berber is treated as

unverified; the installed guide/API is the 0.2.2 contract.

