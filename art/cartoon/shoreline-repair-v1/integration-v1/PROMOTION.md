# Promotion transaction

Use `promote_v2.py` for delivery. `promote.py` and `promotion-preflight/` preserve the first preflight implementation and its results. That first implementation could fail while writing its report after changing production, so it is not the selected promotion helper.

V2 prepares the report directory before production writes, writes the record atomically inside the transaction and rolls the ZIP and ledger back if any write or readback fails. A partially written promotion record is removed on rollback.

The tests under `promotion-transaction-v2/` use only a disposable copied repository and a clearly synthetic native summary. They execute actual file changes there. Report failures before and after the record write restore both prior production files exactly. Removing the two rollback calls makes the test fail with `rollback failed`; restoring them permits the successful disposable transaction. The live archive, ledger and native candidate remain unchanged throughout these controls. These fixtures do not establish native success or human authorization.

After the real final native gate passes and root authorizes promotion, first run the same command without `--promote` for real-summary preflight. Then use a fresh report path for the actual transaction:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/shoreline-repair-v1/integration-v1/promote_v2.py --candidate build/shoreline-repair-v1/integration-v1/run-v2/scrantic_data.zip --native-summary build/shoreline-repair-v1/integration-v1/native-final-v1/captures/summary.json --native-summary-sha256 ACTUAL_SUMMARY_SHA256 --report art/cartoon/shoreline-repair-v1/integration-v1/promotion.json --promote
```

The literal placeholder must be replaced with the hash reported for the completed native summary. V2 requires the candidate identity, full native status, 28 smoke captures, 28 fresh repeats and eight negative controls. It also requires the live archive and ledger to match their prior records. Package and source checks are read from their frozen evidence; the final native/Windows evidence and later catalog checks remain separately owned.
