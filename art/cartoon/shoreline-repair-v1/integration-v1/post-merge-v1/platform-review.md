# Seasonal post-merge platform review

Reviewed primary checkout `D:/.ai-work/projects/johnny-castaway-rebornHD` on 2026-09-17 at main `9b0a4ed1fb5920faf426c4d3aa89e45afadebf07`. This was a read-only source review, with an ignored scratch report as the only output. No UI, native process, browser, device test or production mutation was launched by this audit.

No introduced platform blocker or new confirmed platform defect was found. The remaining concrete issues below already appear in BACKLOG.md. This conclusion is scoped to the reviewed paths and existing evidence, not a claim of complete device or story coverage.

## Reviewed scope

Read all four backend implementations and the shared platform interface: initialization, windows, event translation, surface construction/ownership, clipping/blending, presentation, time/yield behavior, audio open/refill/close and teardown. Also read the PNG loader/decoder and ZIP adapter, the application entrypoint/argument parser, event loop, common sound lifetime, fatal-error path, application Web HTML/JavaScript, shared Web builder and PowerShell wrappers, CMake runtime/archive wiring and CI workflow. Reviewed graphics startup/teardown/composition and normal/atop/mirrored sprite integration, plus selected footprint validation and wave dirty-region restoration. The rest of engine/VM/story behavior belongs to the parallel core audit.

`git diff HEAD^1 HEAD -- platform index.html src/engine/jc_reborn.c src/engine/events.c src/engine/sound.c src/engine/utils.c CMakeLists.txt cmake/RuntimeData.cmake tools/build_web.py scripts/build_web.ps1 scripts/build_web_local.ps1 .github/workflows/ci.yml` is empty. The seasonal change does not alter those platform/entry/Web/build paths.

## Findings and current locations

| Area | Current observation |
| --- | --- |
| New footprint integration | `src/engine/art_style.c:303-397` accepts only the named Cartoon frame/canvas combinations; HD/original fallback retains its ordinary dimensions. `graphics.c:594`, `:619`, `:669` applies offsets in normal, atop and mirrored drawing before the existing clipped blitters. The mirror anchor uses logical width. `island.c:62-114` includes actual offsets and all phase extents in the clipped restore region; `:134-146` restores clean background before recomposing active phases. No new backend allocation or ownership type was added. |
| Surface and PNG ownership | `platform/platform.h:145` specifies borrowed pixels for SurfaceFrom. Backend wrappers retain `ownPixels=0`; failed constructors unwind. `platform/png_loader.c` frees decode storage on failed wrapping and releases WIC COM interfaces. `graphics.c:833-847` explicitly releases sprite pixels before their borrowed wrapper. Window-owned surfaces are freed once by their window destructor. No new accumulating leak was established. |
| Windows input, existing open item | `platform/platform_windows.c:175-239` returns from WM_INPUT without the foreground DefWindowProc cleanup, including failures. BACKLOG already records this API-contract omission. No OS leak measurement was performed here. |
| Common audio startup, existing open item | `src/engine/sound.c:158-166` resets callback state after platformOpenAudio can start the worker; `:79` can call memcpy with the initial NULL pointer and zero length. BACKLOG already requests initialization before open and a real common-sound startup probe. |
| Audio failures, existing open item | Windows refill `platform_windows.c:1072-1080` ignores unprepare/prepare/write results; macOS `platform_macos.m:592` and `:654` ignores enqueue/start results. This is already in BACKLOG. Linux `platform_linux.c:743-767` joins a created worker before freeing its buffer, even after the worker stopped; its bounded ALSA retry path preserves the unaccepted tail. No physical-device behavior was newly tested. |
| Web fullscreen, existing open item | `platform/platform_web.c:152-163` flips a private flag without synchronizing a browser-side exit or request refusal. BACKLOG:131 and the older hash-recorded `docs/front-refresh-audit-evidence/platform/web-fullscreen-observation.json` already document this. That historical probe is not a newly built-main test. |
| Web event/audio/presentation integration | `events.c:262-270` yields each frame and services events during waits. `platform_web.c:557-582` pumps audio while yielding; `:688-738` bounds queue work. The present path `:173-257` re-reads the current WASM heap view each call. `index.html` retains URL/style operand boundaries, toolbar key isolation, bounded log strings/sticky fatal state, scene reload for style changes, and canvas-click audio resumption. No new operability issue was found. |
| Entrypoint and cleanup | `jc_reborn.c` retains config/setstyle before archive/playback, explicit TTM/ADS cleanup, and process-lifetime story mode. `events.c:75-198` and `:237-260` close audio then graphics on user/bounded exits. `graphics.c:246-255` releases saved/background/window ownership. Parsed resource lifetime and live-restart limitations remain the existing backlog scope; normal style switching reloads the Web page. |
| Deployment | CMake selects the appropriate backend/frameworks, keeps the native archive prerequisite, and gives Web an archive object dependency. `tools/build_web.py:27-36` checks the preload payload against the exact archive and refuses stale/missing outputs. PowerShell SDK activation stays in a child shell. No newly non-operable path was found for the supported build flows. |

The no-op native frame yield and surface locks, non-Windows preview-parent adapter, and single-threaded Web audio locks are intentional shared-interface implementations. Translated key-up events are presently ignored by the engine; they are not an incomplete active feature. No new removable dead runtime helper was identified in this scope. Historical macOS comments saying "UNVERIFIED" predate later CI/manual evidence and should not be used as the current validation status.

