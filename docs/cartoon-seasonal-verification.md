# Cartoon seasonal and shoreline delivery

The selected delivery combines the approved two-inlet island, offshore ripples,
complete repositioned side waves, clean white center wave 007, and four seasonal
decorations. The pumpkin retains its red eyes, sharp grin and slight rot. The
inset New Year banner meets the existing palm fronds; the palm drawing is unchanged.

PR 17 is merged into main. The [fresh-main audit](cartoon-seasonal-post-merge-audit.md)
records the post-merge Windows gate, all four CI jobs, package readback and
parallel core, platform and authoring reviews.

The final user decision was "Looks good, proceed" after the combined wave motion
review. The [selection record](../art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/selection.json)
preserves the exact viewer, native evidence and approved wave package identities.
That comparison deliberately retained the older banner. Production additionally
uses the separately [approved inset banner](../art/cartoon/seasonal-v1/banner-inset-v1/selection.json).

## Package and renderer contract

The package contains 47 accepted assets: 28 Johnny drawings, 15 island/environment
assets and four seasonal decorations. Ten existing shoreline PNGs are replaced,
four holiday PNGs are added, and 33 accepted assets retain their previous bytes
and approvals. Original resources and HD proxies remain unchanged.

The enlarged ground and nine wave sprites use four exact
[registered canvas contracts](cartoon-footprint-contract.md). Drawing, mirrored
drawing, atop drawing and wave-background restoration honor their offsets while
retaining the original logical coordinates. Other Cartoon slots and HD/original
rendering retain their existing dimensions and anchors. The matching engine and
data archive must be deployed together; an older engine rejects the larger PNGs.

## Verification record

The [reproduction guide](../art/cartoon/shoreline-repair-v1/integration-v1/REPRODUCE.md)
describes a fresh build from recorded sources. All 14 selected PNGs reproduced
exact bytes; standard pack validation passed before packaging and full-member
checks. The final archive is SHA256
`4d8e573b79b7f0dffdd0fefda6f2fa0833534a1649aa1ff0d2d3bf4724a398c6`.
It contains 2,598 members: 10 replacements, four additions, 2,584 unchanged
baseline members and no removals. All 28 accepted Johnny drawings are unchanged.

Both the real private preview ZIP plus inset banner and a fresh replay using its
saved member map matched the complete final package. A deliberately damaged 007
member was refused with one named failure. Removing the actual guard accepted
that damage; the restored helper accepted the untouched final package. The
[package evidence](../art/cartoon/shoreline-repair-v1/integration-v1/evidence/evidence.json)
retains both successful runs, the source replay and the initial scratch setup
failure, which was corrected without changing artwork.

The final native composition passed 28 smoke captures before 28 exact
fresh-process repeats: 14 paired scenarios and 522 displays per side. These
cover high/low tides, all four decorations, night and shifted scenes, and both
accepted Johnny arrival contacts. Eight named native controls fired and the
restored positive passed. The application observer was freshly compiled against
the selected runtime; its task container exited and all protected inputs stayed
unchanged. This does not establish exhaustive original-executable story parity.

The [native evidence](../art/cartoon/shoreline-repair-v1/integration-v1/native-final/evidence-v1/evidence.json)
binds 199 retained files, including three representative final scene PNGs.
Bulk frame captures remain scratch data with their identities recorded.

The full [Windows gate](../art/cartoon/shoreline-repair-v1/integration-v1/windows-final/feature-v1/result.json)
passed on an inactive desktop. Every smoke stage preceded regression, including
screensaver behavior, art loading/drawing, waves, palms, resource decoding,
lifecycle, frame limits, platform constructors and offline tools. The dump
regression matched all 2,452 golden files. Source inputs were unchanged and the
archive deployed beside the executable matched the final package exactly.
The original input desktop stayed active throughout the run.

The [authoring verification](../art/cartoon/shoreline-repair-v1/authoring-verification-v1/verification.json)
passed 16 smoke tests, then 189 executed regression tests, both generators and
both catalog reproduction checks. Two existing Windows symlink tests were
explicitly skipped for WinError 1314; hardlink and path-preservation tests ran.
Two new history controls failed under executed source-guard removal and passed
with restored sources. The catalog reports 47 accepted and 2,354 pending slots.

The extra CI character-inventory check caught stale generated metadata after
promotion. Regeneration changed only 19 fields: the archive pin, ten shoreline
acceptance links and four holiday acceptance/status pairs. Character counts,
original identities, classifications and historical evidence stayed unchanged.
Existing smoke, regression, nine negative controls and the final CI `--check`
passed. The [refresh record](../art/cartoon/shoreline-repair-v1/character-inventory-refresh-v1/evidence.json)
retains the initial stale-check failure and a reversible exact prior-inventory delta.

Promotion used the recorded V2 transaction. Review found that a report-write
failure in the initial helper could occur outside rollback. Disposable failures
before and after report writing now restore both changed production files;
removing rollback causes a named failure. V1 and its proof remain historical.
See the [promotion guide](../art/cartoon/shoreline-repair-v1/integration-v1/PROMOTION.md).

The [index check](../art/cartoon/shoreline-repair-v1/integration-v1/index-final/README.md)
verifies declared copied evidence and final production bytes in Git's index.
Disposable missing-file and changed-byte controls each produce exactly one
failure naming the altered record; the real index remains unchanged.

## Scope and next work

Cartoon remains a partial preview. Low-tide beach and wave assets, clouds and
night scenery still use fallback artwork. The native comparisons distinguish
those existing gaps from changes caused by this delivery. Review lower beach,
rocks and low-tide waves as a complete scene group before placing more ground
props. Independent objects and vehicle groups can follow, with Johnny-containing
composites kept in their character/story groups.

The [shoreline lessons](art-style-learnings-shoreline.md) preserve source-first
placement, full-size prop contact, recovery of unmasked wave strokes, per-phase
color checks and approval provenance for the next art pack.
