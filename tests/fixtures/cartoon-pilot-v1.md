# Historical Cartoon pilot runtime fixture

`cartoon-pilot-v1.zip` holds 21 exact accepted runtime PNGs plus a `pack.json`
restricted to those same pilot slots. The pack rows are copied from the existing
production ledger, with its aggregate pointer set to the immutable pilot
acceptance. No PNG was rendered, converted or edited.

| Identity | Value |
|---|---|
| Acceptance | `art/cartoon/walk-pilot/calm-focus-runtime-v1/production-acceptance.json` |
| Acceptance SHA-256 | `ce7f3832982bcfbef13f9ce6dc06c1f60ce774b89aca088247442040fd767a0c` |
| Fixture ZIP SHA-256 | `f08e2ed4166397fe9b0b01b15cf7ce767620f362ca17852a62d7b269443cd2fc` |
| Size | 1,279,757 bytes; 22 members |

The real pilot metadata builder validates each PNG against the stored acceptance
and recipe. Original resources, HD proxies, raw image bundles and immutable
approval records still come from the repository; the fixture does not copy or
replace their authority. The ocean PNG accounts for most of this snapshot.

`tests/art_pilot_fixture.py` substitutes these historical bytes only during
historical test cases. Live catalog reproduction separately uses actual
production. A future-state control exposes a simulated accepted 028 replacement
and regenerated schema2 catalog, then runs all historical and replacement tests
against that state. No production file is written by this control.

Keep this snapshot immutable when promoting another drawing. It removes any
test dependency on old Git history, network access or a particular Pillow
version while allowing the current pack to evolve.
