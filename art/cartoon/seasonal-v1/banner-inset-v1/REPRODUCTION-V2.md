# Explicit recipe bytes for integration

Use `export_v2.py`, `recipe-v2.json` and `candidates/v2/` for future integration. This revision corrects recipe serialization and leaves every runtime PNG and the padded banner byte-identical to the shown V1.

V1's inherited export report hashed canonical UTF-8/LF recipe content, SHA256 `94df1f95fa15d03566191faefcea92b415838ad66e5e212fbea2102c13b5a5cb`. Its Windows `write_text` call saved CRLF bytes, whose actual SHA256 is `4a2129320c6527306465206149e279c5b183ecb3730a66d752ccb2c46b03ed9d`. The source pixels, PNGs and recorded native/browser display are unaffected. V1's files, source snapshots, metadata discrepancy and shown evidence are retained unchanged as history.

V2 writes the exact UTF-8/LF bytes with `write_bytes`, and verifies that the saved recipe SHA256 equals the report's `recipe_sha256`. It refuses a noncanonical recipe before producing output. Smoke passed this byte binding and all payload comparisons. Regression invoked a fresh exporter process for exact replay, then a second fresh process with a deliberately CRLF-damaged copy: it failed once with `recipe-crlf.json: recipe bytes must be canonical UTF-8 LF`, printed the executed exporter SHA witness, and created no output. The unchanged canonical recipe remained valid afterward.

Selected V2 recipe SHA256 is `94df1f95fa15d03566191faefcea92b415838ad66e5e212fbea2102c13b5a5cb`. Runtime003 remains `e36e103027d2eee53c58c903cd397770a66e5ffce2683e9c0c8ce6e2d988ff92`, exactly the pixel payload shown at <http://127.0.0.1:8932/banner-inset-v1/review.html>. The PNG identity permits reuse of the preserved native and browser checks without new captures or publication. No final human approval or production promotion is implied.

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/seasonal-v1/banner-inset-v1/export_v2.py --recipe art/cartoon/seasonal-v1/banner-inset-v1/recipe-v2.json --output art/cartoon/seasonal-v1/banner-inset-v1/candidates/v2 --check
```

For a fresh reproduction, omit `--check` and choose a new output directory. `verification-v2-smoke.json` and `verification-v2-regression.json` preserve executed checks and commands. `reproduction-v2.json` binds this corrected authoring set to the historical shown PNG and native/browser binders. Earlier evidence writers must not be rerun into their frozen paths.
