# Reconstructing the standing017 native checkpoint

This directory contains the exact 43 small files named by
`review-evidence.json.files_sha256`, plus `review-evidence.json` itself. Their
relative paths and bytes were preserved. This reconstruction note is separate
and does not modify the byte-bound `README.md` or `HANDOFF.md`.

The preserved `island-review-v1/review.html` needs its 94 `images/` files to run.
Those images, the raw PPM captures, native executable and private ZIP are local
scratch artifacts. They are not included in this tracked package. At the time
of capture they remained under `build/front-arrival/native/` in the arrival
worktree. A published copy contains only HTML and those images under the
`front-arrival017-v1` server slug. Neither local availability nor the published
loopback URL is a permanent distribution guarantee.

## Recover the correct baseline and tools

Use a separate worktree at base commit
`707a20b285fea695b404a02ce9552615561b121a`. Its production archive must have SHA256
`1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63`.
Do not replace the current project's archive to recreate this baseline.
Verify every protected source/header/build/helper identity listed in
`baseline-v1/build.json` before adopting the saved source identity.

The base commit already includes the earlier front and arrival helper packages
that the reconstruction imports. This new arrival authoring folder did not
exist at the base commit. Copy the retained arrival authoring inputs into that
separate worktree if reconstructing its candidate, without changing production
C/header/build inputs or the baseline archive. Required candidate inputs are
the selected raw `017-foot-depth-v3.png`, `candidate-recipe-v1.json`, exporter,
and the exporter's referenced original reference files. Check their recorded
identities before use.

The recorded Linux image was available locally as
`johnny-platform-cleanup:latest`, image ID
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`.
Its compiler/libc versions and complete GCC command are retained in
`baseline-v1/build.json`. The image may not remain installed, and no remote image
availability is implied. A different toolchain or changed executable requires
new capture evidence. Do not identify a newly built binary as the recorded
binary merely because it produces similar pictures.

Host review building and browser checks use Python with Pillow and Playwright.
The candidate exporter requires Pillow 12.3.0. The existing DevToolbox Python
provided these dependencies; no installation was performed for this capture.

## Stage generators in a fresh scratch directory

The host helpers infer the repository as `Path(__file__).parent.parents[2]`.
Use this exact directory depth:

```text
REPRO_CHECKOUT/build/front-arrival/native/
```

Copy only these generator/input files from this preserved package into that
fresh directory:

```text
prepare.py
adapt_candidate.py
prepare_candidate.py
check_helpers.py
prepare_review.py
prepare_publication.py
finish.py
finish_review.py
README.md
HANDOFF.md
```

Do not copy the generated `route_driver.c`, `capture.py`,
`capture_candidate.py`, `build_review.py`, `check_review.py`, or `publish.py`
into scratch first. Their generators refuse existing targets. Do not copy
retained output directories there either: capture and review helpers preserve
existing evidence by refusing to overwrite it. Keep this complete frozen
package elsewhere for hash comparisons. Use another fresh worktree/scratch
directory for another complete run.

Inside the Linux container, the capture scripts intentionally use absolute
mount aliases `/source` and `/out`. Mount the reconstruction checkout read-only
at `/source`, and its new `build/front-arrival/native` directory writable at
`/out`. Use Docker `--rm --init --network none`. Native execution uses Xvfb only;
no workstation window is required. The aliases are part of the recorded build
command and should remain fixed when comparing executable identities.

## Command order

Run on the host from the reconstruction checkout, or supply absolute script
paths without changing the scratch depth:

```text
python -B build/front-arrival/native/prepare.py
python -B build/front-arrival/native/adapt_candidate.py
```

Run inside the mounted Linux image:

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture.py
python3 -B /out/check_helpers.py
```

The first command builds a fresh observer, runs baseline smoke, then full
regression and a fresh-process repeat. The second checks the actual future017
mask against retained native pixels, including an executed rebuilt mutation.
Logs and partial outputs remain available on failure.

On the host, record the baseline's full canvas union and fixed camera:

```text
python -B build/front-arrival/native/finish.py
```

Recover the exact runtime017 PNG from the authoring recipe using the pinned
exporter and Pillow version. For example, with the retained authoring folder
copied into the reconstruction checkout:

```text
python -B art/cartoon/walk-pilot/front-arrival-v1/export.py --recipe art/cartoon/walk-pilot/front-arrival-v1/candidate-recipe-v1.json --output build/front-arrival/export-v3
```

The expected runtime PNG SHA256 is
`60e3a77a64620502d2b5198911a7805e19aaedf07801c7a00a92c030b4924de1`.
The recipe identity is
`32b7588894a0ef9b2aa623b2da5fd5aaaa25af362b61e985a8b4eaa41af34d85`.
If either differs, stop and investigate the inputs instead of changing expected
hashes to fit the result. Exporter checks remain separate from native capture.

Prepare the private archive on the host:

```text
python -B build/front-arrival/native/prepare_candidate.py --png build/front-arrival/export-v3/BMP/JOHNWALK.BMP/017.png --expected-sha256 60e3a77a64620502d2b5198911a7805e19aaedf07801c7a00a92c030b4924de1
```

Run inside the same mounted image:

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture_candidate.py
```

This adds one Cartoon017 member in a private ZIP, retaining all 2,579 existing
members. Native candidate smoke precedes full regression. Every walking display
must remain exact; only the placed mirrored017 canvas may differ. All native
timestamps, origins, flips and delay returns must match the baseline.

Then use the host Python environment with Pillow and Playwright:

```text
python -B build/front-arrival/native/prepare_review.py
python -B build/front-arrival/native/build_review.py
python -B build/front-arrival/native/check_review.py --review build/front-arrival/native/island-review-v1
```

The browser checker serves an ephemeral loopback page, runs smoke before
regressions, and retains its screenshots, reports and deliberately broken
mutation HTML. Only `review.html` and `images/` belong in a published preview.

## Publication and final evidence

`prepare_publication.py` creates a publisher with the original workstation's
absolute destination and loopback URL. It is deliberately specific to this
checkpoint. Do not run it unchanged to publish a reconstruction: the original
slug already exists, and normal publication correctly refuses it. A later
publication needs a newly named destination and URL in a separate adapted
helper, followed by fresh served-identity and browser validation.
`--verify-only` checks the original destination; it does not publish the newly
reconstructed review.

`finish_review.py` likewise expects the exact `export-v3` scratch paths and a
completed `publication.json`. It is a final binder, not a prerequisite for
baseline capture. Run it only after the corresponding new publication checks
and after retaining the documented authoring inputs. Preserve new identities
and provenance alongside the reconstruction; do not overwrite this checkpoint
or imply new human acceptance.

The fixed close-up is `[560,400,400,280]` in HD pixels. The route has 23 travel
poses followed by the real mirrored017 arrival, 47 observed displays over
4360ms, and a 1600ms arrival hold. Captures establish port rendering and logical
timing under maxspeed. They do not establish original-executable rendering,
physical wall-clock playback, or human approval of the artwork.
