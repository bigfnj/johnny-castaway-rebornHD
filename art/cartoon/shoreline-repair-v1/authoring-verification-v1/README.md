# Final shoreline authoring verification

The maintained tools accept the final 47-asset production pack through the existing selected-inheritance and named-footprint rules. No acceptance or geometry guard was relaxed. The pilot catalog retains its 21 historical drawings and original facts, with 16 explicitly replaced slots: six Johnny poses and ten shoreline sprites. Five pilot drawings remain retained. The production catalog records all 47 accepted slots.

The maintained change adds a combined shoreline/history fixture and two damaged-input tests, plus explanatory footprint wording. The fixture keeps historical source canvases and registration intact while current ground, left, center and right families use their separately declared runtime canvases and offsets.

## Ordered checks

`run/smoke.json` records the maintained pack, inventory, pilot history, pilot metadata and production catalog smoke tests, followed by both catalog generators. `run/regression.json` records their regressions and both read-only catalog checks against the same package and maintained sources. The histories and catalogs resolve actual production approval and recipe records; external original resources are not reread. No visual approval or original-executable parity is inferred from these checks.

`controls/controls.json` records two fresh-process source mutations against the new damaged-input cases. Disabling the declared-replacement guard or the recipe/ledger footprint guard causes exactly one named test failure. Each run prints the imported source SHA-256; restored original-source controls pass. Mutants run only from scratch copies. Existing unchanged guard mutation matrices were not repeated.

The unchanged inventory suite explicitly skipped its two Windows symlink cases because this process lacks symlink creation privilege (WinError 1314). Its other nine cases, including hardlink and ordinary path identity, executed successfully. The final report distinguishes scheduled, executed and skipped counts. No symlink result is claimed from this run.

The initial fixture accidentally shared one list between its replacement declaration and newly accepted list. Removing a replacement also altered new-approval coverage and therefore reached an earlier guard. That failed test log is retained in `first-fixture-attempt/failure.log`; independent lists corrected the fixture before the final controls. This was a test-fixture defect, not a production failure.

## Reproduction

Use this checkpoint's exact 47-asset source checkout and toolbox Python. Copy `run/run.py` into a fresh `build/shoreline-repair-v1/final-authoring-v1/run.py`; its repository-root calculation assumes that depth. The output directory must be fresh because the runner refuses to overwrite logs. Run from the repository root:

```
python -B build/shoreline-repair-v1/final-authoring-v1/run.py smoke
python -B build/shoreline-repair-v1/final-authoring-v1/run.py regression
python -B build/shoreline-repair-v1/final-authoring-v1/run.py controls --label controls-v2
```

Use the configured toolbox interpreter in place of `python` where required. Smoke regeneration writes only the maintained catalog JSON/Markdown outputs. Regression and controls do not promote or modify artwork. Do not rerun this historical preservation writer into its existing frozen destination. Preserved maintained-source snapshots identify the executed Windows bytes; working-tree line endings may differ after another platform's checkout.
