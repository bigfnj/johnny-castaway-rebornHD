# Cartoon low-tide delivery

The approved composition adds the exposed beach, detached rock and twelve
low-tide wave frames. Nine island ripple drawings reuse approved unmasked
sources; three rock-ring phases were generated in the same white-foam style.
The broad spacing between ripple families is retained after the user withdrew
that objection. No renderer or animation-code change was needed.

[PR18](https://github.com/bigfnj/johnny-castaway-rebornHD/pull/18) is merged into
main at024c994. Windows, Linux, macOS and Web CI passed before merge. The
[post-merge audit](cartoon-low-tide-post-merge-audit.md) records the subsequent
main-checkout review and deployment checks.

The [acceptance record](../art/cartoon/low-tide-v1/integration-v1/production-acceptance.json)
binds the static approval and the native motion viewer at port8937. Earlier
draft records retain their original pending status. This does not claim that
every selectable clip or original story was individually reviewed.

| Check | Evidence |
| --- | --- |
| Production scope | 61 accepted Cartoon PNGs: 28 Johnny, 29 island/environment and four seasonal assets. The 14 new slots are BACKGRND001/002 and030-041. Coverage remains partial. |
| Package smoke and regression | Maintained pack validation passed all61 assets, then a fresh standard build reproduced the exact reviewed ZIP. All2,598 previous payloads, including the manifest, are unchanged; the final archive has2,612 members. |
| Source reproduction | The static exporter passed first, then island and rock exporters reproduced all14 selected PNGs exactly in an isolated historical checkout. The old pinned archive never replaced live production. |
| Native scene evidence | The reviewed package passed16 smoke captures and16 fresh-process repeats across paired no-decoration, clover, shifted-night, raft1/5, high-tide and front/rear walking cases. Each side has616 displayed records before repeats. The high-tide control remains byte-identical. These are the retained pre-approval runs, bound to the exact promoted package and unchanged runtime. |
| Fresh Windows deployment | Clean build and the full maintained smoke-then-regression gate passed. All2,452 golden dump files matched. The executable's deployed archive equals production. The inactive-desktop launcher preserved the workstation's input desktop. Two symlink privilege fixtures were explicitly skipped. |
| Authoring and inventories | 16 smoke tests passed before189 executed regression tests. Two symlink fixtures were explicitly skipped. Both metadata generators and reproduction checks passed, as did character-inventory regeneration/check. The catalog records61 accepted and2,340 pending slots; Johnny classifications remain unchanged. |

Final archive SHA256:
`a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66`.

The [integration records](../art/cartoon/low-tide-v1/integration-v1/README.md)
include the selected hashes, aggregate approval, package validation and exact
source replay. The [Windows proof](../art/cartoon/low-tide-v1/integration-v1/windows-feature-v1/evidence.json)
retains compact logs and source/deployment identities. The preparation helper's
map-difference control is only a diagnostic on hash maps, not an executed
corrupt-ZIP refusal or guard-removal test.

The historical native-capture commands also pin the old production archive.
Reconstruct those captures from the pre-promotion source snapshot and recovered
static comparison package in isolated scratch. They are not live-main commands.
The saved motion review remains directly viewable without rebuilding captures.

The [reusable lessons](art-style-learnings-low-tide.md) preserve wave ancestry,
white007 selection, common family transforms, alpha-fringe measurements,
native timing and approval scope. Remaining work stays in [BACKLOG.md](../BACKLOG.md).
The later [cloud delivery](cartoon-clouds-verification.md) completes the ordinary
BACKGRND015-017 group. Night and alternate ocean states remain next, followed by
independent props and vehicle groups.
