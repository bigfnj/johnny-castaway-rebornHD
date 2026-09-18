# Cartoon asset build workflow

On 2026-09-17 the user changed the delivery cadence: "build ALL of the assets FIRST, then bulk smoke-test" so visual iteration can move faster. This replaces the earlier requirement to run the entire validation, merge and post-merge audit cycle after every art approval.

The user first requested "2 dozen or more per review", then increased that default on 2026-09-18 to "upwards of 3 to 4 dozen at a time". Queue 36-48 new drawings per ordinary art review, grouping related resources and identifying every frame clearly. Target about 42 where complete families fit; avoid splitting a small coherent family merely to hit an exact number. Targeted corrections may remain smaller and do not count toward the next new-art batch. Use parallel generation where shared style references permit it. Collect exceptions in one review instead of pausing for each prop or small resource. Pause earlier only for a fundamental art-direction decision or a blocker that would invalidate the larger batch.

| Stage | Current practice |
| --- | --- |
| Draw and review | Work through coherent resource families. Use original artwork for geometry and the approved Cartoon artwork for style. Show stills or motion previews where they help the user judge the art. |
| Save approval | Retain the selected raw image, exact prompt and references, export recipe, asset identity and the user's approval scope. Save approved work on the art branch without repeating the full validation cycle. |
| Prepare a usable preview | Check only what is needed to display the draft correctly, such as dimensions, transparency, registration and use of the current approved environment. Fix a visible blocker as it arises. |
| Complete the asset build | Accumulate approved families and an outstanding-asset list. Visual approval is recorded separately from later integrated-pack validation. Do not call pending integration tests passed. |
| Bulk verification and delivery | Once the asset build is complete, assemble the pack and run smoke tests, then regressions. Resolve integration issues, merge and push, then perform the final code audit and update BACKLOG.md. |

The cloud CI run was already underway when this decision arrived. Let it finish, but do not start an additional cloud-only post-merge gate or code audit. Subsequent art iterations do not need a PR or full CI run for each approval. Keep the current CI configuration available for the bulk delivery.

Actual engine changes remain separate from art-only iteration and receive testing appropriate to the changed behavior. Human review remains useful for anatomy, contact, layering and style decisions; it does not require the full software validation cycle first.

NIGHT.SCR and the remaining active ocean screens have visual approval and await integration. Work now covers independent props and vehicle families in larger batches. Preserve all earlier character, shoreline, offshore-wave and seasonal approvals.
