# Revised018 native arrival motion

The user accepted the latest still proportions with "much better proceed".
This checkpoint retains that still-approved runtime PNG, adds arrival motion
verification, and does not grant motion approval or change production.

Candidate archive remains byte-for-byte
`7a50f72fe65382917a1d38412dad97315542831ea5fd06eec9570734a7afdb52`;
018 PNG remains
`21cf94cd90d369b20b6d3b8ef60b7cc2848f919ff828578320502aec9a17c55b`.
Observer binary remains
`203aebb8c15881a41108b2b4fb97f5f9c6d025aa595a678b4dd84906011f7563`.

The existing Front turn smoke/full/fresh-repeat checkpoint is linked by exact
report and log hashes from `native-review/color-v2/front_arc`. It is never
rewritten. New captures live in `build/standing018-proportions/motion-v1`:

- Front waypoint: unmirrored023 to018 at the same logical origin `(433,225)`;
  first018 appears at3240ms. This clip has54 displays and4840ms total duration.
- Rear waypoint: mirrored022 to018, with arrival018 at `(394,209)` from4920ms.
  This clip has74 displays and6520ms total duration. Its starting unmirrored018
  at `(452,254)` is also covered.

Each new clip runs smoke before full and fresh repeat. The earlier accepted-color
baseline is `build/skin-tone/native-review/candidate-v2`, archive
`bdc62b0c34835196e6dfa6541ee54f9c72f9824a0c24a0beab4bee3a33393eaf`.
Actual API, chosen path, draw/flip, delay and display-time transcripts must match
that baseline. Every non018 display remains identical. All018 differences must
stay inside its correctly placed64x154 full canvas; the unchanged renderer
mirrors that canvas about its own width at the recorded origin. A fresh repeat
must reproduce every pixel hash and observed time exactly.

Run `capture_motion.py` on the host with Toolbox Python after the pinned prior
candidate, observer and skin baseline captures exist. It refuses an existing
output directory, mounts source read-only and runs the pinned Docker image with
Xvfb. The actual launch command and source fingerprints are retained in output.
Then run `check_motion.py` in the same image/mounts without Xvfb to exercise the
mirrored018 outside-canvas and retained023 pixel controls. Both operate on copied
memory buffers and leave capture files untouched.

These are port-rendered motion checks, not original-executable timing parity.
The browser and human motion decision are separate. On replay, use fresh scratch
and do not rerun historical evidence writers into their existing destinations.
