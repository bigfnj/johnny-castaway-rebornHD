# Original waiting pose 016

`016-original-native.png` preserves the supplied-original 32×74 RGBA pixels.
`016-original-nearest8.png` is 256×592: each native pixel becomes an exact 8×8
block. The [source record](source.json) binds both PNGs to the preserved original
XPM, decoded RGBA facts, RESOURCE identities and historical decoder identity.
The original resources were not reread and no original executable ran here.

Colors use the port dump's diagnostic palette, with index 0 transparent. This
does not establish original-executable color or compositing parity. The original
gray shadow is part of the image bounds and must not become a foot anchor.

016 is the front-facing waiting pose, heading 0/S. The chest and pelvis face
the viewer. Both elbows project outward and the forearms return inward to the
hands at the shorts/waist sides. The stationary legs are separated, with the
feet directed outward. Avoid copying 017's oblique torso or a walking stride.
Approved 017 can guide identity and expression, while original 016 supplies the
new pose geometry.

Preserve the source's small asymmetries rather than making a perfectly mirrored
stance. In the lower region y≥60, selected red/white/olive original pixels reach
y=71 on the screen-left half and y=68 on the screen-right half. That is a small
3-native-pixel difference, equivalent to 6 HD pixels. These colored extents
exclude gray shadow and black outline; they are not anatomical sole landmarks,
limb identity or a measured ground plane. The exact mask is recorded in JSON.

The first opaque cap row is y=0, spanning x=[15,20), with pixel-edge midpoint
17.5. At the application's 2× canvas scale the midpoint is x=35 and the canvas
is 64×148. Keep the common generated-art scale 0.1. A target [35,0.25] combines
this measured X feature with the previously adopted 0.25-HD-pixel filtering
margin; that Y margin is an authoring decision, not an original coordinate.

The retained compiled C trace records these same-spot turns at node A:

| Heading change | Draws and delays |
|---|---|
| 1 → 7 | 016 unflipped for 120ms, 017 unflipped for 120ms, then 017 unflipped for 1600ms |
| 7 → 1 | 016 unflipped for 120ms, then 017 mirrored for 1600ms |

016 draws at logical (299,243). Unflipped 017 uses (299,243); mirrored 017 uses
(293,243). Preserve those original placements and the repeated final 017 draw.
Do not add transition drawings or normalize poses to a shared visual bounding
box. These facts describe the port's traced state machine; they do not claim
original-executable timing calibration or approval of every story use.
