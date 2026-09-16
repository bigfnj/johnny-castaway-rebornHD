# Foot-v5 contact and motion checkpoint

The landing page opens the exact mirrored arrival: original pose, previous version and corrected foot. Display063 is at4920ms, actual draw `[1,394,209,18]`. Every still uses the same pose crop `[784,410,80,178]` and foot crop `[792,546,60,34]`. The source-original gray shadow and diagnostic colors are explained in About. This is original artwork rendered by the port, not original-executable footage.

The prominent motion link opens the complete two-panel comparison through waypoint_front, front_arc and waypoint_rear. All164 displays and their native timing remain intact. The previous version is the accepted-shorts v2 pose; the new version changes018. Other2593 ZIP payloads are identical. The original panel is a static source reference, never presented as synchronized walking footage.

## Frozen inputs

- Current-v2 archive: `7a50f72fe65382917a1d38412dad97315542831ea5fd06eec9570734a7afdb52`.
- New archive: `561edb2c9b4b4857b723af1505ce8d2654616aae2942325389604a4d88804521`.
- New normalized018: `5ff919bc1db94f19ce163e990f2e00208cb74c9540656ddc8d2ddd5cf05fd15f`.
- Supplied-original diagnostic archive: `d7797181cf2e30699709946f0983b6899f0c7428785f9c596dea8ac150619f20`.

Native inputs are under `build/standing018-proportions/foot-v5-motion`, current-v2 baseline reports are split between `native-review/color-v2/front_arc` and `motion-v1/{waypoint_front,waypoint_rear}`, and the original mirrored source is `build/standing018-proportions/original-mirror-v1/full`. These paths are relative to `build/standing018-proportions` unless written in full. Reconstruct the pinned inputs using the sibling `native-review/foot-v5/README.md`, its linked v2/original evidence and `color/FOOT_V5.md`. The evidence binders identify exact source files and commands; do not substitute whichever production ZIP is current after promotion.

From the repository root, with the toolbox Python:

```text
python -B art/cartoon/standing018-proportions-v1/foot-review-v5/build_review.py --output build/standing018-proportions/foot-review-recreated
python -B art/cartoon/standing018-proportions-v1/foot-review-v5/check_review.py --review build/standing018-proportions/foot-review-recreated
python -B art/cartoon/standing018-proportions-v1/foot-review-v5/negative_controls.py --review build/standing018-proportions/foot-review-recreated --output build/standing018-proportions/foot-controls-recreated
```

On this Windows workstation, invoke `& $env:TOOLBOX_PYTHON` in place of `python`. Output directories must be fresh. The builder first creates `motion/`, then the contact landing. The source-original diagnostic report intentionally has a compact schema: its exact `reference_report_sha256` binds the current-v2 report, and all74 index/time/duration/role/draw observations are compared. Optional segment fields are not fabricated. Two initial incomplete build attempts in ignored `foot-review-v5` and `foot-review-v5-final` exposed those schema differences; their partial records remain preserved and were not published.

## Reused checks and changed coverage

`shared_motion_check.py` is the previous frozen motion checker with only the expected visible panel-label assertion changed from Earlier/Revised Cartoon to Previous version/Corrected foot. Its pixel, timestamp, pose, cache, playback and mirror logic is unchanged. `check_review.py` supplies the new source-binding module explicitly. Both source and derived checker hashes are retained, and preservation verifies the exact one-assertion difference after newline normalization. No previous helper is modified.

The new contact check runs browser smoke before its six exact crop/visibility checks, actual link navigation, Normal playback and return link. It then runs the existing three-clip regression once. Four fresh-process controls reject the old pre-proportions baseline, initial/unmirrored018 in place of the required arrival, the previous PNG in the corrected panel, and a broken motion link. The original helper hashes and named failures are recorded. Unchanged motion mutation matrices are not repeated.

Publication checks two damaged HTML bindings, then serves208 exact files. Served contact smoke precedes six crop/link checks; the full motion files are byte-identical to the locally tested version, so the unchanged full164-display matrix is not run again after publication. The URL is `http://127.0.0.1:8932/standing018-contact-v3/review.html`.

Do not rerun `publish.py` or `preserve.py` into the historical destinations. A future candidate needs new bindings, a fresh output and a new slug. `evidence-v1` retains contact PNGs, exact pages, reports, helper snapshots, screenshot, focused-control logs and linked native/color/original evidence. Full motion PNGs, private ZIPs and executables remain local-only. Recreate them before serving the retained motion page. Technical PASS is separate from the user's later foot-contact decision.
