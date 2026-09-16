# Windows delivery gate

The first full Windows gate for the accepted connecting poses, matched skin
colors and corrected standing 018 passed in 175.554 seconds. The fresh build
was warning-free. All smoke stages preceded regression, and all 2452 decoded
golden files matched. The source and deployed archives both have SHA256
`4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`.

The inventory suite explicitly skipped two symlink cases because Windows
reported privilege error 1314. The hardlink case and the other eight executed
cases passed. No renderer capture-marker failure occurred in this run.

`evidence.json` records the actual ordered stages, tools, binaries and source
bindings. `readback.json` verifies all 46 exact small-file copies and the hashes
of all 32 retained PPMs. `run/running.json` preserves the launcher command and
protected-input snapshot; `run/integration-start.json` adds the production
ledger, acceptance and integration-input hashes. HEAD was recorded before
commit, so these input hashes identify the tested working state.

The launcher created a temporary inactive desktop with `CreateDesktopW` and
started PowerShell there using `CreateProcessW.lpDesktop`. It never called
`SwitchDesktop`. Across 335 polls it checked the user's input desktop and
foreground ownership; 261 native window handles were observed on the inactive
desktop. The input desktop and all protected files remained unchanged.

The copied gate differs only in its repository-root assignment and four
existing `--work` options for separate palm/wave smoke and regression captures.
See `run/gate-adaptation.diff`. Assertions, test order and compiler flags were
unchanged. Native capture logs are retained under `captures/`; large PPMs,
binaries and temporary test archives remain in the ignored run directory
`build/connecting-poses/windows-verification/connecting-color-foot-promotion-v1/`.
Their identities are recorded in the result and evidence. The known intermittent
capture-marker and automatic failure-retention backlog items remain open.

## Replay

Use a separate checkout of the desired source and production archive. Copy
`helpers/run_gate.py` into that checkout at
`build/connecting-poses/windows-verification/run_gate.py`; this depth is required
by its `ROOT = Path(__file__).resolve().parents[3]` calculation. Its `HELPER`
constant references the original machine-local scratch path. The exact imported
file is preserved here as `helpers/motion_review.py`. If that scratch path is
unavailable, change only the new launcher's `HELPER` constant to this retained
copy and record that launcher change. Do not edit the preserved checkpoint.

The launcher needs toolbox Python with Pillow and psutil, PowerShell 7 on PATH,
Windows PowerShell 5.1 for the gate's child scripts, CMake and the installed
Visual Studio C toolchain. This run used CMake 4.3.1 and the Visual Studio 18 2026
x64 generator. Exact compiler configuration is retained under `build/`.

After the archive is final, run the copied launcher with a fresh output label:

```powershell
& $env:TOOLBOX_PYTHON -B build/connecting-poses/windows-verification/run_gate.py --zip-sha256 <archive-sha256> --label <fresh-label>
```

Do not invoke the native gate directly on the interactive desktop. The wrapper
uses the full gate, with neither `-NoBuild` nor `-SmokeOnly`. It removes inherited
`PSModulePath` case-insensitively and retains renderer outputs. Labels refuse
existing output directories. `helpers/preserve_windows.py.txt` is a historical
one-time writer with this run's fixed destinations, not a replay command.

Maintained catalog reproduction, other-platform CI and fresh merged-main
deployment are separate verification steps. This gate does not establish
original-executable animation or palette equivalence.
