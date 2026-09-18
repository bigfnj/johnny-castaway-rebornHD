# Campfire props and raft: 25-drawing review

Prepared on 2026-09-18 after the user's approval of all 28 FIRE1 campfire drawings. This batch awaits its own appearance approval. It does not change the production archive or its 63 Cartoon assets.

Open [the gallery](review.html), served locally at [the 25-drawing review](http://127.0.0.1:8941/campfire-props-v1/review.html). The page offers original comparisons and light/dark checkerboards. Each card fits the artwork for inspection; card size is not native scene scale.

| Group | New drawings | Frames |
| --- | ---: | --- |
| Fish | 9 | FIRE2 001/002/012/013/014/017/018/020; FIRE5 002 |
| Boots | 9 | FIRE2 004/005/009/015/016/019/022/023; FIRE5 001 |
| Squid | 5 | FIRE2 006/007/021/024; FIRE5 000 |
| Raft and paddle | 2 | SRAFT 000/001 |

The selected drawings are version 1 except FIRE2 009/015, which select version 3. The built-in image-generation tool produced each drawing separately. [Generation files](generation/) retain exact request JSON, raw PNG and per-drawing records with reference/output hashes, including the earlier boot attempts. Raw PNG bytes and alpha are unchanged. Shared identity keys are FIRE2 020 for fish, 023 for boots and 006 for squid. SRAFT uses the approved MRAFT 004 wood/rope drawing for material guidance and its own exact original frames for geometry.

## Source interpretation

[Source selection and scene evidence](../fire-v1/next-batch.md) document every slot. [reference/source.json](reference/source.json) binds exact original and HD extractions, their input archives and technical nearest-neighbor views. Original colors are from the port's diagnostic dump palette, not a verified original executable display.

Three identical FIRE2 marker slots (000/003/008) are retained byte-for-byte in `source-preserved/`. They are not counted as drawings. FIRE2 010/011 are small Johnny grip overlays and remain with character work. The historical inventory's `not_johnny` label is too broad for those two frames. MJFIRE tag 47 draws boot 023 followed by grip 010; tag 49 similarly joins fish 013 and grip 010. The original-pixel composite confirms the hand relationship. Correct that classification with the next inventory regeneration; do not promote these grips as approved non-character props.

FIRE2 018 is only a fish tail and 019 only a boot toe/sole piece. Do not fill them out into complete objects. FIRE2 021/024 are compact squid cooking/eating states, not fish skeletons. The original visible pixels of FIRE5 000 mirror FIRE2 024; FIRE5 001 similarly mirrors FIRE2 023. The generated companions preserve visual identity and direction, but are not asserted to be pixel-exact reflections. FIRE5 002 is a distinct fish view. No FIRE5 TTM load was found in the saved static map; its runtime use remains unconfirmed.

## Review and integration boundaries

The gallery draws each entire raw RGBA image. Alpha >= 8 bounds control display size and centering only; no alpha threshold or creative pixel processing is applied to the raw files. Colored RGB underneath alpha zero is invisible in the browser. Inspect light and dark composites before diagnosing a halo from a raw-image viewer.

Known draft differences remain visible for human review: FIRE2 009/015 v3 shorten the overly long v1 shafts while retaining their near-front direction, but are still narrower than the source. The broadside v2 attempts were rejected. FIRE2 022 is wider/flatter, fish 017 is narrower, FIRE5 002 is wider, and fish 013 has a small added upper-front fin. These are recorded interpretation differences, not proof of native fit. Review the whole group before deciding whether further redraws are needed.

Source numeric order is not an animation loop. Fish/boot/squid cooking and eating interleave these props with Johnny in FIRE4 and other components in FIRE3. SRAFT's raft and paddle have separate native origins/layers in SJLEAVES. Full original-canvas fitting, hand/mouth joins, native scene timing, smoke testing and regressions remain at the bulk milestone requested by the user. No fabricated motion preview is used here.

`build_review.py` constructs the gallery and binds selected raw/reference/request/record files in `review-record.json`. `record_root_outputs.py` documents the five root-owned raw copies; the other records were saved by the parallel authoring agents. `prepare_references.py` only extracts references and creates diagnostic enlarged views. These authoring helpers are not runtime code.

## Subsequent direction review, 2026-09-18

The user identified incorrect orientation and eye placement in 13 drawings: fish 012/013/014, boots 005/009/015/019/022, and all five squid views. In particular, the fish are upside-down, boot 009/015 face away from the camera, and four squid frames need both eyes visible. These are semantic pose errors, not merely proportional interpretation differences. The earlier PNGs and shown review remain frozen as history. [The correction review](../campfire-props-direction-v2/README.md) records the exact feedback and revised artwork. The remaining 12 drawings are unchanged and are not implicitly approved.
