# Cartoon016 front waiting turn

017 appearance and the E-to-A arrival were accepted with "looks good, proceed";
see `../approval017-v1.json`. This folder starts the next pose,016, and does not
inherit artistic approval from017. Production remains unchanged.

Original016 provides the front-facing geometry. The approved017 supplies the
Calm focus identity, beard, brimmed sailor cap, proportions and shorts style.
The original32x74 canvas becomes64x148 at runtime; common generated-art scale
is0.1, with cap target[35,0.25]. The original gray shadow is not a sole anchor.

`016-front-v1.png` and `016-toe-fit-v2.png` are exact built-in imagegen outputs.
The matching `016-call-v1.json` and `016-call-v2.json` preserve every prompt and
ordered input. `provenance-v1.json` binds those outputs to the tool-cache bytes
and maps the first call's scratch original-reference path to its preserved PNG.

The first draft's right toe exceeded the exclusive runtime width by0.05HD at
the source alpha8 pixel-center threshold. The exporter refused runtime output.
A narrow image edit tucked that edge inward. It also moved the measured cap
midpoint from513 to512 source pixels, so registration was remeasured rather
than assumed unchanged. No limb warp, pose rescaling or alpha hardening was used.

The second draft passes the fixed64x148 fit. Its nearly level feet differ from
the original's small projected stagger. A color-mask comparison identifies a
possible continuity issue but does not prove foot anatomy or ground contact.
The next visual checkpoint must inspect both actual native turn directions.

| Native turn | Original sequence |
| --- | --- |
| A1 to7 |016 for120ms,017 for120ms,017 for1600ms |
| A7 to1 |016 for120ms, mirrored017 for1600ms |

The native review records a separate actual same-spot wait call before each
turn to show its starting017. Its observed first-timer duration must remain
separate from the requested turn duration. Preserve all actual origins and
reflections; do not interpolate or center each pose independently.

`EXPORT.md` documents reproduction and the exporter evidence. Native evidence
and the human request will be linked here when the review is ready.
