# Local Qwen image evaluation

This isolated evaluation uses a written instruction and two PNG reference images. The test redraws the original SMGIFT039 pixel sprite using the approved SMGIFT041 life preserver as its design reference. The approved SMGIFT039 drawing is shown only for comparison and is not passed to the model.

[Open the review](http://127.0.0.1:8941/local-qwen21-evaluation-2026-09-22/review.html).

The request and source hashes are in `request.json`. The latest execution result is in `record.json`; individual attempts, ComfyUI logs, submitted workflows, and raw outputs are retained under `runs/`. These evaluation files do not replace approved artwork.

Installed components:

- ComfyUI checkout: `D:/.ai-work/ops/comfyui-qwen21`
- Isolated Python environment: `D:/.ai-work/venvs/johnny-qwen21`
- Model files: `D:/.ai-work/models/Qwen-Image-2.1`
- Model revision and verified SHA-256 values: the model directory's `download-record.json`

The model and reference encoder use INT8 weights. The VAE supports RGBA. Both inputs retain their alpha channel through the workflow. The inference server is restricted to localhost port8191, with API nodes and custom nodes disabled. Its process uses offline model loading. The runner stops its own server process tree after success or failure.

Run from PowerShell, after agreeing when the shared GPU can be used. Use a new run ID each time:

```powershell
& $env:TOOLBOX_PYTHON 'D:\.ai-work\worktrees\johnny-cartoon-environment\art\cartoon\local-qwen21-evaluation-2026-09-22\run_trial.py' --run-id preserver-next
```

To check CPU startup, node availability, and model filenames without submitting an inference request:

```powershell
& $env:TOOLBOX_PYTHON 'D:\.ai-work\worktrees\johnny-cartoon-environment\art\cartoon\local-qwen21-evaluation-2026-09-22\run_trial.py' --run-id validate-next --validate-only
```

Rebuild the review after a run:

```powershell
& $env:TOOLBOX_PYTHON 'D:\.ai-work\worktrees\johnny-cartoon-environment\art\cartoon\local-qwen21-evaluation-2026-09-22\build_review.py'
```

Change the prompt and sampling settings in `request.json`. To test different reference files, replace the two `inputs/reference-01.png` and `inputs/reference-02.png` copies and update their file details and SHA-256 values in the request. Keep the original source art intact.

GPU measurements sample total device usage with nvidia-smi and include Windows and other applications. A single run is a compatibility and visual-quality test, not a comparative speed benchmark.

The first completed test is `runs/preserver-v2/`: 1952x544 RGBA output, 177.34 seconds from submission through collection and 191.92 seconds total process time. Sampled peak device memory was 23079 MiB; after shutdown it returned to 2506 MiB. Browser inspection confirmed working transparency. The output follows the scene and reference colors but retains stair-step contours and changes the hand. It is below the approved 039 drawing in quality. All source drawing hashes were verified unchanged.

Official sources: [Qwen model](https://huggingface.co/Qwen/Qwen-Image-2.1), [ComfyUI workflow](https://docs.comfy.org/tutorials/image/qwen/qwen-image-2-1), [quantized files](https://huggingface.co/Comfy-Org/Qwen-Image-2.1). The model's research/evaluation license is saved under the model directory's `provenance/` folder.
