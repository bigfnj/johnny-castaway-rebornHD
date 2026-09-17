# Cartoon cloud delivery

The user accepted the new medium and large clouds with "Yes, keep these clouds".
BACKGRND016/017 join the unchanged approved 015, completing the ordinary moving
cloud family. Production contains 63 Cartoon PNGs: 28 Johnny, 31 island/environment
and four seasonal assets. Coverage remains partial.

The [acceptance record](../art/cartoon/clouds-v1/integration-v1/production-acceptance.json)
binds the exact paired motion review and selected exports. Earlier pending
records remain historical. The night option checked cloud brightness and edges
against the existing fallback background; it does not approve a new night scene.

| Check | Evidence |
| --- | --- |
| Package | Exact reviewed archive `a87a1f52b85277d88129347654a508edf9ca1f82920a31e20b5b41216242f63d`; 2,614 members, with all 2,612 previous payloads unchanged. |
| Art source | Four raw outputs, exact prompts and ordered references retained. Selected v2 exports reproduce with fixed uniform transforms and true-alpha filtering, including a relocated-checkout replay. |
| Authoring review | Two maintained smoke tests followed by 28 regressions passed before review. Invalid binding and escaping-reference controls failed as expected, then restored positives passed. |
| Native review | Eight smoke processes passed before eight fresh repeats. Paired day left/right and shifted night use identical native movement/timing; a no-cloud control is pixel exact. Three damaged-data controls fired. |
| Browser review | All 96 atlas images reconstruct exact native pixels. Actual browser controls, scene selectors, full-scene view and playback end behavior were checked. The reviewed page and media are retained. |
| Integration authoring | 16 smoke tests passed before 189 executed regressions; two Windows symlink-privilege fixtures were explicitly skipped. Metadata, production catalog and character inventory regeneration/checks passed. |
| Windows feature gate | Fresh build, full smoke then regression passed on the first attempt. All 2,452 golden resource files matched, and 32 renderer capture/log pairs were checked. The deployed ZIP equals production; the workstation input desktop remained unchanged. |
| Cross-platform and main | PR CI and post-merge verification follow this feature checkpoint. |

The [review checkpoint](cartoon-clouds-review.md) records the pre-approval work.
The [reusable lessons](art-style-learnings-clouds.md) preserve resource selection,
geometry, alpha and portable prompt-reference handling. Night and alternate
ocean scenes are the next bounded environment work; CLOUDS.BMP use remains
unproven and is tracked in [BACKLOG.md](../BACKLOG.md).
