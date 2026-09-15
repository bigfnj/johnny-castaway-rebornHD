# Inventory source preservation

The inventory CLI now rejects `--output` when it resolves to `--archive` or refers
to the same existing file. The check runs before archive parsing and reference
export. This covers relative paths, file and directory symlinks, and hardlinks.
The diagnostic names the output and source archive. Separate output files retain
the existing behavior, including replacement of an earlier JSON catalog.

No production archive was modified for these tests. Each CLI invocation used a
new disposable archive. Tests assert byte preservation on both rejected and
successful commands; the export control checks that rejection creates no export
directory.

## Verification, 2026-09-15

| Check | Windows, toolbox Python 3.11 | Linux, existing `python:3.11-slim` |
| --- | --- | --- |
| Inventory smoke | 3 passed | 3 passed |
| Inventory regression | 9 passed; 2 explicit symlink skips because the process lacks that privilege | 11 passed, including file symlink, directory symlink, and hardlink |
| Existing art-tool regression | 20 passed | 20 passed |
| Compiled source mutations | 2 fired | 2 fired |

Smoke ran before regression on each platform. Linux used a read-only repository
mount, and all writable fixtures and compiled mutants lived in container `/tmp`.

Run in this order:

```powershell
python -B tests/test_art_inventory.py --smoke
python -B tests/test_art_inventory.py
python -B -m unittest discover -s tests -p test_art_tools.py -v
python -B tests/test_art_inventory.py --mutations
```

The first mutant removes the entire identity guard; the second removes only
existing-file identity, leaving resolved-path equality in place. Each copied
source is compiled to a fresh bytecode artifact. The harness proves its timestamp
advanced and the actual CLI's `main` emitted the unique execution witness. Each
then causes exactly one failure naming `tools/art_inventory.py` and the rejected
source/output identity condition. The real source remains unchanged throughout.

Commit evidence: both `removed_identity_guard` and `removed_file_identity` fired
through the real compiled CLI, with one witnessed identity assertion failure
each, on Windows and Linux.

## Gate and CI wiring

`gate.ps1` runs inventory smoke and approval-history smoke before any regression,
and runs both regression suites in its full mode. A smoke failure stops the gate;
a regression failure contributes to its final failing status. Linux, macOS, and
Web CI jobs execute the same two smoke suites before their regressions. Catalog
reproduction remains in the Linux job.

The existing orchestration checkers now exercise this wiring with disposable
command fixtures. These checks do not launch the native application or claim
native rendering coverage.

| Check | Result |
| --- | --- |
| `tests/Test-GateOrder.ps1 -VerifyMutation`, executed under both PowerShell 5.1 and 7 with the matching gate shell | 20 ordinary controls passed per shell; both new smoke-guard removals and all four new invocation omissions were detected; existing guard mutations and restoration controls also passed |
| `tests/test_web_workflow_flow.py --mutations`, Linux bash | 15 authoring ordering/failure controls passed across Linux, macOS, and Web job commands; all 12 invocation omissions fired; existing Web CI/release controls and four failure-propagation mutants passed |
| Workflow YAML parsing | Parsed successfully with all four expected jobs |

The Windows omission controls execute the changed scratch gate, require its
omission marker and final regression witness, and reject the missing or reordered
test execution trace. CI omission controls execute the remaining commands under
GitHub's bash failure settings and require the expected three command witnesses
before the four-command ordering assertion rejects the omission. These are
behavioral controls, not checks that invocation strings merely exist.

Wiring commit evidence: removing either new smoke guard or any of the four new
Windows smoke/regression invocations was detected under PowerShell 5.1 and 7.
Removing any of those four invocations from each of the three CI host sections
produced one named ordering failure, for 12 detected CI omissions.
