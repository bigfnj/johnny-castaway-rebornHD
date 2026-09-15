# Cartoon rear arrival: frame 018

The user approved this standing pose at the end of the rear walk with
"nailed it, proceed". Production now contains 28 approved assets: twelve
walking poses, this standing pose and fifteen island layers.
The [acceptance](production-acceptance.json) records the exact question,
answer and reviewed bytes; it explicitly inherits the previous 27 approvals.

The original 018 pixels define pose geometry; approved rear frame 023 defines
the Cartoon design. The visible elbow bends out and the hand returns to the
shorts/pocket area. The two resting feet retain their depth offset rather than
sharing an artificial horizontal ground line. Exact prompts are in prompts.json.

Use the established common scale and cap registration. Reference, export and
native review evidence will retain their own identities and limitations.
Do not treat a generated drawing, technical fit or similarity to approved 023
as human approval of this new pose.

## First arrival review

The candidate is shown at
http://127.0.0.1:8932/arrival-cartoon-v1/review.html . Use Normal speed and the
right-hand "New Cartoon arrival" panel. The actual 23-pose rear walk is
unchanged; only the following standing frame 018 differs. The 1,600 ms hold
and the original route's draw-origin shift are preserved. Close-up uses a fixed
camera so the shift remains visible.

Judge the last step into the relaxed stand and the smaller foot's contact with
the sand. Its vertical separation from the nearer foot is greater than in the
original reference; that pixel-region observation is not an anatomical contact
measurement. No additional draw offset or independent scale adjustment was
used to hide the difference.

`candidate-recipe-v1.json` and `candidate-export-v1.json` preserve the exact
reviewed export. The raw image SHA256 is
`4ed63ba9245dd30ac414caadba1a13febac240ffcbfa767c4f939a4bd83ddab2`;
the runtime candidate SHA256 is
`5ab7fb306a39eab69d419f3602101a72e3cca30d15e6432c58a6beaf975e9190`.
The native comparison changes only 018 inside a private archive. Production
promotion uses the existing pack builder and preserves all 2,578 prior members;
every uncompressed member matches the private reviewed candidate. The
[package verification](production-verification.json) records both ZIP hashes.

`prompts.json`, `provenance.json` and `motion-review-v1.json` retain their
historical pending statuses. Later approval lives in the separate acceptance
record. `runtime-recipe-v1.json` adds canonical paths and accepted PNG hashes
to the preserved candidate recipe without altering its rendering fields.
This export used Pillow 12.2.0, distinct from the earlier rear export's 12.3.0.

Read the [arrival lessons](../../../docs/art-style-learnings-arrival.md) before
expanding another waiting/turning family. The [delivery verification](../../../docs/cartoon-arrival-verification.md)
records tests and integration separately from human appearance approval.
