# Korea 0.2.3 higher-quality dialogue

The owner approved the higher-fidelity listening comparison and additional size,
then requested this local rebuild. All 7,632 original Korean dialogue takes are
re-encoded directly from the protected 24 kHz mono FLOAT WAV masters as 24 kHz
Vorbis with SoundFile compression_level 0.35 (previously 16 kHz, 0.95).
Scripts, actors, seeds, directed takes, trim, normalization, fades and existing
headroom are retained. Four clips need additional decoded-peak headroom; the
approved three preview clips decode identically to the complete-bank outputs.
This reduces codec damage; it does not remove noise already present in synthesis.

Dialogue payload: 55,800,679 -> 111,710,069 bytes (+55,909,390). Total dialogue:
8,864.250458 seconds; 850,968,044 bytes if the complete bank were decoded at once
as mono float32. Playback uses individual clips; this is not measured game RAM.
All 7,632 encodes decode, have finite samples, non-silent RMS and peaks below
0.99. 32 profiles, 128 age banks and 50 squad routes are retained. The 827 stock
nonverbal efforts remain byte-identical. No new model downloads or synthesis.
Historical pronunciation remains researched approximation with expert review open.

The owner's accepted size increase is a narrow audio-quality exception to the
older 300 MB combined-media budget. Art remains byte-identical; 0.2.3 media must
stay below 400,000,000 bytes and the complete import ZIP below 600,000,000 bytes.
The audio payload is counted explicitly in update_023/AUDIO_AUDIT.json; final
compressed contribution and archive sizes are recorded after packaging.

Working 0.2.2 voice routing, matching Garrison 0.1.13 helper and speech-volume bus,
private Chinese speech suppression, five native starting sheep, models/player
colour, cavalry skins/animation bindings, Gapsa shield, research payments/book
UI/refunds and all gameplay source remain unchanged. The bank differs only in
content-addressed clip paths; reversing the path map recovers the exact 0.2.2
bank bytes, including durations, context aliases, age/gender and PBG mappings.

## Rebuild and evidence

Use the existing standalone source. Python 3.13 is required by the installed SDK.
Keep TEMP/TMP at F:/aoe_4_temp/Temp_aoe4/k20 for the build.

```text
python -B tools/release023.py
python -B tools/check023.py
python -B tools/build.py --replace-current
```

The CPU encoding recipe tools/quality023.py uses the existing qualified SoundFile/
NumPy/SciPy voice runtime, not SDK Python. `encode` resumes receipt checkpoints;
`audit` decodes every output; `promote` derives the current native manifest and
voice bank from the sealed accepted 0.2.2 baseline. Original generation receipts,
master index and 89 protected original encodes remain unchanged.

Current source/native scope proof: update_023/SCOPE_VERIFICATION.json.
Full encoding provenance: update_023/ENCODED_BANK.jsonl and PATH_MAP.json.
Accepted 0.2.2 ZIP is moved unchanged into archives/quality023-baseline/6175fcef8fff
only after the verified new ZIP is safely copied to release/.
Fresh native build, namespace/CRC, all-member SHA256 readback and ZIP inspection
remain required. Local codec probes are silent dummy-process tests and do not
attach to, install into or interrupt the owner's game.

## Random-crash investigation

The owner reports random single-player crashes during age-up, unit creation and
ordinary play, without save/load. The supplied current warnings.log belongs to
Chagatai; its crash cannot establish Korea's cause. Older Korea log candidates
and their limitations are inventoried in update_023/KOREA_LOG_INVENTORY.json.
Use the game-mode/tuning skills, official API evidence and AoE4 MCP. Do not
declare unrelated logs a Korea diagnosis or promise crash-free native behavior
from static checks. Final audit findings and open native gates are recorded in
update_023/CRASH_AUDIT.json. No arbitrary native/gameplay changes are justified
solely by a random crash without correlated Korea evidence.

No push, tag, publication, installation or other-civilization changes are included.

Final local ZIP: F:\aoe_4_temp\New_custom_civilization\aoe4-korea\release\Koreans-Garrison-0.2.3.zip

Bytes: 199,764,260 (+53,899,867 versus 0.2.2).
SHA256: e65c6b0c165bf5887d6e99d23fc4a1401f15023697a3fe719a4b0935a0274187.
SGA: 374,141,158 bytes; SHA256 112e59cc32f0937cc00d47b846c0673c8d07a8ae2479c9d110bb5c2a63359867.
Fresh native validation/build, namespace/CRC, 10,281 full readbacks, final ZIP CRC/hash and exact non-dialogue preservation passed.

Scoped cleanup removed 2,485,108,361 logical bytes of regenerable staging/native readback/decoded audit caches. Current and rollback ZIP hashes were verified afterward. All protected source, editable/native inputs, voice masters and model weights remain. See update_023/CLEANUP.json.
