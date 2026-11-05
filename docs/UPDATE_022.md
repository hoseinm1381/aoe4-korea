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

# Korea 0.2.2 local audio diagnostic candidate

0.2.1 remains silent in the owner test. Current Berber also fails. The current
client reports native startup/readiness failure before starting an audio backend.
Korea logs show actual native unit matches and queued cues; its channel logs
transport=none with no_consumer. This is a shared client-launch/playback blocker,
not a proved recording or unit-mapping defect. No audible repair is claimed here.

0.2.2 follows the installed guide: it embeds the matching 0.1.13 runtime helper
and adds the documented audio/events.json speech-volume bus. It retains the
working Garrison.audio.forMod("korea") route, compiled PBG mapping, session/pulse/
play/stop lifecycle, local selection/owner gating, bounded polling, cooldowns and
non-repeating banks. There is no loose-audio installer or alternate player launcher.

The installed matching 0.1.13 backend decoded four existing Korean OGG clips
through its documented pipe with a dummy diagnostic PID and gain zero. All four
logged played; this is decoder/admission proof only, not audible listening or
normal-client startup proof. See BACKEND_CODEC_PROBE.json. All existing recordings,
models, native speech suppression and the five native starting sheep are unchanged.

No Korea event is scheduled specifically at 35 seconds. The existing 30-second
water-income scan, 15-second Seowon, 6-second Hangul, 20-second guard, 5-second
patrol and 10-second landmark-kill income timers were inspected. Their feature
conditions and simulation timing are unchanged. Last old test cues show Scholar,
Villager and Spearman replies queued, without a reported SCAR error at the end.
The two Windows crash/hang reports posted near the test actually occurred at
2026-11-02 15:41:08 Tehran and 2026-10-30 20:56:06 Tehran respectively. They do
not identify the current freeze, and the older WATCHDOG filename alone is not
proof that this match suffered a GPU fault.

0.2.2 logs voice and gameplay subsystem phases once per second from seconds
25 through 45 after each controller starts. Last phase without its completion
narrows a repeated stall; logs stop afterward. Whole original source is recovered
by removing only these logging statements, with CRLF normalization explicitly
accounted for. A real-Lua first-minute replay preserves all gameplay call ordering
and reaches 35 seconds; it does not reproduce or rule out a native stall.

46 source regressions pass. Current skill SCAR validators report zero errors;
known warnings resolve to installed Garrison methods, project imports and the
borrowed engine-owned squad group. Full native package checks are recorded after
building in docs/BUILD_VERIFICATION.json and update_022/COMPLETION.json.

Current playback blocker remains outside the mod's source: normal Garrison must
successfully create the per-mod backend. The owner confirms Berber is also silent; a one-mod
isolation test is currently unavailable. A four-owner startup timeout remains
a hypothesis, not an established cause. Do not start an extra backend against a real game,
change client binaries/settings, disable unrelated mods or install into AoE4 as
a hidden workaround. Import/listening, native freeze reproduction, save/load, AI,
multiplayer and measured performance remain pending. No push/tag/publication.

Documentation-led correction: the 0.2.1 SGA omitted scar/garrison/garrison.scar.
0.2.2 now embeds the unmodified installed 0.1.13 helper, as the current guide
requires for adapted mods. Its complete import closure is empty. Real-helper
MessagePack tests cover session, pulse, direct clip and a bridge that becomes
available after start. This removes reliance on an externally supplied helper;
it does not claim to start the client-owned audio backend. Berber is treated as
unverified; the installed guide/API is the 0.2.2 contract.

Built: F:\aoe_4_temp\New_custom_civilization\aoe4-korea\release\Koreans-Garrison-0.2.2.zip

ZIP bytes: 145,864,393; SHA256 6175fcef8fffb0b6a59c1e02f3b4524b42dc14b84d36de591b760c42936ca94e.
SGA SHA256 c9db1bfd4532480359dab6aa13d835764d7cdff994619c17c24e96a0de24f163.
46 tests, 527 native tables, 10281 full member readbacks and ZIP/CRC/namespace checks passed.
Original art/audio unchanged; 0.2.1, 0.2.0 and 0.1.6 rollbacks verified.
This is build/package proof only. Shared audio startup and native freeze remain open.

Post-cleanup ZIP/packaged-SGA/rollback hashes passed. Retired 2,055,641,752 logical bytes of verified reproducible staging; native/editable inputs and recordings/weights remain protected.
