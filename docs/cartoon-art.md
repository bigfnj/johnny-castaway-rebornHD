# Cartoon art production

The [seasonal and shoreline delivery](cartoon-seasonal-verification.md) brings
the current pack to 47 accepted assets, including four holiday decorations and
the approved larger island with clean offshore waves. Earlier family counts
below describe their individual delivery checkpoints.

The [production plan](cartoon-production-plan.md) tracks the completed
[slot catalog](knowledge-base/cartoon-production-catalog.md) and successive
walking families. The current [profile-walk batch](cartoon-profile-walk-plan.md)
covers 001-008 with separate pose, motion and scene reviews.

Read [image authoring lessons](art-style-learnings.md) before starting another
style or animation family. It preserves the Cartoon pilot's generation,
registration, transparency and review experience with links to exact records.
The [Calm focus revision lessons](art-style-learnings-calm-focus.md) add expression
selection, original-pose comparisons, narrowly scoped toe edits and actual
engine review. The six front-oblique walking sprites have a
[portable export recipe and approval](../art/cartoon/walk-pilot/calm-focus-runtime-v1/README.md).
The accepted [rear walking family](../art/cartoon/walk-expansion-v1/README.md)
adds six poses with its own [continuity and fit lessons](art-style-learnings-rear-walk.md).
The [rear arrival pose](../art/cartoon/arrival-pilot-v1/README.md) adds standing
frame 018 and [arrival lessons](art-style-learnings-arrival.md) about contact,
registration and preserving the real transition.
The [front walk refresh](../art/cartoon/walk-pilot/front-refresh-v1/README.md)
is an approved 028/029 replacement with its own
[hip connection and occlusion lessons](art-style-learnings-front-refresh.md).
Its standalone motion and native island scene are approved. The other 26 assets
keep their earlier approvals through explicit selected inheritance; the original
pilot's drawings and pose observations remain preserved as history.
The [standing family](../art/cartoon/walk-pilot/front-arrival-v1/README.md) adds
000/015/016/017 alongside018, covering all eight standing directions and bringing
the pack to 32 assets. Native arrival and direction-ring approvals are scoped
separately from unreviewed story interactions. The
[profile family](../art/cartoon/walk-pilot/profile-walk-v1/README.md) adds 001-008
together, bringing the pack to 40 assets. Both native directions, standing
connections and ordinary 003 departures were approved with "Yes, keep this profile
walk". Ordinary 009/010/012 and unreviewed story interactions remain later work.
Each family retains its actual human review; aggregate pack approvals explicitly
inherit earlier reviewed assets rather than silently replacing their provenance.

Cartoon is an additional art pack. The original resources and HD PNGs remain in
`assets/scrantic_data.zip`; accepted Cartoon PNGs live under
`data/styles/cartoon/`. Python is an offline authoring tool, never a dependency
of the application or screensaver.

The shipped source inventory has 2,391 sprite slots in 116 BMP resources and 10
screens. There are 2,131 distinct sprite PNG byte sequences. Identical source
frames can share an approved drawing, but every runtime slot keeps its original
path. Some frames are transparent placeholders. An inventory count is a coverage
measure, not an estimate of how many character drawings are needed.

## Runtime contract

The style manifest is `data/styles/cartoon/manifest.json`:

```json
{"id":"cartoon","scale":2,"alpha":"straight","coverage":"partial"}
```

`coverage` is `partial` for a scoped preview or `complete` for all source slots.
Use paths matching the HD layout, for example:

```text
data/styles/cartoon/BMP/JOHNWALK.BMP/000.png
data/styles/cartoon/SCR/OCEAN00.SCR.png
```

PNG dimensions normally equal the original logical width and height multiplied
by two. Four [named island footprints](cartoon-footprint-contract.md) permit
explicit extra padding for Cartoon BACKGRND000,003-005,006-008 and009-011 while
preserving the original logical anchors. Other frames keep their original canvas and padding.
The engine uses the original script coordinates. Registered padded sprites flip
around the original logical canvas; legacy sprites flip using the loaded width. Do not
trim, center, or independently fit the character into each frame. Foot placement,
hand/prop contacts, and the connections between island pieces need visual review
at the authored positions. Those landmarks are authoring references, not new
runtime anchor metadata.

