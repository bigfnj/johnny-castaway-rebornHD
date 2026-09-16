# Fresh post-merge authoring audit

Audited main commit `9ea8293f8efbd45a25717b4f8dd3bc5139586259`. The authoring checks passed. The audit found three copied evidence records missing from that commit; the original bytes are now restored and staged for the parent's follow-up commit. No artwork or runtime changes resulted.

| Check | Result |
| --- | --- |
| Maintained authoring smoke, then regression | All commands passed in recorded order: smoke 3 inventory / 1 history / 2 metadata / 3 production; regression 11 inventory / 22 history / 60 metadata / 63 production / 20 pack tools. Two inventory symlink cases explicitly skipped for Windows privileges; hardlink cases ran. |
| Generated catalog freshness | Both maintained `--check` commands passed. |
| Merged checkout byte preservation | 1,352 bundle files, 55,097,158 bytes compared against Git commit blobs. Frozen files are exact. Only the authorized, unbound standing README current-status update differs. |
| Durable evidence closure after restoration | All 24 copied-evidence binders, 1,119 reference checks and 1,041 unique paths match expected SHA256 in both worktree and Git index. |
| Active approval / recipe / production chain | All 43 asset bindings and 55 protected integration inputs passed. Production archive SHA256 is `4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`. |
| Source and image-learning preservation | 102 source/document fingerprints retained. New Python helpers parse. Fresh manual review covered selected maintained pack/catalog/history paths, test fixtures, the v5 color adapter, integration helper and replay instructions. Original-first geometry, fixed registration, material-mask limits and separate visual approvals remain documented. |
| Runtime / maintained code delta | No changes from base `3af0242` in `src`, `platform`, `third_party`, maintained `tools`/`tests`, CMake or CI paths. Platform/runtime audit belongs to the separate audit owner. |

The three omitted records are under `art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/evidence/motion-v1/browser-execution/build/`: `execution.json`, `stderr.txt` and `stdout.txt`. Their nested `build/` directory matched an ignore rule. The initial `missing-evidence-v1.json` failure remains preserved. `restored-evidence-v2.json` proves the staged replacement bytes equal the immutable binder hashes and feature-worktree source bytes. That report distinguishes the original merged commit from the pending follow-up commit. No other missing copied members were found.

Recommended backlog: add a permanent copied-evidence completeness check against the Git index. Resolve destination members from durable binders and require each staged blob to exist with its expected hash. Keep documented external resources and intentionally local bulk captures distinct. Exercise a negative control that omits an ignored nested `build/` member and reports that exact missing path. A comparison of already-staged files alone cannot catch this omission.

`checks.json` and ordered logs preserve fresh execution; `checkout-files.json`, `source-hashes.json`, `restored-evidence-v2.json` and `audit.json` preserve byte and scope evidence. This audit did not rerun old image generation, lengthy raw-source reproduction, native captures or existing source-mutation matrices. Review-record bulk image lists, historical scratch ancestry and supplied external resources are documented reproduction dependencies, not assertions that all such inputs were copied into Git. Parsing and fingerprinting duplicated historical helpers does not claim a line-by-line manual audit of each copy.
