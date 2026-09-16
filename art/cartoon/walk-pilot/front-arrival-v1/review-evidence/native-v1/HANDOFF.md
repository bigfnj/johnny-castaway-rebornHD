# Standing017 native comparison handoff

The proposed standing017 review is published at
http://127.0.0.1:8932/front-arrival017-v1/review.html.
Human approval is pending. Production artwork is unchanged.

The page compares "Current Cartoon walk + HD standing017" with
"Same walk + new Cartoon017". It uses the actual engine E-to-A route, with all
23 approved walking poses followed by mirrored017. Show arrival pauses on the
first arrival display at 2760ms and switches to the fixed close-up. Replay walk
restarts the complete recording; Previous/Next step through distinct poses.
Normal and Slow play the recorded logical cadence. Repetition does not append
a fabricated return walk or turn.

The fixed camera is HD `[560,400,400,280]`. The mirrored017 canvas is
`[586,486,666,636]`, drawn at logical `(293,243)` after walking027 at `(300,242)`.
The 47 native displays span 4360ms, including background updates and the
zero-duration completion witness. Arrival holds for 1600ms. These are port
pixels and logical timing under Linux/Xvfb, not DOSBox or original-binary parity.

| Evidence | Result |
| --- | --- |
| Current baseline | Smoke, full route and exact fresh-process repeat passed |
| Candidate packaging | Exactly one new Cartoon017 ZIP member; all2579 existing members preserved |
| Candidate native | Smoke then full regression passed; 12 arrival displays change only inside017, 35 displays remain pixel-identical |
| Route invariants | All47 timestamps, actual origins, draw/flip calls and delay returns match |
| Dependencies | Only HD017 becomes Cartoon017; approved024-029 and island dependencies remain unchanged |
| Canvas mask | Exact-native-pixel smoke plus five controls passed; rebuilt and executed mask-removal mutation fired |
| Browser | Two smoke checks, four regression groups and three served/executed mutations passed |
| Publication | 95 served HTML/image identities followed by exact47 timestamp and94 rendered pixel checks; controls and1280 layout passed |

Selected source artwork is `017-foot-depth-v3.png`; exact runtime017 SHA256 is
`60e3a77a64620502d2b5198911a7805e19aaedf07801c7a00a92c030b4924de1`.
Its exporter recipe SHA256 is
`32b7588894a0ef9b2aa623b2da5fd5aaaa25af362b61e985a8b4eaa41af34d85`.
The private candidate archive SHA256 is
`795c2ad7fda8586f68d07714e36dc85ec3d2954fd25cd8b3d1c52d94dc55327b`.
The production archive remains
`1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63`.

`review-evidence.json` binds helpers, phase logs/reports, exporter inputs and94
native PNG identities using portable paths. The executable, private ZIP and full
capture image sets remain local scratch artifacts. Root can preserve selected
helpers/reports after review without duplicating these large files.

`README.md` and `evidence.json` retain the earlier baseline-only checkpoint;
their statement that candidate artwork was pending describes that stage. This
handoff and `review-evidence.json` describe the later completed comparison.

All publication copies contain only `review.html` and `images/`. Deliberately
broken browser mutation pages remain in local evidence and were not published.
The helpers refuse existing capture/output directories to retain prior evidence.
