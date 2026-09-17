# Current character inventory refresh after shoreline promotion

CI's additional character-inventory check correctly refused the stale generated inventory after production promotion. No builder, test, classification, source reference, approval record or historical verification file needed a change. Only `art/cartoon/character-inventory-v1/inventory.json` changes in the existing character bundle. Its generated README remains byte-identical.

The exact delta has 19 changed JSON leaves: the production ZIP SHA-256, ten shoreline acceptance pointers, and status/acceptance fields for four newly approved HOLIDAY drawings. Character counts, original identities, resource classifications, scene associations and all other fields remain unchanged. There are still 1,002 outstanding confirmed Johnny slots and 28 accepted Johnny slots. Accepted holiday props remain classified as non-Johnny.

`diagnosis.json` preserves both values of every changed leaf. Reversing those changes in the current inventory and encoding with the unchanged builder's `encode()` reconstructs the exact prior inventory SHA-256. This was executed before regeneration. It retains the historical output without another large JSON copy. All old historical verification records remain unchanged and continue to describe that older snapshot.

`verification.json` records the expected stale check failure, normal regeneration, the existing complete inventory smoke, full regression and final CI `--check`, in that order. Regression passed nine named damaged-input controls and an executed guard-removal mutant, followed by restored positive reproduction. This validates input identity and inventory mechanics, not a new visual classification or approval.

For normal future production promotions, run the unchanged builder without `--check` to regenerate the current inventory, then its smoke/regression tests and `--check`. The exact commands and fresh scratch paths are in `verification.json`. The preserved orchestration scripts assume their original `build/shoreline-repair-v1/inventory-refresh-v1/` depth. Do not run them inside this frozen evidence directory. No browser page was republished and no runtime or image bytes were changed here.

The binder's `files_sha256` keys are relative to this directory. `external_outputs_sha256` names the current generated files from the repository root. Other historical/source hashes in diagnosis and verification describe read-only inputs, not copied child artifacts.
