# Cartoon seasonal decoration drafts

Four standalone HOLIDAY.BMP drawings are in visual review. They are not yet
accepted production assets. The production archive still contains the same43
Cartoon assets, including all28 approved Johnny poses. Work is isolated on
`art/cartoon-seasonal-decorations` from source commit
`397edf8e4b34191ade4be13bc93a215f73b0c631`.

| Frame | Subject | Runtime canvas | Current review |
|---|---|---|---|
| 000 | Halloween pumpkin | 80x68 | Pending |
| 001 | St. Patrick's clovers | 240x94 | Pending |
| 002 | Christmas tree | 112x130 | Pending |
| 003 | New Year banner | 304x94 | Pending |

## Sources and method

`generation.json` retains every submitted prompt, ordered reference and raw
output path. `prompts/` contains readable copies. All four calls used the
built-in image generator; no seed was exposed. First reference: original
geometry guide. Second reference: the approved Cartoon island appearance.
The diagnostic original palette establishes geometry, not calibrated original
executable colors. Existing HD references were inspected for comparison but
were not generation inputs.

`raw/` preserves the four actual returned RGBA images. Generation did not obey
the requested canvas and object sizes exactly: the pumpkin and tree returned
1254x1254 images, and the clovers and banner returned1536x1024. Never treat
prompt coordinates as measured output coordinates.

The technical export uses uniform scale and translation with premultiplied
filtering, then returns straight-alpha PNGs on the unchanged runtime canvases.
No anatomy, contours, colors or alpha masks were repainted. The exact recipe,
raw hashes, runtime hashes and padded outputs preserve those decisions.

## Placement lesson from the first scene capture

Version1 matched the original ground/shadow registration and passed canvas,
alpha, package and native renderer checks. Scene inspection still found the
ground decorations overlapping water at the current Cartoon shoreline. The
existing HD decorations showed the same boundary problem. A passing placement
contract does not prove visual contact with stylized scenery.

Version2 keeps the same generated sources and full sprite canvases. It uses a
slightly smaller uniform scale and moves the ground-contact anchors upward
inside those canvases. The banner is unchanged. This is a documented departure
from original ground registration for the current Cartoon island, pending the
user's scene review. No engine coordinates or island pixels changed. Version1
sources, exports and native evidence remain available as a failed-placement
example; its technical PASS is not visual approval.

## Alpha lesson

The broad green/gray haze in some raw previews was RGB beneath alpha0. Actual
alpha composites were clean. Replacing only hidden RGB produced identical
premultiplied exports. Do not erase or threshold alpha based on an RGB preview.
The drawings also contain faint real alpha1..7 residue, plus intended contact
shadows; these are separate from hidden RGB. Runtime framing can exclude faint
fringe, which is measured and retained in the padded export. No alpha hardening
was applied.

## Review and reproduction

Serve this folder and open `review.html`. Each decoration has matched native
HD-fallback and Cartoon scenes, a full-scene view and original/HD/draft sprite
comparisons. Human review concerns appearance, size and ground/banner placement.
There is no new animation in this batch.

`build_preview.py package --version v2 --output <fresh ZIP>` creates an ignored
diagnostic archive. It retains all2594 existing production members and adds
only the four draft HOLIDAY PNGs. The native runner independently validates
those payloads, full canvases, actual loads, draw positions and changed pixels.
See [native reproduction and limits](native/README.md).

After capturing baseline and candidate, use:

```text
python -B art/cartoon/seasonal-v1/build_preview.py review --version v2 --baseline build/seasonal-v1/native-baseline-v2 --candidate build/seasonal-v1/native-candidate-v2
```

The current reviewer shows native Linux stills with approved standing016 and
the Cartoon island. One existing cloud still uses HD fallback. Day, night and
one shifted island position are technical checks. Calendar selection, cargo
suppression, randomized tide selection and full story interactions are outside
this review. The test driver does not claim to execute those behaviors.

Smoke runs precede fresh regression repeats. Original reference and export
checks retain their own reports. Native evidence binds exact selected export
hashes and compares candidate against baseline, including the no-holiday scene.
Existing authoring tests must use their documented script entry points where
they initialize modules in main(); generic unittest discovery is insufficient
for the production-catalog and pilot-history suites.

After visual approval: record exact approved hashes, promote through the
existing art-pack/catalog workflow, rerun runtime and authoring gates, then
commit/push and audit the merged result. Keep Cartoon labeled as a partial
preview; this batch alone does not finish scenery or character coverage.
