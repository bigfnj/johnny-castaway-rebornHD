# 004 direct PNG composite

The user selected the existing head/upper body/hands/bottle from 004 v3 and the hips and both legs from approved 003 v2, then explicitly authorized direct compositing.

[Final PNG](004-composite-v1.png) · [Record and source hashes](record.json) · [Authorization](../feedback-004-direct-composite-v1.json)

ImageMagick combines the source pixels at native scale. The lower source is translated (-120,+68), with no rotation, scaling, redrawing or deformation. Transparent masks place the waist join behind the foreground arm. The masks trim only the former waist and donor forearm fringe, retaining the original bracelet curve. The source PNGs are unchanged.

`build-composite.ps1` ran successfully under Windows PowerShell 5.1. `record-composite.py` reads the saved images and verifies the retained source regions, alpha bounds and transparent margins. It does not edit images. Across 445,762 visible pixels in the checked head/body and hip/leg regions, no RGBA values changed.

A one-pixel registration mutation was rejected by the pixel comparison, naming `004-composite-v1.png` and the donor hip/leg region. The actual PNG and final record remained unchanged. See [mutation result](verification-mutation.json).

The composite awaits user appearance approval. Native registration, motion review and production integration are not part of this appearance edit.
