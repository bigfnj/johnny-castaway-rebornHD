# Approved island integration and wave studies

The user approved the [two-inlet shoreline](../smooth-shore-v3/README.md).
This folder integrates that exact drawing into a larger registered static
canvas, retaining full-size decorations and logical scene positions.

The static ground occupies a 640 by 180 canvas at offset [-36, -10] from the
original HD sprite origin. Every ground pixel belongs to this one surface.
Historical wave frames were first alpha-masked against it as a diagnostic;
that hides most center foam and is not a completed wave replacement.

The user corrected the next step: original water washes onto sand instead of
only radiating away. The [three-way animated study](wave-approaches-v1/README.md)
compares authentic source animation, offshore ripples and incoming water, all
with St Patrick's Day clovers. The center overlay uses a shared 384 by 256 canvas
at offset [-32, -90], preserving the full generated drawing at a uniform scale.

The user selected the offshore ripple version in the three-way comparison.
The [selection record](wave-approaches-v1/selection.json) preserves the exact
shown artwork and motion. Keep that selected look, including its displayed
side waves. The wider native matrix passed all 24 smoke captures, followed by
24 exact fresh-process repeats and six negative controls. The production
archive is unchanged. The user [requested placement adjustments](seasonal-placement-review.json)
after reviewing the seasonal scene. The pumpkin and tree are accepted; only
the New Year banner needs visible attachments to the palm. That revision and
a comparison prompted by the user's wave-density observation remain pending.

The [seasonal scene review](offshore-scene-review-v1/README.md) presents those
placements with the unchanged full-size props. Its browser smoke and regression
checks passed against exact native pixels and timing across ten scenes.
The [integration plan](integration-plan.json) records the prospective package
and provenance changes for promotion after that review.

Exact static export inputs and outputs are in `recipe-v1.json` and
`candidates/v1/export-report.json`. Smoke and regression records accompany the
exporter. [Native capture instructions](native/README.md) describe actual port
timing and the scope of the source-art reference.
