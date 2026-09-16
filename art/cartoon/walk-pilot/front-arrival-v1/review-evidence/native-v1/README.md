# Current front walk and standing017 baseline

This scratch bundle records the current-main native E-to-A route, labeled
"Current Cartoon walk + HD standing017". It retains all approved024-029 runtime
bytes. There is no candidate017 artwork, production edit, publication, or human
approval in this bundle.

The exact production archive is SHA256
`1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63`.
The checkout is main commit `707a20b285fea695b404a02ce9552615561b121a` on the
isolated arrival feature branch. The preserved front observer is copied byte
for byte. It calls the actual `adsPlayWalk(4,1,0,1)` and observes completed waits,
draw/flip calls, walk delay returns and rendered window pixels.

The local Linux image is
`sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`.
Use its existing `johnny-platform-cleanup:latest` tag, with the repository
read-only at `/source` and this scratch directory writable at `/out`.
Use Docker `--rm --init --network none`; Xvfb is the only display. No native
window is opened on the workstation, and no tools are installed.

Preparation runs on the host:

```text
python -B build/front-arrival/native/prepare.py
python -B build/front-arrival/native/adapt_candidate.py
```

Then run the image command:

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture.py
```

The native program is freshly compiled from the read-only current source, with
full arguments, compiler version, binary identity, build timestamp and protected
source identities recorded in `baseline-v1/build.json`. Native smoke executes
before full-route regression and a fresh-process repeat. Each phase retains its
logs, PPMs, PNGs and detailed report, including failures. Existing output paths
are refused; use a fresh versioned scratch directory for another capture.

Record the fixed camera after baseline capture:

```text
python -B build/front-arrival/native/finish.py
```

The full view is 1280×960. The fixed close-up is HD `[560,400,400,280]`, computed
against the route-wide full canvas union, with no per-pose recentering. The
actual origin is the stored walk row's x minus one and its unchanged y.
Logical maxspeed timing is preserved; this is not a physical wall-clock or
original-executable parity claim. Supplied-original artwork geometry remains
separate from this current-port baseline.

Run the mask smoke, regression controls and an executed mask-removal mutation
inside the same mounted image, without Xvfb:

```text
python3 -B /out/check_helpers.py
```

## Future candidate017 handoff

`prepare_candidate.py` accepts one explicitly hash-bound runtime PNG. It checks
8-bit non-interlaced RGBA and the original doubled017 canvas. The candidate ZIP
adds exactly `data/styles/cartoon/BMP/JOHNWALK.BMP/017.png`; every existing member
is checked byte-for-byte, including all six approved walk frames and the HD017
fallback. This is a private candidate, never a production modification. The
authoring exporter still owns silhouette fit and provenance validation.

```text
python -B build/front-arrival/native/prepare_candidate.py --png PATH_TO_RUNTIME_017 --expected-sha256 EXACT_PNG_HASH
```

Only after a valid candidate is provided, run under the same Xvfb image:

```text
xvfb-run -a -s "-screen 0 1280x960x24" python3 -B /out/capture_candidate.py
```

That helper reuses the bound native executable, runs candidate smoke before
full-route regression, requires every travel display to remain pixel-identical,
and permits a change only inside the actual mirrored017 canvas. All timestamps,
origins, flips and delays must match. Loaded dependencies may differ only by
HD017 becoming Cartoon017. Candidate packaging and native candidate execution
have not been exercised yet because candidate artwork has not been selected.
