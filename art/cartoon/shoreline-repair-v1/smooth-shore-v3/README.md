# Two original shoreline inlets

The user approved this shape: "Yes, keep this shoreline shape." Approval covers
the sand silhouette only; scene and wave integration remain pending.
The user's arrows identify two inward recesses,
not one generic left-hand projection. Their approximate original guide centers
are X520 and X950, about 29% and 67% across the original sandy width. Preserve
these features while keeping the broader beach and smooth intervening coast.

`review.html` compares the new drawing with the authentic extracted source
artwork, using diagnostic colors. The earlier Cartoon draft is also available.
The optional vertical guides identify approximate source inlet centers, not
required exact pixel matches. The original image is never AI-redrawn.

## Authoring record

The built-in image tool made both edits. `generation.json` preserves exact
prompts, ordered references, output paths and SHA256 values. `user-feedback.png`
retains the user's two arrows. `attempt-1.png` added the second inlet but kept
the first too far left. The follow-up moved the first inlet to the right.
`raw.png` is that selected result, unchanged from the generated PNG.
Its alpha ranges from 0 to 254; the generated transparency is preserved without
forcing the interior to 255. A first inspection assumed 255 and was corrected
after reading the actual alpha range. This is not a production opacity gate.

The resulting inlet centers are approximately raw X453 and X985. With the same
display normalization used for V2, these become guide X495 and X941. The first is
still about 25 guide pixels left of the approximate source target; the second
is about 9 pixels left. This is disclosed for visual review, not represented as
an exact contour match. The left bay is more pronounced than the right one.

## Display registration

The existing V2 uniform transform is reused without refitting or deforming
the drawing: scale 0.8370423546302943, translate 116.22182340272792 and
87.36109117013643. Both panels use the registered crop `[128,330,1280,360]`.
There is no resized raster or runtime export in this folder.

Independent alpha 128 inspection found bounds `[71,353,1468,665]`, versus V2
`[75,352,1468,674]`. Across 265 upper-edge samples, the same display transform
gives 0.89 px RMS difference, 1.67 px 95th percentile and 4.19 px maximum. The right
tip stays aligned; the left tip shifts about 3 px. The lower belly is roughly
7.5 display pixels shallower than V2. Judge that difference with the inlets.

## Review boundary

This remains a shape study, without wave artwork or a production installation.
Canvas extent, fitted foam, all wave phases, low tide, shifted/night scenes,
full-size decorations and Johnny contact checks remain pending. The previous
native captures do not validate this new silhouette.

For later packs: distinguish inward recesses from outward projections, measure
their source-relative placement, and inspect the deepest point of an inlet
rather than confusing it with its steep return. Keep a small number of original
coast features instead of generating many prop-sized scallops.

## Verification

The review loaded the original and selected draft, then the previous draft
with guides enabled, without an alert. The source selector and guide toggle
were restored for the final review. Source/output hashes and exact saved
prompts were verified, as were 1536x1024 RGBA dimensions and JavaScript syntax.
The production archive hash remains unchanged. A fresh browser page also loaded
both sources without an alert; no native animation regression
claim is made for this shape-only revision.
