# Legacy cleanup verification

See [the execution plan](legacy-cleanup-plan.md) for phase order and decisions.
This record preserves completed checks and the limits of their evidence.

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

| Phase | Completed evidence |
| --- | --- |
| Native build reliability | Full Windows gate passed without warnings. The actual runtime-data module passed explicit console/screensaver, ALL and data target controls, alternate output paths and deleted-copy recovery without relinking. Both disabled prerequisite mutants failed the named freshness assertion. The isolated real-application wiring and stale-gate controls passed under PowerShell 5.1 and 7. |
| Web/macOS build reliability | Official pinned 6.0.9 container compilation passed as root and UID 1001, followed by host browser smoke and all ten style-control regressions. Six executed build-contract mutants fired. Draft PR CI also passed the real Intel macOS architecture checks, including the compiled ARM64 negative control; no release was published. |
| Decoder output validation | Two complete-stream smoke checks and all eleven decoder regressions passed, including malformed actual RESOURCE archives and the existing LZW full-buffer return. Full Windows gate passed without warnings. All eight controlled scene captures match the frozen baseline byte-for-byte. Three isolated rebuilt decoder mutants fired. |
| Resource ownership | Two focused smoke checks and all five ownership regressions passed against real engine code and Windows surface allocation. Full Windows gate passed without warnings; all eight baseline scenes remain byte-identical. Ten isolated rebuilt ownership mutants fired, including inactive layers, borrowed aliases, reinitialization, saved overlays and repeated teardown. |
| Platform integration | Windows constructor/WIC smoke passed before nine allocation-failure regressions, then the full native gate passed without warnings and all eight baseline scenes remained identical. Worker validation passed 19 Linux pthread/X11 cases and ten Web cases, plus Linux full-application HD/Cartoon startup and the golden corpus. Rebuilt backend mutants fired: 16 Linux, eight Windows and seven Web. Final macOS CI passed 12 ordinary backend cases and all ten rebuilt mutations. Xvfb resize checks do not establish desktop fullscreen negotiation. |
| Final code/API integration | The complete integrated gate passed under Windows PowerShell 5.1 without compiler warnings. It includes the existing native/settings/art/wave/palm/authoring suites and golden corpus, plus decoder smoke then 11 regressions, ownership smoke then five regressions, and platform smoke then nine regressions. Four graphics-caller failure controls and their rebuilt mutants passed on Linux. Independent review confirmed unused-field removal preserves header consumption and EOF checking. All eight controlled scene captures match baseline. |
| Historical renderer comparisons | Against the frozen baseline binaries, all nine complete HD/fallback wave captures and all four palm HD/partial-fallback captures matched byte-for-byte. The focused suites ran smoke before their seven wave and eight palm checks. |

Local integrated logs are `build/cleanup/phase1-native-build/gate.log` and
`build/cleanup/phase2-decoder/gate.log`, followed by
`build/cleanup/phase3-ownership/gate.log`,
`build/cleanup/phase4-platform/gate.log` and
`build/cleanup/phase5-final-integrated/gate.log`. Capture evidence is in the
corresponding `phase2-scenes` through `phase5-scenes` report directories.
Historical comparisons are under `final-wave-history` and `final-palm-history`.
Worker mutation reports are retained
in their isolated build directories, and the corresponding commit messages
record the results. Tests and reproduction commands are tracked in `tests/`.

Draft PR CI run `34927812623` passed Windows, Linux, Web and macOS on `2b330e3`.
It exercised Visual Studio 2022 runtime-data fixtures and real Intel package
verification. An earlier Windows fixture failure exposed short/canonical path
comparison and missing retained diagnostics; the test now resolves the reported
path identity while still requiring the exact stale-data diagnostic and refusal
before smoke. Executable hash/mtime and no-relink assertions were retained.

Final PR [CI run 34928938740](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/34928938740)
passed all four platforms on `5d1fb9d`, including final API cleanup, central probe
wiring, the real macOS compiler/runtime and all ten Cocoa mutations. The mutation
report is retained in the run's `macos-mutation-evidence` artifact and locally at
`build/cleanup/final-macos-mutations/mutation-report.json`.

The first newly wired macOS run exposed a fixture problem: AppKit did not deliver
a synthetic key posted for windowNumber zero before application launch. The test
now supplies an ordered queue of real NSEvent objects and checks exact dispatch
counts while retaining production polling/translation. This does not claim OS
key-delivery coverage. All original assertions remain; no production change was
needed for that failure.

[PR 4](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/4) merged as
`50eb6f4bc4b1bea704d03bbdda360be216be7d31`. The post-merge main rebuild passed
the complete PowerShell 7 gate without compiler warnings, all eight frozen
scene comparisons and [four-platform main CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/34929288040).
The full [independent audit](legacy-cleanup-audit.md) found additional existing
drawing/ownership defects and unused platform state for a bounded follow-up.

## Post-merge audit follow-up

The drawing probe passed two smoke cases before six sanitized regressions.
Independent expected circle pixels prevent a no-op renderer from passing;
12 complete buffers at scales 1 and 2 also matched the pre-fix arithmetic variant
on the tested Linux compiler. All seven isolated rebuilt source mutations fired
the intended diagnostic/assertion, with advanced artifact timestamps and case
execution witnesses. Linux gate-order controls passed 11 cases; all six
continuation mutations fired, including both new drawing phases. Reports are
retained in the drawing worktree under `build/drawing-audit/verified-smoke`,
`build/drawing-audit/verified-regression` and `build/drawing-flow-wiring`.

Independent code review confirmed the cached-name copy precedes release and
subsequent resource lookup uses the new owned name. The unused platform color-key
API had no callers. Removing it preserves active fullscreen state and the
separate PNG alpha conversion. Worker checks passed Windows, Linux and Web
backend smoke then regression.

The integrated follow-up at `b7bc1b0` passed the complete Windows PowerShell 7
gate without compiler warnings (`build/cleanup/phase6-audit-followup/gate.log`).
The complete Linux gate also passed without warnings: PNG, decoder, platform
and drawing smoke before regressions, 11 decoder cases, 16 platform regressions,
four graphics-allocation cases, six drawing regressions with 12-buffer parity,
and all 2,452 golden files. Its retained log/report are under
`build/cleanup/followup-linux/output`.

All eight controlled HD/Cartoon scenes, nine full HD/fallback wave captures and
four palm HD/partial-fallback captures match the frozen pre-cleanup binaries
byte-for-byte. Evidence is under `phase6-scenes`, `phase6-wave-history` and
`phase6-palm-history` in `build/cleanup`. The production archive hash and all
tracked assets, art records and image lessons remain unchanged.

The follow-up is delivered through a separate pull request on
`fix/legacy-cleanup`. Its four-platform checks and the subsequent main workflow
retain the hosted delivery evidence; the local records above describe exactly
what was executed before submission.
