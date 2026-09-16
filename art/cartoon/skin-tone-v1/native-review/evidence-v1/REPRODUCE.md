# Native skin-tone evidence

This bundle preserves the completed eight-clip native comparison and its actual
failure history. It does not confer human color approval or promote an asset.
`evidence.json` binds every retained small file. `readback.json` records an
independent readback of those bytes and the binder itself. The large captures,
archives and binaries remain ignored local outputs; their identities are in
`capture-payloads.json` and `excluded-payloads.json`.

The uncorrected baseline is the selected connecting candidate-v2, SHA256
`21194cf35e5b60eebfa9ba48520509ae8f86a72f26313b945f019671d1f345c5`.
The corrected candidate-v2 is SHA256
`bdc62b0c34835196e6dfa6541ee54f9c72f9824a0c24a0beab4bee3a33393eaf`.
The correction recipe is SHA256
`021d9125b2184cd1389ba990ee6d347ef041bfcca2cec38d6d5258d0a51a2311`.
Root's `../../exports-v2/` retains the corrected PNGs, soft masks and recipe;
the native package staging additionally contains exact decoded L-mask bytes.

## Recover inputs in isolation

Use a separate checkout with the captured runtime source and production ZIP from
commit `3af0242a74f234aab231d9203b48f78ca8e5c1b4`. Keep the currently retained
connecting and skin-tone authoring bundles at their original repository-relative
paths. The captured source hashes, including the prior production archive, are
in `source-pins.json`. Verify them before running. Do not restore files over an
active production checkout or replay writers against published evidence.

Reconstruct the uncorrected package using the retained instructions in
`art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/README.md`:
re-export009-v1,010-v5 with its versioned exporter, and012-v1 at the paths pinned
by candidate-selection-v2; prepare that native baseline and candidate-version2.
The recovered package must have SHA21194cf3… before this review's preparation
accepts it. This step does not need to capture the earlier six-clip review.

Reproduce correction outputs into the fresh expected path using:

```text
python -B art/cartoon/skin-tone-v1/correct.py --output build/skin-tone/export-v2
```

Compare the resulting recipe and every output against the retained exports-v2
records. Historical helpers have fixed output roots. Use empty ignored
`build/skin-tone/native-review` and export directories in the isolated checkout.
Never copy this bundle's generated route_driver.c or trace_driver.c into that
fresh output directory before running prepare.py: preparation generates them and
refuses occupied outputs.

## Native replay

`commands.json` retains the actual host preparation, failed first capture,
successful baseline and candidate-v2 Docker invocations. Adjust only the host
bind source paths for the isolated checkout. Keep `/source` read-only, `/out`
writable, networking disabled and the pinned image identity. That image exists
locally; this repository does not claim remote image availability.

Follow `../README.md` for the exact preparation, packaging, baseline and candidate
entrypoints. Baseline execution compiles a fresh observer and an independent C
trace. It runs all eight smokes before full captures and repeats. Candidate-v2
reuses the same executable and runs the same phase ordering. No workstation
window is opened because all native windows live in Xvfb.

The first candidate-v1 attempt failed before native execution because Pillow was
absent from that image. Its exact diagnostic and preparation are retained in
`records/native/candidate-v1-launch-failure.json` and `records/native/candidate-v1/`.
The final packaging helper decodes masks on the host and binds their L bytes.
The standard-library mask adapter allows the unchanged candidate PNGs and ZIP
to run in the original image. This is a resolved harness dependency, not a
successful candidate-v1 capture or an artwork revision.

## Evidence scope

All eight full clips contain298 displays per package, repeated freshly.
Every API argument, draw, timestamp, origin and flip agrees;286 displays visibly
change only at transformed skin-mask support and12 remain identical. All28
poses are seen and all27 corrected poses visibly change.029 is the unchanged
reference. These native checks constrain the location of scene changes; the
separately retained corrector tests and independent material review establish
the intended RGB transformation and mask meaning.

The final comparison tests have2 smoke cases,6 regressions and4 executed source
mutations. The handoff checks have8 damaged-input controls. Four native controls
substitute a timestamp, unmasked sprite pixel, outside-canvas pixel, and029
reference pixel into actual captured comparisons. Positive controls pass before
and after. These exact existing results are copied without re-execution.

The old baseline build records list the helper files present when compilation
ran. Candidate-related helpers changed to remove the Pillow dependency
and add decoded mask handling before candidate-v2 capture. They were not baseline
rendering dependencies. `helpers/` holds the final native tools, while the original
build records and failure remain byte-exact. Candidate-v2 summary and the control
reports bind the final executable, comparison and checker identities actually
used. No history is rewritten to make the earlier snapshot match the final one.

`preserve.py` records and copies evidence, not artwork. It refuses to overwrite
an existing evidence.json. Its completed run was followed by a separate readback
of all manifest entries; no previously passed native or authoring gate was rerun.
