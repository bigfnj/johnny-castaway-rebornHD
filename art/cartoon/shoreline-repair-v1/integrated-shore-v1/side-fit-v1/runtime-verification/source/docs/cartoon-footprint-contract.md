# Registered Cartoon island footprints

The runtime has four fixed, optional footprint contracts. They add transparent
canvas room without changing RESOURCE dimensions, script coordinates, scene
timing, walking routes, global scale, Original rendering or HD selection.
Supporting a footprint does not approve artwork or establish visual parity.

| Contract | Cartoon slots | Original logical canvas | Legacy PNG | Registered PNG | HD offset | Mirrored HD offset |
|---|---|---|---|---|---|---|
| `cartoon-island-ground-v1` | `BMP/BACKGRND.BMP/000.png` | 280×52 | 560×104 | 640×180 | −36, −10 | −44, −10 |
| `cartoon-island-center-foam-v1` | `BMP/BACKGRND.BMP/006.png` through 008 | 160×25 | 320×50 | 384×256 | −32, −90 | −32, −90 |
| `cartoon-island-left-foam-v1` | `BMP/BACKGRND.BMP/003.png` through 005 | 72×29 | 144×58 | 150×66 | −6, 0 | 0, 0 |
| `cartoon-island-right-foam-v1` | `BMP/BACKGRND.BMP/009.png` through 011 | 72×32 | 144×64 | 154×74 | 0, 0 | −10, 0 |

The authoring ledger row and its referenced recipe row must both declare the
same `footprint` object. For the ground:

```json
"footprint": {
  "id": "cartoon-island-ground-v1",
  "canvas": [640, 180],
  "offset_hd": [-36, -10]
}
```

The center uses its named ID with `canvas: [384,256]` and
`offset_hd: [-32,-90]`. Without a declaration, authoring validation requires the
legacy canvas. Unknown IDs, other slots, incorrect original sizes, freeform
dimensions and different offsets are rejected. PNG format, alpha and approval
hash checks remain unchanged. The runtime manifest retains its existing four
fields; runtime recognizes each built-in contract by the exact slot, original
dimensions and loaded Cartoon PNG size. Old executables reject the larger PNGs,
so deliver the matching engine and art archive together.

At the usual logical base-island draw at 288,279, the ground occupies the HD canvas
540,548 through 1180,728. Center waves retain their logical draw at 364,319; their
registered canvas is 696,548 through 1080,804. These are canvas bounds, not claims
that every pixel is visible. A scene offset is applied before the asset's HD
offset. Mirrored X placement uses
`original_width*scale - registered_width - normal_offset_x`, retaining the old
logical anchor. Normal, mirrored and atop drawing use the same placement helper.

Left waves keep logical origin 270,306, with registered HD canvas 534,612 through
684,678. Right waves keep logical origin 518,303, with registered HD canvas
1036,606 through 1190,680. The side-fit comparison places the unchanged-size
left source at pixel 0,8 inside its padded canvas and the right source at 10,10.
Those source placements are authoring choices; the engine only recognizes the
named canvas and offset. Center waves and the ground keep their existing contracts.

HD fallback remains validated against original×scale when Cartoon is selected.
It never acquires a registered offset. Original decoding still consumes exactly
the bytes described by the original RESOURCE header. Source inventories and
historical approvals remain unchanged. Current catalogs report a declared
footprint separately from original and historical canvases.

The static ground is drawn once before the clean wave background is saved.
Wave bounds account for each actual loaded surface and its asset offset. Each
update restores that background, then draws the active wave families in their
existing update order. Foam may wash over sand and recede; the engine does not
apply a ground mask. Exported foam design and human motion approval are separate.
Low-tide shoreline assets still use their original contracts, so review both
tides, scene offsets, nighttime and character/prop contact before promotion.

## Verification

The existing pack, pilot-history and production-catalog suites exercise
declarations, PNG dimensions and immutable original facts. The compiled headless
probe exercises the real loader and normal/flip/atop draw paths, registered
dirty bounds, fallback and ground restoration. Its synthetic archive/decoder
supplies dimensions; actual PNG decoding and native scene captures remain
separate checks.

```text
python3 -B tests/test_art_footprint.py --output build/footprint-smoke --phase smoke
python3 -B tests/test_art_footprint.py --output build/footprint-regression --phase regression
python3 -B tests/test_art_footprint.py --output build/footprint-mutations --phase regression --mutations
```

The probe requires a GNU-compatible `cc` toolchain and section garbage
collection. Linux CI runs smoke before regression through `tests/unix-build.sh`.
Mutations compile copied sources into fresh binaries, verify timestamp and
execution witnesses, and rerun the unchanged positive controls. They never edit
the working engine or launch a window.
