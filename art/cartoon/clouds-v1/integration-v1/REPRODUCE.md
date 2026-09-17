# Cloud integration reproduction

Production is the exact reviewed additive archive `a87a1f52b85277d88129347654a508edf9ca1f82920a31e20b5b41216242f63d`: 2,614 members and 63 Cartoon PNGs. Its 2,612 preexisting member payloads are unchanged. The maintained packer also reproduced all 2,614 payloads. Its ZIP envelope differs because it rebuilds the entire Cartoon prefix in sorted order, while the reviewed exporter appends the two cloud members to the prior archive order.

`source_sha256` in the active ledger and runtime recipe remains the existing HD proxy identity. Generated raw identities, fixed authoring transforms and request ancestry are separate bindings. The aggregate approval inherits all 61 prior asset rows and approves only BACKGRND 016 and 017. The approval records the exact question and answer, offered viewer cases and their limits. It does not claim that the user watched each selector or that the night backdrop was restyled.

Recover the pinned baseline into ignored scratch from the repository root. This deliberately creates the exact baseline path expected by the preserved promotion-control harness, and creates missing parents first:

```powershell
& $env:TOOLBOX_PYTHON -B -c "from pathlib import Path; import subprocess,hashlib; p=Path('build/clouds-v1/integration-v2/baseline.zip'); raw=subprocess.check_output(['git','show','de1e489e5c2fe3b22d03e8650bfc26cc1d8a12cc:assets/scrantic_data.zip']); assert hashlib.sha256(raw).hexdigest()=='a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66'; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(raw)"
```

Reproduce both PNGs and the exact reviewed archive without replacing the live production ZIP. Use a fresh output directory, or add `--check` to verify an existing output:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/clouds-v1/export.py --baseline build/clouds-v1/integration-v2/baseline.zip --output build/clouds-v1/source-replay-v1/export --candidate build/clouds-v1/source-replay-v1/candidate.zip
```

This replay was executed after promotion and reproduced the promoted ZIP byte-for-byte. The source export retains its historical `accepted:false` status; approval lives in the new production acceptance. Its prompt-reference resolver uses the validated batch-relative suffix under the current checkout, so the preserved request JSON may retain its original absolute reference paths.

The maintained read-only generated-data checks are:

```powershell
& $env:TOOLBOX_PYTHON -B tools/art_review_metadata.py --check
& $env:TOOLBOX_PYTHON -B tools/art_production_catalog.py --check
& $env:TOOLBOX_PYTHON -B art/cartoon/character-inventory-v1/build_inventory.py --check
```

`prepare.py` and `verify_promotion.py` are integration-time writers. Do not replay them against canonical frozen evidence. To re-exercise the recorded transaction controls, use a disposable checkout of this integration and run the recovery and exporter commands above. The harness also expects `build/clouds-v1/candidate.zip`; populate that exact scratch path from the verified replay before running it:

```powershell
& $env:TOOLBOX_PYTHON -B -c "from pathlib import Path; import hashlib; raw=Path('build/clouds-v1/source-replay-v1/candidate.zip').read_bytes(); assert hashlib.sha256(raw).hexdigest()=='a87a1f52b85277d88129347654a508edf9ca1f82920a31e20b5b41216242f63d'; p=Path('build/clouds-v1/candidate.zip'); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(raw)"
& $env:TOOLBOX_PYTHON -B art/cartoon/clouds-v1/integration-v1/verify_promotion.py
```

The controller itself promotes only into fresh disposable roots; it writes its new control report beside its copied helper in the disposable checkout. The recorded cases cover a normal promotion, a corrupt candidate refusal, a partial promotion-record write failure with both production files rolled back, and a restored positive.

The authoring runs reuse the unchanged recorder at `art/cartoon/low-tide-v1/integration-v1/authoring-v1/run.py`. The current cloud package/approval identities are also bound by this integration's final evidence. Smoke preceded generation and regression. All generated outputs, command logs, skips and replay results are explicitly indexed in the final evidence; ignored scratch archives and repeated PNGs are hash-bound rather than copied again.
