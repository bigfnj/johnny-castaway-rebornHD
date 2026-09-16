# Cartoon connecting-pose audit of merged main

This fresh review examined main `9ea8293f8efbd45a25717b4f8dd3bc5139586259`
after [PR #15](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/15)
was merged and the primary checkout updated. It found no new engine or platform
defect. It did find three omitted review records, which the follow-up restores
without changing artwork or the existing evidence binders.

## Findings and action

| Area | Finding and action |
|---|---|
| Runtime regression | `src`, `platform`, maintained `tools`/`tests`, CMake, gate and CI sources have no changes from prior main `3af0242`. Fresh current-source review and executed main tests supplement that comparison. The production ZIP remains `4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`. |
| Review evidence omission | The initial main checkout lacked `execution.json`, `stderr.txt` and `stdout.txt` inside the connecting browser evidence's nested `build/` directory. Git ignore rules excluded them from the feature commit. The worktree had correct copies, so worktree hashing and comparison of already-staged files did not expose their absence. Restore their exact original bytes and explicitly stage them. The failed-before and restored-after checks are retained in the authoring audit. |
| Prevention | Add a maintained check that every declared copied evidence file exists in the Git index with its expected hash. A deliberately omitted file must fail by name. This remains in [BACKLOG.md](../BACKLOG.md); intentional external original inputs and scratch captures need separate treatment. |
| Current documentation | Update the connecting lessons, standing018 index and delivery plan to distinguish current merged status from frozen historical pending decisions. No historical approval, recipe or rejected-image record is rewritten. |
| Dead or incomplete code | Existing decoder-result redundancy, unfinished TTM commands and original-comparison questions remain documented. Shared platform no-op adapters are intentional. Static reachability is kept separate from executed story coverage. |
| Memory and ownership | Reviewed current resource, scene, surface, PNG and audio ownership. Existing process-owned resource teardown and audio startup/error-handling follow-ups remain open. No new accumulating leak was demonstrated. Bounded native ownership tests passed; this audit did not add a sanitizer or physical-device run. |
| Optimization | Full-frame rendering, flip caching and older review viewers remain measurement-first opportunities. The newer viewer's bounded active-clip policy is preserved. No unmeasured speed or memory saving is claimed. |

The three restored records are under
`art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/evidence/motion-v1/browser-execution/build/`.
Their expected hashes remain those already present in the original binder:

| Record | SHA256 |
|---|---|
| execution.json | `bc15c3aab8243e6e501baabf7856779f2f7f5a9ee5373731d455e234fcaf9a09` |
| stderr.txt | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| stdout.txt | `579a1343d50cc61492f92de42a0a11b035b0691c487b83a1da3e8d8c5b6e05db` |

## Fresh verification

| Check | Result |
|---|---|
| Main Windows deployment gate | First attempt passed: fresh build without warnings, all smoke before regression, all 2,452 golden resources exact. Source and deployed archives match. All 32 retained renderer captures have complete pixels and required markers. The user's input desktop stayed unchanged. |
| Main authoring | Nine smoke cases passed before inventory, history, metadata, catalog and pack-tool regressions. Both generated catalogs reproduce. Two Windows inventory symlink cases explicitly skipped for privilege; hardlink controls passed. Linux CI exercised its own inventory checks. |
| Platform CI | Windows, Linux, macOS and Web passed for both the PR and merged main. The exact jobs and steps are retained in the [CI record](cartoon-connecting-poses-ci.json). |
| Core table review | Current bundled resource bytes match the inventory. Independent census covers all 36 endpoint pairs and 63 story endpoint/heading rows. This establishes table consistency, not execution of every story branch. |
| Final evidence readback | After restoration, all 24 durable binders pass: 1,119 expected-hash references cover 1,041 unique paths, each matching both the worktree and Git index. The authoring record preserves the missing-file failure and restored checks. No further omissions were found. Frozen generated images, palette corrections and prior approvals remain intact. |

The [audit record](../art/cartoon/skin-tone-v1/integration-v1/post-merge-v1/record.json)
binds the copied core, platform and authoring reports with their covered paths,
hashes, logs and limitations. This is a source review and the stated test
coverage, not proof that every input or original scene is correct. Physical
audio/display coverage and original-executable scene parity remain separate.

The next useful art work is reviewing shared standing/connecting poses in their
story contexts, then selecting another complete motion family. Keep the chosen
skin reference and original-first contact measurements in that review.
