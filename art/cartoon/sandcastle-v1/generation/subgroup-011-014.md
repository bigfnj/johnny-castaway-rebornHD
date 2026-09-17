# Sandcastle collapse drafts 011–014

Four built-in `image_gen` calls produced one image per frame for the combined 24-drawing art review. These are generated drafts, with no individual human acceptance or runtime fit claim. The exact generated PNGs were copied into this directory without resizing, cropping, alpha cleanup, repainting, or other pixel edits.

Each `NNN-request-v1.json` preserves the exact submitted prompt and ordered reference paths. Each `NNN-record-v1.json` binds the prompt bytes, source output, generated PNG, shared key and reference hashes, actual dimensions, and measured alpha bounds.

| Frame | Drawing | Raw canvas | SHA-256 |
| --- | --- | --- | --- |
| 011 | Lopsided rubble mound with front arch remnant | 1742x903 | `26740d4bec75f605d3f7b3b006145f4b11535a316ed1d4e020f351a6f7fb54f3` |
| 012 | Smaller mound with low front indentation | 1897x829 | `df9db25c1b1858190582e0712ad6d1cc70c9e66ad74cfae813f8b6590a122110` |
| 013 | Flattened final sand remnant | 2135x736 | `5461674b21f1d00479107810d27db4e74d7d6f9281295d2e66c3f3f6a8c8be5f` |
| 014 | Broken castle walls, low front arch and right-hand debris | 1844x853 | `a12b939a7edb25c5826c40d4fb7316a2350fd31f6c13e2d109e5d9e2e05506fd` |

All four files are RGBA with alpha range 0–255. Their visible shapes use the shared key's cream/gold material and dark brown outline. Frame 013 is a particularly flattened interpretation and needs shape judgment with the other collapse states. Frame 014 retains the separated right-hand broken piece. No unrelated scenery or characters were introduced.

There is faint low-alpha residue outside the main contours. In 013 the alpha-1 bounds reach the bottom canvas edge; in 014 they reach both horizontal edges. The alpha-at-least-8 bounds remain inside all four images. These observations are retained in the per-frame records; the raw alpha has not been altered or thresholded. Later export must account for the complete selected alpha rather than silently discard it.

The three references for every call were the corresponding full-canvas original nearest-neighbor guide, shared `000-generated-v1.png` (SHA `d2314cc0259424837ca8d895c1a91a25d992761b083efe898fd144429f25a1ef`), and the exact approved Cartoon island style PNG. Original diagnostic palette colors were deliberately not used as the color target. No tests, exports, native captures, package writes, Git staging, or commits were performed for this subgroup.
