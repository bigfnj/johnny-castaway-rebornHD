# Full Windows gate, inactive desktop

`run_gate.py` adapts the retained skin-tone integration launcher. It uses the
existing committed `motion_review.py` inactive-desktop helper without changing
it. No desktop switch occurs. The maintained root gate still configures/builds,
runs every smoke stage, then its regression stages. Only the copied gate's root
assignment and four existing wave/palm `--work` arguments change, with a saved
diff. These retained captures diagnose a failure without rerunning it first.

Launcher changes are limited to repository/output selection and placing the
invoking Python interpreter directory on the child PATH. `--root` permits a
fresh main-checkout deployment run using the same helper. The PowerShell 7 gate
continues to invoke its existing PowerShell 5.1 test scripts.

Run with the toolbox Python from the repository root:

```text
python -B art/cartoon/shoreline-repair-v1/integration-v1/windows-final/run_gate.py --zip-sha256 FINAL_ARCHIVE_SHA --label feature-v1
```

Scratch output is under `build/seasonal-final-windows/<label>`. The result binds
source and deployed archive hashes, protected source hashes, native windows
observed on the inactive desktop, unchanged input desktop, gate exit and log.
Raw diagnostic PPMs stay in scratch; compact results and logs will be retained
with explicit source paths and hashes. This is a delivery runner using existing
checks, not a new maintained test gate.
