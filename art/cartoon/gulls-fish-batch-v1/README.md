# 42-drawing gull, nest and small-fish batch

The user increased the default art review size to 36-48 drawings on 2026-09-18 and asked to proceed. This batch covers the complete GJGULL1.BMP000-032 and LILFISH.BMP000-008 families. All 42 source slots are distinct original PNGs, contain no Johnny/person or placeholder, and were absent from the production pack and existing generation/review records when selected.

[Open the full gallery](http://127.0.0.1:8941/gulls-fish-batch-v1/review.html). Each drawing is identified by resource/frame and has its original directly below it. The gallery supports filtering and light/dark transparency backgrounds. This is an appearance review; no generated drawing is approved by being included.

| Group | Drawings | Source features to retain |
| --- | ---: | --- |
| GJGULL1 000-007, 025-026 | 10 | Flight phases and head-first dive angles; correct wings and visible eyes |
| GJGULL1 008-024 | 17 | Landing, head/body turns, preening and pecking; gray source shadows are not feet |
| GJGULL1 027-032 | 6 | Four nest construction stages, sitting gull, and one egg in a nest |
| LILFISH 000-008 | 9 | Upright poses, separate head/body and tail pieces, and one/two/three/four-fish catches |

## Source and style

Exact original PNGs and nearest-neighbor viewing references are retained in [reference](reference). [source.json](reference/source.json) binds each original to the supplied-original archive and frame index. The source colors are diagnostic, not verified original-executable colors.

Gull009 is generated first as a shared white/light-gray gull identity with dark feather tips and warm yellow-orange beak and webbed feet. Its side-view eye count must not be imposed on frontal poses. Nest030 establishes the woven brown/tan material. Each frame's exact original controls its geometry. The fish use the existing Cartoon green-body/orange-fin material direction while retaining LILFISH-specific shapes and component roles. Shared draft keys carry no visual approval from other families.

[generation](generation) preserves the exact built-in image-tool requests, untouched raw outputs and per-image source records. [batch-plan.json](batch-plan.json) states the full scope and assembly cautions. The latest boot005/022 approval is separate and remains recorded in [boot-angle-v4 acceptance](../boot-angle-v4/acceptance/appearance-v1.json).

[Selected versions](selected-versions.json) use v2 for gull011 (body direction), gull026 (extra foot removal), fish004 (tail component shape) and fish008 (four-fish count). All other drawings use v1. Earlier attempts remain preserved. Fish008 has four visible heads, but its overlapping middle anatomy still needs human judgment. [Preview checks](preview-checks.json) record gallery loading and controls, with native testing deferred.

## Scene evidence and deferred work

GJGULL1.TTM source tags26,33,34,42,43,45 attribute flight, turning, takeoff and cleaning; the static map also associates this resource with bathing, reading and Gulliver scripts. This is static evidence, not an executed scene timeline. Do not animate the gallery in numeric order as though that were the source sequence.

LILFISH002 is the body/head assembly used with separate tails003/004. MJFISH.TTM loads LILFISH in slot5 at offset15118/tag43. Tags45-48, labeled cycle catch1/2/3/4fish, draw005-008 at offsets15566/15594/15622/15650. The saved map records global slot reuse with GJCATCH3, so preserve that attribution limit. The grouped fish must remain separate animals in the original arrangement.

Native canvas registration, animated contact, complete action timing, shadows, scene joins and the full smoke/regression/audit cycle remain deferred to bulk integration. The production package is unchanged during this draft work.
