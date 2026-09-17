# Incoming water study

Status: proposed center-wave artwork, awaiting human motion review. Nothing in
this folder approves or promotes an application asset.

The user corrected the offshore-only interpretation: original water advances
onto the island and then exposes sand again. The original center cycle is
006, 007, 008, then 006. Its inner water boundary moves locally by about 2 to 8
HD pixels; the three shoreline families update at staggered times.

These three drawings were created with built-in image_gen. Exact prompts,
ordered references, original output locations, hashes and final frame assignment
are in [generation.json](generation.json). Raw filenames record generation
order, not runtime assignment. Measured crest positions put draft 007 first,
draft 006 second, and draft 008 third. The lower-water drawing has more overall
water alpha, so this is a motion study, not a claim of original frame parity.

All use the same quarter-scale registration and the full 384 by 256 canvas.
No phase is moved, fitted, shrunk or clipped independently. Water intentionally
overlaps the approved ground; an inverse-ground mask would erase the behavior
being evaluated. The runtime restores the static background before composing
the next transparent wave state.

The approved island and full-size V5 clovers remain fixed. Side waves are held
constant in both Cartoon variants to isolate this center-shore decision. The
[three-way comparison](../wave-approaches-v1/review.html) includes authentic
original source artwork rendered by the port with diagnostic colors.
