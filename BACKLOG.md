# Backlog - johnny-castaway-rebornHD

The [cleanup verification](docs/legacy-cleanup-verification.md) records completed
checks. The [post-merge audit](docs/legacy-cleanup-audit.md) records review coverage
and evidence limits; the [plan](docs/legacy-cleanup-plan.md) records scope and
decisions. Historical detail remains in Git and the linked art records.

## Open work

| Item | Evidence and next useful action |
| --- | --- |
| Expand Cartoon by complete motion families | The accepted pilot contains six walking poses and 15 island assets. Other directions, low-tide foam, other ocean/cloud variants, holiday/raft scenery and most story animations use HD/original fallback. Keep "Cartoon (preview)" until coverage is complete. Follow the recorded registration, direction and limb-order lessons before generating more art. |
| Establish unfinished TTM command behavior | These are reachable commands, not dead code. The [command review](docs/legacy-command-review.md) records exact opcodes and static occurrences. DRAW_BACKGROUND appears 190 times across 36 resources; SAVE_IMAGE1 appears 60 times across 40. Compare concrete original-engine scenes before changing pixels or ownership. GJGULIVR, MJSAND and WOULDBE are useful starting points. |
| Resolve original sample-ID mapping before sound substitution | The archive has no sound11.wav or sound13.wav. Static disassembly finds one PLAY_SAMPLE 11 in GJCATCH2.TTM and no PLAY_SAMPLE 13 in the 41 shipped TTM files. All 23 embedded original RIFF/WAVE payloads match unique bundled WAV prefixes, so two absent filenames do not establish two lost sounds. Historical extractor numbering is wrong at several offsets; identify the original PLAY_SAMPLE-to-resource mapping before changing cue 11. See docs/knowledge-base/original-reference.md and original-ne-audio.json. |
| Broader malformed LZW validation | The maintenance assessment reproduced accepted empty input, an incomplete first 9-bit code, a nonliteral first code and undefined code 300 after a literal. See docs/lzw-assessment.md for exact inputs and valid controls. Add EOF/code/dictionary/reset validation with varied-width original-corpus controls while preserving the legitimate full-buffer return. |
| Complete resource unload before live restart or pack switching | Parsed resource arrays remain process-owned. Slots borrow decompressed data and resource names refer to map entries. A full unload API needs ownership rules across those aliases. The application starts once per process; no recurring parser leak is claimed. Scene/overlay cleanup is covered separately. |
| Linux desktop fullscreen and physical audio | Real X11 resized-client captures test centering, enlargement, shrinking, bars and native-size recovery. Xvfb without a window manager does not validate desktop fullscreen negotiation. Audio error tests use real pthreads and deterministic ALSA responses, not a physical device. Exercise those paths on desktop Linux. |
| macOS presentation regression automation | Earlier manual Sequoia testing verified orientation, channels, sound, close, resize and fullscreen. New Cocoa event/allocation probes do not replace complete rendered-scene screenshots or physical audio validation. Add native window capture when presentation changes next. |
| Broader audio formats | Web refuses non-mono/non-U8 requests before changing playback state. All 23 shipped WAVs are mono, 11025 Hz, unsigned 8-bit. Stereo needs buffer layout, callback length, channel output and scheduling changes together. The common loader also warns about mixed rates/channels without resampling. |
| Deterministic multi-scene wave phase | File-static wave counters persist and initialization advances them. A seed reproduces a fresh-process run, not arbitrary scene entry after other scenes. Preserve current timing; design a reviewed reset option if deterministic scene seeking is added. |
| Empty story selection fallback | A NULL final-scene selection would re-enter storyPlay without a tick delay. The shipped table supplies candidates, so this remains an unreachable bad-data case. Address it when scene tables become editable. |
| Measure flip caching first | grDrawSpriteFlip blits one column at a time. A scratch flip adds copies and is not an established saving. A reusable sprite cache needs matching slot cleanup and fresh-process interleaved measurements against a variant without the cache. |
| Measure damage tracking first | Full-frame composition and presentation remain. Earlier Web optimization used alternating fresh browsers and exact pixel comparisons; this cleanup makes no new performance claim. Profile representative scales/scenes before adding renderer complexity. |
| Keep later style source storage deliberate | Preserve selected raw art, used ancestors, prompts, acceptance and export recipes. Avoid duplicating the full original archive or every diagnostic capture in each style. Noir/anime also need explicit catalog and authoring-tool registration. |
| Add verified original-resource sound extraction | Checked explicit-path helpers now reject bad input and preserve existing outputs. The legacy sound layout still reads RIFF's first two bytes as a length and applies historical output numbering. The supplied executable proves this defect; the helper refuses its out-of-bounds span before creating output. Add a separately named mode using verified resource identifiers and bounded lengths, with explicit handling of RIFF content versus trailing allocation bytes. See docs/knowledge-base/original-extractor-reference.md. |
| Calibrate complete scenes against the supplied original | All 10 ADS and all 41 TTM names are present. Decoded ADS match; 40 TTM match exactly. SJLEAVES.TTM differs by a removed SET_DELAY 0 in tag 3. The original-only SA_DEMO.BMP and five TTM files without story ADS references need classification, not automatic promotion to missing scenes. Use the knowledge-base event crosswalk and original windowed reference to observe complete branches, timing, transitions and outcomes. |
| Reuse resource inspection for the next art pack | The xesf viewer offers useful resource-list, sprite-sheet, palette and script-pane patterns, but its playback has unfinished commands and its current-line callback is not called. Prefer adding proven inspection conveniences to our existing scene/art tools: show original frame IDs, offsets, direction and complete motion-family contact sheets beside variants. Keep original DOSBox observation as the behavioral reference. See docs/knowledge-base/external-tools.md. |
| Review remaining compiler diagnostics when touching those paths | Pinned Emscripten 6.0.9 still reports existing unused parameters/non-Windows parent-window state and C11 pedantic diagnostics from Emscripten macros; vendored miniz reports its large-file I/O choice. Native Windows phase-one build is warning-free. Keep SDK/vendor diagnostics distinct from actionable project warnings and do not silence them globally. |

