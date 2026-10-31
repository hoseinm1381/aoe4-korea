# Korea research costs - 016 source follow-up, 2026-11-01

The owner reports two olive-oil cost rows instead of books and incorrect upgrade
deductions. This follow-up repairs the existing standalone Korea source. The
0.1.5 player ZIP remains unchanged; 0.1.6 is held source, with no cook, assembly,
package, installation or push. Keep the existing colour and cavalry repairs.

## Findings and corrections

The 91 research abilities contain 195 native variants. All 104 non-default
variants had zero `cost_to_player`, unlike their default variant and retained
research catalogue. Restore those variants to the unchanged intended prices.
The ram research's existing 700-gold price remains gold; Literature research
keeps its existing book prices, and foreign research still costs one allowance.
Research times, recharge times, requirements and effects remain unchanged.

These abilities have empty native action trees and execute through SCAR.
Disable `validate_actions` in every variant, matching the current official paid
SCAR abilities `kremlin_levy` and `hire_ronin_poi`. Their source member digests
and native flags are recorded in `update_016_research/changes.json`. Native
ability payment remains the only debit; the queued upgrade is still made free
by upgrade-targeted modifiers. No extra scripted charge was added.

An additive independent civilization also bundled a second stock
`resource_type_info/merc_byz` descriptor. This is a likely contributor to the
duplicate olive-oil UI and inconsistent resource identity. Exclude that exact,
hash-checked descriptor from the future build while retaining its editable file.
The root stays additive (`override_instances=false`). No installed stock file,
Byzantine descriptor or other civilization is edited. Native confirmation of
the duplicate-registration diagnosis remains pending.

Give Literature research explicit book-cost templates in the native tooltip
dictionary. The entire official dictionary is preserved verbatim; only uniquely
named Korean templates are appended and selected by Korean research abilities.
Their labels come from the native fee tables, with a separate foreign-choice
label. They do not enumerate the duplicate resource descriptors. Existing gold
research retains the native ability template. This introduces a narrow native
tooltip dictionary extension, superseding the older design statement that this
project contains no global-path XAML asset. Stock/default tooltip behavior stays
unchanged in the source. In-game lookup/composition still requires testing.

The payment ledger now falls back to its verified catalogue fee when the native
cost query omits a resource field, and refunds an executed payment if its actor
is already lost. Explicit zero values from the native query remain respected.
The return shape of `Player_GetAbilityBPCost` is not documented in ScarDoc;
missing-field tests are defensive stub scenarios, not evidence of its live shape.

## Validation and preservation

- 12 focused tests pass: all variant/catalogue prices, narrow native leaf diffs,
  unchanged native roundtrips after reversing allowed edits, exact stock XAML,
  book labels, fee/allowance settlement, duplicate callbacks, insufficient funds,
  failed queue, cancellation, actor loss and Observatory rebate.
- 10 applicable native colour/cavalry/hold tests pass; 5 barrage, 6 native-start
  and 2 player-schema tests pass. Total: 35 focused checks. These are not a full
  historical-suite or native-match pass.
- The historical art-only equality assertion now conflicts with this separately
  authorized research change. It was not edited or reported as passing against
  current gameplay. A new check proves that the actual pre-cost snapshot still
  matches its original source hashes, including exact CRLF reconstruction where
  validated by those hashes. The new cost check permits only the declared fee,
  action-validation and tooltip changes. Historical test code remains unchanged.
- All existing native art/audio inputs, editable masters, other source and the
  player ZIP match the pre-cost digests. The root, race, owner and mod identities
  remain unchanged. `VALIDATION.json` records results and current source hashes.

`tools/research016_ui.py` verifies or reproduces the maintained tooltip source
from the compact pinned official dictionary and current fee tables. The future
builder checks variant fees, action validation and exact labels after its build
hold. Use `--write` only for an intentional source regeneration. No cook runs.

Run the focused tests with Python 3.13 and `lupa==2.6` available:

```text
python -B -m unittest discover -s tests -p test_research_016.py -v
python -B tools/research016_ui.py
```

The source-only tests used a temporary dependency target on C:. No new E:/F:
cook/readback/staging caches were created. The known E: task-tools directory is
absent, F: task temp is empty, and `output/current` is absent. Retain compact
before fixtures, the pinned official UI input, sources and current/rollback ZIPs.

After the owner explicitly resumes builds: produce a new candidate, validate its
final member allowlist and independent identity, then test native book tooltips,
exact deductions, insufficient funds, foreign allowances, cancel/death refunds
and Observatory rebates alongside another Byzantine player. Recheck unit player
colours and cavalry movement/combat. Import, multiplayer, save/load, AI and live
performance remain separate gates. Do not replace the player's current ZIP now.
