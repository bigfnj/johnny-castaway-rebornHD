# Legacy cleanup verification

See [the execution plan](legacy-cleanup-plan.md) for phase order and decisions.
This record distinguishes completed checks from pending integration work.

## Baseline checkpoint

Source: main `55b864b8ef54a5c700138e16b74e8d5d62a5d305`, built in the isolated
`fix/legacy-cleanup` worktree before implementation changes.

The PowerShell 7 full gate passed with no compiler warnings: 27 native smoke,
27 screensaver/settings, two art smoke, wave and palm smoke, then 31 art,
seven wave, eight palm and 20 authoring regressions. All 2,452 golden files
matched. The full local log is `build/cleanup/baseline/gate.log` (ignored).

The baseline Windows executable SHA-256 is
`7ac76d5374ab9b36e70cdc442d082a6fafcdb32df66261c8a2df42c770da53ad`.
The production archive SHA-256 is
`fb70d795531d50093dd4a9ac53895a6a20a76efc982d4d7d45a64403b98e68d8`.
Frozen local binaries are under `build/cleanup/baseline-binaries` (ignored).

Eight complete PPM captures were each repeated in fresh processes and matched
byte-for-byte. Each run used `window nosound holiday none seed 9 maxspeed`, the
listed lighting/style/frame count, and `island ads ACTIVITY.ADS 7`, with an
isolated settings directory. Exit code, bounded-run message, capture message and
1280-by-960 PPM output were checked. These are deterministic Windows comparisons,
not a cross-platform RNG guarantee or full story coverage.

| Case | PPM SHA-256 |
| --- | --- |
| HD day, frame 1 | `40281483f3fda613d0ad40e4d7f8c15b43e9075304468a94e446386d2e3552cb` |
| HD day, frame 13 | `f4525bcb857923503373ad1ac2d848cf4e532143f59808cecb44254417972add` |
| HD night, frame 1 | `416e458d62b0457b1ac4988755fa6c8af03e5788b9b182611a8b0d5970cfd6d3` |
| HD night, frame 13 | `0312ce064f78c940028c03b1b893e7370d46e83a7a41ff189acfab14504683de` |
| Cartoon day, frame 1 | `fb8543e3dcf9a5dc95bbcee56b771bffcfb5a6bf46948a73a0bb3e1d4b942d56` |
| Cartoon day, frame 13 | `793ea49e5de5d6d9859c4967867151d78ce76709f9dd7724ee8e409698614d9f` |
| Cartoon night, frame 1 | `8a167889f5a738fe087b88a4434222f2ef82d3282cfcb6e496363d279acf2344` |
| Cartoon night, frame 13 | `f5e09bc9a2cbd7056249abc3b6264fd049bdb3234f8dc3d791369fe236c300c9` |

## Integration status

Implementation phases and post-merge audit are pending. Append actual results
as each phase passes; baseline success alone does not validate later changes.
