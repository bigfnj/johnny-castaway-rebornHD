# Cartoon arrival verification

The user approved standing JOHNWALK 018 with "nailed it, proceed" after viewing
the actual rear walk settle into it on the Cartoon island. The pack now has 28
approved assets: twelve walking poses, one standing pose and fifteen island
layers. The [acceptance](../art/cartoon/arrival-pilot-v1/production-acceptance.json)
records the exact review and inherits the previous 27 approvals.

## Package and scope

The production ZIP SHA256 is
`0748676eb6ab0685abecfeb0bbfb8547d2050e6419bb1cad5f13ccc9f716fedd`.
All 2,578 prior entries are unchanged. The only added member is
`data/styles/cartoon/BMP/JOHNWALK.BMP/018.png`, SHA256
`5ab7fb306a39eab69d419f3602101a72e3cca30d15e6432c58a6beaf975e9190`.
All 2,579 uncompressed members match the private reviewed candidate, whose
container SHA256 is
`bc47235fbb12ed5c2a080471a556e4e61e41e4e4c886de94fd02dd7591d6386d`.
The existing production builder changes ZIP layout but preserves member bytes.
The style manifest, original resources and all 27 previous ledger rows remain
unchanged. [Package evidence](../art/cartoon/arrival-pilot-v1/production-verification.json)
records this independent readback after package validation passed.

The displayed route uses the real `adsPlayWalk(1,3,0,3)` with Linux island seed
11 and path seed 2. Its 23 walking poses remain unchanged; standing 018 replaces
HD during the subsequent 1,600 ms hold. The native origin shift from (302,244)
to (298,240) remains visible through a fixed camera. User approval includes
the smaller foot's contact appearance. Its pixel-region depth differs from
the original reference; anatomical parity and unseen routes/story uses are
not established. The [arrival lessons](art-style-learnings-arrival.md) preserve
that distinction and the exact export dependency, Pillow 12.2.0.

## Verification before delivery

| Area | Evidence |
| --- | --- |
| Export | 3 smoke checks, then 20 regressions and 17 witnessed source mutants passed; the candidate recipe and raw artwork remained exact |
| Native Linux review | Baseline smoke preceded its 47-display regression; candidate smoke preceded its 47-display regression. All walking pixels stayed identical, with differences confined to the arrival canvas |
| Browser review | 2 smoke checks, then 4 grouped regressions covered all 47 times and 94 canvas hashes, stepping, repeat and both camera views; served HTML and PNG bytes matched |
| Review controls | 4 Python helper mutations, 2 served-browser mutations and 1 changed-walking-pixel replay mutation produced named failures with execution witnesses |
| Git byte preservation | Normal checkout smoke passed; removing the arrival attribute produced one named byte-preservation failure; outside text and PNG controls behaved as expected |
| Production package | 28 accepted PNGs passed validation before build; independent readback preserved all old members and equaled the reviewed candidate |
| Pilot metadata | 2 smoke checks, then 60 regressions and 56 executed source mutants passed; the new arrival-prefix removal caused one named failure |
| Full catalog | 3 smoke checks, then 63 regressions passed; both metadata reproduction checks passed on the frozen 28-asset inputs |
| Existing art tools | 20 regressions passed after package and metadata smoke |
| Windows native delivery | The complete unchanged rerun passed: 27 smoke, 27 screensaver, 31 style checks and all 2,452 golden hashes, with the remaining full-gate suites green |

Compact native evidence is [preserved here](../art/cartoon/arrival-pilot-v1/review-evidence/native-v1/README.md).
It pins the saved Linux observer, 59 source/build inputs and all reports. Full
capture sets and binaries stay in ignored local build folders. This evidence
does not claim a fresh engine rebuild or original-executable parity.

[Final metadata evidence](../art/cartoon/arrival-pilot-v1/review-evidence/metadata-v1/verification.json)
preserves command order and source identities. The pilot retains its original
21 assets. The full catalog reports 28 accepted and 2,373 pending slots;
its 51 supplied-original evidence slots remain unchanged. A separate
[integration audit](../art/cartoon/arrival-pilot-v1/review-evidence/integration-v1.json)
verified the complete approval chain and reproduced 018 under Pillow 12.2.0.

## Windows delivery and retained failure

The first full Windows gate passed smoke and the style suites, then failed a
palm capture-marker assertion. Its child exited 0, but stdout ended mid asset
log. This assertion checks the completion marker before opening the PPM; the
test then removed its temporary directory. The existence and content of that
first PPM are unknown. The exact gate output remains locally preserved.

With code and archive unchanged, a fresh inactive-desktop control passed palm
smoke before all eight palm cases. Explicit work directories retained its logs
and images. The subsequent full gate passed. This is an intermittent diagnostic
failure with an unresolved cause, not evidence of a missing image or a repaired
renderer. A backlog item now requests retaining these artifacts on failure.

[Windows evidence](../art/cartoon/arrival-pilot-v1/review-evidence/windows-v1.json)
records all three runs. The successful full-run log SHA256 is
`c08b0fa322fd8c932c8f22f08087053f56d1ffb1b21b52849187cda7dd060185`.
Its 278 desktop observations confirmed the input desktop remained unchanged;
runtime inputs and the deployed production archive stayed exact. Local full
logs remain under `build/windows-gates/arrival-promotion-v1/`,
`arrival-palm-control-v1/` and `arrival-promotion-v2/`.

The pre-commit Git-index audit verified all 55 then-staged arrival files against
their working bytes, including all 30 native evidence links and the complete
28-asset approval/archive chain. Delivery-only Windows evidence is added
separately after that audit.

Merge and post-merge audit results are recorded below when complete.
