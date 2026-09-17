# Bounded shoreline repair preview

This compares the same V5 seasonal props over the earlier Cartoon shore and a
three-sprite shoreline prototype. It does not change the production package.
The cases are no decoration, clovers, pumpkin and tree, all at day/high tide,
offset(0,0), no raft, seed11,1280x960, with the existing same-heading A wait.
New Year is retained in both private ZIPs but is outside these four stills.

The driver adapts `art/cartoon/seasonal-v1/native/driver.c` by adding observation
of every actual BACKGRND draw and stage markers. It keeps native initialization
and `adsPlayWalk(0,0,0,0)` unchanged. There is no forced wave frame or altered
engine timing. The runner imports the hash-pinned earlier `capture.py` for the
compiler/source selection, holiday checks and preserved PPM/PNG codec; it does
not copy those historical helpers into another evidence bundle.

The production-only phase probe was executed first. Actual redraw order was
006,006,009,006,009,003,009,003,007, leaving003/007/009. The repeated neighbors
are expected from true-alpha wave restoration. `islandInit()` leaves the wave
timer at8; the finite A wait uses6 ticks and does not advance it. Its PNG exactly
matches the earlier seasonal no-holiday baseline. This proves the chosen
snapshot, not the complete animation cycle. Detailed original/repair ground
shape judgment remains a visual review.

## Prepare and run

Use the pinned original production ZIP4c8085be... and the preserved V5 recipe.
The preparation checks all four prop PNGs against their export report, retains
all2594 production payloads, then optionally changes only003/007/009. All private
input paths must be inside this checkout. Use fresh output directories.

```text
python -B art/cartoon/shoreline-repair-v1/native/prepare.py --output build/shoreline-repair-v1/props-v5
python -B art/cartoon/shoreline-repair-v1/native/prepare.py --wave003 <selected-003.png> --wave007 <selected-007.png> --wave009 <selected-009.png> --output build/shoreline-repair-v1/selected-v1
python -B art/cartoon/shoreline-repair-v1/native/run.py --baseline build/shoreline-repair-v1/selected-v1/baseline.zip --candidate build/shoreline-repair-v1/selected-v1/candidate.zip --output build/shoreline-repair-v1/native-v1
```

No candidate captures should run before the three wave exports are selected.
For a phase observation alone, the executed command was:

```text
python -B art/cartoon/shoreline-repair-v1/native/run.py --baseline assets/scrantic_data.zip --phase-probe --output build/shoreline-repair-v1/phase-probe-v1
```

Docker uses the existing pinned Linux image, network disabled, read-only source
mount, one fresh writable output mount, `--init` and Xvfb. The unique container
is removed and absence verified even on failure. No workstation window opens.

Each package gets four smoke captures before any fresh-process repeats. The
same executable renders both packages. Checks require exact repeats, observed
003/007/009 with fixed canvases/origins, actual selected PNG load paths, and
every cross-package changed scene pixel inside those wave canvases. Within each
package, holiday differences must stay inside its original decoration canvas.
Two actual-input controls damage final wave identity and an outside-canvas
pixel; both must fail by name, then the unchanged positive inputs must pass.

Source/compiler/archive/driver hashes and commands are retained with the actual
logs. Reports distinguish observed frame identities from visual approval.
Only these three phases are repaired in the prototype; longer animation, other
phases, tides, offsets, time-of-day variants and story execution remain outside
this still-preview scope.

## Executed first prototype

The production-only observation compiled without warnings and matched the
historical seasonal baseline PNG exactly. New helper smoke checks passed2,
then regression passed9 checks (one valid replacement control and8 named
damaged-input rejections). No rendering was used for those temporary package
fixtures. The complete comparison then passed8 smoke captures before8 exact
fresh-process repeats, followed by2 actual-input negative controls. All60
protected inputs remained unchanged, and the task containers were absent after
both launches. The compiler produced no warnings.

The selected baseline ZIP is3d619201ec02bd7566d99c9fbab146301a286cc1056f1407b732921b9e3f8898;
the repaired private ZIP is84376dd94e415e7ee485a79231e17203942d38be678acfe46d1f840f2b93045a.
Both contain2598 members. Exactly3 wave payloads differ;2595 remain identical.
The no-decoration comparison changes20570 scene pixels, all inside the three
wave canvases. These checks establish a faithful comparison, not acceptable
joins, contact, complete animation, or human approval.

The first authoring prototype has documented cropped edges. In particular007
loses57 meaningful bottom-edge pixels in addition to320 intended top-join
pixels;003 and009 also have recorded edge losses. See the per-frame export
reports and aggregate `../candidates/v1/export-report.json`. They remain
limitations despite these passing native checks. Root selected this bounded
diagnostic to inspect ground support and joins before another generation pass.

Executed helper checks are reproducible after the phase probe and V5 package:

```text
python -B art/cartoon/shoreline-repair-v1/native/check.py --baseline build/shoreline-repair-v1/props-v5/baseline.zip --phase-probe build/shoreline-repair-v1/phase-probe-v1/captures/phase-probe --phase smoke --report build/shoreline-repair-v1/check-replay/smoke.json
python -B art/cartoon/shoreline-repair-v1/native/check.py --baseline build/shoreline-repair-v1/props-v5/baseline.zip --phase-probe build/shoreline-repair-v1/phase-probe-v1/captures/phase-probe --phase regression --report build/shoreline-repair-v1/check-replay/regression.json
```

`evidence-v1/` retains the small actual logs/reports and an explicit file index.
Large private ZIPs, PPMs, PNGs and executables stay in ignored build output with
their hashes recorded. Replay writes fresh scratch only; do not overwrite the
historical evidence folder.
