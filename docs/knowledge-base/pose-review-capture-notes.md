# Pose-review capture observations

Observed on 2026-09-15 while preparing an isolated original/current/candidate
walking review. No engine or production-art changes were made for this probe.
The standalone browser animation uses sprite composition separately from these
native captures.

Three isolated 21-asset packs passed their first-pose native smoke. The full
42-display capture stopped at display 20 because required completion messages
were absent from stdout, although the process exited 0 and printed its bounded
stop message. The assertion was retained. At this Windows checkpoint, full
native capture, candidate golden regression and the actual-capture browser
review remained incomplete. The subsequent Linux results are recorded below.

Three failed attempts and one successful separate control produced complete,
identical 1280 by 960 P6 images, each 3,686,416 bytes. This is evidence of missing
log messages, not a demonstrated missing image. Any relationship to the earlier
palm capture failure is unknown.

| Evidence | SHA256 |
|---|---|
| Executable used | `103f1816ea738a5e483646638ffef15cd5e62d320f36b05df3c58981d5db8cd5` |
| Protected production archive | `fb70d795531d50093dd4a9ac53895a6a20a76efc982d4d7d45a64403b98e68d8` |
| Identical display-20 PPMs | `ef8be92625b60b45556196bfd00f473f06174930c7954f942674d05d3ee8e610` |

Fresh inactive desktops and distinct inherited stdout/stderr handles did not
resolve the missing messages. Source inspection found that the bounded-stop
message explicitly flushes stdout; capture and art-usage completion messages
use printf without an immediate flush. Normal exit should flush them. This
observation does not establish a cause or justify a runtime fix.

The initial scratch launcher had a separate defect: assigning `lpDesktop` to
Python's subprocess STARTUPINFO did not marshal that field. A one-frame probe
failed the foreground guard. The corrected scratch launcher uses CreateProcessW
with STARTUPINFOW and verifies that each child window belongs to an inactive
desktop. It never switches the input desktop. No native child remained running
at the end of the investigation.

The scratch helper's independent synthetic tests passed eight negative controls
and browser timing, pairing, controls and failed-image feedback. Those tests do
not validate native rendering or approve artwork. A follow-up can inspect stdout
delivery with separate pipes or instrument CRT flush/handle state in an isolated
diagnostic build.

Local evidence is retained under the art worktree's ignored
`build/original-pose-review/setup-current-v1/original/`: `display-020`,
`display-attempt2-020`, `display-attempt3-020`, `retry-display-020` and
`distinct-handles-control-020` logs and PPMs. The invocation guide and longer
investigation notes are in `build/original-pose-review/README-motion-review.md`
and `CAPTURE-NOTES.md`. These local files are not included in the repository.

## Subsequent Linux review

The existing Docker Desktop WSL environment and `johnny-platform-cleanup:latest`
image provided a windowless Linux/Xvfb capture path. No Windows application was
launched. Docker needed `--init` here so `xvfb-run` could complete startup; its
earlier invocation as PID 1 stayed waiting before the engine started.

The Linux original display-20 probe produced a complete image and all required
completion messages. This does not establish a cause or fix for the Windows
logging failure. A same-seed cross-platform image comparison also failed:
`island.c` uses libc `rand()` to select the ocean and clouds, and Windows and
Linux selected different assets with seed 9. A seed alone is therefore not a
cross-platform scene identity. Record the selected asset paths as well as the
platform and seed when reproducing visual evidence.

Linux seed 11 explicitly loaded the approved Cartoon `OCEAN02.SCR.png`. Current
and Calm focus candidate captures then used that same Linux build and seed.
Both display-20 smoke checks passed before the complete routes: 42 displays,
23 route positions and the 3760 ms endpoint witness per version. Every image
difference stayed inside the placed Johnny canvas. The diagnostic archives
differed only in six walking PNGs; all 15 island PNGs were unchanged.

Both normal archives also matched all 2,452 golden decoder hashes. The browser
player loaded all 84 actual captures and passed seven smoke checks followed by
52 timeline and control regressions. These results validate this Linux review
route, not Windows scene parity, original-executable timing or human acceptance
of the draft artwork. All 75 protected source and input hashes remained unchanged.

Local reproduction scripts, capture reports, image hashes, pair comparisons and
browser results are under `build/original-pose-review/linux-capture/`. The Windows
logging issue remains in `BACKLOG.md`; it was not bypassed or marked resolved.
