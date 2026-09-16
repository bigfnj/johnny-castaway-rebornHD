# Complete supplied-original image source

This source bundle covers every original BMP and SCR slot before any Johnny
classification: 117 BMP resources containing 2,392 frames, plus 10 screens.
The application has 2,391 corresponding BMP slots and 10 screens. The extra
original drawing is `SA_DEMO.BMP/000`. Resource names do not determine whether
a frame contains Johnny.

`frame-index.json` binds every native PNG to its original XPM, original canvas,
row-major index/RGBA hashes and corresponding bundled HD proxy. Those proxies
are mapping references, not the source of these PNG pixels. All 2,453 files in
the preserved native dump were checked against its historical manifest before
export. No original binary or bulk image copy is stored in this source folder.

The PNGs use the port diagnostic dump palette. BMP index 0 becomes transparent;
all SCR indices remain opaque. Original executable colors, compositing and
timing have not been calibrated. The previous independent decoder comparison
covered 79 selected images, not this entire 2,402-image set. This extraction
verifies the complete historical native dump and does not enlarge that earlier
independent-decoder claim. Bounds may include gray shadows.

Use the supplied `RESOURCE.MAP` and `RESOURCE.001` under the locally installed
`C:/JohnCast/SIERRA/SCRANTIC`. The preserved dump cache currently lives under
`D:/.ai-work/worktrees/johnny-maintenance/build/maintenance/original-pixel-reference`.
It must contain `report.json` and `dump/`; its report must exactly equal
`historical-dump-manifest.json`. The historical decoder executable hash identifies
the earlier run, not the Python converter. If that cache is unavailable, restore
or regenerate a local native dump and independently compare it against this
manifest before treating it as the same reference. Do not relabel a different
decoder run as the historical execution.

From the repository root, using Python 3.11 and Pillow 12.3.0:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/character-inventory-v1/source/prepare.py --dump-root D:/.ai-work/worktrees/johnny-maintenance/build/maintenance/original-pixel-reference --original-root C:/JohnCast/SIERRA/SCRANTIC --output build/character-inventory/originals
& $env:TOOLBOX_PYTHON -B art/cartoon/character-inventory-v1/source/prepare.py --dump-root D:/.ai-work/worktrees/johnny-maintenance/build/maintenance/original-pixel-reference --original-root C:/JohnCast/SIERRA/SCRANTIC --output build/character-inventory/originals --phase smoke
& $env:TOOLBOX_PYTHON -B art/cartoon/character-inventory-v1/source/prepare.py --dump-root D:/.ai-work/worktrees/johnny-maintenance/build/maintenance/original-pixel-reference --original-root C:/JohnCast/SIERRA/SCRANTIC --output build/character-inventory/originals --phase regression
& $env:TOOLBOX_PYTHON -B art/cartoon/character-inventory-v1/source/test_prepare.py --dump-root D:/.ai-work/worktrees/johnny-maintenance/build/maintenance/original-pixel-reference --original-root C:/JohnCast/SIERRA/SCRANTIC --extraction build/character-inventory/originals --output build/character-inventory/originals/controls-replay
```

Preparation requires a fresh output directory. Use a different fresh output name
for a repeat; never remove prior evidence just to satisfy the command. Each PNG
path in the index is relative to the chosen extraction directory.

Smoke checks four varied fixtures, including the original-only drawing and a
screen. Regression compares every exported PNG's decoded RGBA with the source
XPM and confirms all 36 established JOHNWALK references. Seven fresh-process
negative controls fail with a named input/frame. A changed pixel with an updated
PNG-file hash still fails original-RGBA validation; removing exactly that guard
allows the same corruption, with the executed mutant-byte hash recorded. A clean
control passes before and after. Original files and production assets remain
unchanged.
