# Seasonal native captures

These stills render current Cartoon island/Johnny artwork with HD holiday
fallbacks through the unchanged native Linux renderer. They are not original
executable captures. No production archive, source code, or existing preview is
modified. No final browser UI is created here.

The baseline was compiled from `397edf8e4b34191ade4be13bc93a215f73b0c631` with
production ZIP SHA256
`4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`.
The driver observes `grDrawSprite` while invoking the actual `adsInitIsland()`
and `adsPlayWalk(0,0,0,0)` functions. The latter is a finite same-heading A wait,
leaving approved standing016 visible. Engine sources and render parameters are
unchanged. This explicitly selected diagnostic state does not execute the story
scheduler, randomized island placement, calendar selection, or cargo-scene
holiday suppression.

## Canvas and placement contract

| HOLIDAY frame | Decoration | Logical origin | Native canvas | Runtime canvas | Default runtime rectangle |
|---|---|---|---|---|---|
| 000 | Pumpkin | (410,298) | 40×34 | 80×68 | [820,596,900,664) |
| 001 | Clover | (333,286) | 120×47 | 240×94 | [666,572,906,666) |
| 002 | Christmas tree | (404,267) | 56×65 | 112×130 | [808,534,920,664) |
| 003 | New Year banner | (361,155) | 152×47 | 304×94 | [722,310,1026,404) |

`src/engine/island.c:299` loads the four-frame resource and draws its selected
frame at these full-canvas origins. There is no walk-specific x-minus-one
adjustment. `src/engine/graphics.c:604` adds the island offset, then multiplies
by render scale2. The logical640×480 viewport therefore renders1280×960.
Do not trim the canvas, move the registration, or resize a candidate to its
visible bounding box.

The holiday layer is composited last (`src/engine/graphics.c:319`), above Johnny,
clouds and palm. Preserve meaningful transparent gaps in the banner and the
ground-shadow silhouette for ground decorations. Candidate PNGs use actual
straight alpha, 8-bit non-interlaced RGB/RGBA/grayscale-alpha accepted by the
maintained loader; an RGBA export is the practical choice here. Legacy HD's
magenta-key cleanup belongs to the HD fallback branch, not Cartoon assets.
Native comparison checks where the changed pixels occur; it does not decide
whether generated artwork has semantically correct shadows or transparency.

The default review state is day, high tide, no raft and offset(0,0). In the
pinned Linux libc, seed11 selects OCEAN02.SCR; seed9 selects OCEAN01.SCR. This is
a measured platform distinction, not a cross-platform RNG guarantee. Diagnostic
groups also exercise NIGHT.SCR and day offset(-80,+20), still at high tide. Low
tide was not added to this bounded check.

## Run

From the repository root, using a locally available Docker image with ID
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`:

```text
python -B art/cartoon/seasonal-v1/native/run.py --archive assets/scrantic_data.zip --output build/seasonal-v1/native-baseline-replay --diagnostics
python -B art/cartoon/seasonal-v1/native/check.py --captures build/seasonal-v1/native-baseline-replay/captures --output build/seasonal-v1/native-controls-replay
```

Use fresh output names; existing evidence is refused. The wrapper mounts the
repository read-only at `/source`, its output at `/out`, disables network,
uses `--init` and Xvfb, and verifies that its uniquely named container no longer
exists after completion. Timeout/error cleanup targets only that container.
All windows remain inside Xvfb; no host desktop window is opened.

For a candidate, supply its ZIP with `--archive` and another new output name.
It must live inside this checkout for the read-only mount. The candidate must
retain all2594 current production payloads exactly and may add only
`data/styles/cartoon/BMP/HOLIDAY.BMP/000.png` through `003.png`. The selected
member routing and full dimensions are validated, then the actual native log
must show those same dependencies. The wrapper records the explicit selected
archive hash. This tool intentionally requires the pinned production baseline;
after later promotion, reconstruct that baseline in an isolated checkout before
replaying these historical captures.

Usable baseline PNGs are at
`build/seasonal-v1/native-baseline-v2/captures/day/{none,halloween,stpatricks,christmas,newyear}/smoke/final.png`.
Night and shifted versions replace `day` with `night` or `offset`. Reports retain
full-image hashes, actual draw coordinates, dependency lists and executable
identity. The no-holiday capture is the clean, same-state scene for composition
diagnostics. Any browser composition from it must be labeled as a diagnostic,
unless independently compared with the native candidate capture.

## Executed checks

All five day smokes passed before their five exact fresh-process repeats.
Night and shifted groups each passed five smokes before five repeats. Across
30 native processes, every holiday differed from its no-holiday capture only
within the actual decoration canvas; every repeated image matched exactly.
All60 protected production source/archive inputs remained unchanged.

Three in-memory negative controls used actual day capture data: incorrect draw
origin, a changed pixel outside the holiday canvas, and a wrong loaded member.
Each fired its named failure, with positive readback before and after.
Nine supplemental copied-input controls exercised retained-payload damage,
member deletion/duplication, unrelated additions, wrong candidate dimensions,
wrong observed state/backdrop, missing cleanup witness, and an unexpected draw
with holiday disabled. A valid addition fixture exercised the other routing
branch using HD bytes purely as a package test, not proposed artwork.

`evidence-baseline-v1/` retains exact small reports, logs, helpers and their
hashes. PNGs, PPMs, executable and repeated ZIP copies remain ignored local
artifacts and are recreated by the commands above. The initial v1 container
stalled in Xvfb startup before launching the app; its launch record is retained.
It was stopped explicitly. The v2 run added Docker's init process, completed,
and verified that no task container survived.
