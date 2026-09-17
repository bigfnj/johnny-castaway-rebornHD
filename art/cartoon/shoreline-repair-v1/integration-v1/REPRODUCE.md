# Shoreline and seasonal integration

The aggregate accepts 14 selected assets and inherits 33 unchanged rows. The final package has 47 Cartoon assets and 2,598 ZIP members. Ten shoreline payloads replace prior art; four seasonal members are added. The other 2,584 baseline payloads stay byte-identical, including every Johnny sprite, palm, ocean, cloud and fallback asset.

The package combines the approved clean-wave review with the separately approved inset banner. `runtime-recipe.json` identifies each selected PNG, raw source or old ZIP member, immutable authoring recipe/report and footprint. Ledger `source_sha256` continues to identify the HD proxy, not the generated raw image. The ten shore rows declare their registered footprints; seasonal rows use their normal original-size canvases.

## Fresh replay

Run from the repository with Python 3.11 and Pillow 12.3.0:

```powershell
& $env:TOOLBOX_PYTHON -B art/cartoon/shoreline-repair-v1/integration-v1/integrate.py --repo . --output build/shoreline-replay-fresh
```

Use a new output directory each time. The helper retrieves the old production archive from Git commit `1aad361fe78dde2c956e05dc451b8d5bab100af0`, verifies SHA256 `4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`, and preserves it in the output. That Git object must be available locally. An explicit `--baseline PATH` also accepts the exact recovered archive.

The frozen exporters are extracted with `git archive` from artifact commit `aafb1ca380f7c50e26347893c30b1ca2a8dc4628` into a separate scratch tree. Its original archive is installed there. `CMakeLists.txt` is included because the side exporter locates its root with that marker. The first setup attempt omitted it and was refused by the recipe contract; its failure logs remain in the evidence. No live archive is swapped during replay.

The banner is the source smoke. Ground, centers, side placement, cleaned007 and the other seasonal props follow. All 14 selected PNGs must reproduce exact bytes. The 33 inherited PNGs come from the pinned prior archive. The maintained `tools/art_pack.py validate` smoke precedes `build`, followed by a complete named-member comparison and a corrupt007 refusal, executed guard-removal witness and restored positive.

`reviewed-wave-members.json` records every member extracted from the exact approved private wave archive. Replay without that ignored ZIP uses this bound member map and explicitly prints its limitation. To independently read the private archive too, add:

```powershell
--wave-candidate build/shoreline-repair-v1/side-clean-selected-v2/candidate.zip
```

The actual integration run did supply the private ZIP. Its complete payload map plus approved inset-banner bytes matched the standard package. A separate fresh replay exercised the saved-map path. ZIP envelopes may differ between private and standard packaging; all named payloads must match. Both successful runs and their exact helper/inputs are preserved separately.

## Promotion and evidence

This helper never promotes. Root authorization and a separate final native composition check precede copying the verified candidate and integrated ledger to production. `production-acceptance.json` records human art approval; the packaging report alone does not establish native or exhaustive story parity.

`evidence/evidence.json` lists every copied evidence file by its integration-relative path and SHA256. Root must stage each listed path explicitly and verify its Git-index bytes, including ignored stdout/stderr files. Its `external_files_sha256` separately identifies the current helper, inputs, acceptance and ledger records. Large ZIPs, replay trees and duplicate PNGs stay in ignored scratch and are explicitly excluded. `native-final/` and `windows-final/` have separate owners and binders; this preservation step does not copy or freeze them.
