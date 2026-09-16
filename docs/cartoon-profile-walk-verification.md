# Cartoon profile walking: delivery verification

The user accepted the complete eight-pose profile walk with "Yes, keep this
profile walk". The [human record](../art/cartoon/walk-pilot/profile-walk-v1/human-motion-approval-v1.json)
binds the exact reviewed art and page. It covers both native F-to-C and C-to-A
routes, standing connections and the two ordinary 003 departure contexts.
Unseen story uses and remaining 009/010/012 poses are separate future work.

## Artwork and review

| Area | Evidence |
|---|---|
| Identity and pose | Approved Calm focus appearance, brimmed sailor cap, beard and shorts retained. Original decoded geometry guides the profile poses. |
| Arm continuity | The user preferred 006's rear arm and approved 008's forward-arm direction. That direction extends through 001/002, with the rear swing through 004/005/006 and passing-pose occlusion in 003/007. |
| Canvas fit | Shared 0.1 scale, explicit per-frame cap registration and original doubled canvases. Foot-fit edits use the image tool; no independent body fitting or limb warping. |
| Exports | Every selected frame passed 3 smoke checks followed by 24 regressions. Existing exporter mutations were not repeated because the exporter stayed unchanged; the initial checkpoint preserves their execution. |
| Native playback | Four clips each passed smoke, full baseline comparison and an exact fresh-process repeat. Only the eight profile canvases change. Original calls, timing, coordinates, flips, backgrounds and approved standing poses remain exact. |
| Browser | Local and served smoke preceded complete display/control regression. All 235 served HTML/image files match their recorded identities. |
| Negative controls | Seven controls fired: two same-canvas frame substitutions, wrong selected path, changed timestamp, changed approved-standing pixel, wrong pose selector and changed served HTML. |

The same-canvas substitutions exposed a preview-packaging gap: matching PNG
hash and dimensions alone did not prove the selected frame identity. The
candidate builder now binds each frame through its source, recipe, export report
and runtime PNG. Both 001-to-005 and 005-to-001 substitutions fail the intended
condition despite equal canvases. This is offline authoring code; no engine
behavior changed.

Native clips contain 34/62/36/64 display records and last 3280/5560/3400/5680 ms
respectively. Those durations are observed logical timing, including the actual
standing holds. They do not establish original-executable timing equivalence.
The review retains zero-duration draw witnesses and repeated source-table poses.
Both panels share one fixed camera for each route and use full-canvas mirroring.

The [native evidence](../art/cartoon/walk-pilot/profile-walk-v1/native-motion-v1/evidence.json)
binds 96 preserved files with SHA256
`93213a10de7b9572ae43dd943c04fac4c0428c75858cadb4f190b95dd5ea8cca`.
Its pending-at-capture status remains historical. The later human record supplies
acceptance without rewriting those bytes. The reviewed private ZIP has SHA256
`d476a447f84dcb996c0ef2e229a18ca5e2b0ad03de57cc538b6933a42318d82c`.

## Reconstruction clarification

The native [reconstruction guide](../art/cartoon/walk-pilot/profile-walk-v1/native-motion-v1/README.md)
requires a separate checkout with the pinned pre-promotion archive. Reproduce
the selected exports and fresh native captures in that checkout's ignored
scratch tree. Keep the retained baseline binders and their evidence alongside
the helpers. Review reconstruction does not require rewriting any historical
evidence file or publishing over the existing local review slug.

`preserve_baseline.py` and `preserve_motion.py` are one-time checkpoint writers.
Their refusal when tracked binders already exist is intentional. Skip those
writers when replaying the already-preserved checkpoint. A separately recorded
new checkpoint needs explicitly different output paths; do not remove or weaken
the historical preservation guards. Local browser validation is sufficient for
a replay when the original publication slug is occupied.

