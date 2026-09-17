# Character inventory post-merge audit

Audited the primary checkout at `bf83559e2fd3c5fc239a0026fd36578dcf3443a6`,
after [PR16](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/16) merged.
All four platform jobs passed for the feature revision in
[CI run 35164043225](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35164043225).
All four jobs also passed on the merged main revision in
[CI run 35164446609](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35164446609).
The follow-up changes only this audit note and one stale backlog sentence.

| Area | Fresh main result |
|---|---|
| Reproduction | Character inventory smoke passed, followed by regression with nine named negatives and the executed PNG-guard-removal proof. Existing art metadata and production catalogs reproduced. |
| Durable files | All 54 inventory files are in Git: 53 declared payloads plus the self-describing delivery manifest. Every declared worktree/index byte hash matches. The earlier isolated-index omitted-file control failed on the named missing record. |
| Original references | Exactly 2,402 unique PNG members, with no missing, extra or duplicate paths; every PNG hash matches the source index. Source/scene binders also passed 33 copied-file/output hash checks. |
| Catalog consistency | Every one of the 2,401 app slots maps to the current production catalog, including approval pointers. Counts independently recompute to 28 accepted Johnny, 1,002 outstanding Johnny and 84 uncertain app slots. Original-only SA_DEMO is never counted as outstanding app art. |
| Production preservation | No changes to engine, platform, maintained tool/test source or production assets relative to pre-task 0e520ee. Source and deployed Windows ZIPs remain byte-identical at 4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be. |
| Scope and lessons | The records distinguish diagnostic palette from original executable color, static script associations from executed scenes, and inventory completion from generated/accepted art. Prior family lessons and approvals remain intact. |
| Download delivery | The served ZIP contains 1,086 selected PNGs plus the full inventory JSON. Every PNG hash matches; downloaded JSON equals the UTF-8 repository inventory. ZIP SHA256: 89fcdc2fec3a6ab2e185cf1cb744f0b32bb6b9441ba2ffa69867d73e9137b3aa. |
| Existing backlog | Runtime findings from earlier audits remain open. This artwork-inventory pass does not claim to fix them. 84 uncertain visual identities and scene execution remain explicit future work. |

The fresh code audit read the merged builder/viewer, original exporter and
controls, contact-sheet helper, scene-map builder/verifier, inventory harness
and CI integration. It found no new actionable code issue. The earlier
filter/link fixes are present. The viewer replaces paginated card and modal
nodes without persistent image/timer caches; ZIP ownership is scoped and
subprocess controls wait for completion and retain diagnostics. This source
review is not a measured browser-memory profile or original-binary timing test.

The evidence audit found one stale sentence in BACKLOG that still described
SA_DEMO as awaiting classification. It is now classified as non-Johnny,
original-only reference art. The sentence is corrected; the separate five-TTM
behavioral question remains open.

The recommended next production group is the four HOLIDAY decorations, then
standalone props and vehicles. Other animated actors and mixed Johnny/prop
drawings still need coordinated pose and scene review. No production-time or
memory saving is claimed from the inventory or viewer changes.
