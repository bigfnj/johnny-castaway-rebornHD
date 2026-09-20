# Targeted corrections

All 24 corrected drawings are pending appearance review. This focused page compares the exact original, the earlier selected Cartoon drawing, and the newly selected correction. It does not imply approval of the other 47 prior drawings.

The groups are five carrying-book poses, seven ruffling-book poses, four clock hands, three propeller phases, two helicopter rotor corrections, and three empty parachutes. Each row repeats the corresponding user instruction from feedback.json and uses its resource-plus-frame key, including where different resources share a frame number.

The root-owned selected-versions.json chooses the new versions. Once that file is complete, run the existing toolbox Python with `-B art/cartoon/gulls-clock-props-corrections-v2/build_review.py` from the repository root. The builder writes review.html, review-data.json, and review-record.json. Serve the repository art/cartoon directory or a containing directory so the unchanged earlier images and exact originals remain reachable through relative URLs.

The page uses the established canvas comparison approach: true image alpha over a light or dark checkerboard, nearest-neighbor display for originals, and uniform aspect-preserving display fitting using alpha8 bounds. This display fitting does not modify source files or create runtime exports. Every loaded canvas is marked with `data-loaded="true"`; the page reports 24 of 24 comparisons ready after all 72 panels have loaded. Search accepts resource names and frame numbers, and group links clear the search before navigating.

Saved requests, untouched raw outputs, generation records, original/earlier bindings, selected versions, user feedback and page identities are retained in the review provenance. Native testing and final production integration are deferred. No production archive or runtime code is changed by this review builder.
