# Shark identity corrections

The user identified the animal in the departure scenes as the established gray shark with razor teeth and a sneaky demeanor. The earlier dolphin interpretation is superseded. This pass covers 27 drawings, including partial bodies and exposed fins.

correction-plan.json freezes the previous drawing per frame and assigns the first correction version. selected-corrections.json selects later refinements where needed. The exact original governs anatomy and gesture; GJFFFOOD019 and SHARK025 supply established shark identity and tooth design. The other 45 drawings keep their current selections.

New requests and byte-exact built-in ImageGen outputs are stored as versioned siblings in mermaid-departures-and-dates-batch-v1/generation/. The focused HTML review compares the original, previous interpretation and new shark correction. Appearance approval remains pending.

Open the [27 shark corrections](http://127.0.0.1:8941/shark-identity-corrections-v1/review.html) or the [full 72-drawing batch](http://127.0.0.1:8941/mermaid-departures-and-dates-batch-v1/review.html). Each focused card shows the exact original, frozen previous drawing and current correction, with links to its prompt, image record and PNG.

SLEVEJM1 009 and the solo SLEVEJM2 gestures require a separate pectoral fin projecting from below the face. Interpreting that projection as a dolphin beak or extended shark jaw produces the wrong anatomy. The selected corrections separate the compact toothy face from the raised fin. Earlier jaw interpretations remain unselected history. Fin-only and submerged drawings keep the face hidden where the source does.

build_review.py rebuilds the focused page from the frozen plan plus selected-corrections.json. select_in_main_review.py applies those candidates through the main batch's shark-correction-overrides.json, then verifies that all other 45 selected image hashes and versions remain unchanged. check_review.py checks the served focused page, exact file records, immutable history, links, filters and actual transparency; it does not grant appearance approval or validate native motion.
