# Delivery evidence in the Git index

`spec.json` explicitly lists the copied-file fields of the selected motion,
package, native, promotion, authoring and Windows evidence binders. It also
checks selected source/approval inputs and final production identities. Each
binder is itself checked. Scratch captures and historical references to the
old production ZIP are not mistaken for files that should be copied.

After staging the declared files, run:

```text
python -B art/cartoon/shoreline-repair-v1/integration-v1/index-final/check.py --spec art/cartoon/shoreline-repair-v1/integration-v1/index-final/spec.json --output build/shoreline-index-fresh
```

The checker reads actual indexed blobs, not just worktree files. A disposable
index then drops one bound capture log and must produce exactly its missing-path
failure. A second control changes that indexed log's bytes and must produce
exactly its byte-mismatch failure. The actual index is checked again and must
remain unchanged. The successful final result is retained beside this guide.

This is a scoped delivery check. Generalizing binder discovery into maintained
authoring tooling remains in BACKLOG.md. Git text conversion can change ordinary
source file line endings; immutable art evidence uses its existing `-text`
attributes, and this check preserves its recorded file-byte hashes.
