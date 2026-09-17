# Merged low-tide authoring and package review

Reviewed primary checkout `024c9943a08ede16cfa24ed37aa768cf1f020b63` against its first parent `da787d63279ea91bd6c637e02133821339470bfc`. No maintained tools, tests, runtime or build-flow files changed in this merge. The unrelated untracked `-e` file was neither read nor modified. Only this report and `package-readback.json` are new delivery artifacts from this review.

Freshly executed on merged main, all exit 0:

```text
python -B tools/art_review_metadata.py --check
python -B tools/art_production_catalog.py --check
python -B art/cartoon/character-inventory-v1/build_inventory.py --check
```

No regeneration was needed. The production catalog has 61 accepted and 2,340 pending slots out of 2,401. The historical pilot remains 21 assets with its earlier facts intact. Johnny inventory counts remain 1,002 outstanding, 28 accepted and 84 uncertain; the fourteen newly accepted low-tide assets are scenery.

## Package and committed evidence

The current archive is exactly `a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66`, matching the human-reviewed package and aggregate approval. Its 2,612 unique members add only BACKGRND001/002/030-041. All 2,598 prior payloads, including the runtime manifest, are unchanged. The 47 inherited ledger rows and pilot replacement history are unchanged. Every new runtime PNG and HD-proxy source hash matches its recipe. Normal low-tide canvases need no new footprint declaration.

Fresh readback checked 325 unique bound paths against both actual merged Git blobs and checkout bytes. All 245 copied evidence files are present and byte-exact: 64 static-native, 118 wave-native, 41 feature-Windows and 22 authoring copies. This is a new committed-main readback, not the earlier feature-index result.

Four differences outside those frozen copies are ordinary text checkout conversions. The two maintained tools `art_common.py` and `art_pack.py` have CRLF historical source-snapshot fingerprints and LF Git blobs. The generated production catalog JSON/Markdown have LF recorded/Git bytes and CRLF working copies. Each pair is identical after CRLF-to-LF normalization under `text:auto` and `core.autocrlf=true`. The JSON records both raw digests and the resolved text basis; it does not label these raw bytes identical. There are no missing committed artifacts or unresolved digest differences.

## Inspected behavior and limits

The package validator checks source identity, PNG bytes, alpha and canvas before packaging. The catalog resolves explicit approval inheritance and the newly accepted complement, while pilot metadata retains its original scope. Build wiring still refreshes the archive through the executable's `jc_runtime_data` dependency (`cmake/RuntimeData.cmake:11-17`); CMake's Web preload dependency and `tools/build_web.py::verify_artifacts` still bind the Web data payload to the source ZIP. This pass reviewed those unchanged paths; it did not repeat the platform builds.

The new static, reuse and rock exporters retain the recorded common transforms, premultiplied filter and scoped alpha visibility operations. The accepted static fringe losses and phase040's five pixels of maximum alpha3 remain explicit. `integration-v1/replay.py` reconstructs its pinned source snapshot and older archive in isolated scratch, checks snapshot membership, and compares all fourteen output hashes. Its preserved replay result and forty input identities were read back here; that exporter replay was not rerun.

`integration-v1/prepare.py:99-124` writes aggregate records beside itself. Its documented reproduction therefore belongs in an isolated checkout. Its `member_negative_control` at line148 is an in-memory map diagnostic, not an executed damaged-ZIP refusal or source-guard-removal result. Current documentation states that limit accurately.

One current replay note is useful: the frozen `waves-native-v1/README.md` command describes the pre-promotion authoring environment. `capture.py:17,43` requires the earlier `4d8e573b...` live archive, so it cannot run directly against promoted main. Native reconstruction also needs the historical source snapshot and recovered static candidate. Preserve the frozen helper; clarify this in current delivery guidance or the existing shared-replay backlog item. This affects offline evidence reconstruction, not the deployed runtime.

No substantive new package, approval, catalog or build-flow defect was found in this bounded review. Fresh execution was limited to the three check commands above. Earlier smoke/regression, native, Windows and source-replay results were verified as preserved evidence, not rerun or presented as new results. Original external resources, original-executable colors and scene coverage were not revalidated.
