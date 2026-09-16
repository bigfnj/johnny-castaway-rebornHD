# V5 foot contact captures

The user accepted the shorts but identified the smaller foot still standing over
water at the mirrored arrival. These private captures test the new foot-only
candidate without changing production or earlier approvals/evidence.

`capture_contact.py` uses the unnormalized v5 runtime
`183cdf4b4f23e4164e7e290456ff8b8082301b8d952ad577b186ab4663a9c5b2`.
It runs Front turn smoke and Rear waypoint smoke then full, only to check contact.
At the same native mirrored arrival `[1,394,209,18]`, display063/4920ms, both feet
now visually reach the shore/sand. The front smoke is also grounded. Same-camera
nearest4 crops remain in the separate raw diagnostic output.

`capture_normalized.py` uses the tested color-normalized v5 runtime
`5ff919bc1db94f19ce163e990f2e00208cb74c9540656ddc8d2ddd5cf05fd15f` and
recipe `044d421dc3d0a33451f7c4dff34b9a5e375a544ddee848dca83f755b2382af8f`.
The private package replaces only018 in reviewedv2
`7a50f72fe65382917a1d38412dad97315542831ea5fd06eec9570734a7afdb52`;
all2593 other payloads remain exact. The baseline is current v2, not the older
short-torso018. Its Front turn captures are in `native-review/color-v2/front_arc`;
its waypoint captures are in `motion-v1`.

Each of Front turn, Front waypoint and Rear waypoint runs smoke before full and
fresh repeat, using the unchanged observer. Actual route/flip/origin/timing
transcripts must match reviewedv2. Every non018 image stays identical;018 changes
must remain inside its placed64x154 full canvas. `check_normalized.py` exercises
two altered actual-image buffers against the reused frozen comparison function,
with exact failures and restored positive controls. No original recapture is
needed; original-mirror-v1 remains the original geometry reference.

Run both capture helpers with Toolbox Python on the host; they locate their
pinned inputs, refuse existing scratch outputs and launch Xvfb in the pinned
Docker image with source read-only. After normalized completion, run
`check_normalized.py` in that image with `foot-v5-motion` mounted at `/out`.
Commands, source identities and per-display hashes are retained in output.
Historical evidence writers are one-time only; skip them when replaying into
fresh scratch. Contact and motion human approval remain separate from these
technical results. No shadow was generated to mask the original foot gap.
