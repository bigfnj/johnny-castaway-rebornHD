# Independent cloud preflight

Read-only review at `de1e489e5c2fe3b22d03e8650bfc26cc1d8a12cc`. Production `assets/scrantic_data.zip` is SHA-256 `a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66`, with 2,612 members and 61 Cartoon assets. This checkpoint concerns only two proposed additions, `BMP/BACKGRND.BMP/016.png` and `017.png`. The separate `CLOUDS.BMP` reference frames are not implicitly included.

| Frame | Logical canvas | Runtime canvas | Current selection |
| --- | --- | --- | --- |
| BACKGRND015 | 128 x 36 | 256 x 72 | Approved Cartoon, retain exact bytes |
| BACKGRND016 | 192 x 57 | 384 x 114 | HD fallback, target new Cartoon PNG |
| BACKGRND017 | 264 x 76 | 528 x 152 | HD fallback, target new Cartoon PNG |

Direct ZIP readback gives accepted015 SHA-256 `d7f6f6608cb18ac169b6e4378cb5c12c30a9139d7925c36e8a02f1c8eea41649`, HD016 `05487f196124175837e0685f7efc09a27e10306961ed8583157a718d842d012b`, and HD017 `17c76381bdd32a00d82475966483eab59403b4baac7d801c7b423790f42c2a80`. The 015 ledger points to `island-pilot-v1/palm-sand-cloud/recipe.json` and the Calm focus production acceptance, which records that exact PNG. The source manifest and newly prepared original references agree on both target dimensions. A handoff's 258 x 72 description for 015 was a message typo; its actual PNG and reference record correctly say 256 x 72. The historical placement expression `SCREEN_WIDTH - 129` is not its canvas width.

`src/engine/art_style.c:350-430` selects Cartoon first, then matching-scale HD, then decoded original fallback. Clouds use ordinary exact 2x dimensions and zero registered offsets. They require no footprint declaration or runtime modification. Cartoon retains authored alpha; the HD fallback separately keys opaque RGB168,0,168. `island.c:326-375` clears the cloud layer, advances native positions, draws 015 through 017 and mirrors the full sprite for the opposite wind. Preserve the complete canvas and its registration.

Night chooses `NIGHT.SCR` (`island.c:161-169`), but neither the PNG loader nor cloud drawing applies a night tint. The same authored cloud RGB/alpha appears against day and night backgrounds. Human review should therefore include white brightness, gray undersides and translucent edge halos on the actual night scene alongside unchanged015. Original reference images use the documented diagnostic palette and do not establish original-executable nighttime colors. Explicit cloud state fixtures must be labeled as such; seeded natural selection can produce zero clouds and differs across libc implementations.

The minimal maintained authoring sequence below runs from the repository's `tests` directory, with the toolbox Python selected through its existing environment variable. These are recommendations, not executions by this audit.

```powershell
& $env:TOOLBOX_PYTHON -B -m unittest -v test_art_tools.ArtToolsTests.test_true_alpha_preserves_opaque_magenta_and_binary_control test_art_tools.ArtToolsTests.test_build_is_repeatable_preserves_originals_and_refuses_overwrite
& $env:TOOLBOX_PYTHON -B -m unittest -v test_art_tools
```

The first command is the focused smoke; the second runs the 28 maintained authoring tests, including damaged dimensions, PNG format, alpha, source/hash and duplicate-member controls. The eventual cloud exporter still needs actual two-frame source/recipe/output replay and its own changed-guard controls. These synthetic tests alone do not verify newly authored pixels.

The native owner supplied this planned entry point, from the repository root, with the actual candidate path and digest substituted:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/clouds-v1/native-v1/run.py --candidate <private-candidate.zip> --candidate-sha256 <sha256> --output build/clouds-v1/native-v1/<fresh-output>
```

The adapter is being prepared and was not available for inspection at this preflight. Its agreed minimum is day in both winds, shifted night, and a zero-cloud exact control; all case smokes precede fresh process repeats. It will use the real cloud scheduler with explicit source-valid positions/speeds, recording draw/flip, timing and blit extents. Require exactly two added PNGs, all 2,612 prior payloads unchanged, unchanged015, and a resulting 2,614-member / 63-Cartoon candidate. Meaningful native differences must stay within the recorded moving016/017 canvases; zero-cloud output must be identical. Source and package hashes must stay fixed through smoke and repeats.

`tools/art_pack.py:104-132` replaces the entire Cartoon prefix when building. Do not pass a two-row-only ledger to its build command: use all 63 rows or the native owner's exact checked two-member overlay. A two-row ledger is suitable only for standalone validation of those two files. No production promotion, catalog regeneration or full Windows gate is needed for this review-only checkpoint. No gates or captures were run and no production files were changed by this audit.
