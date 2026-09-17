# Backlog - johnny-castaway-rebornHD

The [cleanup verification](docs/legacy-cleanup-verification.md) records completed
checks. The [post-merge audit](docs/legacy-cleanup-audit.md) records review coverage
and evidence limits; the [plan](docs/legacy-cleanup-plan.md) records scope and
decisions. Historical detail remains in Git and the linked art records.
The later [maintenance audit](docs/maintenance-post-merge-audit.md) and
[maintenance verification](docs/maintenance-verification.md) cover the second pass
and the original-first art metadata work.
The [standing-family audit](docs/cartoon-standing-post-merge-audit.md) covers
merged main`fecfdb3`, the 32-asset delivery and its fresh deployment checks.
The [profile-walk audit](docs/cartoon-profile-walk-post-merge-audit.md) covers
merged main `c903fb5`, the 40-asset delivery and fresh core/platform/authoring review.
The [connecting-pose audit](docs/cartoon-connecting-poses-post-merge-audit.md)
covers merged main `9ea8293`, the 43-asset delivery and the restoration of three
omitted review records. It found no new engine or platform defect.
The [character inventory audit](docs/cartoon-character-inventory-post-merge-audit.md)
verifies the complete reference delivery and records the standalone-art recommendation.
The [seasonal and shoreline audit](docs/cartoon-seasonal-post-merge-audit.md)
covers merged main `9b0a4ed`, the 47-asset delivery and fresh core, platform and
authoring review. No new code blocker was found; the open items below remain.

## Open work

