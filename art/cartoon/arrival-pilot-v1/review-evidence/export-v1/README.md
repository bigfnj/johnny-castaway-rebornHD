# Arrival export verification

Run from the repository root with Python and the recipe's exact Pillow 12.2.0
dependency. The sanctioned `python` interpreter on the authoring machine has
that version; `$env:TOOLBOX_PYTHON` currently has Pillow 12.3.0 and correctly
fails this recipe's version guard. Check the selected interpreter before running;
do not alter the preserved recipe to bypass that guard.

```powershell
python -B -c "import PIL; print(PIL.__version__)"
python -B art/cartoon/arrival-pilot-v1/test_export.py --phase smoke --recipe art/cartoon/arrival-pilot-v1/candidate-recipe-v1.json --output build/arrival-export-verification
python -B art/cartoon/arrival-pilot-v1/test_export.py --phase regression --recipe art/cartoon/arrival-pilot-v1/candidate-recipe-v1.json --output build/arrival-export-verification --mutation-check
```

The saved smoke result records three passing checks. The subsequent regression
result records 20 behavior checks and 17 executed source mutations, with one
named failure per mutant. Both results name the exact exporter and test sources.
The exporter remained unchanged while the native candidate was captured.
Use a fresh output directory for a new run; existing candidate outputs are
preserved. The candidate recipe's bytes are identical to the tested recipe.

At this initial candidate check, existing art tools also passed 20 regressions
and both maintained metadata generators passed reproduction checks against the
then-current 27-asset production pack. Later human acceptance and 28-asset
integration are recorded separately in `../../production-acceptance.json`.