The earlier static builders also target their historical review-evidence
directories. An isolated post-merge probe reproduced the original first-pose
HTML and record with the pinned 32-asset baseline. With the promoted archive,
the same builder left HTML unchanged but rewrote the saved record's archive
hash. Use the production reconstruction above for accepted art. Recreate static
history only in an isolated scratch harness that redirects `ROOT`/`HERE` and any
derived path globals to copied inputs, the recorded baseline and fresh outputs;
a separate checkout alone does
not redirect the hard-coded destinations. Leave the accepted historical files
intact. This reproduced offline helper limitation is tracked in BACKLOG for the
shared tooling successor.

## Integration

The standard pack builder produced SHA256
`1649218b32a4d11595806f8680e351a4f47950fcefbafdf8de758c2d225913db`.
All 2583 prior member payloads remain exact, with eight added sprites, 2591 total
members and 40 Cartoon assets. Every member equals the reviewed private ZIP.
The complete ZIP hashes differ because the standard builder orders entries
differently. Earlier ledger rows, runtime manifest and pilot-history declaration
remain unchanged.

All eight annotated runtime recipes reproduce the reviewed runtime and padded
PNG bytes exactly. Package smoke validates all 40 assets before the complete
member regression. A deliberately corrupted 001 produces one named failure
from the recorded executed helper; the unchanged positive candidate remains exact.
The [integration record](../art/cartoon/walk-pilot/profile-walk-v1/production-integration-v1/verification.json)
has SHA256 `d34f5578feb002fd942c7e811223734754736ad8c3e8e7f48ed02351b20a4c54`.

Maintained authoring smoke passed inventory 3, history 1, pilot 2 and full
catalog 3 checks before regression. Inventory ran 11 cases with 2 explicit
Windows symlink-privilege skips; its hardlink and remaining 9 cases passed.
History passed 22 checks, pilot metadata 60, full catalog 63 and pack tools 20.
Both generated catalogs reproduce. They report 40 accepted and 2361 pending
slots out of 2401, with 51 supplied-original evidence slots. Historical original
pose facts remain unchanged. No maintained tools or tests changed.
The [authoring record](../art/cartoon/walk-pilot/profile-walk-v1/production-integration-v1/authoring/verification.json)
preserves all command results and logs with SHA256
`3789d82eb0b454d152498e7796e26d00bee8f4712afb9ca387e2f8f31c50265a`.

The full Windows gate passed on its first attempt: clean build, ordered smoke
then every regression suite, and all 2452 golden-resource files byte-identical.
All 32 retained renderer captures and required markers were complete. The run
used an inactive desktop, preserved protected inputs and kept the user's active
desktop unchanged. No new runtime or maintained test/tool source was changed.
The [Windows record](../art/cartoon/walk-pilot/profile-walk-v1/review-evidence/windows-v1.json)
has SHA256 `0f27ae3c395e809db37570d1ad2d7c61d89d6b94887174100d0a103600d3864b`.
Large capture and build artifacts remain in the ignored local verification tree.

The [independent integration audit](../art/cartoon/walk-pilot/profile-walk-v1/audit-production-integration-v1.json)
reproduced all eight recipes in fresh processes and checked all old payloads and
ledger rows, complete reviewed-private member equality, 102 protected inputs,
96 native evidence files and 65 integration bindings. Both catalogs reproduce.
It found no new actionable defect. Its SHA256 is
`79694fd2b591bd3b6f5df6c01ff1c3d65767d78a974791a5e3ba051beae7879e`.

PR14 merged tested feature head `3295acc1d8b4979b14891cbb2bac82b4dfd2c149` as
main `c903fb57ce5c4224dede16992288c70f47a7a3d7`; their complete trees match.
[Feature CI](https://github.com/bigfnj/johnny-castaway-rebornHD/actions/runs/35109871512)
passed all four platforms. The [post-merge audit](cartoon-profile-walk-post-merge-audit.md)
records fresh source review, local deployment and the remaining follow-ups.
