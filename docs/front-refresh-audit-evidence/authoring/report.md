# Post-merge authoring audit

Audited main commit `71f3e5f8d158e4d6a7315fe633d3c9944a4b21e5` read-only. No new actionable finding in the authoring, approval-history, pack or evidence paths reviewed. No tracked files were changed by this audit.

| Validation | Result |
|---|---|
| Inventory | 3 smoke, then 11 regression tests; two Windows symlink cases explicitly skipped for missing process privilege |
| Pilot history | 1 smoke, then 22 regressions, including the 84-test future-promotion replay |
| Original pilot metadata | 2 smoke, then 60 regressions |
| Full production catalog | 3 smoke, then 63 regressions |
| Front exporter/viewer | 2 smoke, then 15 regressions using frozen historical inputs |
| Catalog reproduction | Both `--check` commands passed without regenerating maintained files |
| Frozen export/review | All six runtime PNGs match current production; all 20 declared review files and the complete review record reproduce exactly |
| Production archive | Matches accepted SHA256; exactly 028/029 changed against pinned prior archive, with 2577 of 2579 members unchanged |
| Evidence | All 48 protected evidence file hashes passed; linked approval records passed independent hash checks |

All five smoke suites finished before the first regression suite. Logs, portable command records and exact source fingerprints are retained alongside this report. Unchanged mutation suites were not rerun.

## Coverage and source review

- `art/cartoon/walk-pilot/front-refresh-v1/export.py:110`: input and runtime identities, fixed uniform registration, source-center fit failure, exact retention of previous PNG bytes, reproduction from frozen inputs. The alpha-8 fit limit is stated accurately; it does not claim every low-alpha fringe fits.
- `art/cartoon/walk-pilot/front-refresh-v1/review.py:19`: all 23 stored E-to-A rows use the original draw convention. The final two walking drawings are 025 then 027. The fixed union camera is built at line 57. Its 1000ms endpoint hold is labeled diagnostic and does not claim the native 017 arrival.
- `src/engine/walk.c:189`: the source still draws at stored x minus one; travel delay six and arrival delay eighty at lines 212-214 agree with preserved 20ms-tick native evidence. No original-executable calibration is claimed.
- `tools/art_production_catalog.py:160`: selected nested inheritance preserves each asset's approval origin and checks complete ancestor chains. Active coverage, recipe, canvas and production PNG checks start at line 223.
- `tools/art_review_metadata.py:183`: explicit pilot replacements are separated from historical variants. Historical facts and review scope stay attached to their original drawings.
- `art/cartoon/walk-pilot/front-refresh-v1/test_tools.py:232`: an exercised promoted-production alternative verifies fixture isolation. The mutant runner at line 285 demands a witnessed executed source and exactly one named failure.

The complete approved front-oblique walk contains six drawings, 024-029, reviewed together across 23 positions. Earlier approved 024-027 remain exact bytes; the latest pass contributes 028/029. Native HD017 remains unchanged, and only the reviewed E-to-A route is approved by this evidence. The partial Cartoon pack still has 28 accepted slots out of 2401.

## Remaining work already recorded

`BACKLOG.md:15` already calls for tracing front arrival017 and the complete wait/turn family before generation. Eight of ten unique wait/turn-table drawings remain HD. `BACKLOG.md:16` separately requires tracing original033-035 with010 through their TTM uses and timing before describing them as a complete frontal cycle. This audit found no reason to reopen completed history or fixture work.

The root audit owns fresh native deployment testing. This authoring audit launched only headless browser tests and did not rerun native captures, original binary playback or physical-device checks.
