# Korea 0.1.6 ZIP built - 2026-11-01

The duplicate Gapsa spear is fixed by restoring its left-hand shield. The verified
0.1.6 ZIP also includes the pending colour, cavalry and research payment/UI repairs.
Read [the release handoff](docs/UPDATE_016_RELEASE.md) and `docs/update_016_build`.
The owner explicitly resumed building, superseding the historical hold below for
this release. Native fresh-match acceptance remains pending. No push or install.

---

# Korea research payment/UI repair - source only, 2026-11-01

The owner also reported duplicate olive-oil costs and incorrect research charges.
The source now corrects 104 free non-default ability variants, gives Korean
research book-cost tooltips and repairs refund handling. Read
[UPDATE_016_RESEARCH.md](docs/UPDATE_016_RESEARCH.md) and its validation receipts.
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

# Koreans — independent Garrison civilization

Current local repair candidate: **0.1.5**, `release/Koreans-Garrison-0.1.5.zip`.
Corrects Korean body material keys, lifecycle alternatives on custom rigid
models, and the unavailable Hwacha cleanup API. Existing editable geometry,
textures, rigs, voices, gameplay and stable identity are preserved.
Read [the repair handoff](docs/UPDATE_015.md) and [player instructions](START-HERE.md).
Fresh native appearance/animation and barrage retesting remain pending.
No new commit, push, tag, publication or installation is authorized.

0.1.2 populates native Unique Units/Technologies, explains the actual civilization
mechanics, corrects research ages and spaces tech-tree icons at the native pitch.
Civilization labels are plural and the selector uses the existing flag fallback.
World gameplay, stable IDs and HD loading/art resources are preserved. Berber
audio is smaller; existing compact Vietnamese voices retain their current codec.

Players need the single ZIP. Follow [the test instructions](START-HERE.md).
Developers use this complete repository: editable art/rigs/textures, original
audio, native inputs, typed whole-file attribute source and recipes live here.
There are no separate required source/art/sound downloads.

- [0.1.2 changes and evidence](docs/UPDATE_012.md)
- [Native package verification](docs/BUILD_VERIFICATION.json)
- [Source regressions](docs/SOURCE_TESTS.json)
- [Size measurements](docs/SIZE_REPORT.json)
- [Developer workflow](docs/DEVELOPMENT.md)
- [Design boundaries](docs/DESIGN.md)
- [Release policy](RELEASES.md)

Start with `START_DEVELOPMENT.cmd`. Local rebuild with Python 3.13 and the
installed Garrison 0.1.8 authoring/core plus Content Editor:

```text
python -B tools/inputs.py verify
python -B tools/build.py --replace-current
```

Native staging uses one temporary `garrison-independent-builds/<owner>/current`
directory per civilization to avoid copying thousands of tiny files twice on
F: exFAT. Failed diagnostics are protected. Verified staging may be cleaned only
after checking the final ZIP and retained inputs. The current source workspace
does not change. Current stock prerequisite evidence is retained under `source/`.

The tested 0.1.1 ZIP remains under `archives/tested_0.1.1/`; its exact native Codex
is a hashed regression fixture. Source/UI snapshots are in `docs/update_012/before/`.
The earlier standalone split came from accepted combined Garrison 1.1.0 commit
`d58326f447b6444332e9a15c42c7496d57fb26be`. Normal/combined sources are preserved.

Credits: **hosein81 and chilly5**.

Korean models are now bound through private native visual resources. Native appearance, animation, lifecycle and performance acceptance remain pending.

After verifying a build, preview staging retirement with `python tools/cleanup_staging.py`; apply it with `--apply`. The tool preserves player ZIPs, source, masters, native inputs and receipts.
