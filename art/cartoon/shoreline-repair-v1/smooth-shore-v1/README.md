# Broad smooth shoreline shape study

The user rejected the scalloped front edge after the local contact fixes and
asked to push it farther out and smooth it substantially. This supersedes
the assumption that small extensions around individual props are the desired
island design. The generated draft replaces those notches and bumps with one
broad front curve. It remains a shape study pending human review.

`raw.png` is the unmodified built-in image-generation output. `prompt.txt` and
`generation.json` preserve the exact prompt, input identity and output identity.
`user-feedback.png` preserves the supplied crop illustrating the jagged edge.
The browser comparison only displays registered crops of the old and new raw
images. It does not claim an application render or runtime acceptance.

The new curve extends beyond the old sprite canvas union. In particular,
the gap at world X684..728 below Y662 cannot contain the broad front coast.
The old master crop also ends at world Y686. Exporting into that union would
cut the new drawing into an unwanted shape. Do not shrink, shift or crop it
back to force compliance.

Current runtime `art_style.c` and the maintained pack/catalog tooling require
the original scaled dimensions. The surface blitter uses loaded surface
dimensions, so a narrowly specified larger static island canvas appears
possible at the same origin. That is an implementation option, not yet a
validated or accepted contract change. Confirm needed extent from the chosen
drawing, update explicit pack metadata and validation together, and check
wave-base restoration, low tide, scene offsets and character ground contact.

Existing foam was authored for a smaller coast. Geometry analysis predicts
that a much larger ground mask can hide one center foam phase entirely.
After the shape is accepted, fit the wave artwork to the new coast and review
all phases in motion rather than masking away the mismatch.

Lesson: settle the overall ground silhouette and usable beach area before
fixing individual prop contacts. A smooth larger beach should not be forced
to retain the original small asset rectangles or accumulate local scallops.

Production assets, runtime code and previous review records are unchanged.
