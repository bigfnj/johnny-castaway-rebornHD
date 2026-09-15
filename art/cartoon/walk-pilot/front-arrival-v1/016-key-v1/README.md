# Cartoon016 front waiting turn

017 appearance and the E-to-A arrival were accepted with "looks good, proceed";
see `../approval017-v1.json`. The user subsequently accepted016 and both reviewed
front turns with "Yes, keep this turn"; see `approval-v1.json`. This is a separate
approval from017. Production remains unchanged.

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
Both actual native turn directions were reviewed and accepted as shown; that
artistic acceptance does not relabel the drawing as exact original anatomy.

| Native turn | Original sequence |
| --- | --- |
| A1 to7 |016 for120ms,017 for120ms,017 for1600ms |
| A7 to1 |016 for120ms, mirrored017 for1600ms |

The native review records a separate actual same-spot wait call before each
turn to show its starting017. Its observed first-timer duration must remain
separate from the requested turn duration. Preserve all actual origins and
reflections; do not interpolate or center each pose independently.

`EXPORT.md` documents reproduction and the exporter evidence. The native review
is at http://127.0.0.1:8932/front-turn016-v1/review.html; the exact human question
and selected identities are retained in `review-request-v1.json`.

Both native directions passed smoke followed by full regression, retaining
18 and16 displays over1960ms and1840ms respectively. Only the two016 displays
per clip change; the other30 displays and all pixels outside016 remain exact.
The original017 private baseline and the full production archive remain intact.
The published page passed69 served-file identity checks followed by browser
checks for both directions, native pixels, logical timing, controls and crops.
The subsequent human judgment accepted the displayed foot motion in both turns.

Native helpers, reports and reconstruction notes are preserved under
`review-evidence/native-v1/`. Large native captures and private ZIPs remain local
scratch artifacts; their recorded hashes do not imply permanent availability.
