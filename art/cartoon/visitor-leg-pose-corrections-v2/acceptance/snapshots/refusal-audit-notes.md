# Prior image-generation refusals

At baseline `4ecd33ee02455754a14957719ff0ee2b80843ff0`, **SSUZY1.BMP 003 is the only previously refused frame without a generated drawing**. No additional unresolved refusal was found in the retained prior art records.

| Frames | Status at baseline |
| --- | --- |
| SSUZY1 000, 002 | Recovered with successful drawings. |
| SSUZY1 001 | New attempt failed; the older successful drawing is explicitly retained. |
| SSUZY1 003 | Original attempt and two later attempts returned no image. The prior gallery shows its original only. |
| SSUZY1 009 | Later v1 failed; the targeted v2 edit succeeded. |
| SBREAKUP 015, 016 | One parallel attempt reported a block without identifying the failed member; neither result returned. Both separate v2 attempts succeeded, and the later fix pass also produced both. |

SSUZY1 004–010 were initially deferred without generation calls. That deferral is not seven refusals. Frame 009 had a separate later failure and recovery. SSUZY1 011 is a successful retained bottle drawing with no recorded refusal.

The audit searched 6,022 committed JSON, Markdown, text, log and YAML files under `art/cartoon`, including 4,423 JSON files. Baseline blobs were used where checked-out bytes differed. Failure records, historical summaries and the prior gallery's selected outputs were read together; pinned output and record hashes were checked. Technical exporter fit refusals, deliberate negative controls and native/build failures do not count as image-generation refusals.

[The pinned report](prior-refusal-audit.json) records the source paths, hashes and per-frame reasons. This audit deliberately excludes `visitor-leg-pose-corrections-v2`, including its new 003 attempt. It covers retained repository records, not unrecorded tool history; no rejected image was available to inspect.
