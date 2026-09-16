# Connecting-pose native baseline

This is the current 40-asset Cartoon pack with HD fallback for JOHNWALK009,
010 and012. It is not an original-binary capture. The separate original sprite
references and static reviews establish the artwork geometry comparison.

The six real public `adsPlayWalk` clips are configured in `config.py`:

| Clip | Public travel call | Selected path | Displays | Total logical duration |
| --- | --- | --- | ---: | ---: |
| Front arc | `adsPlayWalk(3,3,2,7)` | DC | 36 | 3400ms |
| Rear arc | `adsPlayWalk(3,6,4,2)` | DE | 38 | 3640ms |
| Front entry/exit | `adsPlayWalk(2,1,1,1)` | CB | 36 | 3400ms |
| Front-to-profile | `adsPlayWalk(4,7,2,6)` | EC | 50 | 4600ms |
| Front waypoint | `adsPlayWalk(3,7,5,3)` | DCF | 54 | 4840ms |
| Rear waypoint | `adsPlayWalk(1,3,4,5)` | BAE | 74 | 6520ms |

Each clip first invokes an actual same-spot, same-heading wait call to show its
approved standing pose. The observer reseeds libc RNG to2 immediately before
each prime and travel call. The island seed is11, high tide, daytime, offset0,0,
without a raft or holiday. The separately called prime lasts120ms under the
current port's initial timer; there is no fabricated standing hold. Every real
display, including background updates and zero-duration boundaries, is retained.

`config.contract()` enumerates exact rows from the original-derived489-row
walk table. Before rendering, `native_core.build()` compiles unchanged current
`walk.c`, `calcpath.c` and `utils.c` with a drawing/delay observer, runs all12
prime/travel cases, and requires exact frame, mirror, position and returned-delay
agreement. Only after that succeeds does it compile the full Linux engine
observer. The real public calls then verify selected paths, stored rows, draws,
delays, stage durations,20ms accumulated ticks, resource selection and cleanup.
This is evidence for the current port. It does not establish original-executable
path selection or timing parity.

## Recreate the baseline

Use a separate worktree at source commit
`3af0242a74f234aab231d9203b48f78ca8e5c1b4`, then copy this new helper directory
from the evidence commit into the same repository-relative location. Do not
replace production assets in a working checkout to recreate an old baseline.
After later promotion, running `prepare.py` directly against the newer archive
intentionally fails its baseline identity assertion.

Required production archive SHA256:
`1649218b32a4d11595806f8680e351a4f47950fcefbafdf8de758c2d225913db`.
It contains40 accepted Cartoon PNGs and2591 total named ZIP payloads.

The helper locates the repository on Windows and uses
`build/connecting-poses/native-motion-v1` as its scratch root. Start with that
specific scratch root absent or freshly staged; keep earlier attempts under
separate names. The tools refuse to overwrite their completed output folders.

1. Run `prepare.py` with Python3 from the repository. On this workstation:

   ```powershell
   & $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/prepare.py
   ```

2. Confirm the existing Docker image digest, then use the pinned image shown
   below. Replace both host mount paths with the absolute paths of the scratch
   worktree. `/source` and `/out` inside the container are required literal mount
   points; the observer compile arguments use them directly.

   ```powershell
   docker image inspect johnny-platform-cleanup:latest --format '{{.Id}}'
   ```

   ```powershell
   docker run --rm --init --network none --mount type=bind,source=D:/.ai-work/worktrees/johnny-cartoon-connecting-poses,target=/source,readonly --mount type=bind,source=D:/.ai-work/worktrees/johnny-cartoon-connecting-poses/build/connecting-poses/native-motion-v1,target=/out sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72 xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /source/art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/capture.py
   ```

   This runs all six one-display smoke captures first, then each full clip and
   an exact fresh-process repeat. It records every individual native log and
   report, independent trace, compiler output and protected input hashes.
   Failure writes `baseline-failure.json`; retain the failed output directory.
   Rendering occurs only inside Xvfb, without a workstation window.

3. Run the baseline negatives in the same pinned image and mounts after
   `baseline-v1/summary.json` reports PASS. Replace the `xvfb-run ... capture.py`
   suffix above with:

   ```text
   python3 -B /source/art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/negative_baseline.py
   ```

   Retain its stdout/stderr exactly as
   `negative-controls/baseline/execution.log`. The original run used the local
   Python subprocess wrapper recorded beside the execution. It uses no Xvfb
   because the only fresh native execution is the unchanged-C draw observer.
   The nine controls cover the source-table fingerprint, row count, explicit
   pose sequence, arrival role, sentinel placement, duration budget, compiled
   waypoint prediction, captured selected path, and terminal display role.
   Positive contracts and the actual captured parser input pass again after
   restoration. No production source or archive is edited by these controls.

4. `preserve_baseline.py` copies small completed reports, logs, drivers and
   exact executed helper snapshots into `evidence/baseline-v1`, with a portable
   `baseline-checkpoint.json` binder. It requires the negative execution log.
   For a rerun, retain the original binder and use a separate helper-directory
   copy when making a new preservation checkpoint.

All PPM/PNG sequences, private ZIP copies and native binaries are intentionally
local only. Their hashes and display metadata remain in the small retained
reports. Later candidate capture and browser review are separate evidence and
do not change this baseline. The original still approval of009 does not by
itself approve010/012 or any complete motion sequence.