## Maintenance completion results

| Area | Change and evidence |
| --- | --- |
| CLI frame range | Parsing accepts 1 through UINT32_MAX and rejects conversion overflow. Comparing before increment stops the maximum without changing ordinary capture timing. Three rebuilt negative controls and eight historical scene captures verify the boundaries and unchanged pixels. |
| Web delayed audio | The existing short wait loop services the audio queue. Advancing-clock probes and actual GJHOT browser playback verify all 9,672 sound-24 PCM bytes in ten contiguous buffers; removing the pump creates the expected scheduling failure. Physical speaker output remains separate. |
| ALSA setup and delivery | Every setup result is checked, the actual rate is returned, partial frame tails survive retries/recovery, and close stops pending retries before joining/freeing. Five backend smoke and 32 regression cases passed; 17 rebuilt delivery mutations fired. An already-blocking device call and physical playback are not measured by those fixtures. |
| Web diagnostics | Preserve 64 startup and 448 recent messages, limit retained message length, bound stderr history and keep fatal status sticky. A Chromium heap test also catches V8 substring backing-store retention; clipped messages now have detached storage. |
| Shared Web builder | The PowerShell entrypoint delegates to the pinned shared builder, assembles a servable directory, preserves caller state and supports an explicit local SDK. Both PowerShell versions performed real container builds. Local SDK activation uses child-process fixtures; an actual local SDK compiler was unavailable. |
| Legacy helper I/O | Both extractors use explicit input/output and layout arguments, validate source spans, check I/O, preserve pre-existing files and roll back only their own outputs. Original walking data matches 489 records. Correcting the historically wrong sound layout remains explicit follow-up above. |

## Legacy cleanup results

The verification record is authoritative for which phase checks have completed.

| Area | Change and evidence |
| --- | --- |
| Native asset deployment | Executable targets use the runtime-data prerequisite for archive-only changes and deleted deployed copies. Generator fixtures and an isolated actual application test exercise dependency wiring and stale-gate refusal. |
| Unix failure propagation | A failed build stops smoke/regression even when executables exist. Executed control-flow mutations check refusal and ordering. |
| Web toolchain | CI/release share official Emscripten 6.0.9 pinned by image digest. Only acquisition retries; compilation failures stop. Actual SDK/preload bytes are checked and browser tests run on the host. The setup action's codeload and deprecated Node-runtime dependency are removed. |
| macOS package architecture | An explicit Intel runner and real lipo check preserve x86_64 packaging. A compiled ARM64 control proves mismatch refusal. No release is cut in this cleanup. |
| RLE/LZW short output | Both decoders refuse an incomplete result before returning partially written memory. Complete controls, malformed RESOURCE fixtures and rebuilt mutations accompany the 2,452-file golden comparison. |
| Layer/slot ownership | Inactive benchmark layers, standalone saved overlays, zero-sprite BMP names, graphics surfaces and previous ADS state are released. Borrowed background/data aliases remain borrowed. Real engine allocation probes exercise repeat teardown and reinitialization. |
| Linux audio ownership | Creation is tracked separately from worker activity. Close joins a created worker before freeing its resources; running/error state uses atomics. Real-pthread controls cover error exit and reopen. |
| Platform allocation failure | All four backends refuse failed constructors and unwind acquired state. Borrowed wrappers leave caller pixels alone; WIC frees pixels if wrapping fails. Required engine callers report construction failure. |
| Events/presentation/audio contracts | Linux/macOS drain ignored events. macOS observes quit during dispatch. Linux scales into its actual client rectangle with centered nearest-neighbor aspect preservation. Web refuses unsupported audio contracts. |
| Unused code | Removed 35 write-only fields and unused version allocations, the ignored display background parameter, four unreachable post-lookup NULL branches and the empty intro reset. Every original header byte still goes through EOF-checking readers. Unused platform helpers/globals are removed. |
| Post-merge drawing and name ownership | Replaced negative signed shifts in both circle loops without changing tested pixels. Odd-width packed screens now fail with a resource-naming diagnostic in rendering and dumping. Repeated zero-image BMP loads release the previous name, including when the request aliases the cached name. Sanitized controls and seven rebuilt negative controls verify the fixes. |
| Post-merge unused platform state | Removed the uncalled color-key API and its unused fields/branches across all four backends, the write-only macOS fullscreen field and an unused scene counter. Active fullscreen state and PNG alpha handling remain intact. |
| Architecture records | The guide now describes verified startup, rendering and ownership. The command review corrects old opcode numbers and distinguishes working operations from reachable no-ops. |

