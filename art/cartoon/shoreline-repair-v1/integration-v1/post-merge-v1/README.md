# Fresh main audit records

These records belong to merged main `9b0a4ed1fb5920faf426c4d3aa89e45afadebf07`.
See the [audit](../../../../../docs/cartoon-seasonal-post-merge-audit.md) for the
results, unresolved backlog and validation limits.

`evidence.json` binds the copied reports, fresh package/CI/index results,
deployment identities and collection script. The script requires the original
scratch records and is a record of collection, not a command to regenerate the
review findings. The executable and screensaver are separate CMake targets.

`index-spec.json` extends the previous delivery's explicit binder list with
these copied records and `../windows-final/main-v1/`. Run the unchanged checker
with this specification and a fresh scratch output directory. Its missing-file
and wrong-byte controls use a disposable Git index. `index-final.json` records
the audit follow-up's staged-file check; it does not recursively hash itself.

The three reviews are source reviews. Their descriptions of earlier probes
remain historical. `main-ci.json` and the separate Windows main gate bind fresh
execution on the merge commit. No runtime or artwork change accompanies this
audit follow-up.
