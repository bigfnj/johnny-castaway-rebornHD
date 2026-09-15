# Cartoon front arrival and standing family

Work starts from main `707a20b` on `art/cartoon-front-arrival-family`.
The approved front walk 024-029 stays intact. This batch begins with the
separate original standing pose 017, reviewed as a key before more drawings.
017 appearance and its front-walk arrival are approved in `approval017-v1.json`.
016 and both front waiting turns are approved in `016-key-v1/approval-v1.json`.
The remaining standing drawings000/015 and the complete direction ring are
approved with "excellent, proceed" at standing-ring-v1. Production integration
and delivery verification follow these separate art decisions.

This delivery completes all eight standing directions with five unique sprites:
new000/015/016/017 and existing Cartoon018. The full wait/turn table uses ten
unique sprites; existing Cartoon023 and ordinary HD003/009/010/012 account for
the rest. The original eight-new-pose scope was split after the dependency trace
showed003 recurring inside the HD001-008 profile walk. Those ordinary turns
belong with a complete profile-walk/context batch. Their original-only
preparation is in `ordinary-turns-v1/reference/`; no new ordinary artwork was
generated or approved.
The first native checkpoint is the existing 23-position E-to-A front walk into
017, including its mirrored use, original draw-origin change and 1600ms hold.
The final checkpoint reviews000/015 with all approved standing views in both
native heading orders. See `remaining-waits-v1/` for its sources and evidence.

Use supplied-original pixels for pose geometry and the approved Calm focus
character for appearance. Stored 017 faces screen-right; the engine mirrors it
for the E-to-A arrival. Reference gray ground shadow is not sole placement.
The original diagnostic palette is not original-executable color calibration.

Preserve prompts, ordered inputs, raw outputs and exact exports. Maintain the
common character scale and explicit cap registration; do not use independent
silhouette fitting or camera recentering to hide motion discontinuities.

## First visual checkpoint

Selected source: `017-foot-depth-v3.png`. The approved arrival review is at
http://127.0.0.1:8932/front-arrival017-v1/review.html.
The left panel is the accepted Cartoon walk ending in existing HD017; the right
uses exactly the same walk followed by the new Cartoon017. "Show arrival"
pauses on the standing pose in the fixed close-up; "Replay walk" restores the
complete movement. This review does not cover the later turn poses or story uses.

`provenance-v1.json` binds all three generation calls, their ordered references,
raw outputs and technical measurements. `candidate-recipe-v1.json` reproduces
the selected 80x150 candidate. `candidate-export-v1.json` records its output
identity. The original request is preserved in `review-request-v1.json`;
the subsequent response and its exact scope are in `approval017-v1.json`.

| Check | Result |
| --- | --- |
| Export | Smoke 3/3, regression 19/19, 16 executed mutations each produced one named failure. |
| Native arrival | Smoke then full route passed. All 47 display times match; 35 displays are identical and 12 arrival displays differ only within017. |
| Preview | Two smoke checks, four regression groups and three executed browser mutations passed; published images and controls checked. |
| Production | Unchanged. This is a private candidate with one additional ZIP member. |

The selected runtime PNG SHA256 is
`60e3a77a64620502d2b5198911a7805e19aaedf07801c7a00a92c030b4924de1`.
Reports and native reconstruction notes are under `review-evidence/`.

## Reproduce the candidate export

Run from the repository root with Python and Pillow12.3.0. On this workstation
use the toolbox interpreter in `$env:TOOLBOX_PYTHON`. Output directories must be
new. These commands reproduce technical candidates, not approval or promotion.

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/export.py --recipe art/cartoon/walk-pilot/front-arrival-v1/candidate-recipe-v1.json --output build/front-arrival/reproduced-export
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/test_export.py --phase smoke --recipe art/cartoon/walk-pilot/front-arrival-v1/candidate-recipe-v1.json --output build/front-arrival/reproduced-tests
& $env:TOOLBOX_PYTHON -B art/cartoon/walk-pilot/front-arrival-v1/test_export.py --phase regression --mutation-check --recipe art/cartoon/walk-pilot/front-arrival-v1/candidate-recipe-v1.json --output build/front-arrival/reproduced-tests
```

The stored original-reference preparation is immutable. See `reference/README.md`
before using historical preparation material, and `trace/README.md` for the
original-installation prerequisites of the separate scene/table trace.

## Lessons from this draft

- Distinguish a standing pose from the adjacent walk silhouette. Use the original
  body yaw, outward elbows and planted stance as geometry authority.
- Do not treat the original gray ground shadow as a foot landmark. The original
  colored foot extents have about6HD pixels of projected vertical separation.
  The first generated draft had about19.3HD. Two narrow image edits reduced that
  to about8.4HD; these are color-mask observations, not anatomical contact proof.
- A requested downward edit may move less than requested. Measure the resulting
  pixels after each generation and retain the attempt, prompt and input order.
- Remeasure cap registration even when an edit requests an unchanged upper body.
  Such wording is intent, not a guarantee of identical pixels.
- Final fit and hashes do not establish a natural arrival. Review the native
  final step and hold at Normal speed before expanding the family. Hand placement
  remains part of this human check.
