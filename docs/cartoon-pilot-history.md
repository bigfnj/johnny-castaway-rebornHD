# Preserving the Cartoon pilot when replacing artwork

The original-first pilot catalog covers the same 21 original slots throughout
production. Its stored original pixels, recipe transforms, raw image hashes and
human decisions belong to those historical drawings. Replacing a runtime PNG
must not make an older visual approval appear to approve that replacement.

The full production catalog remains the authority for all active slots. It
resolves selected-subset inheritance through accepted records, preserves each
row's actual review origin and validates the production PNG and recipe hashes.
The pilot catalog uses that same inheritance resolver when explicitly moved to
history mode.

## Replacement declaration

When a replacement is human-approved and promoted, add `pilot_history` to
`art/cartoon/pack.json`. Keep the earlier acceptance and its raw bytes unchanged.
This illustrative declaration replaces only 024; a real integration must list
every pilot slot whose accepted image, recipe or review origin changes:

```json
{
  "pilot_history": {
    "acceptance_record": "art/cartoon/walk-pilot/calm-focus-runtime-v1/production-acceptance.json",
    "sha256": "ce7f3832982bcfbef13f9ce6dc06c1f60ce774b89aca088247442040fd767a0c",
    "replaced_assets": ["BMP/JOHNWALK.BMP/024.png"]
  }
}
```

The pack's normal `acceptance_record` points to the new aggregate acceptance.
That record inherits the selected unchanged assets and declares the newly
accepted complement using the existing production-catalog format. Its changed
pack rows point to the actual new review and recipe. An unchanged pixel image
with a new recipe or human-review origin is also an explicit replacement of the
historical mapping. An empty replacement list is valid only when every pilot
mapping is retained.

The history declaration pins the complete original acceptance independently of
selected inheritance. It therefore remains meaningful if every original pilot
asset is eventually replaced. It does not broaden the pilot's 21-slot original
reference import, waive an acceptance, or promote pending artwork.

## Catalog output

Without the declaration, the existing schema v1 behavior and production checks
continue unchanged. With it, schema v2 preserves each `original` and historical
`variant`, then adds a separate `production` mapping containing status, PNG hash,
canvas, current ZIP member, recipe and originating acceptance. A replaced
historical variant has `member: null`: its old hash must not be presented as the
bytes currently at that ZIP path. Its raw source bundle and recipe remain linked.

The previous `current_human_review` becomes `historical_pilot_human_review`,
and per-slot review observation IDs become `historical_user_review_ids`.
`historical_pilot_acceptance_record` points to the unchanged pilot decision;
`current_acceptance_record` points to the active aggregate. The new per-slot
production records link the review that actually approves each current drawing.
Original reference facts and older deviations never become measurements of the
replacement artwork.

In schema2, retained foot-clearance observations use
`historical_pilot_disposition` and
`historical_pilot_variant_independently_remeasured`; the limits explicitly say
their acceptance belongs to the historical Calm focus pilot. Schema1 wording and
keys are preserved for the existing production mapping.

Both the historical approval versus recipe checks and the current production
approval, recipe, canvas and PNG checks must pass. Immutable approval-chain
hashes use exact file bytes, including newlines; preserve new art records with
the same Git `-text` policy as the other immutable art families.

## Verification

Run `python tests/test_art_pilot_history.py --phase smoke`, then
`python tests/test_art_pilot_history.py --phase regression --mutation-check`.
Historical tests use the [frozen accepted runtime fixture](../tests/fixtures/cartoon-pilot-v1.md),
while live catalog reproduction checks actual production. Replacement fixtures
substitute existing, equal-canvas PNGs only in test I/O; they never edit or promote
production artwork. They cover an approved replacement,
selected nested inheritance, unchanged original facts and prior evidence,
undeclared replacements, pending approvals, stale hashes and wrong canvases.
An exercised future028-promotion control runs both complete historical suites
against a simulated live schema2 pack and regenerated metadata. Historical tests
therefore stay useful after the current production artwork changes.

Also run the original pilot and full production catalog smoke/regression suites
and regenerate their maintained outputs. New replacement reviews still require
human inspection of the complete motion and actual island scene.
