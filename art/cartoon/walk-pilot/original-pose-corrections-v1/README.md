# Original-pose review and expression direction

The user selected **6. Calm focus** on 2026-09-15. This approves an expression
direction for subsequent work across the complete walking family. It does not
approve new runtime sprites. The 21 production assets remain unchanged.

[acceptance.json](acceptance.json) records the selection separately from the
historical awaiting-selection status in [expression-prompt.json](expression-prompt.json).

![Six expression concepts](expressions-v1.png)

The sheet's reading order is Curious, Considering, Knowing, Discerning,
Intrigued, and Calm focus. The preserved 1222 by 1287 PNG is the exact returned
image, including its background/alpha and labels. It has not been cropped,
resized, cleaned or extracted into sprites.

## Source and generation

The built-in image generator received the exact prompt in
`expression-prompt.json` and one explicit image reference: the accepted
1024 by 1536 `024-generated-v7.png` from the existing
[directional-cycle source bundle](../directional-cycle-v1/README.md).
Its SHA-256 is
`63088f5c18e71d49fb61f733e564d5f9461c55f622e124b5eeaf9aa5cbd1ee2b`.

[provenance.json](provenance.json) records the actual tool parameters, reference
order, returned file identity and both exact prompt-string and prompt-file
hashes. The original raw reference already exists in its source bundle, so it
is not duplicated here. No rejected pose correction was used as an expression
reference.

## Rejected first pose attempts

Before the expression selection, the assistant rejected three generated pose
attempts after visual review:

| Frame | Attempt | Reason |
|---|---|---|
| 024 | correction v1 | Better inward foot angle, but the trailing foot was raised. |
| 028 | correction v1 | No clear correction of the anatomical leg-order reversal. |
| 029 | correction v1 | Overlap changed, but the head shifted upward and the cap clipped. |

Their exact prompts and reference order remain in [prompts.json](prompts.json).
The provenance records their output hashes, dimensions and rejection reasons.
Unused failed PNGs remain local; they are neither promoted nor claimed as
ancestors of the selected expression concept.

## Original geometry references

The pose attempts used full native canvases from the supplied-original RESOURCE
dump, enlarged by exactly 16 with nearest-neighbor sampling. BMP palette index
0 became transparent RGBA zero; other dump-palette colors remained unchanged.
The preparation verified independently repeated native bytes and copied the
accepted Cartoon raw references byte-for-byte.

The provenance retains the original resource, decoder, dump, native PNG and
16x-reference hashes, canvas dimensions, preparation method and Python/Pillow
versions. Original PNGs and binaries are not duplicated. Original-executable
palette, compositing and rendering parity are not established by these decoded
references. The new expression is an artistic direction, not evidence of the
original character's facial expression.
