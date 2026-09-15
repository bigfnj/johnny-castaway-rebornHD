# Complete waiting-ring native review

Only waiting sprites000 (side) and015 (back) are new in this comparison.
Approved016/017 are added in a private baseline above unchanged production;
existing018 and all other production members remain exact. The candidate adds
only000 and015 above that baseline. No engine timing or production assets are
modified.

`config.py` defines both eight-step adjacent-heading rings, their separate
native front-facing priming call, candidate frame IDs, default direction and
camera. `prepare.py` retains the prior observation wrappers and extracts only
the generic build/hash/protection functions by Python AST source spans. The
native driver calls the real `adsPlayWalk`; it does not draw synthetic poses.
The observer's inherited `TURN` log prefix identifies those reused wrappers.

| Actual native clip | Displays | Duration | Candidate differences |
| --- | --- | --- | --- |
| Decreasing headings, default | 108 | 13,880ms | 41 displays differ inside000/015;67 exact |
| Increasing headings | 22 | 1,080ms | 8 displays differ inside000/015;14 exact |

Each clip starts with `adsPlayWalk(0,0,0,0)`, then makes eight separate calls
between adjacent headings until it reaches heading0 again. Every call resets
the path RNG seed to2; island initialization uses seed11. The native priming
call lasts120ms. Decreasing-heading calls return6 then80 ticks and last1720ms.
Increasing-heading calls return80 immediately but last120ms because the public
wrapper initializes its first timer to6 and does not assign that first return
to the timer. Captures preserve this behavior. It is not claimed to match the
original executable, and this art phase does not fix it.

Both baseline clips passed smoke, full capture and exact fresh-process repeat.
Candidate smoke preceded full regression in each direction. Actual API calls,
draw ordinals, repeated rows, flips, origins, completed waits and timestamps
match. All prior-approved pixels remain exact, including outside the actual
placed000/015 canvases when new art is visible. This mask proves technical
isolation, not anatomical correctness.

The full-canvas union is HD `[568,478,688,636]`; the fixed close-up remains
`[560,400,400,280]`. The local page retains all260 panel-display references.
Identical image bytes share147 PNG URLs and one loaded Image object per URL.
There is no cropping, resampling or timestamp removal in those image files.
The long direction is the default. A duration note explains the fast direction;
all eight headings are directly selectable. Pose stepping retains repeated
native draw calls, and playback selects the final display at shared timestamps.

Local browser smoke passed before every native pixel/timestamp, all16 heading
selection/crop checks, control/cadence checks and1280×900 visibility checks.
Root visual review precedes publication. Human acceptance is separate from
these technical checks.

Executed negative controls preserve the published page. The exact native Python
parser/comparison modules first passed an unchanged recorded-capture replay,
then rejected a changed display timestamp and one changed pixel in approved016.
These are guard replays, not fresh native engine mutation builds. A fresh browser
ran the exact existing checker on a scratch page with the heading selector
shifted by one; smoke passed, then the heading-state assertion failed once.
The publisher also rejected changed HTML bytes with a named identity failure.
Module/page hashes and failure logs are retained under `negative-controls/`.
No unexpected capture or browser failure occurred in this complete-ring batch.

## Reconstruction and commands

The production archive must remain SHA256
`1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63`.
Use a separate checkout whose production source/header/build identities match
`baseline-v1/build.json`. Preserve the independent native trace at
`art/cartoon/walk-pilot/front-arrival-v1/trace/trace.json`.

Recover approved017 and016 runtime PNGs at the exact paths in `config.APPROVED`.
The private baseline SHA256 is
`16421422b99f7573c005b9525c62364bc7072e6e0008292d062f9ac1a9d0ac0a`.
Recover the candidate runtime PNGs and recipes at `candidate-selection.json`'s
paths, checking every recorded hash. The candidate ZIP SHA256 is
`ee180c8b6aa1e07024132bae808fc4d2fcc136714dd12152468a3c9fc511aa2c`.

The helper repository-root assumption is `Path(__file__).parent.parents[2]`.
Use a fresh directory at `REPRO_CHECKOUT/build/front-arrival/waits-ring-v1/`.
Stage `config.py`, `prepare.py`, `capture.py`, `candidate-selection.json`,
`prepare_candidate.py`, `capture_candidate.py`, `review-template.html`,
`build_review.py` and `check_review.py`. Do not pre-copy generated
`route_driver.c`, `native_core.py`, private ZIPs, capture directories or review
outputs. Those existing outputs are refused to retain earlier evidence.

`prepare.py` also reads the prior016 observer and capture source. Copy exact
`route_driver.c` and `capture.py` from
`art/cartoon/walk-pilot/front-arrival-v1/016-key-v1/review-evidence/native-v1/`
into `build/front-arrival/front-turn-v1/`. The prior executable and captures do
not need to be rebuilt merely to provide these two source inputs.

Host preparation:

```text
python -B build/front-arrival/waits-ring-v1/prepare.py
```

Use existing Linux image `johnny-platform-cleanup:latest`, ID
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`.
Compiler/libc versions and exact arguments are retained. The image's continued
local or remote availability is not promised. Mount the checkout read-only at
`/source` and this scratch directory writable at `/out`, using Docker
`--rm --init --network none`. Those fixed mount aliases are required by the
capture scripts. No workstation window is opened; only Xvfb is used.

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture.py
```

After baseline completion, run on the host:

```text
python -B build/front-arrival/waits-ring-v1/prepare_candidate.py
```

Then inside the same mounted image:

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture_candidate.py
```

Use host Python with Pillow and Playwright for:

```text
python -B build/front-arrival/waits-ring-v1/build_review.py
python -B build/front-arrival/waits-ring-v1/check_review.py
```

After those positive checks, `negative_native.py` runs inside the same mounted
Linux image (no Xvfb needed for recorded-input replay); `negative_browser.py`
runs on the host with Pillow/Playwright. Run the publisher after root visual
clearance, then `finish.py` after the negative controls. `finish.py` binds small
evidence only after rechecking every protected production input.

`publish.py` is specific to the original workstation's server root and
`standing-ring-v1` slug. It must only run after visual clearance. A new
reconstruction needs a newly adapted destination/URL and fresh served checks;
do not overwrite the old preview. `--verify-only` checks the existing slug
without copying files. Publish only HTML and `images/`.

Large native PNG/PPM sets, private archives, native executable and screenshots
remain local scratch artifacts. A small checkpoint can retain their identities,
helpers, source trace, logs/reports and HTML without copying those large files.
