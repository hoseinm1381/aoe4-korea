# Korea 0.2.5 loading failure - 2026-11-04

Three confirmed new-build loading failures precede Korea script execution.
Game: 17.0.12260.0; Garrison: 0.1.15. The imported archive matches shipped 0.2.5 SHA256.
All dumps: 0xc0000005 read at RelicCardinal.exe+0x1c4adc4, RDX=0, attempted address 0x10.
All agent logs: provider_error / civilization_runtime / "declared resource pack must contain exactly its native Observer and Race parts".
Race admission occurs, but no civilization_resources_retained event follows. Sixteen observed stamp loads fail per session with the same owner-context error.
KoreaIndependent never registers and KOREA025_VOICE_CONTROLLER_DISABLED never prints. The voice controller has not run.
Earlier 0.2.4 sessions on 17.0.12182 successfully retained/mounted the same owner's resources before attribute acquisition.
The native service's part_count=6 also occurred in those earlier working loads; it is not by itself evidence of bad Korean mod.bin metadata.

Required client correction: requalify Garrison resource-part discovery/validation and mounting for 17.0.12260. Verify civilization_resources_retained, dispatcher registration, and the disabled-voice marker before retesting gameplay.
Do not patch native offsets, bypass the failed guard, strip metadata/art/audio, or rewrite Korean gameplay to conceal this failure.
No safe mod-side repair has been established. No new ZIP, game/client change, installation, publication or cleanup was performed.
Both 0.2.4 and 0.2.5 ZIPs remain byte-identical. The original random in-match crash remains unresolved.

Evidence: FINDINGS.json and Korea-025-loading-crash-evidence.zip. The bundle contains local game/agent logs and minidumps; it has not been sent to anyone.
