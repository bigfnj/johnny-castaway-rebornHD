# Character inventory and handoff

The September16 inventory pass extracts and classifies original artwork across
the application. It does not generate new Cartoon assets or alter runtime code.
The source production ZIP remains
`4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`.

## Coverage and decisions

| Item | Result and next action |
|---|---|
| Complete source universe | 2,402 original image slots across127 resources:2,392 BMP frames and10 screens.2,401 map to app slots; SA_DEMO.BMP/000 is reference-only. |
| Confirmed pending Johnny | 1,002 runtime slots across76 resources:431 whole-body drawings,189 parts and382 composites. They contain968 distinct original RGBA/canvas images. Preserve duplicate slot identities and independent approval. |
| Accepted Johnny | All28 current Cartoon slots remain accepted and are available beside the original references. |
| Uncertain content | 84 app slots retain tiny actors, alternate identities or ambiguous fragments for contextual review. They are included in the outstanding-reference download. |
| Core walk remainder | Seven drawings:014,030-035.013 is a placeholder. C-to-D and water-exit scripts are separate review groups. |
| Mixed drawings | Johnny sometimes shares pixels with a rod, boat, other actor or scene. Keep those together when planning artwork; isolated prop batches cannot finish these images. |
| Next production recommendation | Start HOLIDAY000-003, then standalone props and vehicles. Defer mixed character/prop scenes. This is a workflow recommendation, not a measured time saving. |
| Lessons | The character playbook consolidates identity, gait, yaw, limb visibility, registration, source geometry, feet/contact, alpha, palette and approval/evidence lessons. Historical art records remain intact. |

Counts are image slots, not unique animations, outcomes or generation calls.
The diagnostic dump palette is not the original executable's calibrated color.
Gray source shadows are not anatomical foot landmarks. Visual classification is
a recorded review judgment; the84 uncertain cases remain visible rather than
being silently omitted.

## Deliverables

- [Complete inventory and reproduction instructions](../art/cartoon/character-inventory-v1/README.md).
- [Exact reference PNG archive](../art/cartoon/character-inventory-v1/reference-originals.zip).
- [Original extraction provenance](../art/cartoon/character-inventory-v1/source/README.md).
- [Static scene/draw associations](../art/cartoon/character-inventory-v1/scene-map/README.md).
- [Character playbook](cartoon-character-playbook.md).

The generated browser supports scope/type/resource/search filters, pagination,
full-image inspection, accepted Cartoon comparisons and JSON/ZIP downloads.
It starts with confirmed outstanding Johnny. It renders at most60 cards per
page and lazy-loads thumbnails; this is a bounded rendering policy, not a
measured memory or speed claim. It has no playback timers or persistent cache.
Native PNGs are preserved unmodified; thumbnails are display-only.

## Verification

Original extraction smoke preceded complete pixel regression. All2,453 files
in the historical dump matched its preserved manifest, and all2,402 PNGs matched
the original XPM RGBA semantics. The established36-frame JOHNWALK reference
also matched. Seven executed source negatives and a guard-removal proof are
retained under `source/verification/`.

Static scene mapping passed2 smoke tests, then8 regressions. Four isolated
guard-removal controls each produced the expected named failure.15,368 static
sprite draws are mapped conservatively:11,441 unique script-slot attributions,
3,908 multi-resource ambiguities and19 unresolved local loads. These are not
executed scene coverage. The earlier independent decoder comparison still
covers79 selected images; this pass does not expand that claim.

The combined inventory reproduced byte-for-byte after smoke. Nine isolated
damaged-input controls rejected stale source identity, missing resource review,
duplicate frame overrides, unknown frames, incomplete reviewed-page coverage,
missing port coverage, missing/duplicate ZIP members and a modified PNG. A
copied helper with only its PNG identity guard removed accepted the same corrupt
PNG; the original rejected it and restored positive input passed. Results are
under `art/cartoon/character-inventory-v1/verification/`.

Existing authoring smoke passed before regression: metadata2+60 tests and
production catalog3+63 tests. Metadata regeneration changes only the master
lessons document fingerprint. The runtime archive and all accepted art are
unchanged.

The actual localhost browser was exercised through its controls. All seven
scope totals agreed with the inventory; the JOHNWALK filter returned exactly
014/030/031/032/033/034/035; next/previous pagination, empty-search recovery,
accepted comparisons and image inspection worked.28 accepted cards exposed56
comparison images. The seasonal filter exposed exactly HOLIDAY000-003.
Screenshots of the worklist and comparison dialog were visually inspected.
No warning/error entries were returned by the browser log query during those
checks. This is a scoped interaction observation, not a general runtime audit.

An independent code review found and fixed two new viewer issues before
delivery: accepted non-Johnny scenery was omitted from the Other art filter,
and published notes pointed outside the exported directory. The revised filter
retains all1,288 non-Johnny/placeholder source slots, and published notes use
local review links or maintained repository document URLs.

The existing engine/platform audit backlog remains open. This inventory does
not claim to repair or retest those unrelated runtime findings.
