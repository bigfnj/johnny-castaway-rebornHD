# Tanker motion review: bar removed from 000–002

This review replaces only Cartoon TANKER 000, 001 and 002 with their raw generated v2 PNGs. The elevated red bar and its tall supporting posts were removed. The other angles retain the selections shown in `tanker-motion-v1`.

This is a targeted removal review, not a completed correction of the tanker's changing perspective. All tanker artwork remains pending human approval. The ship's other perspective and proportion concerns are still outstanding.

`build_review.py` reads the immutable prior `sprites.json`, replaces only the three Cartoon bindings, and records each replacement's SHA-256, canvas dimensions and alpha-at-least-8 bounds. It does not alter any PNG. The resulting `sprites.json` retains all original bindings and all other Cartoon bindings.

The page fetches `../tanker-motion-v1/source-sequence.json` directly. Its 76 draws, mirroring, positions, timing, fitting and viewing controls are unchanged. This is an isolated source-script replay at the port's nominal timing, not a capture of the original executable. Artwork is uniformly fitted to each original sprite's visible bounds for inspection; final runtime placement remains pending.

Use the 000, 001 and 002 buttons to inspect the edited drawings. The 006, 007 and 009 buttons remain available to compare the existing angles. Both panels share one sequence position and playback clock.

Review URL: http://127.0.0.1:8941/tanker-motion-v2/review.html

Lightweight preview check on 2026-09-17: all 28 PNG paths exist and exactly the three intended Cartoon bindings differ from v1. The browser loaded both panels, the 002 jump reached draw 26 at source position 154,176, and the screenshot showed the bar and tall posts absent. The 000 jump reached draw 24, mirrored at 156,175. Play switched to Pause and the review was left playing at half speed. No full smoke/regression or native-runtime test was run for this art-only iteration.
