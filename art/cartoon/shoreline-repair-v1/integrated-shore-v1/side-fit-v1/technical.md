# Side-wave comparison footprints

The enlarged ground masks substantial parts of the old side waves. Moving the original unmasked drawings as whole families, then recomputing the same ground visibility mask, recovers those strokes without resizing or repainting them. `geometry.json` records all nine high-tide phases and their exact inputs. Alpha mass includes translucent fringe and is not a count of wave lines.

The evaluated left translation is [-6, 8] HD pixels. It retains 99.94%, 99.95%, and 91.94% of source alpha mass for frames 003, 004, and 005. The right translation is [10, 10], retaining 99.42%, 97.10%, and 98.28% for 009, 010, and 011. Frame 005 still has some intended ground occlusion. These are comparison candidates, not visual approval. Ground and center waves remain unchanged.

| Family | Exact original logical size | Registered runtime canvas | Normal offset | Mirrored offset | Unmodified source placement |
| --- | --- | --- | --- | --- | --- |
| 003-005, `cartoon-island-left-foam-v1` | 72 x 29 | 150 x 66 | [-6, 0] | [0, 0] | 144 x 58 at [0, 8] |
| 009-011, `cartoon-island-right-foam-v1` | 72 x 32 | 154 x 74 | [0, 0] | [-10, 0] | 144 x 64 at [10, 10] |

The resource name, frame family, original dimensions, loaded dimensions, selected Cartoon style, and scale 2 must match. Legacy canvases remain valid. Original resources, logical draw coordinates, HD fallback, and production archive bytes are unchanged. Existing normal, flipped, and atop draw paths already use the shared offset helper. Existing dynamic wave dirty bounds already include actual loaded sizes and offsets; no additional graphics or island source change was needed.

## Executed verification

Compiled headless probes passed 5 smoke cases before 44 regression cases. All 13 rebuilt source mutations fired at their named witnesses, including seven new side-family cases. All 13 restored positive cases then passed. The probe covers legacy/new loading, wrong frame/source/canvas/style/scale, actual normal/flip/atop placement, shifted scenes, surface cleanup, and redraw of both side boundaries when foam recedes.

Authoring checks passed 11 smoke tests before 178 regression tests, followed by both current metadata/catalog reproduction checks. Four fresh-process mutations allowing wrong family slots or wrong original dimensions produced the intended single failing test; the restored positive passed. Synthetic ledger, recipe, and PNG fixtures exercise pack/catalog handling. No production package was written.

`runtime-verification/verification.json` binds the exact reports, logs, tested source snapshots, and geometry measurement. Snapshots preserve actual tested bytes under the existing `-text` art attribute. Maintained source files may acquire platform-specific line endings on checkout; the snapshots retain the source hashes reported by these runs.

## Reproduction

Use a fresh checkout of this change based on `bea77690ea03a7b7c6e3488cb88bee0148b13c1d`, with Python and Pillow plus a C compiler. For exact recorded source bytes, copy `runtime-verification/source/` over the checkout root before testing. The remaining files come from that base and this source change. The production archive must remain SHA256 `4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`.

The executed compiler environment was Docker image `sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72`, with networking disabled. Mount the fresh checkout read-only at `/source` and a fresh host output directory at `/out`. Run these two commands in separate containers and separate output directories, in order:

```text
python3 -B /source/tests/test_art_footprint.py --output /out --phase smoke
python3 -B /source/tests/test_art_footprint.py --output /out --phase regression --mutations
```

From the checkout root, run the ordered authoring helper below. It requires a fresh, absent `build/side-fit-v1/authoring` directory and writes only there. Its report retains each exact subprocess command and the order of smoke, regression, checks, and mutations.

```text
python -B art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/runtime-verification/run_authoring.py
```

`measure_geometry.py` can recompute `geometry.json` from the pinned production archive and retained offshore source/output PNGs. It uses Pillow only and does not alter images. Historical evidence reports are records, not scripts to overwrite during replay; use fresh scratch outputs.

The C probe uses a synthetic surface decoder, not a full PNG/native scene capture. Native animation and the visual acceptability of these translations require the separately prepared A/B capture. These checks do not approve the new wave placement or change art approval history.
