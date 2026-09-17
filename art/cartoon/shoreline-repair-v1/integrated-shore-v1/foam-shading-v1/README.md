# Center wave shading revision

The user noticed a dark shadow appearing during one frame of the selected
offshore animation. The selected raw 007-v2 contains 123,597 pixels with alpha
at least 8 and all RGB channels below 100. Adjacent phases 006 and 008 have
none. This is actual visible shading, not only hidden RGB beneath transparency.

The built-in image generator edited that frame using 006 as a palette reference.
The new raw contains no pixels meeting the same dark-color test. The exact
prompt, ordered inputs and output hash are preserved in generation-v1.json.
The source remains untouched after generation. The prompt requests the same
stroke geometry, but visual comparison must establish the actual result.

The technical export uses the existing full-source quarter-scale registration,
384 by 256 canvas and ground visibility mask. No hand repaint or alpha cutoff
is applied. This one center correction is combined with the six repositioned
side-wave drawings for a native before/after motion review.

The user approved the white foam appearance in the displayed still comparison;
`appearance-approval.json` binds that approval to the exact screenshot and PNG.
The approved island shape and other center phases remain unchanged. Production
promotion still requires review of the combined repositioned animation.
