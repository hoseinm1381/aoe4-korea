# Korea 0.3.10

Current release **0.3.10**. Restores native construction and ruin controllers on all nine custom landmarks.
Fresh-match verification is pending.

[Download the playable ZIP](https://github.com/hoseinm1381/aoe4-korea/releases/tag/v0.3.10) · [Build notes](docs/UPDATE_0310.md).

For development, clone with Git LFS and see [DEVELOPMENT.md](docs/DEVELOPMENT.md).

---

# Korea 0.3.8

Wavy Korean selection flag and highest-detail landmark meshes. See the [0.3.8 release notes](docs/UPDATE_038.md).

---

# Korea 0.3.7

The nine unique buildings use stock-contract sRGB albedo textures. The Stone Pagoda has darker stone and courtyard finishes. See the [0.3.7 art and restart investigation](docs/UPDATE_037.md).

---

# Korea 0.3.6

Nine unique buildings have separate historically inspired palettes and raised player-colour accents. The Stone Pagoda is taller. The ordinary Keep barrage readiness check, barrage weapon reloads, Codex connectors and card dates were updated. See [the 0.3.6 notes](docs/UPDATE_036.md).

---

# Korea 0.3.5

Korean landmarks, the keep, and the wonder have painted wood, warmer stone, and broader player-colour details. Lumber and mining camp shelters now show player colour on timber. See the [0.3.5 art and verification notes](docs/UPDATE_035.md) and GitHub Releases for the playable ZIP.

---

# Korea 0.3.4

Tiger Hunters have distinct Feudal, Castle, and Imperial armor. Korean cavalry use separate native charge and fighting attachments, with restored shields and native bow animation. The Blender masters and weapon atlases are in `authoring/art034`. See [the 0.3.4 build and verification](docs/UPDATE_034.md) and GitHub Releases for the player ZIP.

---

# Korea 0.3.3

Rebuilt Horsemen, Knights and Mounted Hwarang, including their horses and all three distances of detail. The editable Blender masters and shader atlases are in `authoring/art033`. See [the cavalry build and verification](docs/UPDATE_033.md) and GitHub Releases for the player ZIP.

---

# Korea 0.3.2

Local Garrison ZIP: `release/Koreans-Garrison-0.3.2.zip`. Restores the 0.3.0 landmark model controllers and increases dynamic player colour on the nine unique buildings. See [0.3.2 verification](docs/UPDATE_032.md).

---


# Korea 0.3.1

Local Garrison ZIP: `release/Koreans-Garrison-0.3.1.zip`. Restores subtle owner-colour strips, the six Korean landmarks’ native repair visuals, and Palace barrage cleanup. The Palace’s owner Delete command is removed. See [0.3.1 verification and test steps](docs/UPDATE_031.md).

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

# Korea 0.2.5 voice-controller-disabled diagnostic

Current local ZIP: `release/Koreans-Garrison-0.2.5.zip`. All voice code/audio, art, tuning and 0.2.4 tracing retained. Voice controller startup is disabled. Exact 0.2.4 ZIP remains beside it. See `docs/UPDATE_025_VOICE_DISABLED.md` and `docs/update_025/COMPLETION.json`. Native crash outcome pending.

Earlier release history follows.

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



# Koreans - independent Garrison civilization



Current local audio diagnostic candidate: **0.2.2**, `release/Koreans-Garrison-0.2.2.zip`.

Read [player instructions](START-HERE.md), [0.2.2 handoff](docs/UPDATE_022.md)

and [native package receipt](docs/BUILD_VERIFICATION.json).



Korea and Berber are silent after a shared Garrison startup/readiness failure

leaves no audio consumer. 0.2.2 embeds the matching runtime helper, uses the documented speech-volume bus and adds bounded

freeze-phase diagnostics. It is not an audible-playback fix for a missing backend.

Five native starting sheep and every existing recording/model/gameplay fix remain.



The release retains original Korean unit-family and gender voices with four

age-specific dialogue banks, multiple alternative lines and independently

synthesized takes. It uses the ordinary single-ZIP Garrison import-and-Play route.

Existing models, dynamic player colour, cavalry skins, Gapsa shield, research

prices/book UI/refunds and gameplay values are preserved against exact 0.1.6.



Historical scripts and phonetic approximations are documented with source locators,

meaning, confidence and model limits. They are not verified ancient pronunciation.

Expert/native-speaker listening and native gameplay acceptance remain pending.

Repair and religious targets use safe neutral acknowledgements where the maintained

presentation command boundary cannot qualify the exact action target.



The repository retains typed whole-file native tables, current art/rig/texture

masters, original voice references, lossless dialogue WAVs, scripts, generation

seeds/batch receipts and self-contained native audio. Ordinary rebuilds require

no voice-model download or other civilization checkout. Free generation tools and

pinned model weights remain separately protected under

`F:/aoe_4_temp/ai_voice/tts-workstation`.



Use `START_DEVELOPMENT.cmd`, Python 3.13 and the installed Garrison authoring/core:



```text

python -B tools/inputs.py verify

python -B tools/release022.py verify

python -B tools/build.py --replace-current

```



Build in the existing source and one current output/staging location. Failed

logs and exact rollback inputs are protected. Do not push, install, tag, publish

or perform broad drive cleanup under the local voice-build authorization.

The exact 0.1.6 ZIP remains under `archives/voices020-baseline/e48869987e4c/`.



[Development workflow](docs/DEVELOPMENT.md) Â· [Design](docs/DESIGN.md) Â·

[Release policy](RELEASES.md) Â· [0.1.6 fixes](docs/UPDATE_016_RELEASE.md).

Credits: **hosein81 and chilly5**.



Documentation-led correction: the 0.2.1 SGA omitted scar/garrison/garrison.scar.

0.2.2 now embeds the unmodified installed 0.1.13 helper, as the current guide

requires for adapted mods. Its complete import closure is empty. Real-helper

MessagePack tests cover session, pulse, direct clip and a bridge that becomes

available after start. This removes reliance on an externally supplied helper;

it does not claim to start the client-owned audio backend. Berber is treated as

unverified; the installed guide/API is the 0.2.2 contract.

