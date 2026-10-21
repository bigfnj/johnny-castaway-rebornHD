# Johnny date scenes: new drawings

This folder holds the next new-art batch, separate from earlier appearance corrections.

September 25, 2026: all 64 selected drawings now have saved built-in ImageGen candidates, exact requests and generation records. The [new-only appearance review](http://127.0.0.1:8941/next-scenes-batch-v1/review.html) covers SMDATE2 (12), SMDATE3 (16), SMDATE4 (9), SMDATE5 (12), and SMDATE9 (15). The shadow-only SMDATE2 004 is excluded. Source-specific detached caps, cropped body parts and joined character drawings are retained. `selected-versions.json` chooses corrected versions; earlier attempts remain saved.

The prompt set is under `generation/RESOURCE.BMP/NNN-vN-request.json`; returned images and their hash records are beside each request. Every selected output was visually compared with its original, including light and dark alpha composites. Appearance approval is pending. Existing approvals and production assets were not changed by this batch.

The frame list is `selection.json`, mapping resource names to numeric frame IDs. Run `prepare_references.py` after that list is settled. It copies the original PNG bytes from the character inventory, checks their archive hashes, and writes nearest-neighbor inspection copies, contact sheets, source provenance and a batch plan.

Before generating each frame, inspect its exact original and neighboring phases. Write the observed camera direction, gaze, near/far limb ownership, joints, hidden parts and prop attachments in the exact request. Use approved Cartoon references for identity and materials. See [workflow](../../../docs/cartoon-art-build-workflow.md) and [pose lessons](../../../docs/art-style-learnings-pose-and-action.md).

Use one built-in ImageGen call for each drawing. Save its exact argument object at `generation/RESOURCE.BMP/NNN-v1-request.json`, with `arguments.prompt` and `arguments.referenced_image_paths`. After generation, run:

```powershell
& $env:TOOLBOX_PYTHON art/cartoon/next-scenes-batch-v1/record_output.py RESOURCE.BMP NNN 1 RAW_OUTPUT_PATH
& $env:TOOLBOX_PYTHON art/cartoon/next-scenes-batch-v1/build_review.py
```

The recorder copies the tool PNG without alteration and saves the request, reference and output hashes. Versioned outputs are retained. `selected-versions.json` can choose revisions explicitly; absent entries use v1. Optional `review-notes.json` maps frame keys such as `RESOURCE.BMP-000` to short appearance notes.

`build_review.py` refreshes `review.html`, `review-data.json` and `review-record.json`. The page pairs each selected drawing with its exact original, links its request and generation record, and labels pending or failed results. Serve this folder through the local art server so review data can load.

No appearance approval, production integration or native motion validation is implied by generation or the review page. Source canvas placement, multipart registration and native timing are later integration work.
