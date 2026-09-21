# Worker thumb and rope edits

Draft selections for human review are LILIPUTS.BMP078 v1 and 093 v1 in this family. No appearance approval or runtime approval is implied.

078 uses the prior worker-tool-pose-corrections-v2 078 v2 as the edit target. Its corrected shoulder arrangement is retained: the near free arm reaches down in front of the torso, while the far hammer arm emerges behind the head. The thumb has moved from the image-left/upper-left side of the grip near the handle butt to the image-right/lower-right side toward the hammer head. The wrist, diagonal hammer and crouching pose remain coherent.

093 uses the prior worker-tool-pose-corrections-v2 093 v1 as the edit target. The user's new explicit instruction to attach the rope supersedes the earlier detached interpretation. The right end of the slack left rope now joins a compact wrap around the nearby wooden peg, just below its top. The peg stays directly under the mallet and close to the worker. The empty hand and remaining body pose are retained.

Both exact requests were saved before their built-in image generation calls. The recorder copied raw outputs without alteration and recorded target hashes, request hashes, output hashes and raw cache paths. No artistic postprocessing was used.

| Frame | Output SHA256 | Canvas | Edge alpha maximum |
| --- | --- | --- | --- |
| 078 v1 | 64a729ff348e8a00bb35683ea70535222a5b050b9ec4561d5a87bfc0410fdc5f | 1342x1172 | 0 |
| 093 v1 | b0db6185458a42cd52c02dd82153027c4f70e8912b5105ff7746e4577a5e5656 | 1649x954 | 0 |

Both outputs are RGBA with alpha range 0 to 255. Technical light/dark composites were inspected at build/worker-thumb-rope-alpha-review.png. No visible halo, cut contour or extra limb was found. Native fitting and motion were not tested in this draft edit pass.
