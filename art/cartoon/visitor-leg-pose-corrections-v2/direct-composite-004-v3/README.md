# SSUZY 004 inward belly curve

[New transparent candidate](004-composite-v3.png), awaiting review.

The user circled the skin protrusion beneath the forearm in v2 and asked for an inward-curved belly. This direct PNG edit trims that edge into a smooth curve and closes the small existing transparency gap at the forearm join. The current proportions and leg pose remain as in v2.

Only 6,062 pixels changed, all within source-canvas box `[410,650,642,768]`. Every pixel outside that box is identical to v2. The [record](record.json) preserves the output hash, request, previous candidate, and exact build script.

[Light detail](belly-detail-light.jpg) and [dark detail](belly-detail-dark.jpg) show the new join. [Previous candidate](../direct-composite-004-v2/004-composite-v2.png) remains available.

Run `publish_review.py` to update the existing reviews. For subsequent still-review rebuilds, pass this directory's `record.json` to the mermaid builder's `--direct-composite-004` argument. No production integration or native motion approval is recorded.
