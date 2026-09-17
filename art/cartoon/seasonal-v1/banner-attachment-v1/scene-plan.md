# Banner attachment comparison plan

Historical preparation plan, written before the new runtime banner was supplied.
The completed capture and browser results are recorded in `review/README.md`
and the separate evidence binders; the future-tense steps below preserve the plan.
The user accepted the pumpkin and tree and selected the offshore waves. This
follow-up concerns only the New Year banner's visible attachment to the fronds.

Use the exact selected offshore package at
`build/shoreline-repair-v1/offshore-selected-v1/candidate.zip`, SHA256
`ab5c8094b461307b87d68d2bb148eae5b9ce56d93cb6b93805c27c7fbd8e24ac`, as the before
panel. The private after package may change only
`data/styles/cartoon/BMP/HOLIDAY.BMP/003.png`. Its original runtime canvas is
304x94, drawn at HD722,310 before a scene offset. All other ZIP payloads,
including pumpkin, tree, clovers, ground and all nine wave phases, stay exact.

After the exported PNG and its hash are handed off, stage a fresh package:

```text
TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/prepare.py --baseline build/shoreline-repair-v1/offshore-selected-v1/candidate.zip --runtime <exported003.png> --runtime-sha256 <handoffSHA256> --output build/banner-attachment-v1/selected-v1
```

The preparation script is a scaffold until that handoff. Its new refusal checks
must be exercised with the real positive input and a bounded damaged-input
control before relying on it.

Reuse the frozen integrated-shore observer's `build`, `one`, `verify_log`, and
capture codec functions. Its `capture.py` SHA256 is
`f2e0684f6726ce53951988b5d44c101d3efe44f07e6b3b66277499a9f12a1bae`; its `driver.c`
SHA256 is `beb8beae0c3b54562fe51285d184d55ccd2b185fe34cf97b7801d2536abd1b59`.
Both new comparison panels have the enlarged island, so both use the existing
selected-ground validation branch. The old top-level package checker expects
ten shoreline changes and cannot be called unchanged for this banner-only pair.
A small new adapter in `native/capture.py` replaces only that pair/comparison
orchestration; `native/run.py` launches it windowlessly in the pinned image.
There is no new renderer or engine edit.

| Case | Native arguments: holiday, night, dx, dy, low tide, route mode, waits |
|---|---|
| Day banner | `4 0 0 0 0 0 20` |
| Night banner | `4 1 0 0 0 0 20` |
| Shifted day banner | `4 0 -80 20 0 0 20` |

Run the three before/after smoke pairs, then their fresh exact repeats using
the already installed Linux image
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`
and Xvfb. Source mount stays read-only; fresh output is writable. Existing
public repeated-wait calls record the natural phase sequence. No phases are
forced. Confirm matching actual native timestamps, Johnny poses, wave phases,
cleanup and PNG source hashes. Every changed scene pixel must remain inside
`[722 + 2*dx, 310 + 2*dy, 304, 94]`; this also proves the wave imagery is unchanged.

For the new page, show before/current attachments versus new attachments.
Default to a banner/frond close-up, with whole-island and the exact earlier
wave close-up `[660,550,430,185]` as optional views. Apply the actual scene
offset equally to both panels. Capture the full 2400ms sequence, but display
the same observed 1440ms wave-phase loop used by the old wave comparison. Verify
the 1440ms phase closure against the actual report before enabling that loop.
Keep all display timestamps and avoid an invented endpoint hold. Framing and
loop length differed between earlier views despite unchanged wave exports.
This is only one presentation difference; the separate shoreline geometry and
wave-placement audit is not resolved by this comparison.

The scaffolded native command, after package preparation, is:

```text
TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-attachment-v1/native/run.py --baseline build/shoreline-repair-v1/offshore-selected-v1/candidate.zip --candidate build/banner-attachment-v1/selected-v1/candidate.zip --output build/banner-attachment-v1/native-v1
```

At plan creation no scaffold execution or native pass was claimed. The new
adapter's outside-banner pixel guard includes an
executed damaged-pixel control and restored positive in the eventual run.

No existing viewer, frozen report, approved art or production archive changes.
Final banner contact and appearance remain a human judgment after capture.
