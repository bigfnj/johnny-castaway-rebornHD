# Original profile-walk references001-008

These are original-only technical references. No Cartoon pixels, artistic approval or production change is supplied by this folder. The eight source records preserve their complete original frame rows, including encoded uses, from `art/cartoon/walk-expansion-v1/reference/metadata.json`. That metadata and its source/extractor are pinned by exact file hash in `source-index.json` and `prepare.py`.

The source is the previously verified supplied-original XPM dump. All36 JOHNWALK XPM identities and the historical dump report's resource/engine identities are checked before any output is created. The commercial RESOURCE files and original executable were not reread or rerun. Original indices use the port dump palette and index0 transparency; original-executable color, compositing and timing remain unverified. Gray shadow pixels are part of the original raster and do not establish foot contact.

Each `NNN-original-native.png` retains the complete native canvas. Each `NNN-original-nearest8.png` is exact8-times pixel replication, with no smoothing, cropping, recoloring, body fitting or retouching. Its source record distinguishes raw XPM, decoded RGBA and PNG file identities.

| Frame | Native canvas | Runtime canvas at2x | Original top-row span, x end-exclusive | Suggested cap target at2x |
| --- | --- | --- | --- | --- |
|001|48x72|96x144|35..37|72,0.25|
|002|48x73|96x146|34..36|70,0.25|
|003|40x76|80x152|26..28|54,0.25|
|004|40x74|80x148|32..34|66,0.25|
|005|48x72|96x144|36..38|74,0.25|
|006|48x74|96x148|34..36|70,0.25|
|007|32x75|64x150|23..25|48,0.25|
|008|40x75|80x150|30..32|62,0.25|

X is the pixel-edge midpoint of the original first opaque row, doubled. Y0.25 is the existing authoring filter margin, not a point measured from the original. The suggested generated-art transform retains uniform scale0.1. These cap measurements do not replace original route positions or justify a common whole-body height, ground-bottom alignment or added head bob.

## First checkpoints

Start with003, then001. Both unflipped originals face screen-right; the native engine supplies horizontal flips for opposite travel.

003 shares000's40x76 original canvas and cap measurement, making it a useful identity bridge from the approved profile stand. In003, the visible arm hangs toward the shorts hem, the support shin is nearly upright, and its long foot points screen-right. A second bent leg/foot is tucked behind it, with a small foot silhouette protruding on the screen-left side above the support sole. Preserve that overlap and lift. Do not turn it into two flat parallel standing feet. This sprite also serves ordinary turning, so an isolated pose approval is not complete motion approval.

001 opens the stride widely. The screen-right foot reaches forward with toes visibly higher than its heel; the screen-left rear leg extends diagonally back, its heel raised and foot sloping toward the trailing toe. The visible arm swings behind the shorts. It is a useful second test of foot roll and the open gap between legs, complementing003's close overlap. Exact contact points and anatomical left/right identities have not been annotated.

Other useful visual checks:002 and006 bring the rear foot into a more vertical downward orientation while the forward foot reads flatter;004 and008 show the step opening from the overlap;005 resembles the opposite stride extreme but differs in limb overlap and arm placement;007 is a narrow passing silhouette with substantial leg occlusion. Do not infer anatomy solely from those screen halves or clone one half-cycle into the other. These are visual observations of original pixels, not replacement geometry or a calibrated gait model.

## Approved identity reference

The separately approved profile000 raw is `art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/000-profile-v1.png`, SHA256 `ae989a65335c10a24da3176ff6fd568dc4a2cb6fddda185002c60dcdae3d3a12`. Its accepted runtime member is `data/styles/cartoon/BMP/JOHNWALK.BMP/000.png`, SHA256 `9fef4cef56033a7cf35c36d96a839c42e7d7d23832acf0a34ebc6ff52e040e96`. Use it for the cap, scruffy beard, face, proportions, shorts and line style. Walking geometry comes from the original frame under review.000's waiting-ring approval does not approve new001-008 art.

## Reproduction and checks

Use the repository and Pillow12.3.0. The dump root contains `report.json` and `dump/BMP/JOHNWALK.BMP.000.xpm` through035. The existing local source is the maintenance worktree's `build/maintenance/original-pixel-reference`. Its path is intentionally supplied by the caller rather than embedded in portable records.

```text
python -B art/cartoon/walk-pilot/profile-walk-v1/reference/prepare.py --dump-root <original-dump-root> --output build/profile-reference-reproduction
python -B art/cartoon/walk-pilot/profile-walk-v1/reference/prepare.py --check --output art/cartoon/walk-pilot/profile-walk-v1/reference
python -B art/cartoon/walk-pilot/profile-walk-v1/reference/test_reference.py --phase smoke --dump-root <original-dump-root> --report build/profile-reference-smoke.json
python -B art/cartoon/walk-pilot/profile-walk-v1/reference/test_reference.py --phase regression --dump-root <original-dump-root> --report build/profile-reference-regression.json
```

Preparation requires a fresh output directory and never writes to the supplied dump. The two smoke checks passed before eight regression controls. Each control executes the actual helper in a fresh Python subprocess and requires its source-hash witness. Damaged native/enlarged pixels, original facts, cap registration, source provenance, frame scope, an existing output directory and changed raw XPM bytes each produced the intended named refusal. Disposable container hashes are rebound in semantic controls, so stale JSON hashes cannot mask missing pixel or geometry checks. `smoke.json` and `regression.json` retain exact outcomes. No native renderer or original-executable comparison is claimed by these authoring checks.
