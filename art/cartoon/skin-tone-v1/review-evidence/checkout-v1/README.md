# Byte-preserving checkout check

The new skin bundle contains hashes of scripts and JSON as well as PNGs.
Its `.gitattributes` entry disables text conversion, matching existing art
bundles. A temporary real Git index and fresh checkout with Windows autocrlf
preserved the corrector bytes. Removing the entry changed the corrector's
bytes and triggered its named identity failure; restoring the entry passed.

`report.json` retains all three cases. The script was executed from
`build/connecting-analysis/test_skin_checkout.py`; to replay, copy it there in
an isolated repository copy with this historical evidence output absent.
It creates and cleans only its own temporary Git repositories and never stages
or changes the application repository's index.
