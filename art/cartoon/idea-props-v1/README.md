# Cartoon idea-prop drafts

This art-only batch contains the independent lightbulb, exclamation mark and question mark from `LITEBULB.BMP` frames 000, 001 and 004. Johnny drawings 002 and 003 are excluded. The user approved all three v1 appearances in the [combined prop review](../props-batch-v1/acceptance/appearance-v1.json); runtime fit and native behavior remain pending.

| Frame | Draft | Actual raw canvas | Appearance |
| --- | --- | --- | --- |
| 000 | `generation/000-generated-v1.png` | 1254 x 1254 RGBA | Warm yellow lightbulb, metal base and seven detached rays |
| 001 | `generation/001-generated-v1.png` | 1536 x 1024 RGBA | Golden outlined exclamation mark with a wide emphasis burst |
| 004 | `generation/004-generated-v1.png` | 1254 x 1254 RGBA | Golden outlined question mark and separate dot |

`generation/001-generated-v2.png` is a preserved, unselected alternative. A targeted haze-removal edit had already started when alpha sampling showed that several broad amber areas in v1 were hidden RGB at alpha 0. Both versions retain hidden amber RGB in those sampled areas. No visible-halo defect or successful fix has been established. The displayed v1 is now appearance-approved; the alternative v2 is not covered by that approval.

The original PNGs in `reference/` are exact members of the tracked original-reference archive. Enlarged guides use nearest-neighbor pixel replication with transparent padding. Their diagnostic palette supplies geometry, not target colors. Exact approved palm and Johnny runtime PNGs supply the Cartoon outline and painted-shading context. [Source identities](reference/source.json) bind these files to their archive and acceptance records.

The built-in imagegen tool produced one initial image per requested prop and one targeted exclamation alternative. Exact prompts and ordered image paths are in `generation/*-request.json`; [the generation record](generation/record.json) binds every request, input and untouched returned PNG. No CLI fallback or programmatic artwork editing was used.

Only visual inspection and basic image/hash/alpha readback were performed. Requested square sizes were not returned exactly. Faint nonzero alpha extends beyond the visible artwork, including alpha 1 at the question mark's bottom edge; all of it is retained. The alpha-8 bounds in the record are measurements, not applied cutoffs. Final uniform export registration, size consistency, native scene checks and bulk smoke/regression/audit are deferred. No runtime exports, production package, ledger or engine code were changed.
