# Legacy cleanup plan

Baseline: main `55b864b8ef54a5c700138e16b74e8d5d62a5d305`.
The user authorized end-to-end execution after read-only exploration, with smoke
before regression at each major phase, parallel work where useful, delivery to
main and a final independent audit. Pause for a fundamental behavior decision or
visual review that needs the user.

## Ordered delivery

| Phase | Implementation | Required evidence |
| --- | --- | --- |
| Baseline | Isolated integration and worker worktrees; record existing behavior and asset identity. | Existing Windows gate, source archive hash and controlled HD/Cartoon captures. |
| Build reliability | Preserve Unix build failures; refresh native data for explicit targets; verify macOS package architecture; use pinned Emscripten Docker compilation. | Failure propagation, archive-only changes, custom output paths, real compiler/package identities, native/Web smoke then regression. |
| Decoder validation | Reject underproduced RLE/LZW output while retaining legitimate LZW full-output returns. | Complete/short controls, rebuilt guard mutations and full decoded corpus parity. |
| Resource ownership | Release inactive owned layers, saved zones and old slot state; pair initialization and release without freeing borrowed aliases. | Compiled allocation tracking, repeat/release controls, rebuilt mutations and unchanged HD/Cartoon captures. |
| Platform cleanup | Handle constructor allocation failures, Linux audio worker ownership, event draining, Web mono contract and Linux aspect-preserving presentation. | Fault injection into actual code, pthread/error controls, event ordering, Web audio assertions and X11 window captures. |
| Code and records | Remove proven unused fields/helpers/arguments, investigate reachable no-op commands and correct stale records. | Caller/ownership review, preserved parsing behavior, smoke then golden/pixel regression. |
| Delivery | Commit and push the tested branch, merge to main, rebuild and audit the merged code. | Four-platform CI; final review of regressions, lifetime, unused code, non-operable calls and measured optimization opportunities. |

Each phase integrates in this order even when work is developed in parallel.
Source-mutating checks use isolated worktrees/builds. Windows graphical tests run
one at a time. A new failure guard must be deliberately defeated: require one
named test failure, a rebuilt artifact witness where applicable, restoration and
a clean rerun. A skipped capability must be stated in the verification record.

## Decisions and boundaries

| Decision | Reason |
| --- | --- |
| Preserve original coordinates, timing, artwork and archive bytes | Cleanup must retain the approved scenes and their fallback behavior. |
| CMake 3.19 minimum | CMP0112 permits a data-copy prerequisite using target output directories without introducing a dependency cycle. |
| Explicit Intel macOS runner/package verification | Retains the advertised x86_64 package contract. |
| Emscripten 6.0.9, compilation-only container | Retains compiler behavior while removing the setup action's codeload dependency; browser tests stay on the Ubuntu host. |
| Nullable platform constructors with checked callers | Allocation failures should unwind ownership and report through existing error handling. |
| Linux nearest-neighbor presentation | Keeps source colors and deterministic scaling; logical rendering remains unchanged. |
| Enforce Web's implemented mono unsigned-8-bit audio contract | Unsupported formats must be refused before changing playback state; stereo conversion is separate behavior work. |
| Retain process-owned parsed resource arrays | Their borrowed names/data require a separate complete-unload design; scene-owned allocations are covered here. |
| Investigate reachable no-op opcodes before changing semantics | A called command is not dead code. Document actual opcodes, callers and evidence gaps. |
| Keep performance rewrites separate until measured | No saving is claimed from unmeasured caching or compositing proposals. |

Preserve historical image records. Update BACKLOG.md with completed fixes,
remaining findings, evidence limits and the next useful action. The final report
must state actual validation and include a concise decision/recommendation table.