Sprite PNGs require an alpha channel. The validator accepts portable 8-bit RGBA
or grayscale+alpha sprites; opaque screens may also use RGB. PNGs must be
non-interlaced. Transparent screens are rejected because the engine treats screens
as opaque. New Cartoon art uses straight alpha and may contain opaque magenta;
it does not depend on the HD pack's legacy color key.

Animated waves need a clean background on each update so partially transparent
pixels do not accumulate and transparent pixels reveal the island again. When
an active tide has a Cartoon wave replacement, the engine restores the wave
area and composes the current wave families in their last-update order. A mixed
wave pack therefore also recomposes its HD fallback families, which can change
edges that the legacy renderer retained from older frames. HD selection and
Cartoon packs without active wave replacements keep legacy wave rendering.

Author complete active wave groups together: frames 003-011 for high tide and
030-041 for low tide. Review family overlaps, island offsets and both tides in
motion. A partially completed wave group is useful for diagnosis, but should
not be the production visual review target.

## Reference export

Use Python 3.9 or later, with only its standard library. Run the following from
the repository root:

```text
python -B tools/art_inventory.py --archive assets/scrantic_data.zip --output build/art-work/catalog.json
python -B tools/art_inventory.py --archive assets/scrantic_data.zip --export build/art-work/reference --resource JOHNWALK.BMP --resource BACKGRND.BMP --resource OCEAN00.SCR
```

Repeat `--resource` for another exact BMP or SCR name. Omit it to select every
asset. Export copies the bundled HD PNG bytes without resizing or redrawing, and
refuses to overwrite a reference file whose contents have changed. The catalog
records original dimensions, source hashes, and exact-byte aliases.
These HD proxies are distinct from supplied-original pixels. Use the
[original-first review catalog](knowledge-base/cartoon-art-metadata.md) for
original frame identities, source observations and their evidence limits.

Keep references, candidates, and accepted staging files in ignored
`build/art-work/`. Final shipping PNGs belong in the archive, so they do not need
a second tracked loose-file tree. Keep the approved style guide, prompt recipes,
reference hashes and acceptance ledger in small tracked authoring records.

## Generating and reviewing art

Use the built-in imagegen tool. Inspect local reference images before using them
as edit targets. Keep the approved character sheet and style reference fixed
across calls; each frame also receives its original pose/canvas reference. An
accepted adjacent frame can help continuity, but should not replace the canonical
character reference. Record the actual prompt and available tool metadata. Do not
claim a seed or model identifier that the tool did not return.

Generate one runtime asset or targeted revision per call. Contact sheets are
reference and review material; a generated grid is not assumed to preserve frame
count, order or registration. Save candidate outputs separately. Technical export
may enforce an approved size and placement, but an artistic correction goes back
through imagegen. The inventory and packaging tools copy image bytes unchanged;
recorded technical export recipes handle approved scaling and placement.

The useful review points are the initial character/island direction, the first
short motion loop, the playable pilot, and each completed scene family. Check
identity, outline thickness, clothing, frame-to-frame movement, and contact with
objects at actual playback scale and timing. A correct PNG header cannot establish
that Johnny looks consistent or that a joke still reads.

The first full walking/island slice can cover `JOHNWALK.BMP` (36),
`BACKGRND.BMP` (42), and one fixed ocean screen. That is 79 slots before any
additional scene resources. A smaller initial motion test should declare its
smaller scope explicitly. The selected scene's ADS/TTM loads must be checked:
`STAND.ADS` references `MJAMBWLK.TTM` and `MJTELE.TTM`, so its name alone does
not establish the required sprite set. Island backgrounds/clouds are randomized;
preview runs need a controlled state and verified asset selection. Record the
platform with a seed: the same seed can select different ocean or cloud assets
on Windows and Linux.

PNG replacement also leaves TTM drawing primitives and original animation timing
in place. Inspect palette-drawn effects in the pilot. A redraw does not add
in-between frames or produce a different animation cadence.

