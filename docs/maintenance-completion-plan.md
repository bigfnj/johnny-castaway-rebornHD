# Maintenance completion plan

Baseline: main `c582c3e3088b1cb464a6aa19b3846af4e089e23e`.
Read-only exploration preceded implementation. The user authorized execution,
parallel worktrees, smoke before regression after each phase, delivery to main
and an independent audit after merging.

| Phase | Work and acceptance |
| --- | --- |
| Baseline | Reuse the completed main PowerShell 5.1 gate and four-platform CI, retain its binaries and the original archive hash, and preserve historical scene references. |
| CLI | Check conversion errors and the uint32 frame range. Compare the counter before incrementing so the largest supported limit terminates without changing the ordinary stopping point. Test parser boundaries, actual event shutdown and frozen scene pixels. |
| Audio | Pump Web audio during existing short waits. Check each ALSA setup result and complete partial writes before requesting another callback. Test exact sample order, advancing-clock scheduling, recovery, shutdown and reopen. |
| Diagnostics | Bound app-owned Web log count and message length while preserving startup context, recent output, stderr evidence and sticky fatal status. Exercise actual page behavior and deliberate retention failures. |
| Tools | Keep the Windows Web wrapper as a compatibility entrypoint to shared build/validation/page assembly, retaining explicit local SDK support. Check extractor I/O and expose paths while preserving legacy extraction layout and 489 walking records. |
| Delivery | Integrate in order, run full native/Unix/Web smoke and regression plus four-platform CI, merge and rebuild main, then audit production paths and update BACKLOG.md. |

Web and tooling development proceed in separate branches while CLI and Linux
audio changes are implemented in the integration worktree. Windows graphical
tests run serially. New guards require isolated negative controls with the
intended failure, rebuilt artifacts and execution witnesses where applicable.
PowerShell scripts that write files must execute under both 5.1 and 7.

## Decisions

| Decision | Reason |
| --- | --- |
| Preserve artwork, archive bytes, animation coordinates and ordinary capture timing | The accepted art and previous full-frame comparisons remain the reference. |
| Keep the Web queue and Asyncify design | Servicing the existing waits addresses the current call path without an audio architecture rewrite. Visual pause still allows the current sound to finish, matching native playback. |
| Keep the local SDK option with shared validation | Existing Windows callers may use EMSDK; the container remains the default for the Python/CI path. Remove workstation-specific discovery and avoid changing the caller's directory/environment. |
| Preserve extractor byte-selection semantics | At planning time the original executable was unavailable. The user subsequently supplied a working DOSBox installation: its walking data matches all 489 rows, while its sound resources expose a historical length and numbering defect. Keep the checked legacy mode explicit; a separately verified resource-ID extraction mode is recorded as follow-up. |
| Assess LZW independently | The prior short-output fix is not a complete decoder validation. Establish precise reproductions and compatibility requirements before any additional decoder change. |
| Preserve unfinished original commands | Their intended behavior requires original-engine evidence. Full resource unload, new audio formats and renderer optimization remain separate feature/design work. |

The ALSA setup and retry behavior follows the official
[PCM interface](https://www.alsa-project.org/alsa-doc/alsa-lib/group___p_c_m.html)
and [hardware-parameter reference](https://www.alsa-project.org/alsa-doc/alsa-lib/group___p_c_m___h_w___params.html).
Controlled device responses and browser scheduling traces do not establish
physical speaker output or desktop fullscreen behavior.

## Added reference research

During implementation the user requested a durable knowledge base, comparison
with the supplied original, and research of the public scene guide plus
`xesf/castaway` and `xesf/dgds-viewer`. These tasks run in parallel with code
verification. Record source revisions, resource/script comparisons and observed
behavior separately; no catalog count establishes full animation parity.
The original was successfully launched and then configured to remain windowed
at the user's request. Preserve this workstation preference in later testing.
