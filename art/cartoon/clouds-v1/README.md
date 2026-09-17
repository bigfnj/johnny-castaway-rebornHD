# Cartoon moving clouds

The user accepted the displayed clouds with "Yes, keep these clouds". See
`integration-v1/production-acceptance.json` and the
[delivery verification](../../../docs/cartoon-clouds-verification.md).
Earlier generation, recipe and native evidence retain their pending status as
historical checkpoints; the later acceptance record binds the exact reviewed art.

The ordinary island cloud selector draws `BACKGRND.BMP` frames 015, 016 and
017. Frame 015 is already approved Cartoon artwork. This batch prepares the
two companion drawings at their existing 384 x 114 and 528 x 152 HD canvases.
The original drawings guide silhouette and placement; the approved cloud guides
color and line treatment. The existing approved 015 remains unchanged.

`CLOUDS.BMP` is a separate four-slot resource. Its name does not establish a
runtime use: the current source and recorded script map do not prove one.
Those drawings are outside this batch until their use is established.

## Baseline

- Source commit: `de1e489e5c2fe3b22d03e8650bfc26cc1d8a12cc`.
- Production archive: `assets/scrantic_data.zip`.
- Archive SHA-256: `a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66`.
- Existing production coverage: 61 approved Cartoon assets, partial coverage.
- Branch: `art/cartoon-clouds`.

## Records

`prepare_style.py` extracts exact approved style references. It makes no pixel
edits. `style-reference/source.json` binds these copies to their source members.
The original-reference export and runtime preflight are recorded separately.

Selected exports are `export/BMP/BACKGRND.BMP/016.png` and `017.png`.
`generation/record.json` identifies the four raw tool outputs, selected v2
drawings and edit ancestry. Exact prompts and ordered local references are in
`generation/requests.json`, `016-v2-request.json` and `017-v2-request.json`.
`recipe.json` binds the export inputs and fixed uniform transforms.

The medium cloud's v2 silhouette is slightly shallower than the original. Its
alpha-8 area is about 89 percent of the original silhouette; the larger cloud's
is about 100 percent. These diagnostic area comparisons do not establish art
approval. See `preflight/generated-fit-review.md` for the measurements and
`export/comparison.png` for original-versus-Cartoon drawings at equal HD scale.

Generated artwork uses the built-in image tool, one call per cloud and revision.
Raw output, exact prompts and ordered reference paths are retained. Technical
export uses a documented uniform scale and translation with premultiplied alpha
filtering. No alpha threshold, background key or painted silhouette correction
is applied.

Review must show native movement in both wind directions beside the existing
clouds, with the approved island and ripple assets from this baseline. Explicit
fixture state must be identified as such. Human art approval is separate from
technical checks, and production integration follows that approval.
