# Current 0.1.2 retest

Follow START-HERE.md and docs/UPDATE_012.md. Record each result explicitly.

## Earlier broader validation checklist

# Korea native acceptance checklist

Current package: `Korea-Garrison-0.1.0-trial.1.zip`. These checks are pending; do not mark
them passed from source tests or a successful build. Nothing was installed.

1. Close AoE4, import/update this ZIP through Garrison 0.1.9+, enable it, and
   disable the old combined pack. Launch a fresh process.
2. Select Korea directly beside stock civilizations, native Standard,
   Tuning Pack None, a human player, standard starting army/resources and Dark Age.
   Start with a stock opponent. Check dropdown/flag/loading artwork and match load.
3. Check capital, starting units/resources, all-age construction/production,
   technology/landmark progression and native Codex. No chooser or conversion
   should be needed, and no second resource grant or starter spawn should occur.
4. Check Literature display/income/storage, both starting research allowances, first free Scholar, Seowon menus, foreign technologies, archer/horseman transformations, Hwacha barrage, landmarks and naval units.
5. End the match and start another in the same process. Check cleanup, stock
   opponents, then separately test all three independent civilizations together.
6. Save/load, custom AI, Nomad, later-age starts, multiplayer and performance
   each require their own qualification. Record exact settings and logs.

Native donor civilization startup StateTrees are deliberately absent from the
independent carrier; the maintained dispatcher owns the custom lifecycle. Check
passives and native dependencies during the gameplay comparison. No inherited
stock-civilization behavior is assumed proven by the neutral carrier.

Capture warnings.log and Garrison native events before the next launch if a
package fails. Preserve this ZIP and its SHA-256 from BUILD_VERIFICATION.json.
No push, tag, GitHub release publication or installation is authorized here.
