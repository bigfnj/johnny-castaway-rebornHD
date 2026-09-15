# Supplied-original image decoding comparison

The supplied original and bundled archives contain different decoded pixel
indices in the three resources used by the first art-metadata pilot. Executed
decoder comparisons support the supplied-original pixel planes for these
resources. They do not establish why the bundled artwork differs, or original
runtime rendering parity.

## Inputs and decoder provenance

The original `RESOURCE.MAP` and `RESOURCE.001` are the files identified in the
[original reference](original-reference.md). The bundled input is
`assets/scrantic_data.zip`, SHA-256
`fb70d795531d50093dd4a9ac53895a6a20a76efc982d4d7d45a64403b98e68d8`.
The original resource pair, executable and bundled ZIP retained their recorded
raw-byte hashes after the comparison. No original binary, extracted image or
replacement artwork is included with this note.

The native dump executable had SHA-256
`6ac61dc53dc926a311d89fcf2e27ff7cefbbac7f4c60e2491f69114230400865`.
Its decoder, resource reader and pixel packing sources are unchanged between
knowledge commit `98a817e71521ceccc445f6da6d36f36e41ff43b7` and integration commit
`9f0f03f978469003a9269cb62fdf271600395679`.

The separate JavaScript execution used Node.js `v24.16.0` and unmodified
[xesf/castaway](https://github.com/xesf/castaway/tree/dea9bde8f0421bce6697bd1d2efcc813803c79b8)
commit `dea9bde8f0421bce6697bd1d2efcc813803c79b8`. It imported the
[resource reader](https://github.com/xesf/castaway/blob/dea9bde8f0421bce6697bd1d2efcc813803c79b8/src/dgds/resource.mjs),
[BMP reader](https://github.com/xesf/castaway/blob/dea9bde8f0421bce6697bd1d2efcc813803c79b8/src/dgds/resources/bmp.mjs),
[SCR reader](https://github.com/xesf/castaway/blob/dea9bde8f0421bce6697bd1d2efcc813803c79b8/src/dgds/resources/scr.mjs)
and compression modules directly, without frontend dependencies. Static review
also checked the pinned
[dgds-viewer](https://github.com/xesf/dgds-viewer/tree/4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49) checkout
`4b98c8794fa9f6e000b6c4b2a1d4f7e623c88f49`; it was not another executed decoder.
The C and JavaScript LZW implementations are structurally similar, so their
agreement alone is limited evidence of algorithmic independence.

A distinct decoder also ran on all three original compressed streams: the
installed `7z.exe` command, which identifies itself as NanaZip 7.0, version
2609.1, using `NanaZip.Core.dll` version 26.03. That core library's SHA-256 was
`b256ab04e827c93c99553c69165bcb196d422e66177f491707c7044c5e587be9`.
Each invocation exited zero with empty stderr and produced the exact declared
packed bytes, equal to both the JavaScript result and repacked native indices.

## Executed comparison

All three original resources use compression method 2 (LZW); their bundled
counterparts use method 1 (RLE). Every selected stream decoded to its declared
length. All 79 images in each distribution agreed exactly between native and
JavaScript index planes, for 158 image comparisons. The original LZW streams
also agreed byte-for-byte with NanaZip's `.Z` decoder.

| Resource | Images per distribution | Packed bytes per distribution | Original/bundled equal images | Changed pixel indices |
| --- | ---: | ---: | ---: | ---: |
| `JOHNWALK.BMP` | 36 | 48,476 | 0 | 1,574 |
| `BACKGRND.BMP` | 42 | 92,656 | 0 | 806 |
| `OCEAN02.SCR` | 1 | 153,600 | 0 | 48 |

These are index comparisons before applying transparency, scaling or compositing.
Every corresponding canvas has equal dimensions. The selected resources include
all pilot frames: `JOHNWALK` 024 through 029, `BACKGRND` 000 and 003 through 015,
and `OCEAN02`.

`JOHNWALK.BMP.024` is 32 by 75 and differs at exactly 47 indices. Of those, 44
change to index 5; the remaining transitions are `5 -> F`, `7 -> 8` and `8 -> 7`,
once each. `BACKGRND.BMP.000` is 280 by 52 and differs at 9 indices;
`BACKGRND.BMP.013` is 24 by 145 and differs at 41. The 640 by 480 ocean differs
at 48 indices: `8 -> 9` three times, `B -> 9` once and `F -> B` 44 times.

Packed-byte SHA-256 values, with frames concatenated in resource order:

| Resource | Distribution | SHA-256 |
| --- | --- | --- |
| `JOHNWALK.BMP` | Original | `02685f6036438814ef61e71554883c538428878c61841f1035af14c051ff09f4` |
| `JOHNWALK.BMP` | Bundled | `ceecced2a49254a91da9a7b7cee5ed8eb1ad82c3d7f050c50b716662c16ac73f` |
| `BACKGRND.BMP` | Original | `7a4485d04b7105b144f0afaf9736abfc2139c1428f4b1a3265118e6ee59978de` |
| `BACKGRND.BMP` | Bundled | `904047d6c11f30a2c474fa89bb53152f3dae21286d2ed0f7847de23e466a8686` |
| `OCEAN02.SCR` | Original | `9657e21fdc3bc36e847031cd5f743c9e36adb42b0cb9fe9b59be6ba815fe82db` |
| `OCEAN02.SCR` | Bundled | `671f4672f39ed427519c9e1b0c5634aa1616ee55652fc2f01c43043650506d78` |

## Repeating the method

Keep original files read-only and place all extracted data in disposable local
storage. Use `loadResources(mapArrayBuffer, volumeArrayBuffer).resources[0]`
and `getEntry(name)` from the pinned JavaScript reader. Convert Node buffers to
exact ArrayBuffer slices using their byte offsets and lengths. Pass entries to
`loadBMPResourceEntry` or `loadSCRResourceEntry`, and compare each image's
`buffer` indices against its native XPM pixel rows.

For these BMP entries, the image count is the little-endian uint16 at offset 16;
the `BIN` chunk starts at `18 + 4 * count`, following all widths then all heights.
For the selected SCR entry, `BIN` starts at offset 20, after its `DIM` chunk.
With `b` the `BIN` start, its uint32 size is at `b + 4`, compression method at
`b + 8`, and declared uint32 output size at `b + 9`. The compressed byte span is
`[b + 13, b + 8 + chunkSize)`, so its length is `chunkSize - 5`. Decode that span
with the pinned `decompress` function, require exact declared length and require
every result to be an integer byte. The pinned LZW reader can return a prefix
after catching an error; a returned value alone is insufficient evidence.

For the separate `.Z` check, prefix the unchanged original compressed span with
`1F 9D 8C`. This header selects block mode and a 12-bit maximum dictionary width,
matching these streams' clear code 256 and 9-to-12-bit code growth. It does not
prove that every DGDS encoder variant or malformed stream is `.Z` compatible.
Capture binary stdout directly, for example:

```python
wrapped.write_bytes(bytes.fromhex("1f9d8c") + compressed_bytes)
result = subprocess.run(["7z.exe", "x", "-so", str(wrapped)], capture_output=True)
assert result.returncode == 0 and result.stderr == b""
assert len(result.stdout) == declared_bytes
assert result.stdout == javascript_packed == native_repacked
```

For both formats, unpack sequential bytes high nibble first, then low nibble,
in row order; BMP images are concatenated. There is no planar rearrangement.
Repack each pair of native indices as `(first << 4) | second`. All selected
widths are even, avoiding the C reader's unsupported odd-width BMP case. The
RLE implementations use the high bit to select repetition of `control & 127`
bytes; otherwise the control byte is the literal count. Neither count adds one.

## Limits and consequences

A broader native-only comparison found 2,401 common XPM images with equal
dimensions and dump palettes, of which 61 had identical index planes. That is
separate from the independently executed 79-image scope above. Dump palette
equality also does not prove the original executable selected the same palette.

For these selected resources, agreement at the packed-byte stage across decoder
executions rules out the native nibble assembly as the cause of the observed
differences. The supplied-original decoded pixels are supported as distinct
reference data; bundled and HD proxy pixels must retain separate provenance.
The archive's editing or conversion history remains unknown. No original-engine
palette, transparency, occlusion, scaling, animation timing or complete scene
parity is established by this comparison.
