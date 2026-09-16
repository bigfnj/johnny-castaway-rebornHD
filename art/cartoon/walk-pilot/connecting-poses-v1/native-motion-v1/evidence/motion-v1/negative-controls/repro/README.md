# Executed control helpers

`check_native_candidate_v2.py` locates the repository by its assets directory.
Run this exact snapshot with the toolbox Python and `-B`, after candidate-v2
smoke/full/repeat completes. It reads the preserved capture reports and PPMs,
changes comparison inputs only in memory, and refuses to overwrite native-v2.json.

The other three snapshots were authored under `build/connecting-analysis/` and
derive the repository with `parents[2]`. To replay those, stage the exact snapshot
at its original filename under that directory in a separate prepared checkout,
then run it with `-B`. They refuse to overwrite their earlier control directories.
Their existing output trees retain the actual positive and mutated helper bytes,
fresh-process witnesses and logs. Version1 proofs remain scoped to version1.
