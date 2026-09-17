# Reusing approved white waves for low tide

Read-only source review, 2026-09-17. This is authoring guidance, not approval of new low-tide exports. No runtime, art source, production archive or tracked record was changed. Parent owns new rock generation and another agent owns the nine island-wave reuse exports.

The approved white offshore artwork exists and should be the first reuse source for the island. Current low-tide waves 030-041 are older fallback drawings, not the approved high-tide ripples. A low-tide preview retaining those fallback waves does not show the intended final style. The rock needs a ring-shaped adaptation: the high-tide sources are open coastal arcs, and a uniform translation or rotation of one arc cannot create the original horseshoe geometry around a rock.

## Exact approved sources

Paths below are repository-relative. The prefix `S` means `art/cartoon/shoreline-repair-v1/integrated-shore-v1/`.

| Phase | Selected raw source | SHA256 |
| --- | --- | --- |
| 006 | S/foam-refresh-v1/006-raw.png | be78ddda6468fdd3d00c20589e700a50fbb6150157591eb1070eeb718e87c5bd |
| 007 | S/foam-shading-v1/007-raw-v1.png | bccf1e15c476c78ed7ffb6f842eaa001c763eff4209c63b3d47162097c5fa8f2 |
| 008 | S/foam-refresh-v1/008-raw.png | ae9e3795f81be28436ebff6a7c90b19c8998377d0754e4e8ed990ed46bfca2a8 |

Final center PNGs are `S/foam-refresh-v1/candidates/v2/BMP/BACKGRND.BMP/{006,008}.png` and `S/foam-shading-v1/candidates/v1/BMP/BACKGRND.BMP/007.png`. Their respective SHA256 values are `2d2c93478a8e06b99a8a86d832bccdf1327d6d1a55cf79a2593dff49dcbd0db5`, `4ff1c6672e10d67e789c01584f1fb0dc1299016e391809eca8e5047e4cf1acea`, and `623c8f3fb8a4905a15917db963542f178d86472f0809134227bc2053fa800c56`.

For moving them onto a different shore, use their `candidates/.../audit/NNN-unmasked.png` counterparts or regenerate once from the pinned raw, not the already ground-masked production PNGs. This recovers the original white strokes before the old shoreline removed them. The clean 007 audit is under foam-shading-v1, not foam-refresh-v1.

The six side raw ancestors are in `art/cartoon/island-pilot-v1/side-waves/source-images.zip`, SHA256 `8b6cd7ee6a573e5c7f5be893b472c8ef1d48024228aaf058351dad340758ee67`: `003-generated-v2-fresh8x.png` and `{004,005,009,010,011}-generated-v1-10x.png`. Their original exports were 144x58 on the left and 144x64 on the right. The final side recipes reused these unmasked PNGs from prior production archive SHA256 `4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`, available from Git `1aad361fe78dde2c956e05dc451b8d5bab100af0:assets/scrantic_data.zip`. Do not run the old recipe against today's changed live ZIP.

`S/side-fit-v1/recipe-v1.json` records the exact source member hashes. Its final outputs are under `S/side-fit-v1/candidates/v1/BMP/BACKGRND.BMP/`. Left sources were pasted at [0,8] into 150x66 with asset offset [-6,0]; right sources were pasted at [10,10] into 154x74 with offset [0,0]. No resampling occurred in that repositioning. Their ground visibility was recalculated at the new world coordinates.

## Reusable export and phase method

`art/cartoon/seasonal-v1/export.py::resample` is the frozen premultiplied RGBa filter: oversampled BICUBIC affine followed by LANCZOS downsampling. `S/foam-refresh-v1/export_v2.py` uses one call per raw, with common source-to-world transform x=.25*raw_x+696, y=.25*raw_y+548. Its full-source footprint is 384x256. `S/foam-shading-v1/export.py` reuses that path for the corrected 007. Reuse these primitives in a new low-tide recipe; do not change a frozen high-tide recipe or stack repeated resamplings.

`S/foam-refresh-v1/generation.json` records the useful phase technique: an accurately registered ground guide plus authentic original phase geometry and approved white foam style references. Generate the first thin broken arc; use it as a style and geometry reference for neighboring phases, varying small breaks and crest spacing while keeping common endpoints and scale. Prompts asked for two or three interrupted white/cream strokes with restrained pale cyan accents, true alpha between strokes, no sand, ocean fill, glow or dark shadow. Prompted movement was checked afterward because generation can move a crest in the opposite direction.

High-tide ground is owned solely by 000. These selected waves contain foam, not duplicated ground. `art/cartoon/shoreline-repair-v1/foam-contact-v2/export.py::occlude` computes effective foam alpha A*(255-ground_alpha)/255 and preserves RGB. This is an explicit offshore visibility mask, not exact global translucent ground-over-foam compositing. Moving an already masked sprite cannot recover deleted strokes. If new low-tide offshore ripples need land exclusion, align the full source first and inspect its interaction with the approved low beach/rock; do not blindly reuse the high-ground mask or mask intended incoming wash.

