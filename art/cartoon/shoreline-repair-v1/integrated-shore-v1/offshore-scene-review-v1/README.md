# Offshore island scene review

Open the [preserved comparison](page/review.html) or the
[local published page](http://127.0.0.1:8932/offshore-scene-review-v2/review.html).

The user has selected the offshore wave direction. This page asks for the
appearance and placement of the pumpkin, Christmas tree and New Year banner
on that island. Clovers, tides, night and Johnny's routes provide context.
It does not install or approve a production package.

Both panels use the same full-size draft decorations. Earlier Cartoon is a
private baseline package, not original artwork and not the shipped production
archive. The selected panel has the enlarged ground and offshore foam.
Low tide retains existing pixel-art beach/rock/wave layers; night and day
clouds retain their existing background artwork. These are mixed-art states,
not newly generated scenery.

The five decoration views are single native still states. Playback is disabled
there. Motion views preserve all recorded display ordinals and 20 ms port-tick
timestamps, including zero-duration display changes. Playback stops at the
recorded endpoint instead of inventing a hold or loop. Normal and Slow change
only playback speed. Both panels share the same crop, shifted by the actual
night scene offset. Full scene exposes every native pixel.

Full scenes are stored as deduplicated, unchanged 64x64 RGBA crops packed into
four lossless 2048x2048 PNG atlases. The browser reassembles their exact 1280x960
pixels; the original PNG hashes, report hashes, atlas and tile hashes, and
tile-to-frame mapping are in the manifest. Nothing is repainted,
rescaled or interpolated into the captured artwork. Only atlases needed by the
selected scene are loaded, with at most four image requests. Canvas drawing
occurs when its recorded frame or view changes. The playback clock resets when
tab visibility changes.

## Reproduce

First finish the sibling native observer's `--phase full` capture and fresh
repeats. Its source and capture requirements are in `../native/README.md`.
The historical capture directory for this review is
`build/shoreline-repair-v1/offshore-full-v1/captures`.

Run `build_review.py --captures <captures> --output <fresh review directory>`
with the toolbox Python. Then run `check_review.py --review <review> --phase
smoke` followed by the same command with `--phase regression`. The latter
requires the matching smoke record and checks reconstructed native pixels,
timestamp boundaries, still controls, both cameras, and playback controls.
`check_inputs.py --captures <captures> --work <fresh control directory>` checks
a wrong-case report, a valid PNG with one changed pixel, and refusal to overwrite
an existing output. These controls leave all native inputs unchanged.

Use fresh output directories for replay. Keep published HTML, manifests and
historical evidence unchanged. Browser checks are technical evidence only;
human seasonal placement approval remains separate. The final browser and
publication records are in `evidence/`; `evidence/evidence.json` pins each
delivered file and links the sibling frozen full native matrix evidence.
