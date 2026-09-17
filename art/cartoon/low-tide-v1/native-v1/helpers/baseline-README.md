# Current Cartoon low-tide baseline

Captured from branch `art/cartoon-low-tide`, commit `da787d63279ea91bd6c637e02133821339470bfc`, using the unchanged production archive `4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6`.

Both no-decoration and clover smoke captures passed before both fresh-process repeats. Each case contains 61 actual native displays over 144 requested ticks (2,880 ms), with every low-wave frame 030 through 041 observed. All captured pixels, timing, calls, draw positions and report bytes repeat exactly. All 60 protected runtime/production inputs remained unchanged. The fresh compiler emitted no stderr; Docker exited 0 and left no task container.

The representative full 1280x960 images are:

| Image | SHA256 |
| --- | --- |
| `captures-v1/none/smoke/final.png` | `3bdea9c72a812dcd0cec944beadd76436cdecace24506a7e0116d305391eaf1d` |
| `captures-v1/clover/smoke/final.png` | `5c7c8c3ee5d8d68fb4a758f4b21f6bbaa0b6acdb6c9ad4beccd23bc8d86745d7` |

Both images were visually inspected. They show the current mixed-art state: approved upper island/palm/Johnny and clovers, existing HD lower beach/rock/low waves, and existing cloud fallback. The fallback palette is not a supplied-original color reference.

## Actual selected scene

The unchanged observer uses seed 11, Cartoon, daytime OCEAN02.SCR, low tide, zero scene offset, raft 0 and 24 repeated `adsPlayWalk(0,0,0,0)` calls. No phase values are forced. The native wait path displays Johnny016 unmirrored at logical 299,243. Clover mode selects HOLIDAY001 at logical 333,286, canvas 240x94. State selection is explicit and does not test calendar/cargo policy, random story selection or original executable behavior. Native ticks are recorded requests; this max-speed capture is not a wall-clock playback measurement.

| Layer/family | Native logical origin | Actual canvas in HD pixels |
| --- | --- | --- |
| Ground000 | 288,279 | 640x180, actual surface at 540,548 |
| Beach001 | 249,303 | 768x138 |
| Rock002 | 150,328 | 128x60 |
| Waves030-032 | 233,323 | 240x96, 256x96, 240x96 |
| Waves033-035 | 367,356 | 352x56 each |
| Waves036-038 | 558,323 | 176x96 each |
| Waves039-041 | 129,340 | 208x58 each |

The logs record low-wave logical draws and display phases. The retained observer directly logs actual surface placement for ground/high waves, not low-wave surface blits. The low-wave positions above therefore identify the observed logical draw and canvas, not a newly instrumented low-wave surface destination. Existing low frames have no selected footprint offset.

## Execution and evidence

Executed host command from this worktree:

```powershell
& $env:TOOLBOX_PYTHON -B build/low-tide-v1/baseline-native/run.py
```

`launch.json` preserves the full command, commit and pinned existing Docker image. The source mount was read-only, networking disabled, rendering isolated under Xvfb, and no workstation window was opened. `captures-v1/build.json` binds the fresh executable, compiler command and compiled sources; `inputs.json` binds runtime/production/helper hashes. No tracked helper or runtime file was edited. The scratch adapter reuses the frozen observer, codec and final placement verifier with its current-approved-footprint branch. It does not run the historical prior-production or 14-change package contract.

| Record | SHA256 |
| --- | --- |
| `launch.json` | `10ccc7745c8fe498dc260a13b989e454d3c414eeffb7051c635b5bbfc6fbf6b0` |
| `captures-v1/inputs.json` | `71e3bef729d6934835135bb8b1b6f3b30d0450a8e0191de82f47281a1b50e981` |
| `captures-v1/build.json` | `7c506bde8596d57113509955271927f703b5c652252e29dc2408dfec00995839` |
| `captures-v1/summary.json` | `b35db16764e93362d6392e0f281bb90148cc21a9c4ff9e19408c3ab618239063` |
| Both `none/{smoke,repeat}/report.json` | `7603f2022db205caa737bd21732dfd16df48a6bcf530faddb641aa45f5778626` |
| Both `clover/{smoke,repeat}/report.json` | `f21469d5e5a47b1e39d53f04c3e9024efca7c620e67855d8eb03faefd3ca897b` |

The launcher refuses existing outputs. Keep this baseline immutable; any replay must use a fresh sibling scratch directory containing the two adapter scripts. Bulk PPMs, local archives and executable remain ignored scratch evidence, not a proposed durable artifact bundle.
