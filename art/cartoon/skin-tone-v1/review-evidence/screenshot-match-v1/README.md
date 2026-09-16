# Screenshot-to-source match

Image 1 is mirrored JOHNWALK024 in the Front waypoint clip, native display007 at360ms. Image 2 is mirrored JOHNWALK029 in that clip, display005 at240ms or display006 at320ms. Those two camera crops are identical, although their full1280x960 captures differ outside the camera.

The identification uses the whole native scene and the full sprite-canvas rectangle, including silhouette, face, arms and foot placement. It does not infer frame identity from skin-color statistics. Both matches exceed99.6% exact RGB pixels in the scene and in the sprite-canvas rectangle. The remaining differences are small screenshot/display-rounding differences, so this is not a byte-identity claim. The next distinct pose has a mean RGB error greater than5/255; each selected scene is below0.03/255.

`result.json` binds the existing user screenshots, native capture PNGs, reports, camera record and executed matching script. `execution.json`, `stdout.txt` and `stderr.txt` retain the actual run result. Screenshot bytes stay in `art/cartoon/walk-pilot/connecting-poses-v1/review-evidence/skin-color-audit-v1/`; they are referenced by repository-relative paths and SHA256 rather than duplicated here.

The lighter source is `art/cartoon/walk-pilot/front-refresh-v1/029-heel-fit-v2.png`. Its exact approved runtime is frozen in `art/cartoon/skin-tone-v1/inputs/029.png`. `../../human-palette-reference-v1.json` binds the exact user answer and both source and runtime identities. The pack row's `source_sha256` is not the generated reference image's hash; the generated artwork's hash comes from its export recipe and is recorded separately.

To repeat the comparison, retain or reconstruct the connecting native candidate-v2 capture and review-v1 records using `art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1/README.md`. Then run the following from the repository root with Pillow and NumPy available:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/skin-tone-v1/review-evidence/screenshot-match-v1/match_screenshots.py --output build/skin-tone/screenshot-match-replay.json
```

Choose a new output path. The script refuses an existing result and never changes artwork, screenshot bytes, capture data, or the historical approval records. The command used for the preserved run is in `execution.json`; its output points to this directory because that was the first creation of `result.json`.
