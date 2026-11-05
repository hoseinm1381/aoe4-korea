# Korea 0.2.5 voice-controller isolation

Owner authorized disabling the voice controller while retaining every voice file and the exact 0.2.4 ZIP.
The only packaged script edit is a false local switch and early return in KoreaVoice_Start.
Start and restore cannot register voice polling or squad events, begin an audio session or submit cues.
Imports, Garrison helper, bank, recordings, native speech suppression, gameplay, tuning, visuals and 0.2.4 tracing remain.
Custom unit speech is expected to be silent. Existing non-speech game sounds are retained.
This is a crash-isolation candidate, not a proven crash fix.

Import 0.2.5, enable Korea, and start a fresh single-player Standard / Tuning Pack None match.
First repeat the same map/opponents/speed/cheats as a failure and continue beyond its previous duration.
The log must contain KOREA025_VOICE_CONTROLLER_DISABLED and must not contain KOREA_VOICE_STARTED or KOREA_VOICE_QUEUED.
Preserve warnings.log/scarlog and a matching dump immediately after a crash/freeze, before relaunch.
Native import, crash outcome, repeated matches, restore and multiplayer remain unqualified.
