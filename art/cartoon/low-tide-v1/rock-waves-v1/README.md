# White offshore ring for the low-tide rock

The island's nine approved high-tide wave drawings are reused separately in `../wave-reuse-v1`. This folder contains the different geometry needed around the low-tide rock: three open elliptical ripple phases,039-041. They were generated with built-in image_gen using the approved bright white center ripple as the style reference and original039-041 as geometry references. Exact prompts, ordered reference paths and all raw outputs are retained. No prior approved Cartoon rock-ring asset existed.

The raw images are1536x1024 RGBA. `export.py` registers all three with the same uniform0.157 scale and translation into208x58 canvases at native world258,680. It imports the established premultiplied filter and existing alpha visibility helper. The latter keeps offshore foam from painting over the already approved rock002; RGB is not recolored. This is the selected offshore interpretation, not a reconstruction of the original's blue-filled ring or incoming wash.

`exports-v1/export.json` binds prompts, raw inputs, references, helpers, transforms and output bytes. No alpha>=8 is cropped in any phase. Phase040 loses five filtered fringe pixels of maximum alpha3; the other phases have no filtered nonzero crop in the padded export audit. No alpha threshold or hand cleanup is applied. The raw sources have no alpha>=8 pixels whose maximum RGB channel is below100. Resampling introduces one such small edge pixel in exported039; the native composition has no broad dark-shadow layer. Appearance still requires human motion review.

First exports passed the maintained PNG canvas validator. A fresh process exported to `build/low-tide-v1/rock-repeat-v1`; all ten files, including reports and technical rock close-ups, reproduced exactly. Run with a fresh output directory:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/low-tide-v1/rock-waves-v1/export.py --output build/low-tide-ring-replay
```

The close-ups under `audit/` are technical composites on the captured pre-wave background, not native animation captures. The combined candidate and native motion review live in the parent folder. Static beach/rock approval does not approve these new ring phases.
