# Native low-tide wave review

Serve this folder and open `review.html`. The right panel uses nine re-registered approved island ripples and three new rock-ring phases. The left panel is explicitly the old low-tide fallback on the same approved low beach/rock. It is not the accepted high-tide Cartoon wave set.

Two native clips are included: no decoration and St Patrick's clovers. Each runs3840 requested milliseconds, covering two1920ms low-wave phase recurrences. Normal and Slow playback, pause, previous/next changed image, replay, time scrubbing, full/close-up view and hiding the comparison are available. The whole captured clip repeats; this does not claim the moving cloud loops seamlessly.

`manifest.json` binds the exact native capture reports and89 lossless WEBP images. Each of100 retained native images is reconstructed from its scene base and two rectangular pixel patches. Sky patches retain the moving cloud; wave patches retain the actual renderer output. The builder compared every reconstructed full1280x960 RGB image to the corresponding native capture. No illustration, interpolation, color conversion beyond the capture's RGB representation, or generated animation is substituted for native frames.

All81 displayed records per native case remain in the copied reports. Browser timelines retain the last actual display at each shared timestamp and omit consecutive identical images, preserving their native times. `checks.json` records exact image/report readback, all100 reconstructions, native timing comparison and four in-memory controls: wrong time, shifted patch, wrong PNG hash and wrong encoded pixels. Restored positives pass. `check_review.py` reruns those bounded checks from the repository root.

Browser smoke showed loaded images and normal playback after the disabled loading state. Subsequent UI checks exercised pause and next/previous change, clover selection, full scene, slow speed, hiding the comparison, scrubbing to1920ms, and replay. Final review was left on clovers, close-up, comparison hidden, Normal speed. This confirms the controls and visible artwork, not human acceptance of motion.

The candidate ZIP is `a89874307d77d805ab41ef55ba87e45e98ce6e9e589e1bea0d081629e5745d66`; its fresh repeat and pack report reproduced byte-for-byte. It adds only the14 low-tide members and preserves all2598 existing production payloads. Static001/002 appearance is already approved. New placement of reused030-038 and new ring039-041 remain pending human review. No production promotion has occurred.

The native smoke/repeat evidence and extended night/raft/high-tide/walking checks are recorded under `../waves-native-v1/`. Those tests measure the explicit selected scenes and preserve the existing story/character behavior; they do not establish exhaustive original-program parity.
