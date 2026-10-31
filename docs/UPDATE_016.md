# Korea research payment/UI repair - source only, 2026-11-01

The owner also reported duplicate olive-oil costs and incorrect research charges.
The source now corrects 104 free non-default ability variants, gives Korean
research book-cost tooltips and repairs refund handling. Read
[UPDATE_016_RESEARCH.md](UPDATE_016_RESEARCH.md) and its validation receipts.
The colour/cavalry repair is preserved. The build hold remains; the current player
ZIP is still 0.1.5. Native payment, tooltip and appearance acceptance is pending.
Earlier source-preservation statements apply to their original art-only phase.

---

# Korea colour and cavalry repair - source only, 2026-10-31

The owner reports that 0.1.5 runs but its units are white and non-Scout cavalry
does not animate. Those two native acceptance gates failed. The current source
contains the 016 repair; the player ZIP remains the byte-identical 0.1.5 ZIP.
The owner explicitly prohibits building the final ZIP while playing. project.json
now holds the build, before staging, native assembly or package replacement.

## Diagnosis and correction

The Korean atlas preserved stock skin/hair masks but erased stock owner-colour
red inside the original-UV region. Its small authored red strip was effectively
unused by sampled body geometry. Restore exact donor owner masks into the 0.74-U
atlas region, retaining Korean skin/hair channels and new authored strips. Stock
mask alpha is zero; the previous authored masks had full-white alpha. Restore
native zero alpha for bodies, equipment and Hwacha. The alpha mismatch is proven;
its precise rendering effect needs native testing and is not claimed in isolation.

The previous cavalry SKLN described standalone humans (73 bones) or horses (86),
while the real animator owns the combined 127-bone horse/rider skeleton. Riders
also named their skin root metarig_root, absent from that animator, and horse and
rider both named their merged mesh unit_mesh and material korean unified atlas.
Use exact current Chinese combined donor SKLN partitions and bind records for
16 Horseman, Lancer and mounted Hwarang body/mount resources. Every skin name now
maps to the combined owner. Native independent skin roots (e.g. stirrups) retain
their original donor parent layout. One gaia_props entry absent from the smaller
donor palette retains its existing bind; the complete animated owner has it.
Use distinct asset-specific mesh, LOD and material names for all 72 unit resources.

Every native vertex/index buffer remains byte-identical. Positions, UVs, weights,
LODs, albedo, geometry detail, Scout/infantry animation records, animation clips,
graphs, tables, SCAR, identity, voices and original editable masters are preserved.
The active colour sources are authoring/art016/patterns and
source/art016/material-overrides.json; original art013/014 masters remain intact.

## Evidence and limits

- 11 native regressions cover actual old failures, all 72 body/mount resources,
  16 combined cavalry contracts and 98 bound body/equipment/Hwacha mask streams.
- New masks retain BC3 compression and complete independent-channel mip chains.
  All 98 native masks decode and compare with source within mean error 2/255.
- MASK_READBACK.json records UV-centroid area samples. Examples: Spearman
  0.0 -> 13.4%, Villager 0.0 -> 23.6%, Gapsa 0.0 -> 24.6%, Horseman 0.0 -> 13.5%,
  Lancer 0.0 -> 18.2% of full LOD1 surface area. These are bounded offline samples,
  not visible-screen percentages. Atlas red coverage is substantially broader.
- player-colour-review.png is an illustrative source-atlas red/blue tint review,
  not an engine rendering or exact engine shader simulation.
- Historical 014/015 native tests use the real before-016 snapshot for their old
  release contracts; current 016 tests independently qualify intentional changes.
- 39 applicable tests passed across separate runs: 24 historical update, 4
  other current-source and 11 focused native/guard/preservation checks. The 11
  unchanged Lua tests were not rerun because lupa was removed in earlier cleanup;
  every SCAR byte is preserved. See VALIDATION.json and source-checks016.log.
- All 1,275 native and 1,904 editable inputs verified. The maintained recipe
  reproduced all 293 applied native files byte-for-byte in C: scratch only.
- No Content Editor cook, civilization assembly, final ZIP, installation, live
  game manipulation, Git push, native gameplay/performance or multiplayer claim.

## Reproduce without a final build

With configured Python 3.13 and the installed Garrison SDK, run
`python -B tools/art016/verify.py` and `python -B tools/inputs.py verify`.
Mask readback uses a bounded C: temporary diagnostics directory. For source
regeneration, set KOREA_ART016_STAGE to an owned scratch folder; run
`python -B tools/art016/repair.py prepare`, use Pillow-enabled Python for
`tools/art016/masks.py`, then `python -B tools/art016/repair.py stage`.
This regenerates native inputs from preserved 015 data; it never builds an SGA
or ZIP. Do not rerun historical 014 recipes as the current colour authority.

Building remains held until the owner explicitly resumes it. At that point,
set the next version/update policy and final baseline from 015, qualify exact
archive changes, then separately test at least two player colours and cavalry
idle/walk/run/charge/melee/ranged/death transitions in a fresh native match.