## Accepted artwork and earlier fixes

The user accepted the directional walking preview with "looks good" and the
complete island motion with "approved, it looks great". These approvals remain
authoritative; cleanup changes no production artwork bytes.

- [Walking acceptance](art/cartoon/walk-pilot/directional-cycle-v1/acceptance.json)
- [Island acceptance](art/cartoon/island-pilot-v1/acceptance.json)
- [Motion review](art/cartoon/motion-review.md)
- [Reusable image lessons](docs/art-style-learnings.md)

The art delivery preserved all 2,550 original archive members. Alternate-state
API checks covered tides, ocean/night screens, clouds, raft stages, holidays and
offsets; integration coverage does not mean those states are fully styled.

Earlier fixes remain closed: wave alpha restoration; selected Cartoon palm
source-atop; PNG premultiplication; script/tag/pixel bounds; atomic Windows
temporary-file creation; sound0 loading and failed-audio WAV cleanup; island
pointer/cloud sprite cleanup; conditional fade allocation; screensaver version
resources, child preview, settings and focus; macOS close/fullscreen/aspect.

The Windows screensaver remains primary-monitor-only by the user's choice.
Do not reopen that as a bug. Web tab closure is managed by the browser; the lack
of an engine EVENT_QUIT for closing a tab is not a resident-process wedge.

## Claims that did not hold

| Rejected claim | Evidence |
| --- | --- |
| Existing HD art had bright alpha halos | The decoder mismatch existed, but all 2,402 historical HD PNGs had only alpha 0 or 255. It could not cause partial-alpha halos on those pixels. Premultiplication was corrected before soft-alpha art. |
| Linux/macOS need an outer audio callback lock | soundCallback takes the mutex itself. Another non-recursive pthread lock would deadlock. Windows critical sections have different recursive behavior. |
| New Year spans January or needs AND | The comparisons select Dec 29-31 and Jan 1. Replacing OR with AND selects no date. Evaluate date windows over actual dates. |
| macOS renders upside down | Manual Sequoia review showed correct orientation and colors. It found real close/fullscreen/presentation bugs instead; those were fixed. |
| Local CMake cannot use Visual Studio 2026 | CMake 4.3.1 offers and defaults to that generator here. CI must also cover its own Visual Studio version. |
| grSaveZone/grSaveImage1 are dead code | TTM dispatch calls them. Correct opcodes are 0xA054 and 0x4214; RESTORE_ZONE is 0xA064. They need behavior investigation. |
| Shipped TTM data reached the old odd-byte tag over-read | The old defect existed, but all shipped TTM data had even, exact decoded size. Malformed fixtures establish the guard, not corrupt original scenes. |

## Testing lessons

Use isolated settings and fresh processes for deterministic scenes. Saved story
day changes eligible scenes. Day/night branches consume RNG differently; one
seed with no clouds is not proof of a rendering defect.

Negative tests need the intended diagnostic or executed assertion, not merely
nonzero exit. A timeout is a harness failure. Native mutants require artifact
and execution witnesses; a source-text match cannot prove a guard runs.
Normalization controls must vary changed and unchanged inputs, including Windows
short-name and canonical paths. Retain child logs when a CI fixture fails.

Fatal-error reporting must recognize redirected stderr. No console window does
not justify a dialog: CI child processes lack one too. Windows PowerShell 5.1
remains part of the contract even when the outer gate uses PowerShell 7.

Browser freeze checks need bounded Playwright waits; page.evaluate can wait
indefinitely on a blocked page. Do not cache Wasm heap views across memory growth.

Inspect native window pixels for presentation. A green headless dump proves
decoding, not orientation, fullscreen or audible sound. The original archive and
image acceptance records remain the reference for later style work.
