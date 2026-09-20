# Five motion-blur refinements

GJVIS3.BMP 007-009 receive blurred spinning blades; 010/011 receive blur on the small lower rotor while preserving the large top rotor. The user approved all five selected v1 drawings on 2026-09-20 with "approved, lets continue". [Exact acceptance](acceptance/appearance-v1.json) binds the reviewed versions. Other drawings receive no implied approval.

The focused gallery has original, previous correction, and blurred motion columns, grouped into propellers and rotors. Search accepts resource/frame text; Clear and group links reset it. Light/dark checkerboards expose the existing transparency. The established canvas code fits alpha8 bounds uniformly for display, without modifying raw pixels. Each decoded canvas is marked loaded, and all 15 panels must load before the page reads 5 of 5 comparisons ready.

Once the root-owned selected-versions.json and generation records are complete, run toolbox Python with `-B art/cartoon/propeller-motion-blur-v3/build_review.py` from the repository root. It writes review.html, review-data.json and review-record.json. Serve art/cartoon or a containing directory so the original and previous correction URLs resolve. The record binds each selected output, request, references, previous records and feedback alongside the page identities.

The previous 24-correction gallery remains unchanged. Native fitting, animation and production integration remain deferred.
