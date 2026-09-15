# Original executable extraction reference

The local original installation confirms the compiled walking table and exposes a historical sound-extractor defect. This is a version-specific byte comparison, not a change to the runtime archive or a redistribution of the original executable.

The inspected `WINDOWS/SCRANTIC.EXE` is 295,952 bytes, SHA256 `7811b526b36bba2f08326d7a680f2f063190b4278e5a36393fde5a02080b0262`. The accompanying [machine-readable report](original-extractor-reference.json) records all fixed offsets, RIFF lengths, exact bundled-file matches and original RESOURCE hashes. Its source label is logical and contains no machine-specific absolute path.

## What was verified

The maintained `extract_walk_data` executable read exactly 489 six-byte records beginning at `0x188EA`, exited successfully and produced the same formatted rows as `src/data/walk_data.h`, including the final separator. The prior loop's effective count of 489 was correct for this executable. The final record begins at `0x1945A`; the required end position is `0x19460`.

Every one of the sound helper's 24 offsets points to a `RIFF`/`WAVE` header in this executable. There are 23 distinct offsets because `0x43400` occurs twice. At each offset, the complete corresponding bundled WAV, including its existing trailing bytes, matches an exact prefix of the original executable. The JSON records those matches; no sound file was replaced.

The helper's historical length rule reads the first unsigned little-endian 16-bit value and adds eight. For a RIFF header, the first bytes are `RI`, so this rule requests 18,778 bytes for every sound. The RIFF-declared length is instead represented by a 32-bit value at offset four plus eight. Declared RIFF lengths also differ from the complete bundled-file lengths, so changing that one read alone would not recreate the existing archive byte-for-byte.

The checked helper was run with its explicit `legacy-fixed-offsets` layout against this executable. It exited with one input-naming failure at `0x45A00`: the requested 18,778-byte span extends beyond the 295,952-byte file. Input preflight completed before any output was created; the output directory remained empty. This refusal is the intended checked-I/O behavior, not evidence that the original audio is absent.

| Legacy output number | Matching current archive sound |
|---|---|
| 1 through 10 | Same number |
| 11 | 14 |
| 12 | 12 |
| 13 | 17 |
| 14 | 24 |
| 15 and 16 | Same number |
| 17 | 0 |
| 18 through 24 | Same number |

The installed `RESOURCE.001` (1,175,645 bytes) and `RESOURCE.MAP` (1,461 bytes) differ from the current archive members. Their source hashes are recorded. This comparison establishes inequality only; it does not attribute the difference to a version, patch or resource transformation.

## Maintenance boundary and follow-up

The current maintenance change intentionally preserves the explicitly named legacy sound layout and its numbering. It adds checked input/output, explicit paths, preservation of existing outputs and failure cleanup. It does not silently reinterpret or remap original data. Walk extraction now has positive parity evidence for this particular executable; synthetic tests still do not establish parity for every original release.

An evidence-backed follow-up is a separately named original-resource sound extraction mode. It should verify the executable/resource layout, use the actual sound identifiers and bounded resource lengths, distinguish declared RIFF content from resource padding, and prove every result against the known original-to-archive matches. Keep the historical mode explicit if compatibility is retained. The current maintenance pass does not implement that mode.

The original executable and production ZIP were hash-checked after the reference run and remained unchanged. The ZIP SHA256 was `fb70d795531d50093dd4a9ac53895a6a20a76efc982d4d7d45a64403b98e68d8`. Actual extraction outputs and console logs remain in ignored local test storage; only the facts, hashes and mappings are recorded here.