| Item | Evidence and next useful action |
| --- | --- |
| Style the remaining sky and ocean states | The [low-tide delivery](docs/cartoon-low-tide-verification.md) completes BACKGRND.BMP001/002 and030-041 as one approved scene group. CLOUDS.BMP000-003, NIGHT.SCR and alternate ocean screens beyond OCEAN02 still use fallback. Review clouds next, then night/ocean states as coherent scenes, retaining both accepted tide compositions. Keep Cartoon labeled as a partial preview. |
| Resume from the complete character inventory | The [extracted worklist](art/cartoon/character-inventory-v1/README.md) covers all2,402 supplied-original image slots, including2,401 app slots and original-only SA_DEMO. It retains1,002 outstanding confirmed Johnny slots across76 resources,28 accepted character slots and84 uncertain app slots. These are drawings, body parts and composites, not distinct scenes. Resolve ambiguous tiny actors/fragments in context before removing them from the queue. The [playbook](docs/cartoon-character-playbook.md) preserves the lessons for the next pack. |
| Continue independent props after the environment group | The [seasonal delivery](docs/cartoon-seasonal-verification.md) integrates the approved island, clean offshore waves and all four HOLIDAY.BMP decorations, including the inset banner. Keep the incoming-wash alternative as an unselected reference. Follow the remaining environment states with independent props, then vehicle directions. Some vehicle/story images contain Johnny or uncertain occupants; keep those with their character/scene groups. This ordering reduces anatomy review dependencies; no production speedup was measured. |
| Expand Cartoon by complete motion families | Production contains61 assets:28 Johnny poses,29 island/environment assets and four seasonal decorations. The [production catalog](docs/knowledge-base/cartoon-production-catalog.md) tracks all2,401 slots and supplied-original references. Front024-029, rear011/019-023 and profile001-008 are delivered, as are standing000/015/016/017/018 and ordinary connecting009/010/012. The [connecting delivery](docs/cartoon-connecting-poses-verification.md) includes the accepted lighter skin palette and corrected018 foot contact. Other scenery states, rafts and most story animations still use fallback. Keep "Cartoon (preview)" until coverage is complete; PNG coverage does not review palette primitives, fades or every story interaction. |
| Review connecting poses in their story contexts | Ordinary native walking review covers009/010/012, including intermediate waypoints. Separately attributed static TTM sites are009=5,010=8,012=2; these counts do not establish executed story coverage. Exercise the actual story placements before claiming every use reviewed. Preserve the accepted geometry, skin palette and exact native walking timing separately. |
| Generalize the copied-evidence Git index check | The fresh PR15 main checkout lacked three browser-execution records inside an ignored nested `build/` directory, although the feature worktree contained their correctly hashed bytes. The final audit restored and explicitly staged all three unchanged records. PR17 now supplies a [delivery-specific checker](art/cartoon/shoreline-repair-v1/integration-v1/index-final/README.md), with 627 bindings verified on fresh main and real missing-file and wrong-byte controls. Generalize its explicit binder selection into maintained evidence tooling for later packs. Keep intentional external original resources and scratch captures distinct from copied durable evidence. The original omission affected evidence storage; runtime art and all 2,594 members of that earlier package were correct. |
| Compare first-pose and direction-dependent waiting against the original | Existing `ads.c:1110-1114` initializes timer and delay to6, then replaces only delay with the first `walkAnimate` result. Same-heading and positive-adjacent cases return the terminal80 immediately, retaining a six-tick timer; negative-adjacent cases return6 then80, which the later assignment honors. Current native direction-ring captures total1080ms increasing versus13880ms decreasing; these are sums of requested waits, not stopwatch measurements. Source/table reachability includes eligible STAND#15-to#1, #1-to#2 and repeated#1, but no random-story run was captured. Before changing the scheduler, compare same-heading and both adjacent directions against the windowed original, including pose onset, destination hold and next-scene onset. Preserve current art approvals separately. Compact native ring evidence is under `art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/review-evidence/native-v1/`. |
| Review shared standing poses in their story contexts | The [wait/turn trace](art/cartoon/walk-pilot/front-arrival-v1/trace/trace.json) identifies31 static017 draws across eight TTM resources, including17 in SJLEAVES.000 has8 sites across5 resources;015 has1 in GJVIS5;018 has1 in SJLEAVES;016 has no attributed static TTM sites in this trace. Original and port counts agree, but linear script attribution does not execute every branch. Native arrival and direction-ring approvals do not review these story placements or contacts. Exercise them before claiming complete scene coverage, preserving the original-versus-port SJLEAVES delay distinction. |
| Author and scene-review the seven remaining core walking drawings | [Static mapping](art/cartoon/character-inventory-v1/scene-map/remaining-walk.json) places014/030-032 in native C-to-D travel and MJFISHC actions. Frames033-035 belong to MJDIVE tag2, Walk out of water, with010 and017 neighbors; they are not a new compiled walking loop. Capture actual placement, clipping and timing before authoring each group. Sprite013 is a tiny placeholder. Static mapping is complete; Cartoon generation and native scene review remain pending. |
| Complete foreground raw-input cleanup on Windows | `platform/platform_windows.c:175` handles `WM_INPUT` and returns without `DefWindowProc`, including error exits. [Microsoft's contract](https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-input) requires that cleanup call for foreground `RIM_INPUT`. Add one common cleanup path and controlled success, failure and ignored-input tests. This is an existing API-contract omission; no OS-resource leak was measured. |
| Initialize common audio state before starting the worker | `src/engine/sound.c:165` resets `currentRemaining` without locking after `platformOpenAudio` has started the Linux worker, whose callback uses that state under a mutex. Initialize callback state before opening audio and test actual `sound.c` startup with the worker; backend-only tests use their own callbacks. Also avoid the initial silence path's `memcpy(stream, NULL, 0)` at line 79. This is a source-established startup synchronization gap; no audible corruption or race-detector result is claimed. |
| Validate saved story day before advancing the date | Unmodified `story.c:102` increments the configured day before clamping it at line 106. Actual `config.c` input `currentDay=2147483647` with a stale date produced one UBSan signed-overflow diagnostic; ordinary progression, day-11 wrap and the same invalid day with a current date passed. [Probe evidence](docs/calm-focus-config-boundary.json) records the exact isolated test. Normalize before incrementing and replace unchecked `atoi` at `config.c:139` with bounded parsing. This is malformed-config evidence, not a normal story progression failure. |
| Classify original versus bundled pixel differences | Independent decoder executions agree for all 79 images in JOHNWALK, BACKGRND and OCEAN02, while original versus bundled indices differ in all 79. The [comparison](docs/knowledge-base/original-image-comparison.md) records 2,428 changed indices and unknown conversion history. Broader native-only results are separate. Calibrate original palette/compositing and determine the cause before replacing bundled resources or treating HD proxies as canonical. |
| Establish unfinished TTM command behavior | These are reachable commands, not dead code. The [command review](docs/legacy-command-review.md) records exact opcodes and static occurrences. DRAW_BACKGROUND appears 190 times across 36 resources; SAVE_IMAGE1 appears 60 times across 40. Compare concrete original-engine scenes before changing pixels or ownership. GJGULIVR, MJSAND and WOULDBE are useful starting points. |
| Establish original clipping behavior for drawing primitives | Sprites respect the active draw zone, while rectangle fill and pixel-based line/circle paths only enforce surface or screen bounds. There are 111 DRAW_RECT commands in six TTM resources and 52 SET_CLIP_ZONE commands overall; SBREAKUP tag 34 combines 12 rectangles and four clip changes. Trace whether a primitive crosses its active zone and compare the original before changing semantics. Static reachability does not establish a visible scene defect. |
| Resolve original sample-ID mapping before sound substitution | The archive has no sound11.wav or sound13.wav. Static disassembly finds one PLAY_SAMPLE 11 in GJCATCH2.TTM and no PLAY_SAMPLE 13 in the 41 shipped TTM files. All 23 embedded original RIFF/WAVE payloads match unique bundled WAV prefixes, so two absent filenames do not establish two lost sounds. Historical extractor numbering is wrong at several offsets; identify the original PLAY_SAMPLE-to-resource mapping before changing cue 11. See docs/knowledge-base/original-reference.md and original-ne-audio.json. |
| Broader malformed LZW validation | The maintenance assessment reproduced accepted empty input, an incomplete first 9-bit code, a nonliteral first code and undefined code 300 after a literal. See docs/lzw-assessment.md for exact inputs and valid controls. Add EOF/code/dictionary/reset validation with varied-width original-corpus controls while preserving the legitimate full-buffer return. |
| Bound overlong TTM strings without executing their tail | The reader copies at most 255 characters, then consumes the next byte as if it were the terminator. A compiled probe using unmodified main TTM code showed a 256-character LOAD_PALETTE string followed by embedded SET_DELAY bytes changing delay/timer to 123; short and 255-character controls retained six. Reject an overlong string or consume it fully within the resource bound. This was malformed-input evidence, not a shipped-scene regression. |
| Define and enforce the CLI seed range | Unlike frame counts, seed still uses strtol without errno/range validation, then casts long to unsigned int. An overflowing positive decimal before version was accepted by the actual Windows executable, while seed abc was rejected. Choose a fixed documented range and test boundary/overflow values across Windows and Unix before relying on large seeds for reproducible art captures. Existing small-seed captures are unaffected by that range defect. Separately, [native art captures](docs/knowledge-base/pose-review-capture-notes.md) showed that the same small seed selects different oceans on Windows and Linux through libc rand(); record selected asset paths and platform with every visual fixture. |
| Complete resource unload before live restart or pack switching | Parsed resource arrays remain process-owned. Slots borrow decompressed data and resource names refer to map entries. A full unload API needs ownership rules across those aliases. The application starts once per process; no recurring parser leak is claimed. Scene/overlay cleanup is covered separately. |
| Remove redundant decoder-result checks when touching resource loading | `resource.c` lines 117, 189, 282 and 336 check decompressed pointers for NULL, but the current decoders allocate successfully or terminate. These branches are unreachable under that contract. Keep their removal separate from the reachable unfinished scene commands; no performance benefit was measured. |
| Linux desktop fullscreen and physical audio | Real X11 resized-client captures test centering, enlargement, shrinking, bars and native-size recovery. Xvfb without a window manager does not validate desktop fullscreen negotiation. Audio error tests use real pthreads and deterministic ALSA responses, not a physical device. Exercise those paths on desktop Linux. |
| macOS presentation regression automation | Earlier manual Sequoia testing verified orientation, channels, sound, close, resize and fullscreen. New Cocoa event/allocation probes do not replace complete rendered-scene screenshots or physical audio validation. Add native window capture when presentation changes next. |
| Exercise Windows/macOS post-open audio failures | Windows refill ignores waveOutUnprepareHeader, waveOutPrepareHeader and waveOutWrite results, though initial queue setup checks errors. macOS ignores AudioQueueEnqueueBuffer and AudioQueueStart results. Add controlled device-error probes for those active paths before selecting retry or shutdown behavior; no physical-device failure was reproduced in this audit. |
| Diagnose an intermittent native palm capture failure if it recurs | The first local PR 6 main gate failed one partial-fallback capture after all smoke passed. Its temporary native log was removed before the cause could be inspected. Focused smoke and all eight palm regressions then passed. Capture assertions now preserve exit code and native output after scratch cleanup; this diagnostic change does not claim to fix an identified runtime cause. See the maintenance verification for later full-gate results. A later isolated pose-review capture exited 0 with the bounded-stop marker but omitted final capture/usage stdout markers. Three retained PPMs were complete and hash-identical to a successful control. Fresh inactive desktops and distinct inherited stdout/stderr handles did not resolve the marker failure. Its cause and any relationship to the earlier palm failure remain unproven; this is not evidence of a missing image. |
| Isolate unattended native captures from interactive hotkeys | A later 400-frame smoke stalled at frame 158 because pause was on and maxspeed had been toggled off. A preserved dump proved the normal Sleep loop; the user confirmed accidental input. Keep hotkey behavior tests, but consider an explicit unattended capture mode or isolated test desktop for other native tests so workstation typing cannot pause them. Do not call this a renderer deadlock or conflate it with the earlier palm failure. |
| Retain native-test artifacts after a failed capture-marker check | The first arrival018 Windows gate exited a palm child with code0 but stdout ended mid asset log and lacked the capture marker. `tests/test_palm_renderer.py` checks that marker before reading the PPM, then its default temporary directory is removed on failure; the PPM's existence is therefore unknown. The first front-refresh gate repeated the symptom for HD E-to-D after every smoke stage passed. A retained unchanged rerun passed smoke and all8 palm checks with 17 complete images and markers; a separate fresh full gate passed. [Front verification](docs/cartoon-front-refresh-verification.md) preserves the failed and successful log identities separately. Retain automatically allocated palm and wave work directories on failure, print their locations, save timeout partial output, and clean up successful runs. Test both failure retention and successful cleanup without weakening capture-marker assertions. The post-merge audit found the same retention structure in `tests/test_wave_renderer.py`; cover both helpers when fixing it. These observations do not establish the missing-marker cause or prove a missing image in the original failed run. |
| Broader audio formats | Web refuses non-mono/non-U8 requests before changing playback state. All 23 shipped WAVs are mono, 11025 Hz, unsigned 8-bit. Stereo needs buffer layout, callback length, channel output and scheduling changes together. The common loader also warns about mixed rates/channels without resampling. |
| Deterministic multi-scene wave phase | File-static wave counters persist and initialization advances them. A seed reproduces a fresh-process run, not arbitrary scene entry after other scenes. Preserve current timing; design a reviewed reset option if deterministic scene seeking is added. |
| Empty story selection fallback | A NULL final-scene selection would re-enter storyPlay without a tick delay. The shipped table supplies candidates, so this remains an unreachable bad-data case. Address it when scene tables become editable. |
| Measure flip caching first | grDrawSpriteFlip blits one column at a time. A scratch flip adds copies and is not an established saving. A reusable sprite cache needs matching slot cleanup and fresh-process interleaved measurements against a variant without the cache. |
| Measure damage tracking first | Full-frame composition and presentation remain. Earlier Web optimization used alternating fresh browsers and exact pixel comparisons; this cleanup makes no new performance claim. Profile representative scales/scenes before adding renderer complexity. |
| Keep later style source storage deliberate | Preserve selected raw art, used ancestors, prompts, acceptance and export recipes. Avoid duplicating the full original archive or every diagnostic capture in each style. Noir/anime also need explicit catalog and authoring-tool registration. |
| Add verified original-resource sound extraction | Checked explicit-path helpers now reject bad input and preserve existing outputs. The legacy sound layout still reads RIFF's first two bytes as a length and applies historical output numbering. The supplied executable proves this defect; the helper refuses its out-of-bounds span before creating output. Add a separately named mode using verified resource identifiers and bounded lengths, with explicit handling of RIFF content versus trailing allocation bytes. See docs/knowledge-base/original-extractor-reference.md. |
| Calibrate complete scenes against the supplied original | All 10 ADS and all 41 TTM names are present. Decoded ADS match; 40 TTM match exactly. SJLEAVES.TTM differs by a removed SET_DELAY 0 in tag 3. The original-only SA_DEMO.BMP is now classified as non-Johnny reference art outside the port. Five TTM files without story ADS references still need behavioral classification, not automatic promotion to missing scenes. Use the knowledge-base event crosswalk and original windowed reference to observe complete branches, timing, transitions and outcomes. |
| Reuse resource inspection for the next art pack | The xesf viewer offers useful resource-list, sprite-sheet, palette and script-pane patterns, but its playback has unfinished commands and its current-line callback is not called. Prefer adding proven inspection conveniences to our existing scene/art tools: show original frame IDs, offsets, direction and complete motion-family contact sheets beside variants. Keep original DOSBox observation as the behavioral reference. See docs/knowledge-base/external-tools.md. |
| Share exporter and native-review configuration for later families | The017 and016 authoring checkpoints preserve the same premultiplied filtering with different source hashes, cap targets and canvases. A copied native adapter initially retained a017 metadata label while packaging016; comparison checks rejected it before review. The new000/015 shared exporter now requires an explicit frame and recipe match, with historical-filter parity and executed mutation checks. Future native review should likewise make frame identity, registration and route inputs explicit shared configuration before larger batches. Preserve historical exporters/recipes and their exact bytes; verify new common tooling against their outputs instead of rewriting accepted evidence. This is a maintenance opportunity, not a measured speedup. |
| Review remaining compiler diagnostics when touching those paths | Pinned Emscripten 6.0.9 still reports existing unused parameters/non-Windows parent-window state and C11 pedantic diagnostics from Emscripten macros; vendored miniz reports its large-file I/O choice. Native Windows phase-one build is warning-free. Keep SDK/vendor diagnostics distinct from actionable project warnings and do not silence them globally. |

## Profile-walk authoring checkpoint

The later [connecting delivery](docs/cartoon-connecting-poses-verification.md)
closes the connecting-pose, skin-palette and standing018 foot promotion items.
The user accepted the matched lighter colors, retained the revised shorts and
torso, then accepted foot-v5 with "much better proceed". Production uses27
outputs from the frozen color bundle and the separately exported/normalized018.
All2594 payloads match the final reviewed private package;15 island assets remain
unchanged. Future image generations must receive fresh color/material checks
and original-foot-contact comparisons before motion approval.

Historical static-preview reconstruction needs explicit output isolation in the
future shared authoring tool. An isolated execution of the actual profile
`build_review.py` reproduced its frozen HTML and record with the old 32-asset
archive. With the promoted 40-asset archive, it left the HTML unchanged but
overwrote the existing `review-record.json` archive hash. The current README and
delivery guide now direct old-checkpoint replay to an isolated harness with
pinned copied inputs and redirected fresh outputs; a separate checkout alone
does not redirect the fixed destinations. Original tracked evidence was not
changed. Add configurable output paths and refusal of mismatched existing records to the successor, with
historical and promoted archive controls. This affects offline evidence replay,
not application rendering.

The post-merge review also identified a small offline-tool cleanup opportunity:
the profile native viewer preloads all 234 unique full-scene captures and redraws
both canvases on every animation tick, even between pose changes. Its cache is
bounded by the capture set; this is not evidence of an accumulating memory leak.
Before longer reviews, measure lazy loading and redraw-on-change in a shared
successor while preserving this accepted checkpoint's exact helper/evidence
bytes. No performance saving is claimed without a measured comparison.
The connecting-pose viewer currently uses the same preload/redraw pattern for
290 unique captures across six clips. Include that larger review when measuring
the shared successor; its capture cache is also finite.
The new skin-color viewer references 548 unique native images but loads only
the selected clip and releases prior clip references. Browser regressions check
exact active-clip membership; removing cache release triggers a named failure.
This is a verified loading policy, not a measured memory or speed saving.
Keep the historical viewers intact and carry the policy into a shared successor.

The [approved profile family](art/cartoon/walk-pilot/profile-walk-v1/README.md)
contains 001-008, including the lowered 003 tucked foot and revised far-arm
swing. The user accepted both native directions and ordinary 003 departures
with "Yes, keep this profile walk". Every selected export and all four native
clips passed smoke before regression. The earlier 32 asset payloads remain exact
as this family brings the pack to 40. Preserve the
[image lessons](docs/art-style-learnings-profile-walk.md) for future style packs.

## Standing-family capture evidence

The [standing delivery](docs/cartoon-standing-verification.md) again encountered
the Windows palm capture-marker failure. This time its scratch gate retained
the failed artifacts: the child exited0 and produced a complete1280x960 PPM,
while stdout ended mid asset path without the marker. An unchanged focused
smoke/regression rerun passed; its corresponding image is byte-identical to
the failed run. This establishes a valid saved image for this occurrence,
not the cause of the incomplete stdout or a runtime fix. The permanent
palm/wave failure-retention item above remains open.

## Front-walk post-merge audit follow-ups

The [fresh audit](docs/front-refresh-post-merge-audit.md) reviewed merged main
`71f3e5f`. These additional findings are in pre-existing code; none was introduced
by the front-walk artwork or authoring changes.

| Item | Evidence and next useful action |
| --- | --- |
| Handle incomplete TTM tag tables and zero-offset lookup | `ttm.c:171` fills missing tag IDs with 65535 but leaves offsets unset. Compiled untouched-source controls with two declared tags and one actual tag returned allocator fill 2779096485 for sentinel lookup; zero-fill entered the `ttmFindTag` loop until the bounded probe timeout. Valid-tag and ordinary missing-tag controls passed. Reject or bound incomplete tables, initialize retained fields, and ensure lookup advances when an offset is zero. This is malformed-metadata evidence, not a shipped-scene failure. |
| Report resource-dump write and close failures | `dump.c:169` ignores `fclose`, as do the screen and script writers. Actual `dumpBmp` returned normally after an output targeting `/dev/full` produced `fclose=-1`, `errno=28`; a regular-file control passed. Check writes and final close, name the failing output, and preserve golden output on success. Only the BMP writer was fault-injected in this audit. |
| Synchronize Web fullscreen with browser state | `platform_web.c:152-163` flips a private flag without a fullscreen-change callback or checking the request result. An existing local Web build entered on Alt+Enter, exited through `document.exitFullscreen()`, ignored the next toggle, and entered on the following one. The source issue is present on merged main; this observation used a hash-recorded older local build, not a fresh merged build. Observe actual fullscreen state and handle failed/deferred requests; test browser-side exit and re-entry. Null probe exit/error fields are not liveness or error-free evidence. |

## Front-walk tooling prerequisites

The inventory CLI now rejects output/source identity before parsing or reference
export, including resolved aliases and hardlinks. Windows and Linux smoke and
regression controls preserve disposable source ZIPs; compiled guard-removal
mutations fire. The [verification](docs/art-inventory-identity-verification.md)
also covers gate ordering and omission controls under PowerShell 5.1/7 and the
Linux/macOS/Web CI commands. This resolves the reproduced inventory overwrite.

The [pilot-history model](docs/cartoon-pilot-history.md) now supports explicitly
declared replacements while preserving the original 21-slot approval and pose
facts. Historical test fixtures remain separate from live production checks.
A simulated accepted 028 replacement exercises both suites against schema 2,
so subsequent replacements do not depend on schema 1 assumptions. New artwork
still needs its own human review and an explicit history declaration when
promoted. The approved front 028/029 replacement now uses that explicit history
declaration: 19 original pilot mappings are retained and two are replaced.

## Cartoon production foundation

The later [rear walking delivery](docs/rear-cartoon-walk-verification.md) records
six newly accepted sprites, 27-asset pack integration and inherited approval
validation. Its human approval includes the native island 8-to-9 transition.
The subsequent [arrival delivery](docs/cartoon-arrival-verification.md) adds
approved standing 018, bringing production to 28. Its review preserves the
original route's draw-origin shift and disclosed foot-depth observation.
The [complete standing family](docs/cartoon-standing-verification.md) then adds
000/015/016/017, bringing production to32 assets while retaining all earlier
member payloads. Five standing drawings cover eight reflected directions.

The complete production slot catalog now checks shipped coverage, accepted
recipe/PNG identity, reference provenance, duplicate candidates and HD-proxy
blankness. The original-first pilot metadata preserves its historical facts
and now maps current replacements separately.
One Linux CI step runs both metadata smoke suites before their regressions and
reproduction checks. Local execution of the actual CI commands passed; damaged
approval, missing-command and suppressed-exit controls failed as intended.
This resolves the manual-only authoring-check item. The
[verification record](docs/cartoon-production-verification.md) records evidence
and the current delivery state.

## Calm focus walking revision

The user approved the [actual island preview](art/cartoon/walk-pilot/calm-focus-runtime-v1/production-acceptance.json)
on 2026-09-15 with "looks good", including the two toe-clearance edits after the
standalone review. This resolves the pending art decision for the six displayed
walking poses. The original observations remain attributed to the user's
comparison: Cartoon 024 was requested to turn its trailing right foot inward;
the user identified original 028/029 as anatomical left foot forward, right foot
back. The displayed reversed-leg artistic difference and 026/027 lift are
accepted as shown, not relabeled as exact original anatomy. The
[image lessons](docs/art-style-learnings-calm-focus.md) preserve that distinction.
The [revision verification](docs/calm-focus-walk-verification.md) records packaging,
metadata, native checks and the subsequent audit.
That audit also corrected README's obsolete claim that Windows screensaver mode
ignored activation loss. The existing handler and screensaver tests already
implement and cover that behavior; no runtime change was needed for the correction.

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