No performance result is claimed. Existing full-frame composition/presentation and per-column mirrored sprite drawing remain the backlog's measurement candidates (`graphics.c:690-695`, `:282-331`). Linux/macOS/Web blitters still use per-pixel bound checks, while Windows clips once; consolidating those implementations could reduce maintenance duplication, but requires exact clipping/alpha parity tests and measurements before claiming a saving. No extra optimization item is needed to block this delivery.

## Existing execution evidence and its limits

The retained final native summary is `art/cartoon/shoreline-repair-v1/integration-v1/native-final/evidence-v1/captures/summary.json`, SHA256 `ad1bff5c0aee930dff4f4825f05952aa0cbfc644e3fc384b29b398ea6719244a`. Fresh readback reports PASS, 14 paired cases, 28 smoke captures followed by 28 fresh repeats, and eight named negative controls. It covers selected high-wave phases, low-tide fallback, holidays, night/offset scenes and Johnny routes. This audit did not rerun that matrix.

Current `assets/scrantic_data.zip` SHA256 is `4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6`, equal to that summary's candidate. Native input record SHA256 is `dea04fcd2ba4c4fa0644d807627d7b9a6ad0c39ff8e6c3300ac1fcb65eec9e13`. Of its 48 runtime source/CMake paths, 45 match current working-tree bytes exactly. `art_style.h`, `graphics.c` and `island.c` have different CRLF versus mixed LF/CRLF working-tree representations; their retained snapshots exactly match current text after CRLF-to-LF normalization. `git diff 1aad361fe78dde2c956e05dc451b8d5bab100af0 HEAD -- src platform CMakeLists.txt` is empty. Preserve the historical snapshot hashes rather than describing all current file bytes as identical.

The parent reported a fresh full inactive-desktop Windows gate and all four main CI jobs passing on this HEAD while this source audit ran. Those runs belong to the parent's separately retained evidence. I reviewed `.github/workflows/ci.yml` and `tests/platform-cleanup.md` to establish scope, not to replace their logs with this review. Linux Xvfb presentation and controlled audio probes do not establish desktop window-manager fullscreen or physical audio; Cocoa event/allocation probes do not replace rendered-device coverage. No new device/fullscreen/original-executable, sanitizer, race-detector or performance measurement is claimed.

## Current working-tree source hashes

These SHA256 values pin the actual bytes read, including current checkout line endings. The graphics/island/art-style files were reviewed at the integration locations stated above rather than as a second exhaustive core audit.

| Path | SHA256 |
| --- | --- |
| platform/platform.h | d44c885dac7188ce20c1c9b726e43f0796a1312639ad2136b248469ad1b0f11b |
| platform/platform_windows.c | 4db7c0906dd3b572a931afb0c711b203b68e76321f102baaf1f9bb8a7543b4db |
| platform/platform_linux.c | c57c9aefad8f40e959116772438f0bdbda7403438b1b7188f2453cbecbc66687 |
| platform/platform_macos.m | 4f1a5dd1d0aab31c223f9a3ed9f7f2e540d4fd8bca329ca28dba8cb9e15af365 |
| platform/platform_web.c | 559e223cbf6f6ba51ad6d9a2a6ae4c3a1685fbb28d9625b1efc59ca3be48ee4b |
| platform/png_loader.c | 05cbc18bc03a3c7b48c15c2ae010242b37b489302acabf753192605aaeffaf1d |
| platform/png_decoder.c | e98e3e9a9c3970d8366bcb5e7c8e57a7e5e71b0fad3913d42638cc072fdc2f6a |
| platform/zipvfs.c | 1cb46f55871ac87a0f4ddee7d463282e822269875c77e49f81e101a1c2adec49 |
| index.html | c7190a5a3a0f2aa073bcc570bbbdfc7dcc5044d47c040ebe97619f2191cb85b2 |
| src/engine/jc_reborn.c | 50d9904cffd7c3cba9877ecec383370c612622ccd31a5a013e77755903c358c4 |
| src/engine/events.c | 041ac9fce76af2c3e1fc2eeef56ea9b92b45e1a4adc0087d5318720ccc2d57d2 |
| src/engine/sound.c | eec8a1b43e33eccbd4e7f835ca55b7d9ab952818f2093f6a996d69d1ce6a91ee |
| src/engine/utils.c | c50c4ae6de6a59e4fbd1a169592eb920778449f8c000175cb55d66595343c10f |
| src/engine/graphics.c | fded8d14dbfa432242170e0a16010cb882d02f437d31e5a317bfe2baafcee392 |
| src/engine/island.c | 78795472d233c9b54bcd8ff32e032358e5e19434e4de7d2fdb26f521d6600737 |
| src/engine/art_style.c | f6519bfbb7fb9af09ae19b3d41b546bb644dda1952160eef1956ad7466051513 |
| CMakeLists.txt | 0090f05332c00493b4f4fdd30fc6a25efd6b383a6f3373a3eb0c98d7a65d0962 |
| cmake/RuntimeData.cmake | 636026ff42a78acb3716f61c44988ebf3d307313dc5964d752e1f28e6f16e905 |
| tools/build_web.py | 602a0f1a7d7db27f27f0a9ae7d13b4ca49a6be108176202f2827f7a47764b259 |
| scripts/build_web.ps1 | 4ecdfe6c6eb97e64b64b7fc7859b2651c26350baecc7720b8341bde766aba1ec |
| scripts/build_web_local.ps1 | d7e48fbab143d5e3428895db4f4dabbde4347c25cffc386d683e6fcf50a48c03 |
| .github/workflows/ci.yml | 8ee81e0e250e5d4b3a08c7cf39d1b41b18481d5fd48a36bad198258bb8864915 |
| BACKLOG.md | 62ef96d8ffa180557fdcd4cefa7fc489a365a9ba56f2f8c2d7f810c3796b1362 |
