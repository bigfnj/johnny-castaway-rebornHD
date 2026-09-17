# Low-tide candidate capture preparation

Completed against provisional static candidate V2, SHA256 `f46e5cac5508b00cc7a675be4eaf843029cebfeabe80c849c8fa5f311813b92b`. Both native smokes and fresh-process repeats passed. Production is unchanged; artwork acceptance remains separate.

The launcher requires `--candidate-sha256 <selected SHA256>` and accepts `--candidate <path>` if the final filename differs from `build/low-tide-v1/static-candidate-v1.zip`. Run with the existing toolbox Python. It uses the already installed, pinned Docker image, no network, read-only source mount, an isolated Xvfb and hidden host subprocesses. Output must be fresh and stays in this scratch folder.

The candidate must preserve all 2,598 production payloads exactly and add only Cartoon `BACKGRND.BMP/001.png` (768 by 138) and `002.png` (128 by 60). The exact baseline executable is copied and hash-verified; this does not claim another source build. The frozen baseline source/helper identities must still match.

Two actual low-tide cases, no holiday and clovers, each run 24 native wait calls. Both smokes finish before fresh-process repeats. The comparison requires unchanged timing, Johnny, all draw records and all pixels outside the exclusive HD rectangles `[498,606,1266,744]` and `[300,656,428,716]`. Three small damaged-input controls exercise the old-wave payload, new canvas and outside-pixel checks. No source or image is mutated by these controls.

The twelve old low-wave assets remain untouched. Their opaque pixels can visibly stamp old sand over the new beach. A technical PASS does not assert that these mixed-art waves are visually acceptable.

## Before-wave option

The frozen driver's first displayed frame occurs after `adsInitIsland()`. `islandInit()` already draws the low beach and rock, saves the wave base, and runs four initial wave draws. There is no existing switch for a pre-wave display.

The separately authorized `prewave.py` scratch observer saves the real `grBackgroundSfc` immediately after the native `BACKGRND002` draw and before the first `islandAnimate()` call. This is an initialization background-surface capture, without clouds, holiday or Johnny, not a normal displayed full scene. No engine change or synthetic assembly is used. Both baseline and candidate runs passed; the three subsequent displayed frames in each run equal the original observer's matching prefix exactly. The modified observer source and fresh executable/build identities are preserved in `prewave-v1`.
