# Wait/turn trace evidence

`trace.py` and `trace.json` are exact snapshots from the first batch inventory.
The report covers489 supplied-original walk rows,41 original and41 port TTM
identities, and116 cases compiled from the production C state machine. It does
not render the original executable or grant artwork approval.

Reconstruction requires a separate checkout of base commit
`707a20b285fea695b404a02ce9552615561b121a`, the supplied original Windows
installation containing `WINDOWS/SCRANTIC.EXE` and
`SIERRA/SCRANTIC/RESOURCE.MAP`/`RESOURCE.001`, a compatible existing decoder
probe, and the local `johnny-platform-cleanup:latest` container image identified
in the report. Original binaries and that image are not bundled here.

First stage an exact copy of the preserved `trace.py` at
`build/front-arrival/trace/trace.py` in the reconstruction checkout. The helper
launches that exact repo-relative path inside its read-only Docker mount, so
running only the preserved file is insufficient. Then invoke the staged helper
with `--repo CHECKOUT --original-root ORIGINAL_INSTALL --probe DECODER_PROBE`.
It validates original byte identities against stored source records. The output
is `CHECKOUT/build/front-arrival/trace/trace.json`, irrespective of the invocation
location. Use a fresh scratch checkout to retain previous results.

The script's original docstring describes its original scratch placement.
The trace may update its reported source commit when run from a different
checkout; that is new evidence and must not overwrite this preserved report.
