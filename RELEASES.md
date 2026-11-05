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



# Korea 0.2.0 local voice candidate - 2026-11-02



Read [the voice/build handoff](docs/UPDATE_020_VOICES.md) and current package receipt. The local ZIP and exact 0.1.6 rollback are verified. Historical/native listening and gameplay acceptance remain separate pending gates; no new publication or installation. Older release notes below are history.



---



# Current source-only upload - 2026-10-31



Current source/player candidate: **0.1.2**. The owner authorized committing and

pushing developer source at 02:15 AM system time. Player release publication,

tags and installation remain unauthorized. Native acceptance remains pending.

See docs/SOURCE_PUBLICATION.md. Older preparation statements below are history.



---



# Korea release policy



Current local candidate: **0.1.0-trial.1**. No push, commit, tag, publication or

installation is included in this preparation.



The player delivery is exactly one Garrison import ZIP containing one

civilization-role SGA, its manifest and player notes/cover. Do not upload source,

art, sound, input-pack ZIPs or checksum files as additional release assets.

Keep checksums and verification receipts in repository documentation.



All developer inputs remain as whole files in this one repository. The release

folder is ignored by Git. When explicitly authorized later, publish source to

this civilization's existing repository and attach only the verified player ZIP.

GitHub-generated source archive links are separate from uploaded release assets.

Do not promise their LFS payload behavior without verifying that download path.



Documentation-led correction: the 0.2.1 SGA omitted scar/garrison/garrison.scar.

0.2.2 now embeds the unmodified installed 0.1.13 helper, as the current guide

requires for adapted mods. Its complete import closure is empty. Real-helper

MessagePack tests cover session, pulse, direct clip and a bridge that becomes

available after start. This removes reliance on an externally supplied helper;

it does not claim to start the client-owned audio backend. Berber is treated as

unverified; the installed guide/API is the 0.2.2 contract.

