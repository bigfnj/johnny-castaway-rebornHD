# Rejected first mask draft

The initial chromatic mask picked up a few cap-edge pixels. The discovery came
from a spatial check of the top10 rows, independent of the palette algorithm.
`findings.json` records actual coordinates, mask weights and before/after RGBA.
These are cap samples, not a complete inventory of cap leakage.

This draft was not shown for user approval or placed in production. The exact
first corrector, calibration and28-frame recipe remain here. To reproduce it,
copy the skin-tone bundle to an isolated checkout and put this corrector at that
copy's bundle root, then run it into a new scratch directory. Do not execute it
directly in this evidence folder: its relative input paths expect the bundle root.

The successor adds cap exclusions drawn from the original input sprites.
Independent protected-material landmarks remain a separate verification source.