## Practical low-tide mapping

The approved low beach 001 is 768x138 at HD origin [498,606]; rock 002 is 128x60 at [300,656]. Keep their shells, starfish, sand and rock static. Low waves are unflipped at these logical origins:

| Low family | HD origin | Runtime canvases | Initial reuse recommendation |
| --- | --- | --- | --- |
| 030-032 left | [466,646] | 240x96, 256x96, 240x96 | Reuse unmasked 003-005 in one common family transform. The 144x58 source rectangles permit about 1.6x uniform scale inside 240x96 before filter fringe. This is a size estimate, not a verified shoreline placement. Keep 031's extra canvas padding distinct from artwork scale. |
| 033-035 center | [734,712] | 352x56 each | Reuse 006, clean007, 008; actual measurements below show near-direct fit. Check placement against the approved lower beach, not the old upper shore. |
| 036-038 right | [1116,646] | 176x96 each | Reuse unmasked 009-011. A common uniform factor around 1.2 fits the 144x64 source rectangle with padding; derive its final translation from the actual coast. No per-phase stretch or independent fit. |
| 039-041 rock | [258,680] | 208x58 each | Use a new shallow open-top ring based on original 039-041 geometry and the approved white style. The new rock is visibly wider than the old contact region, so include the actual approved rock as a placement-only guide. |

Measured unmasked center bounds, right/bottom exclusive:

| Phase | A>0 | A>=8 |
| --- | --- | --- |
| 006 | [28,103,357,156] | [30,105,355,154] |
| clean 007 | [25,101,362,156] | [26,104,360,154] |
| 008 | [27,100,362,158] | [29,102,359,156] |

The common A>0 union is 337x58; the common A>=8 union is 334x54. Meaningful artwork fits a 352x56 canvas at unchanged scale, but all faint pixels cannot fit by translation alone: the union is 2 HD pixels too tall. A single common reduction no larger than 56/58 (about .9655) geometrically fits that envelope before filter fringe; another choice is explicit canvas padding. Do not call a meaningful-alpha fit a full-alpha fit or silently delete the fringe. This finding was sent directly to the export owner.

Four low families advance in a staggered global sequence every 160 ms. Each family changes every 640 ms, with a complete three-phase recurrence of 1920 ms. Initial phases are 030/033/036/039. Preserve native timing rather than copying the high-tide 1440 ms review loop. Source center 033-035 exposes progressively more ground overall, so original low-tide phase order cannot be inferred from the opposite high-tide incoming-water study. The user selected the offshore style; do not turn this reuse into an unrequested incoming surf remake.

At this review the only generated rock-ring file found is the newly created `art/cartoon/low-tide-v1/rock-waves-v1/039-raw-v1.png` and its `generation-039-v1.json`. Parent confirms this was just generated, not previously approved artwork. Its prompt explicitly uses original 039 geometry, approved high-wave 006 style, and the approved new rock placement. It is a new low-tide candidate, not evidence of prior ring acceptance.

## Approval and color limits

Old authoring recipes still say accepted=false or comparison-only because they are frozen historical checkpoints. Final high-wave acceptance is in `S/side-fit-v1/selection.json`, SHA256 `2e3796f8417a98bc249f71d3d9599a3f1dc5be987eb2c0f0c11818eb426341bb`, then `art/cartoon/shoreline-repair-v1/integration-v1/production-acceptance.json`. The user chose offshore ripples and later accepted the repositioned sides plus clean center with "Looks good, proceed". This does not approve new low-tide placement automatically.

The clean 007 was an imagegen correction, not programmatic recoloring. `S/foam-shading-v1/generation-v1.json` and `appearance-approval.json` preserve that distinction. Old 007 had 123,597 pixels with alpha>=8 and max(R,G,B)<100; the corrected raw and neighboring 006/008 have zero. Check actual alpha and RGB together: hidden RGB under alpha zero is not a visible dark shadow.

An explicit authorization for code color correction exists in `art/cartoon/skin-tone-v1/human-palette-reference-v1.json`: "Use image 2's lighter tone; correct colors in code" (the stored exact response uses a typographic apostrophe). That record is scoped to Johnny skin with geometry and alpha preserved, not a blanket approval to recolor or erase wave material. Reusing the already approved white wave pixels avoids inventing either a new color operation or a new permission claim.

Recommended review is the approved static low tide plus all four complete wave families, with no props and with clovers, then a shifted/night scene. Inspect crest alignment, rock-ring clearance, visible dark pixels and full alpha retention at native scale. Existing native restoration should expose unchanged static sand when a phase retreats. This report introduces no gate or test harness and makes no unexecuted test claim.
