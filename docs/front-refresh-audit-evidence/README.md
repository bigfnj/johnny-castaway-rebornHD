# Retained front-walk audit records

These are snapshots from the read-only audit of main `71f3e5f`. See the
[audit narrative](../front-refresh-post-merge-audit.md) for findings, validation
and limits. No captured application binaries are stored here.

`core` contains the precise source coverage, compiled probe witnesses and probe
sources. To use its recorded container command, first copy `run_probes.py`,
`ttm_tag_probe.c` and `dump_write_probe.c` into the repository's
`build/front-refresh-postmerge-audit/core/` directory. The runner expects the
repository mounted read-only at `/src` and a fresh writable scratch directory
at `/out`; the core README records the image and invocation. A timeout in the
malformed-tag case is a defect witness, not a passing application test.

`authoring` preserves the audit report, portable command results, coverage and
source fingerprints. Raw test logs remain in the original local
`build/front-refresh-postmerge-audit/authoring/` folder; their SHA256 values are
in `results.json`. All five smoke suites preceded the regression suites.

`platform` preserves the coverage/results, focused logs and the fullscreen
observation. The browser probe expects its original path under
`build/front-refresh-postmerge-audit/platform/` and serves the local `build_web`
folder. Its retained-build hashes identify the observed files; their exact
source revision was not established. The null exit/error values do not prove
engine liveness. The two failed supplemental gate-order attempts remain
explicitly non-passing and are distinct from the successful full feature gate,
deployed smoke/regression and four-platform merged-main CI.
The three failed fixture/diagnostic logs are stored as `.log.json` records;
encoding their `utf8_text` as UTF-8 reconstructs the exact original log bytes
and matches the recorded SHA256, including trailing whitespace.

Worktree fingerprints identify the bytes observed on the audit machine.
Git blob IDs or tracked-byte hashes, where supplied, identify repository content
independently of checkout line-ending conversion. Source coverage is described
per file; neither fingerprint counts nor passing tests establish an exhaustive
proof that no defect exists.
