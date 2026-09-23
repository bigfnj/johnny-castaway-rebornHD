# SMGIFT020–022 gesture correction pass

Built-in imagegen edited the current expression-v1 cartoons against the exact original pixel references. Exact prompts are saved beside each output. All raw PNGs remain unchanged, with their original generated alpha. These are new candidates for appearance review, not user approvals.

| Frame | Preferred version | Visual observations |
| --- | --- | --- |
| 020 | v2 | The emerging hand now points inward at her own upper chest. Its index extends toward her body while the remaining fingers curl. The happy face and low near arm remain. |
| 021 | v2 | The raised index fingertip touches her lower lip in a playful coy gesture. The other fingers are curled; the wrist and bent forearm remain connected. Her cheerful profile is preserved. |
| 022 | v3 | Both arms have separate bent elbows, forearms and wrists. The near/front forearm is shorter and rises diagonally to its hand near her chest. The far hand has a backward-C opening toward image-left, with thumb below and curled fingers above. The far upper arm is partly hidden behind the torso and near forearm, while its separate elbow and forearm remain visible. Her existing laughing face remains. |

022 v2 repaired the long near forearm and separated the arms, but the far C-shaped hand opened toward image-right. One targeted v3 edit reversed only that hand/wrist orientation. Both versions remain saved. No calls failed or returned moderation errors.

Verification: all four raw generated images were copied byte-for-byte. All 15 request/reference/output SHA-256 pins match. Each PNG is RGBA with alpha range 0–255 and edge alpha zero. No selector, gallery, production asset or native animation state was changed.

