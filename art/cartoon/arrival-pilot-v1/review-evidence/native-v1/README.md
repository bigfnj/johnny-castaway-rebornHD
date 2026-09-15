# Arrival 018 native review

The displayed page was
`http://127.0.0.1:8932/arrival-cartoon-v1/review.html`, HTML SHA256
`d5dc40f835f04c410dfa48c20e4c44057f3a98754a02b9eada1bad7799261877`.
This folder preserves the technical checkpoint. Any human decision belongs in
a separate acceptance record; passing these checks does not assign approval.

Both panels use the current 27-asset Cartoon island and rear walking family.
The baseline arrival is packaged HD frame 018. The candidate changes only that
arrival to the new Cartoon frame 018. There is no original-executable rendering
claim and no synthetic turn or extra hold appended to the route.

The unchanged engine API `adsPlayWalk(1,3,0,3)` executes the direct B-to-A route.
Its 23 travel poses use 120 ms intervals; frame 018 then holds for 1600 ms. The
47 recorded displays include real background updates and a zero-duration final
witness at 4360 ms. The final walking frame 022 has logical origin (302,244),
followed by arrival 018 at (298,240). These original table coordinates are kept.
The fixed close-up rectangle (580,440,400,280) in HD screen pixels covers every
walking/arrival canvas and preserves the visible origin shift and sand contact.

## Bound identities and outcomes

- `source-reuse.json` verifies every one of the 59 historical protected build,
  source and driver-test inputs against the current checkout. Only the archive
  changed. The current 27-asset archive has all 2578 uncompressed members equal to
  the previously reviewed rear-walk candidate archive. No production source was
  patched or recompiled for these captures.
- The saved Linux observer SHA256 is
  `831a6ada20ac1e1d68d822e325b2a664ec5a1ca22522b82d3fff7e01aaacc2b8`.
  `historical-build.json` preserves its compiler arguments, source hashes and
  fresh-build timestamp. `helpers/route_driver.c` records the observation-only
  linker wrappers, real API call and cleanup. The island/path seeds are 11/2 in
  this Linux environment, not portable random-number promises.
- The baseline production ZIP SHA256 is
  `1daf8f95614fde8efd85745a8baac02a41d88c2775a91374d66959174220aa7e`.
  The private candidate ZIP SHA256 is
  `bc47235fbb12ed5c2a080471a556e4e61e41e4e4c886de94fd02dd7591d6386d`.
  It adds only `data/styles/cartoon/BMP/JOHNWALK.BMP/018.png`, SHA256
  `5ab7fb306a39eab69d419f3602101a72e3cca30d15e6432c58a6beaf975e9190`.
  All 2578 previous members, including original RESOURCE data and all 27 approved
  art assets, remain unchanged. There are no diagnostic resource overrides.
- Baseline smoke preceded full-route regression. All 47 baseline RGB captures
  exactly matched the previously reviewed current scene. Candidate smoke then
  preceded its full-route regression. All walking displays stayed byte-identical;
  each arrival differed only inside its 64x154 canvas. Every observed row,
  timestamp and art dependency matched apart from the intended 018 path swap.
- Browser smoke passed before four grouped regressions. All 47 logical timestamps
  and 94 full-canvas RGBA hashes matched the captured PNGs. Play/pause, speed,
  pose stepping, last 022-to-018 transition, repeat, fixed close-up and 1280/1600
  layouts passed. The served HTML and 94 served image hashes were checked again.
- Four isolated Python helper mutations each produced one named failure with an
  exact executed-source witness. They cover preview-only input, wrong frame ID,
  raw-source identity and altered pixels outside the permitted arrival canvas.
  The pixel control varies changes inside, outside left/right and above/below.
  Two served-browser mutations cover stopped timing and drawing baseline pixels
  on the candidate side during a real arrival state. These Python/JavaScript
  mutations did not modify or rebuild the production executable.
- A further comparison replay changes one background pixel in the first actual
  walking capture. The real `capture.py` refuses it as
  `full: unchanged-full-frame:1`; removing that guard yields exactly one named
  test failure. All replay inputs are bound to the saved native report. Only the
  subprocess seam supplies those recorded files instead of running the engine
  again. This is a comparison-guard test, not another native execution.

Raw/candidate pixels, recipe and export report are bound by their recorded
hashes. Source-center and filtered alpha-8 bounds fit the runtime canvas; this
does not promise absence of every lower-alpha filtering fringe. This review
does not establish anatomical parity, original executable palette/compositing,
physical audio or native wall-clock playback speed. The observer runs maxspeed
and records engine logical delays, which the browser replays without interpolating
new poses. Human judgment of the far foot and ground contact remains separate.

## Reproduction

The scratch directory convention is `build/arrival-native-review/` in the
checkout. Copy the helper snapshots there if recreating the local setup.
`setup.py` expects the preserved prior build and captures under the sibling
`johnny-cartoon-production/build/rear-native-capture/`; those large captures and
the saved binary are not duplicated here. It refuses changed production source
or a different current ZIP. The historical build command and complete driver
are retained if the binary must be rebuilt, but a rebuild has a new executable
identity and must receive new capture evidence rather than adopting the saved
hash. The prior reviewed reports identify the comparison pixels.

With the exact saved build and prior captures present:

```powershell
python -B build/arrival-native-review/setup.py
```

Use the existing Linux image
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`,
with the checkout read-only at `/source`, scratch directory at `/out`, and prior
capture directory read-only at `/prior`. The enclosing Docker command uses
`--init`. Run the current baseline, then prepare and capture the one-path candidate:

```sh
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture.py
```

```powershell
python -B build/arrival-native-review/prepare_candidate.py --exports build/arrival-export-v1 --output build/arrival-native-review/candidate-v1
```

```sh
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture.py --candidate /out/candidate-v1
```

The exporter is documented separately in this pilot. Its exact output recipe
and report are copied here as the native capture inputs. Build and test the page:

```powershell
python -B build/arrival-native-review/build_review.py --candidate build/arrival-native-review/candidate-v1 --output build/arrival-native-review/island-review-v1
python -B build/arrival-native-review/check_review.py --review build/arrival-native-review/island-review-v1
python -B build/arrival-native-review/check_guards.py
```

The browser checker requires the toolbox Python's Pillow and Playwright/Chromium.
It serves a temporary local HTTP origin. `publish_review.py` copies only this new
version's HTML/images to the existing 8932 review root and checks actual served
bytes; it refuses to overwrite a prior served version. `adapt_review.py` records
how the new helper was derived from the historical rear-walk viewer; reproduction
uses the final `build_review.py` snapshot. `evidence.json` hashes each retained
input/report/helper. Large PNG/PPM sets remain local, with all individual PNG and
RGB hashes and per-display timings retained in these records.