## Acceptance ledger and packaging

The authoring ledger is separate from the small runtime manifest. For example,
`art/cartoon/pack.json` can declare a one-frame preview:

```json
{
  "schema_version": 1,
  "runtime": {
    "id": "cartoon",
    "scale": 2,
    "alpha": "straight",
    "coverage": "partial"
  },
  "required_resources": [],
  "required_assets": ["BMP/JOHNWALK.BMP/000.png"],
  "assets": [{
    "path": "BMP/JOHNWALK.BMP/000.png",
    "source_sha256": "replace with the source_sha256 from the catalog",
    "sha256": "replace with the accepted PNG SHA-256",
    "alpha": "transparent",
    "recipe": "approved-character-v1",
    "reference_sha256": [],
    "review": "record the actual review outcome"
  }]
}
```

Replace the example hash strings with lowercase 64-character SHA-256 values.
Per-asset `alpha` is explicitly `opaque`, `transparent`, or `blank`; the validator
checks that classification against decoded pixels. `transparent` requires some
visible pixels and some alpha below 255. `blank` means all alpha values are zero.
Screens must be `opaque`. Provenance fields such as `recipe` and `review` are
retained in the author ledger and are not interpreted as runtime settings.

`required_resources` expands entire resource groups; `required_assets` lists
individual paths. A partial pack must satisfy its declared nonempty scope.
Complete coverage requires every source BMP/SCR slot, including placeholders.
Each accepted file must be listed once and match its recorded hash. Unrecorded
PNGs in the accepted directory are rejected to catch stale or misplaced files.

Put files beneath the accepted directory using their relative runtime paths,
then validate and build a separate candidate:

```text
python -B tools/art_pack.py validate --archive assets/scrantic_data.zip --ledger art/cartoon/pack.json --accepted build/art-work/accepted
python -B tools/art_pack.py build --archive assets/scrantic_data.zip --ledger art/cartoon/pack.json --accepted build/art-work/accepted --output build/art-work/cartoon-candidate.zip
```

The builder refuses to overwrite the input archive or an existing candidate. It
replaces only `data/styles/cartoon/` when updating an existing style. Every other
member is preserved and its uncompressed content hash is verified after packing.
Accepted PNG bytes are verified too. Duplicate ZIP member names, unsupported or
corrupt PNGs, wrong sizes, missing coverage and alpha mismatches produce a named
failure. A partial pack is reported as `partial` on every successful validation.

Style entries use sorted names, fixed timestamps, and fixed compression settings.
Repeated builds with the same Python/zlib toolchain and inputs are byte-identical;
pin that toolchain when exact archive-byte reproducibility matters. Preserving
original member contents does not promise identical compressed streams across
different compression implementations. Re-running a generation prompt is also
not deterministic: accepted PNG bytes and their hashes are the durable result.

Use the candidate in a separate run directory for actual playback and native
screensaver checks. Compare old members, run existing regression checks, and review
the intended scenes before adopting it as the production archive. A scoped preview
must remain clearly identified until its missing artwork is completed.

## Refreshing runtime artwork

After adopting an approved archive in `assets/scrantic_data.zip`, run the normal
native build so `jc_runtime_data` refreshes the archive beside the executable:

```text
cmake --build build --config Release
```

For an explicit target build, use:

```text
cmake --build build --config Release --target jc_runtime_data
```

The native executable targets also depend on `jc_runtime_data`, so building
only `jc_reborn` or `jc_reborn_scr` refreshes the archive even when no link step
is needed. CMake 3.19 or newer is required. The full `gate.ps1` uses the normal build. Web
builds declare the archive as an input and regenerate their preload data when
it changes.

## Tool checks

```text
python -B -m unittest discover -s tests -p test_art_tools.py -v
```

These tests include deliberately broken dimensions, coverage and duplicate paths.
Each CLI mutation must produce exactly one failure naming the affected asset.
Controls cover opaque magenta, binary and partial alpha, all PNG row filters and
supported color types, unchanged legacy member bytes, and repeatable packaging.
