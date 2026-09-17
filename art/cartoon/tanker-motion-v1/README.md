# Tanker motion review

The user requested animation to inspect the long crosswise structure in000-002 and the yaw of006/007 relative to009. The [browser comparison](http://127.0.0.1:8941/tanker-motion-v1/review.html) replays all76 tanker draws from GJVIS6 tag9, preserving frame repetitions, coordinates and horizontal flips. It starts at half speed and offers centered and path views, pause, single-step, a timeline, and direct frame selection.

This is an isolated layer replay from the decoded source commands, not an original-executable or native-port capture. Timing uses the port's nominal4-tick/80ms delay per draw:6.08seconds at Normal speed. The normal ADS call executes one pass. The review's optional repeat control repeats that pass for inspection. [Source notes](source-notes.md) and [complete command context](context.json) retain the source identities and control-flow evidence.

The left panel uses exact original PNGs. The right uses the current selected Cartoon raw files, unchanged. `sprites.json` binds all28 image files and their alpha>=8 bounds. Canvas drawing applies uniform scale only, centers meaningful art horizontally inside the original visible rectangle, and aligns its bottom with the original bottom. This exposes current silhouette/proportion differences without warping the drawing. It is a provisional comparison fit, not a production export or accepted registration.

Centered view displays each original canvas at8x, with a common bottom baseline. Path view uses the original x/y coordinates with one fixed2.1x camera: `(x+60,y-115)`. This close-up includes the entry/exit sprites beyond the original screen boundary so their orientation remains visible. It is not a complete scene background or a reproduction of scene clipping.

Initial inspection shows the Cartoon end-on views are proportionally too shallow, and006 reads more as a flat profile than the original. The specific physical meaning of the original crosswise structure remains a visual interpretation, not a documented ship-part identification. Human motion review is pending. Do not redraw or accept the tanker based solely on this preview's construction.

The user separately approved the other19 ship-batch drawings with "the rest look fine btw." Their scoped acceptance is retained in `../ships-batch-v1/acceptance/appearance-nontanker-v1.json`. All14 tanker drawings remain pending. No PNG, production archive or engine code changed for this review.
