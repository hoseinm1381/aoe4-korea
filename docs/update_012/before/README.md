# Korea — independent Garrison civilization

Local **0.1.1** candidate from accepted combined Garrison 1.1.0, source
`d58326f447b6444332e9a15c42c7496d57fb26be`. Nothing is committed, pushed,
tagged, published or installed by this preparation. The previous package was tested by the owner; this update requires the focused native retest below.

Players use the one ZIP in `release/`: **Korea-Garrison-0.1.1.zip**.
Import through Garrison 0.1.9+, enable Korea, and select Korea directly with
native Standard and Tuning Pack None. Use a human player and standard Dark Age
army/resources. Disable the old combined pack while testing.

Developers use this whole repository. Gameplay, editable art/rigs/textures,
available audio, recipes and accepted native rebuild inputs live together as
ordinary files. There are no separate art/sound downloads or source ZIP packs.

- [Developer workflow](docs/DEVELOPMENT.md)
- [Design and migration boundaries](docs/DESIGN.md)
- [Player test instructions](START-HERE.md)
- [Release policy](RELEASES.md)
- [Native package verification](docs/BUILD_VERIFICATION.json)

Start with `START_DEVELOPMENT.cmd`. For a local rebuild:

```text
python -B tools/inputs.py verify
python -B tools/build.py --replace-current
```

Requires Python 3.13 and installed Garrison 0.1.8 authoring/core plus AoE4 Content
Editor. The starter checks tools; it never downloads, installs or publishes.
Korean custom models remain deferred. Credits: **hosein81 and chilly5**.

## Local verification

The current repository-contained build and complete archive/ZIP readback passed.
Thirteen source regressions and SCAR static validation passed. See
[verification](docs/BUILD_VERIFICATION.json), [source checks](docs/SOURCE_TESTS.json),
[player-schema review](docs/PLAYER_SCHEMA_REVIEW.json) and
[size measurements](docs/SIZE_REPORT.json). Test the native checklist in
[docs/NATIVE_TEST_CHECKLIST.md](docs/NATIVE_TEST_CHECKLIST.md) before acceptance.
