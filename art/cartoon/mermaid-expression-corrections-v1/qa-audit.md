# Final artifact audit

Status: pass_with_documented_limitations. Audited 2026-09-21T19:45:17.025354+00:00.

66 revised mermaid candidates are accounted for: 38 SMGIFT, 15 SMGLIMSE and 13 earlier SBREAKUP. The 30 retained entries and 5 mermaid no-image outcomes account for all 101 expected mermaid entries. The two SSUZY cleanup attempts are separately recorded as no image returned.

67 PNG variants have matching output records, raw tool byte copies and image statistics. All 299 checked SHA-256 pins match. All 74 attempts have exact saved prompt/reference wrappers and exactly one saved image record or error record. No expected frame is missing.

All 66 preferred candidates are RGBA, contain transparent pixels, and keep alpha>=8 content strictly inside the canvas. SBREAKUP006 v1 remains as a superseded edge-halo variant; v2 is selected. SBREAKUP006 v2 and SMGIFT004 v1 have alpha range 0-254, preserved unchanged.

SMGLIMSE012, 013 and014 have individual moderation errors. SBREAKUP007 and008 have no saved returned image after a concurrent-group error; the blocked individual request is unknown. SSUZY004 and005 have captured output-stage moderation errors. These known outcomes are not counted as missing records.

Preferred versions: v1 throughout the revised candidates except SBREAKUP006 v2. The gallery selector was absent at audit start, so this is a saved-artifact inventory audit rather than a gallery selection check. Native motion and production integration were not checked. The captured request files cannot independently prove the network payload.

Deviations: None.
