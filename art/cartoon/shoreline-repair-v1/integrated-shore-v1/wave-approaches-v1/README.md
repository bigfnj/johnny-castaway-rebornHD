# Three-way clover wave comparison

Status: human art review pending. Open [review.html](review.html).

| Panel | What it shows |
| --- | --- |
| Original source | Authentic original island, wave and clover sprites rendered by the port at nearest 2x. Colors are diagnostic. This is not original-executable footage. |
| Cartoon offshore ripples | Approved enlarged island and full-size V5 clovers, with the earlier center foam constrained outside the sand. |
| Cartoon wash onto sand | The same island and clovers, with a new transparent water-and-foam layer allowed to cross the sand edge. |

Only center wave frames 006, 007 and 008 differ between the Cartoon packages.
The six side-wave frames are identical. Side-wave run-up remains follow-up work
after this direction review. The approved sand silhouette is unchanged.

Each native clip contains 51 display records over 2400 ms from twenty actual
same-heading waits. All nine high-tide wave phases occur. The page loops the
first complete 1440 ms wave cycle using those observed timestamps, with no
interpolation or invented holds. Each family's phases are staggered as in the
port. The full reports retain all native displays, including repeated pixels.

The page defaults to a close-up of the clovers. Whole island, slow playback,
phase stepping and timeline scrubbing are available. Source pixels are only
cropped for delivery; the page uses the same world-coordinate crop in all panels.
The native reference's colors are not a calibrated original palette.

## Reproduction and evidence

The sibling [native observer](../native/README.md) records package creation,
native build and capture commands. Each clip must pass smoke and then match a
fresh native repeat before `prepare.py` packages it. Its arguments point to the
three `smoke` directories; it verifies report status, source image hashes,
timing/pose agreement, wave coverage, repeat agreement and loop closure.

[manifest.json](manifest.json) retains exact report, executable, archive and
image hashes. Each panel's `native-report.json` is a byte-for-byte copy of the
native report; display PNGs are unchanged pixel crops with their own hashes.
The two art recipes and raw generation prompts remain in
[foam-refresh-v1](../foam-refresh-v1/README.md) and
[wash-over-sand-v1](../wash-over-sand-v1/README.md).

The incoming generation's requested phase order did not exactly match its
output. Source drawings were assigned by measured crest position, preserving
their pixels and shared registration. The low-crest phase has a broader water
ribbon, so human motion review matters. Technical checks do not approve it.
