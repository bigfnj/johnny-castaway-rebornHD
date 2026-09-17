# Footprint implementation verification

This checkpoint verifies the two named runtime footprint contracts and their
authoring declarations. It does not promote shoreline artwork or establish
visual approval. Original resource dimensions, legacy PNG behavior and the
production ZIP remain unchanged.

`verification.json` records the final 384x256 center contract run: compiled
smoke before regression, six rebuilt source mutations with exact failure
witnesses, authoring smoke before regression, five authoring mutations, and
Linux gate ordering/early-stop controls. `compiled`, `authoring` and
`linux-flow` contain the small results and logs. Binary hashes and rebuild
witnesses are retained; executables are omitted.

The initial stale catalog reproduction failure is retained separately. The
catalog was regenerated for the changed island source and learning-document
hashes, then fresh smoke and regression passed. Earlier scratch runs with
superseded footprint dimensions are not evidence for the final contract.

Windows results are separate additions: v1 stopped during configure because
the scratch copier omitted `cmake/RuntimeData.cmake`. It did not run tests.
The v2 copy includes that directory and uses the unchanged test writer under
Windows PowerShell 5.1 on an inactive desktop. Its result and exact logs state
whether smoke and mutation execution completed. The historical Linux summary
predates this separate Windows run; its stated Windows limit is not rewritten.

The helper `.py.txt` files are exact scratch snapshots, not directly runnable
at this preserved location. To replay, restore them to
`build/shoreline-repair-v1/footprint-tests/`, use fresh output directories,
and run with the installed toolbox Python. `run_windows_ps51.py` creates an
isolated source copy and uses the retained existing inactive-desktop API;
its inputs pin that helper. The byte-identical helper is already retained at
`art/cartoon/skin-tone-v1/integration-v1/windows-v1/helpers/motion_review.py`
(SHA256 `86312fd1bad0786c2e1ee56c9eb6aab69cb1bf9f1295ec84430769877490f55d`).
For replay, set the scratch launcher's `HELPER` to that retained file instead
of relying on the historical workstation path. It never changes the shared
runtime. The compiled
Linux probe commands are documented in `docs/cartoon-footprint-contract.md`.
Do not rerun this one-time preservation writer over the historical bundle.

The full selected-art tide/night/scene-offset/character matrix remains a
separate requirement once the wave direction is approved. No such coverage is
claimed here.
