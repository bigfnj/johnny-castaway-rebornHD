# Reconstruct the matched island diagnostic

Use a disposable checkout containing these seasonal helpers and the source revisions pinned by `source-identity.json`. The engine source was unchanged from commit `397edf8e4b34191ade4be13bc93a215f73b0c631`. The required production archive is SHA256 `4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`. Later seasonal promotion requires recovering that prior archive into the disposable checkout, not changing a current production installation.

Prerequisites are Docker with the already provisioned Linux build image `sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`, host Python with Pillow, the tracked `art/cartoon/character-inventory-v1/reference-originals.zip`, and the original resource pair at the local path expected by `prepare.py`. The captured host used Pillow 12.2.0. Text label rendering in the comparison sheets is diagnostic presentation, not a production asset export contract.

The supplied `RESOURCE.MAP` hash is `3d9ec330aab96bbe5a44ce34f5945703862e82b195088590b7adfef5d7345da7`; `RESOURCE.001` is `df9c2213f7c0abacf4e302cb53a476f9f220579c07ba350b167e351eed548eae`. `prepare.py` verifies these against the retained source catalog. If that user-local installation is unavailable, provide the exact pair in a disposable environment before running. Do not substitute the bundled resource pair silently.

Restore `helpers/prepare.py`, `capture.py`, `run.py`, `measure.py` and `matched_clover.py` to the fresh directory `build/seasonal-v1/island-footprint/` in that checkout. Their `parents[3]` root calculation requires exactly that scratch depth. Do not execute them in this evidence directory. Restore the pinned seasonal native dependencies at their repository paths, including `art/cartoon/seasonal-v1/native/capture.py` and `driver.c`; snapshots are in `helpers/dependencies/`. The pinned capture codec remains at `art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py`. Verify these and the compiled source hashes using `source-identity.json` before capture.

Run one command at a time from the disposable checkout root:

```text
python build/seasonal-v1/island-footprint/prepare.py
python build/seasonal-v1/island-footprint/run.py
python build/seasonal-v1/island-footprint/measure.py
python build/seasonal-v1/island-footprint/matched_clover.py
```

`prepare.py` refuses an existing original-only diagnostic ZIP and creates the adapted scratch driver, source-image extracts, and `preparation.json`. `run.py` compiles that driver against unchanged native engine/platform sources in the pinned container, then captures original/HD/Cartoon by high/low tide by no-holiday/clover. Each art variant starts with a no-holiday high-tide smoke. These are 12 bounded diagnostic stills, not another full regression or timing matrix. The container has no network, mounts the checkout read-only, uses Xvfb rather than the workstation display, and is removed explicitly.

`measure.py` reads the six no-holiday scenes and original clover reference, then recreates the column measurements and two diagnostic diagrams. `matched_clover.py` creates one additional private original-scene archive with only the exact existing HD clover restored, captures it with the same compiled driver, and compares it to the existing Cartoon high-tide clover scene. Its container is also removed. It writes the two matched PNGs and `matched-clover.json`.

The preserved `matched_clover.py` is the cleaned reproducible helper: after the successful capture, one unreachable `if False` image-save expression was removed. No executed behavior or captured output changed; the binder describes this source-only cleanup rather than claiming those exact helper bytes launched the earlier capture. All other scratch helper snapshots are the bytes used for their recorded outputs.

For readback, compare the retained input/source hashes and decoded capture pixel hashes first. ZIP envelopes and generated label PNG bytes can depend on tool versions; those differences must not be treated as visual differences. The current measurements and matched PNGs are byte-bound by `evidence.json`. Reproduction outputs belong in the disposable scratch directory. Never overwrite these historical reports or rerun a preservation writer into this bundle.
