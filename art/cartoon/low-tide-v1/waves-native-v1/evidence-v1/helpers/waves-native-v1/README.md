# Low-tide wave native review adapter

The baseline is the approved static beach/rock package `f46e5cac5508b00cc7a675be4eaf843029cebfeabe80c849c8fa5f311813b92b`, with existing low-wave fallback art. A candidate must retain every baseline payload and add only Cartoon BACKGRND030 through 041, each with its original HD canvas. The shipped production archive remains unchanged.

The driver includes the pinned existing native observer and adds an explicit raft argument plus actual low-wave surface and raft draw logs. It uses the original wait and public walking calls. The initial group contains no-decoration and clover scenes, each with 32 waits and at least 3,840 requested ms. Every smoke in a group must pass before fresh-process repeats begin. Each process starts fresh so the engine's persistent island phase counters have identical initial state.

The completed comparison uses wave candidate `a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66` at source commit `99961340e68bf5161217770e6a80dfeddea9e62b`. All eight baseline and candidate cases passed: 16 smokes followed by 16 exact fresh-process repeats across the initial and extended groups. Waiting cases contain 81 displays over 3,840 requested ms; the front and rear routes contain 55 and 75 displays over 4,840 and 6,520 requested ms respectively. Every low waiting case observes all twelve wave phases. All 81 high-tide comparison displays are pixel-identical.

Actual-log raft-state and low-surface mutations and an outside-pixel mutation each failed with the intended single message; restored positives passed on both initial package runs. The separate high-tide witness changes a pixel inside a low-wave rectangle: low mode accepts that one-pixel change, high mode rejects it with its exact-pixel message, and the restored high positive passes. Compiler stderr is empty across all four builds. The completed native logs contain no warning/error/failed/ALSA/segmentation matches, and all four launchers report no surviving task container. Human motion acceptance remains separate.

The first selected low-wave PNG activates the existing wave-base restore path. The fallback baseline stamps one updated family; the candidate may redraw all active families after restoring the saved background. The checker therefore compares actual displayed phase tuples, timing, native calls, character and static draw records, not total low-wave draw-row counts. Differences are restricted to the clipped union of the twelve original wave rectangles. The high-tide control requires exact whole-scene pixels.

Use the existing toolbox Python. The baseline command is:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/low-tide-v1/waves-native-v1/run.py --group initial --output build/low-tide-v1/waves-native-v1/baseline-initial-v1
```

After a candidate ZIP and its exact SHA256 are supplied, run:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/low-tide-v1/waves-native-v1/run.py --group initial --candidate <candidate.zip> --candidate-sha256 <SHA256> --baseline-captures build/low-tide-v1/waves-native-v1/baseline-initial-v1/captures --output build/low-tide-v1/waves-native-v1/candidate-initial-v1
```

All output folders must be fresh children of `build/low-tide-v1/waves-native-v1`. The launcher uses the existing pinned Docker image, no network, a read-only source mount, an isolated Xvfb and hidden host subprocesses. This does not take over the workstation display.

The completed `extended` group covers shifted night clovers at native offset (-80,+20), raft states 1 and 5, the high-tide exact control, and low-tide public front/rear walking routes. Matching captures are in `baseline-extended-v1` and `candidate-extended-v1`. The `all` group is available for a fresh complete run; do not repeat already-passed groups without a concrete reason.

Public routes use the existing seeded DCF and BAE calls. Their low-tide execution checks the rendered character/scenery interaction; it does not prove natural story selection or universal foot contact. Explicit island state bypasses calendar/cargo eligibility, night retains its existing fallback scenery, and timings are logical tick requests rather than performance measurements. This adapter does not establish human art acceptance.

Each group's `summary.json` lists its completed cases and the cases belonging to the other group; all eight cases are complete across the two groups. Exact commands, image ID, source/helper hashes and build identity are retained alongside the native logs/reports. `evidence-v1/evidence.json` and its readback bind compact exact copies. Initial none/clover pixels are referenced through the root-owned lossless browser manifest; representative extended finals are retained locally. Bulk native frame sequences, private ZIPs and executables remain scratch and are hash-bound rather than copied. The one-time preservation writer refuses an existing evidence folder; do not rerun it into the frozen bundle during reconstruction.

No original executable or workstation display is tested. Night, cloud and raft visuals retain their existing fallback artwork. Representative final walking frames show the selected standing sprites on the island; this is bounded visual inspection, not universal story/contact validation. No new actionable runtime defect was observed. Keep the earlier `native-v1` evidence immutable.
