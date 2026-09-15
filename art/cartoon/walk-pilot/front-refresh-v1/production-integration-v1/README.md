# Approved front walk integration

`verification.json` records the 2026-09-15 package smoke and subsequent independent regression comparison. The archive contains 2,579 members. Only Cartoon 028 and 029 changed; the other 2,577 members, including all original resources and the runtime manifest, remain identical. The final archive is byte-identical to the native-reviewed private archive (`1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63`). A deliberately corrupted scratch ZIP produced exactly one failure naming 028, then was removed.

`rebuild.py` materializes all 28 accepted PNGs in a fresh scratch directory, runs `tools/art_pack.py validate`, then builds a separate archive. It independently reads every ZIP member, verifies the exact two-frame delta, checks the frozen evidence identities and preserves the other 26 pack rows. An optional private candidate permits direct comparison against the reviewed ZIP as well. The default does not promote anything.

To reproduce after promotion, recover the old archive from commit `4551081495eee81e5e5bf2d8b5f00a5619a176a2` in a separate detached worktree. Run each command separately, substituting fresh local paths:

```text
git -C <repo> worktree add --detach <baseline-checkout> 4551081495eee81e5e5bf2d8b5f00a5619a176a2
python -B <repo>/art/cartoon/walk-pilot/front-refresh-v1/production-integration-v1/rebuild.py --repo <repo> --baseline <baseline-checkout>/assets/scrantic_data.zip --output <fresh-scratch-directory>
```

The baseline ZIP must hash to `0748676eb6ab0685abecfeb0bbfb8547d2050e6419bb1cad5f13ccc9f716fedd`. The approved checkout supplies the current pack and frozen exported 028/029 PNGs. This packaging helper uses the Python standard library and does not regenerate artwork. Reproducing the source-to-PNG export separately requires the recorded Pillow 12.3.0 workflow in `../review-evidence/motion-v1/`.

If the private reviewed ZIP is available, append `--private-candidate <private-zip>`. The original integration used `build/front-native-review/candidate-v1/scrantic_data.zip`. Its absence is explicitly recorded in reproduction reports; expected member hashes still derive from the pinned baseline plus the two pinned accepted PNG identities.

`--promote` is reserved for integration into a checkout whose production ZIP still has the pinned baseline identity. It replaces that ZIP only after successful smoke, complete member checks and the executed corrupted-member control. It refuses a checkout that has already been promoted. Reproduction reports are written into the new scratch directory; do not overwrite this historical verification record or any earlier human approval/capture evidence.

The human acceptance is recorded separately in `../production-acceptance.json`, including the exact island response `pass- proceed` and the earlier standalone response `much better proceed`. This package verification does not expand their visual review scope. Native scene capture, browser checks and platform gate results have separate records.
