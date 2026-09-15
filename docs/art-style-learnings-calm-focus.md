# Calm focus walking revision: reusable image lessons

This adds to [the original art-style lessons](art-style-learnings.md) without
changing that historical record. The user approved the standalone walking
preview on 2026-09-15, then approved the later toe-clearance edits and their
actual in-scene rendering with "looks good". The exact six exported sprites and
inherited island artwork are recorded in the
[production acceptance](../art/cartoon/walk-pilot/calm-focus-runtime-v1/production-acceptance.json).

## Keep reference truth and artistic acceptance separate

Use supplied-original pixels and source draw records for pose reference. The
original-first JSON catalog describes image identities, canvas sizes, transforms
and human observations; it does not replace the PNG artwork or prove anatomical
correctness. Enlarged original reference colors come from the decoder's
diagnostic palette, not a verified original-executable capture.

The user confirmed that frame 028 still has the opposite leg forward, then
accepted the displayed six-frame walk after reviewing it in motion. Preserve
that decision as an accepted artistic difference. Do not relabel it as a
successful original-pose correction or alter the original reference observations.

## Expression prompts need a visible action

The user selected expression 6, Calm focus, and preferred its full-body key to
the later raised-eyebrow variant. Naming the expression alone often preserved
the old downcast gaze. An eyes-only request to move both pupils from the bottoms
of the eye whites to their vertical centers, looking ahead, produced a visible
change. Use the selected key as an explicit expression reference. Preserve the
sailor cap's projecting dark brim, scruffy beard and established proportions.

These edits also redrew pixels outside the requested eye region. Similar-looking
heads and bodies are not byte-identical assets. Recheck registration after each
generation rather than trusting a prompt that says to preserve everything else.

## Change one difficult feature at a time

Repeated combined leg, shorts and expression requests retained the incorrect
leg attachments. Forcing the near thigh across the other thigh produced a
wrapped or hanging shorts panel, which the user rejected. A follow-up still
looked wrong in both shorts and foot perspective. Restarting from the earlier
approved drawing avoided carrying that rejected fabric shape forward.

After motion acceptance, two narrowly scoped toe-clearance edits were more
effective. Frame 028's projecting toe shortened by about 3.5 HD pixels; frame
029's outer edge retreated about 1.1 HD pixels. Both retained the common 0.1
scale and existing affines. Their upper-body alpha-8 silhouettes stayed within
two raw pixels per axis of the reviewed images, or 0.2 HD pixels. This supports
technical preview, not unchanged-pixel or anatomical claims.

Keep prompts, reference order, exact returned PNG hashes, ancestry and each
acceptance scope. Rejected outputs used as references remain actual ancestors;
a fresh attempt from an earlier approved source does not inherit those rejected
outputs merely because they occurred earlier in the conversation.

## Review the rendered result at both scales

The padded standalone viewer deliberately exposed complete feet beyond the
game's canvas boundaries. Its motion approval did not establish that those
images could be installed without clipping. The runtime exporter must use the
actual per-frame canvases, common scale and recorded cap registration. Per-pose
foot fitting previously introduced body popping and must not return.

A common shrink was evaluated before the toe edits. Keeping cap targets fixed
would require at least a 14.14% reduction for horizontal clearance. A shared
translation could reduce that to 5.69%, but retaining approximate foot height
would lower every cap by about eight HD pixels. The targeted edits preserved
the reviewed family size instead.

Measure alpha and composited pixels when checking export differences. A maximum
straight-RGBA channel difference of 255 in frame 028 occurred at alpha 1 in both
images; its premultiplied effect was only 1. Conversely, cap-edge differences
between direct and padded filtering are real: white-background channel changes
reach 10 to 12 at five or six pixels per frame. Frame 029 has two exterior cap
fringe pixels with alpha 12 and 8. Do not describe these exports as having zero
filtered clipping. No missing opaque foot pixels were found.

The standalone route has 23 recorded positions with 120 ms per pose and a
diagnostic one-second endpoint hold. Its final transition is 025 to 027; a
blind six-frame repetition is not an exact reproduction of that route. Browser
timing tests validate the viewer's handlers and frame mapping, not the original
executable's timing or the port's native rendering.

Follow the composed preview with actual engine captures. The subsequent Linux
review covered all 42 displays and preserved every pixel outside Johnny's
placed canvas. Record selected background assets with platform and seed: the
same seed selected different oceans on Windows and Linux because their libc
random sequences differ. For local browser review, keep lossless capture PNGs
in a versioned folder beside the player rather than embedding all 84 in a
roughly 150 MB HTML document.

## Evidence

- [Expression, attempt history and standalone acceptance](../art/cartoon/walk-pilot/original-pose-corrections-v1/README.md)
- [Accepted runtime recipe and source provenance](../art/cartoon/walk-pilot/calm-focus-runtime-v1/README.md)
- [Original-first art catalog](knowledge-base/cartoon-art-metadata.md)
- [Bounded native capture logging observations](knowledge-base/pose-review-capture-notes.md)

New style packs should begin with an original-pose reference and one reviewed
character key, then prove a complete motion family at runtime scale before
expanding scene coverage.
