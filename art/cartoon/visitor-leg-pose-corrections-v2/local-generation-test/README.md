# Local FLUX.2 editing tests

The authorized isolated environment is `D:/.ai-work/venvs/johnny-flux2-klein`. Its interpreter is `Scripts/python.exe`. No changes were made to the Wallpaper Engine or shared media environments.

The official model is cached outside the repository. Its exact snapshot, revision, file sizes and download verification are in [model-download.json](model-download.json). Installed versions and CUDA/import checks are in [environment.json](environment.json).

[Compare the five raw results](review.html). The [test summary](test-summary.json) separates technical image output from visual correctness. Two 006 prompt approaches kept the wrong knee position. The 009 trial removed the bottle and retained the accepted leg connection, but the approved built-in 009 gives a clearer pose progression. Two later 004 trials, using the rejected cartoon first and the original sprite first, both retained the rejected hip geometry. Neither local 004 result is selected.

The original reference PNGs are unchanged. Each run records its actual input, composited over white and scaled for the local RGB pipeline. No local result is a transparent production sprite.

For another authorized run, use the isolated Python interpreter to execute `run_edit.py` with `--request`, a new `--run-id`, the recorded `--model-path`, and `--run`. Without `--run`, it prepares and records inputs without loading the model. The process uses only the downloaded local snapshot, records timing and peak PyTorch allocation, and exits after one image. Existing run folders cannot be overwritten.

Example in PowerShell using the saved inputs:

```powershell
& 'D:/.ai-work/venvs/johnny-flux2-klein/Scripts/python.exe' -B 'D:/.ai-work/worktrees/johnny-cartoon-environment/art/cartoon/visitor-leg-pose-corrections-v2/local-generation-test/run_edit.py' --request 'D:/.ai-work/worktrees/johnny-cartoon-environment/art/cartoon/visitor-leg-pose-corrections-v2/local-generation-test/requests/006-direct.json' --run-id 006-another-trial --model-path 'D:/.ai-work/cache/hf-cache/hub/models--black-forest-labs--FLUX.2-klein-4B/snapshots/e7b7dc27f91deacad38e78976d1f2b499d76a294' --run
```

The original built-in attempts, including their failures, remain available in the separate historical prompt handoff. The successful new built-in prompts are linked from the main frame review.
