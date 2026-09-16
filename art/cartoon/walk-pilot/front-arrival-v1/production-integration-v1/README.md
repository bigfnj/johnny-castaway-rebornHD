# Standing-family production integration

This checkpoint adds `JOHNWALK` 000, 015, 016 and 017. Its 32-asset ledger preserves all 28 prior accepted rows and the historical pilot replacement declaration. The standard `tools/art_pack.py` builder produced archive SHA256 `096a12695b4279ad9bf57537b5d6f9b18d7dab2666298ca8a4cb3fd72e0ba3d6`.

All 2,583 named member payloads equal the reviewed native private archive (`ee180c8b6aa1e07024132bae808fc4d2fcc136714dd12152468a3c9fc511aa2c`). Every one of the 2,579 previous payloads is unchanged. The ZIP files differ because the native review appended entries with copied HD metadata, while the production builder sorts and normalizes Cartoon entries. Archive envelope equality is not an artistic approval condition.

`inputs.json` binds the frozen ledgers, runtime-source map, approval records, original references, exporters and native review evidence. `verification.json` records the ordered executed commands and their log hashes. Logs live under `evidence/`; each export subfolder retains the reproduced recipe and report. Exported PNGs are reproducible and the runtime PNGs are also in production. Human acceptance is recorded separately in `../production-acceptance.json` and its linked decisions; the technical reports do not grant approval.

## Reproduce

Use Python with Pillow 12.3.0. Obtain the baseline `assets/scrantic_data.zip` from repository commit `707a20b285fea695b404a02ce9552615561b121a` into a separate file using a Git archive or binary-safe Git extraction. Verify its SHA256 is `1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63`. Keep the present checkout and historical evidence intact; the frozen ledger snapshots allow replay after later promotions. No original commercial installation, native executable or container is needed for this package reproduction.

From the repository root, with a fresh output path:

```text
python -B art/cartoon/walk-pilot/front-arrival-v1/production-integration-v1/rebuild.py --repo . --baseline build/front-arrival/production-baseline-v1.zip --output build/front-arrival/standing-reproduction
```

If the private reviewed candidate remains available, also supply `--private-candidate build/front-arrival/waits-ring-v1/candidate-v1/scrantic_data.zip`. Its exact identity and every member will then be compared independently. Without it, the helper explicitly reports that private comparison was not rerun; the pinned baseline and four approved member identities remain checked. The initial delivery supplied this private archive.

The helper reproduces all four annotated recipes, compares both padded and runtime output hashes to the original reviewed reports, runs package smoke, builds with the standard pack builder, checks every archive member and executes a corrupted-000 archive in a fresh child process. Its exact one-file failure and the executing helper hash are required before recording the control as fired. The scratch corruption is removed afterward.

`--promote` is optional and was used for the initial delivery. It only permits replacement while the current production ZIP still equals the pinned baseline and the current ledger equals the frozen 32-asset snapshot. Default reproduction does not modify production. Choose a fresh output directory on every run.

## Recorded limits

`packaging-assumption.json` retains the first failed whole-ZIP-equality assumption and its content-comparison result. The final contract compares named payloads and records the two ZIP hashes separately. No artwork or renderer failure was involved.

Native/human scope remains the approved 017 arrival, 016 front waiting turns and the two complete standing-ring orders. This checkpoint does not approve ordinary turns, profile walking or every story use of these globally addressed sprites. The distinct native timing of the two standing-ring orders is preserved.
