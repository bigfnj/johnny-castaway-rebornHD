HD assets (PNG override) support
===============================

This fork can optionally override the original Johnny Castaway RESOURCE.001
sprites and screens with external PNG files rendered at higher resolution.

How it works
------------

At startup the engine opens `scrantic_data.zip` (must live next to the
executable). If that zip contains `data/hd/manifest.json`, HD mode is enabled:
the engine reads the "scale" value (e.g. 2) and renders at 640*scale x
480*scale while keeping logical coordinates at 640x480.

HD assets are loaded by path lookup inside the zip — NOT from a loose
filesystem directory. The earlier version of this README described an on-disk
`data/hd/` folder; that was inaccurate. All HD PNGs must live inside
`scrantic_data.zip` alongside the original game data.

Required zip layout
-------------------

Your `scrantic_data.zip` should contain:

    data/RESOURCE.MAP                # always required
    data/RESOURCE.001                # always required
    data/sound1.wav .. sound24.wav   # always required (see tools/extract_sound)

And optionally, to enable HD:

    data/hd/manifest.json            # triggers HD mode (must have "scale": N)
    data/hd/SCR/<NAME>.png           # HD replacement for a screen
    data/hd/BMP/<NAME>/<NNN>.png     # HD replacement for an individual BMP sprite

Examples:

    data/hd/SCR/OCEAN00.SCR.png              # replacement for the OCEAN00.SCR screen
    data/hd/BMP/MJJOG2.BMP/000.png           # sprite 0 of MJJOG2.BMP
    data/hd/BMP/MJJOG2.BMP/001.png           # sprite 1 of MJJOG2.BMP
    data/hd/BMP/MJJOG2.BMP/...

Sprite indices are zero-padded 3-digit (000, 001, 002, ...).

Minimum manifest.json:

    { "scale": 2 }

Supported scale values: 2..8 (integer).

Enabling HD for an existing install
-----------------------------------

1) Start from a zip that contains the base game data:
        data/RESOURCE.MAP
        data/RESOURCE.001
        data/sound1.wav .. sound24.wav

2) Add HD assets into the same zip under `data/hd/`:
        data/hd/manifest.json
        data/hd/SCR/<NAME>.png ...
        data/hd/BMP/<NAME>/<NNN>.png ...

3) The zip must be named `scrantic_data.zip` and placed next to `jc_reborn`
   (or `jc_reborn.exe` on Windows; or baked into the web build via the
   CMake `--preload-file` option).

If `data/hd/manifest.json` is absent or has scale <= 1, HD mode stays off and
the engine falls back to the built-in RESOURCE.001 decoder at 640x480.

If HD mode is on but a particular PNG is missing, that one asset falls back
to the built-in decoder (scaled to match the rendered resolution); the rest
of the HD pack still applies.

Fallback behavior when a specific PNG can't be loaded
-----------------------------------------------------

- PNG fails to open (not found, corrupt, unsupported format) → the engine
  decodes the legacy RESOURCE.001 asset and nearest-neighbor-scales it by
  `scale`. So the scene still renders, just without the HD quality for that
  particular asset.
- Unsupported PNG formats (as of 2026-04-20): 16-bit depth, paletted,
  Adam7-interlaced. 8-bit RGB and 8-bit RGBA (standard export formats) are
  fully supported on all platforms.

Transparency
------------

PNG sprites use real per-pixel alpha.

- Preferred: export PNGs with an alpha channel.
- Backward compatibility: fully-opaque pixels whose RGB is the classic
  "magenta key" color (A8-00-A8) are automatically converted to transparent
  at load time. This means older HD packs that relied on the magenta key
  continue to work without modification.

Screen PNGs (.SCR) are treated as opaque backgrounds and any alpha channel
on them is ignored.

Platform support (as of 2026-04-20)
-----------------------------------

PNG decoding is supported on all four target platforms:
  Windows  — via Windows Imaging Component (WIC)
  macOS    — via the vendored minimal PNG decoder
  Linux    — via the vendored minimal PNG decoder
  Web      — via the vendored minimal PNG decoder (Emscripten/wasm)

Earlier versions of this fork only implemented PNG decoding on Windows;
that limitation has been removed.
