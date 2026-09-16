# Skin-tone native review

This is a separate review against the exact uncorrected connecting candidate
`21194cf35e5b60eebfa9ba48520509ae8f86a72f26313b945f019671d1f345c5`.
It is not a comparison against production's HD connecting placeholders.

The six connecting routes retain their API arguments, path seed2, island seed11
and source-table contracts. Two extra same-heading calls at A cover standing015
(heading4, row104) and016 (heading0, row100). Each clip has a prime call followed
by the same wait call. The native first-timer behavior predicts120ms per call,
despite the returned80-tick animation value. This harness neither normalizes
that behavior nor claims original-executable timing parity.

`legacy.py` checks exact hashes before importing the existing connecting compiler
and parser. Their config is intentionally this review's config. The parser is
called with the connecting PNG dependencies present for both packages. No frozen
helper or production source is modified. Some inherited diagnostic labels still
say "connecting capture"; the surrounding report states this color-review scope.

## Candidate boundary

`prepare_candidate.py` consumes an explicit correction export directory.
It binds the current correction script, input index and calibration hashes to
the exported recipe; checks all28 canonical frame/member mappings, PNG/RGBA
identities, dimensions and unchanged alpha; and requires every changed RGB pixel
to lie within that sprite's actual L-mask support (`weight > 0`). Frame029 must
remain byte-identical. It does not infer semantic skin membership from the mask:
independent mask review and the correction tool's tests own that judgment.

The private ZIP replaces the28 existing Johnny members, including the unchanged
029 control, and preserves every other member byte-for-byte. There are no
additions or removals. The preparation record and copied recipe, masks and index
pin what the native capture will use. It refuses existing candidate directories.
Host packaging also decodes each L-mask to a hash-bound `.l` byte file. The
standard-library `mask_data.py` adapter reads those exact bytes during capture;
the pinned native image does not contain Pillow. All28 decoded files were
independently checked against their retained PNG masks.

## Scene comparison

Each baseline and corrected clip runs a smoke check before full/repeat captures.
Across all eight full clips, actual draw coverage must equal all28 frame IDs.
Every observed API segment, wait, draw order, timestamp, placement and horizontal
flip must agree with the baseline; loaded dependencies must also agree.

`skin_compare.py` places the actual mask at `(draw_x * 2, draw_y * 2)` and mirrors
its columns when the real draw is flipped. Changed scene pixels are allowed only
at nonzero mask support. This protects the remainder of the character as well as
the background, rather than allowing arbitrary changes inside the character's
canvas. The unchanged029 control remains a full-display equality case.
All27 corrected poses must be visibly exercised if the final recipe changes27.

These checks establish identical pixel positions and alpha at package level,
and skin-mask-limited scene changes at native level. They do not independently
prove that a supplied mask has perfectly separated skin from other materials.
Palm occlusion can hide allowed source changes; no scene pixel outside the
transformed support is allowed to change.

## Invocation after correction freeze

Preparation and packaging run on the host from the repository root, using a
fresh ignored output tree:

```text
python -B art/cartoon/skin-tone-v1/native-review/prepare.py --baseline build/connecting-poses/native-motion-v1/candidate-v2/scrantic_data.zip
python -B art/cartoon/skin-tone-v1/native-review/prepare_candidate.py --export build/skin-tone/export-v2 --candidate-version 2
```

The captured correction is `export-v2/recipe.json`, SHA256
`021d9125b2184cd1389ba990ee6d347ef041bfcca2cec38d6d5258d0a51a2311`.
The corrected candidate-v2 ZIP SHA256 is
`bdc62b0c34835196e6dfa6541ee54f9c72f9824a0c24a0beab4bee3a33393eaf`.
Reproduction needs fresh scratch outputs; the commands intentionally refuse to
overwrite preserved candidates and reports.

Both capture entrypoints run in the existing Linux image
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`.
Bind the repository read-only to `/source`, bind the new
`build/skin-tone/native-review` folder to `/out`, disable networking, and run
through Xvfb:

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /source/art/cartoon/skin-tone-v1/native-review/capture.py
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /source/art/cartoon/skin-tone-v1/native-review/capture_candidate.py --candidate-version 2
```

The locally available image is pinned; this document does not claim it is
remotely distributed. Native windows remain inside Xvfb. Baseline compilation
verifies a fresh executable timestamp and independent compiled C draw traces
before capture. Outputs and failures remain in the new ignored tree.

## Focused comparison checks

```text
python -B art/cartoon/skin-tone-v1/native-review/test_compare.py --phase smoke --report build/skin-tone/native-review-toolchecks-v3/smoke.json
python -B art/cartoon/skin-tone-v1/native-review/test_compare.py --phase regression --mutation-check --report build/skin-tone/native-review-toolchecks-v3/regression.json
python -B art/cartoon/skin-tone-v1/native-review/check_inputs.py --export build/skin-tone/export-v2 --prepared build/skin-tone/native-review/candidate-v2 --report build/skin-tone/native-review-toolchecks-v3/inputs-v2.json
python -B art/cartoon/skin-tone-v1/native-review/check_native.py --candidate-version 2 --report build/skin-tone/native-review/negative-controls/native-v2.json
```

Executed preparation checks: eight Python helpers parsed/imported and all eight
source contracts cover the28 expected frames. The comparison tests passed two
smoke cases followed by six regressions, including normal/mirrored placement,
nonzero soft-mask support, an unchanged control, unmasked neighbors, and pixels
outside the sprite canvas. Four fresh Python processes compiled deliberately
mutated comparison source; disabling skin support, mirroring, outside-row or
outside-side checks each caused one named test failure. Each child printed its
actual compiled-source hash.

Final comparison reports are in
`build/skin-tone/native-review-toolchecks-v3/{smoke,regression}.json`.
`inputs-v2.json` records eight fresh-process damaged-input refusals, positive
checks before and after, and exact PNG-to-L decoding for all28 masks. The controls
substitute same-canvas009/010, alpha008, unmasked RGB000, mask012, cap binding009,
source row009, correction source identity, and decoded mask009.

`negative-controls/native-v2.json` records four controls against actual captured
front-arc reports: changed timestamp, an unmasked character pixel, a pixel outside
the character canvas, and a029 reference pixel. Each fired its named assertion;
positive comparisons passed before and after. No frozen capture was modified.

## Executed native result

All eight baseline smokes passed before full captures and fresh repeats. All
eight corrected smokes then passed before corrected full captures and repeats.
The full comparison covers298 displays:286 visibly change within transformed
skin support and12 remain identical. All28 Johnny poses are exercised, all27
corrected poses have visible scene changes, and029 remains identical. The route
display counts are36,38,36,50,54,74 followed by5 and5 for wait015 and wait016.
Every repeat agrees exactly. Source, production archive and protected inputs
remain unchanged; no production promotion occurred.

The first candidate-v1 launch failed before any native call because the container
lacks Pillow. Its preparation/package and `candidate-v1-launch-failure.json` are
retained. The host-decoded L-mask adapter resolved that dependency without image
installation or artwork changes; candidate-v1 and candidate-v2 ZIPs are identical.
The baseline build's helper snapshot predates that adapter fix. Those candidate
comparison helpers were not used to render baseline captures. The candidate-v2
summary pins the final helpers actually used, including the comparison helper;
the prepared decoded masks and final helper files must accompany reproduction.
