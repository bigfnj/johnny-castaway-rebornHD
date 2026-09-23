# Gesture and fin pass audit

Status: pass. Audited 2026-09-21T20:21:39.289480+00:00.

The rebuilt gallery has 103 entries: 56 revised, 43 retained, 1 later revision blocked and 3 blocked. All 22 SBREAKUP entries select the previous drawing pinned by earlier-inventory.json. None of the 13 newer happy SBREAKUP candidates is selected.

Selected updates match the requested versions: SMGIFT013/018/020/021 v2, SMGIFT022 v3, SMGLIMSE012/013 v2, and SMGFTWAV003/007 v2. SMGIFT014 has no revised image, with expression v1 retained in the previous panel and the blocked v2 request linked. SMGLIMSE014 remains blocked with no revised image.

All 56 selected mermaid records have matching raw PNG copies, correct request/reference/output bindings, RGBA transparency and inset alpha>=8 content. All 691 unique checked pins match; all 645 local file links resolve. The HTML embeds the same review data and has the expected 257 mermaid image canvases.

Defects: None.

SSUZY viewer/cleanup is excluded; its two blocked rows are counted only for the 103-entry total. Browser rendering, HTTP availability, native motion and production integration were not tested. No art or gallery files changed, and the earlier qa-audit files remain historical.
