# Korea 0.3.7

The 0.3.6 match screenshot shows the enlarged Stone Pagoda with pale ledges and courtyard. The installed match log confirms the 0.3.6 archive. The nine landmark albedos were encoded as linear BC3 (format 22). The current stock `unit/albedoTexture` exemplar decodes as sRGB BC1 (format 19) and carries the native `TSRI` marker. Treating the original paint values as linear light makes the game rendering brighter than the sRGB preview.

All nine opaque albedos now use the stock sRGB format, linear-light mip filtering, and the native marker. The Pagoda also has charcoal-green ledges, warm weathered stone, and a darker earth courtyard. The dynamic owner masks, UVs, geometry, lifecycle controllers, and other material slots retain their verified 0.3.6 values. The actual game view still needs a fresh match.

## Match exit and restart investigation

Windows recorded an `AppHangB1` for RelicCardinal 17.0.12260.0 at 12:33:27 on 2026-11-10. Windows event 1002 reports that the process stopped responding and was closed. The 12:29:18 game session logs `MPMatchSetup::RestartMatch` and rehosting at 12:33:00.806, followed by repeated game-mode discovery through 12:33:22. The existing paired Korea trace was active immediately before the request. The recorded path has no entry into Korea's voice-stop, lifecycle-cleanup, or UI-cleanup callbacks and no fatal SCAR stack. The WER bundle contains metadata and system readings without a thread dump. The earlier 0.3.5 log records a full application quit, but there is no matching 0.3.6 Quit Match failure trace. The Garrison client on this machine reports version 0.1.17.

This evidence locates the recorded hang in the restart path. It leaves the engine, Garrison, and other loaded content as unresolved owners. The color ZIP changes nine texture members only. A same-settings stock match and a Korean match through the same launcher, followed by a hang dump if one stalls, are needed to distinguish those owners.

The installed stock SCAR routes the game-over delegate through the scripted victory conditions, including surrender. It does not expose the native rehost sequence seen in the hang log. Seventeen targeted offline tests passed. A separate Lua harness exercised the actual Korea dispatcher, initialization, cleanup, UI, modifier removal and voice code for two successive mock matches and an English control. It verified that repeated game-over callbacks removed the rules, HUD, squad callbacks and active modifiers once per match, including shared and already-cancelled handles. The native engine and Garrison calls were mocked.

## Source

`tools/art037/srgb_landmarks.py` stages the exact texture contract and `tools/art037/build_overlay.py` composes it over the verified 0.3.6 archive. The edited Pagoda texture master is in `authoring/art037`. The other eight 0.3.6 masters remain the editable paint sources.

The ZIP is 211,015,661 bytes (-620,681 from 0.3.6). Garrison validated 543 native tables, and all 10,392 archive members passed readback. Nine albedos changed and 10,383 members matched 0.3.6. [Archive receipt](BUILD_VERIFICATION.json) · [Landmark readback](update_037/native-albedo-readback.json).
