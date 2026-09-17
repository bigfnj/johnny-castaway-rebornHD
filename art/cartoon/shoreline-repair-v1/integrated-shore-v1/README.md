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

The original side waves are held constant between Cartoon variants for the
center decision. Native scene acceptance, side-wave behavior, the wider tide
and holiday matrix, and production promotion remain pending. The production
archive is not changed by these studies.

Exact static export inputs and outputs are in `recipe-v1.json` and
`candidates/v1/export-report.json`. Smoke and regression records accompany the
exporter. [Native capture instructions](native/README.md) describe actual port
timing and the scope of the source-art reference.
