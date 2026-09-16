# Standing018 contact comparison

The user approved the corrected skin colors, then asked to compare the opening
Front turn standing pose with the original because its smaller foot appears above
the water. This diagnostic contains no geometry edits and grants no new artwork
approval.

The three panels show original sprite and original island, original sprite on the
Cartoon island, and current Cartoon. Both original panels decode the supplied
`RESOURCE.MAP` and `RESOURCE.001` through the unchanged port. The port initializes
its diagnostic palette, so these panels establish placement and shape, not the
original executable's colors. This is not a DOSBox capture.

All panels show the first unmirrored018 draw at logical `(478,216)`, HD origin
`(956,432)`, at0ms. Full sprite canvas is64x154. Identical fixed crops are
`(940,425,95,175)` for the whole pose and `(954,548,66,40)` for the feet; nearest
pixel enlargement preserves the original silhouette. The isolation and Cartoon
images differ at zero pixels outside the018 canvas.

`prepare.py` creates private archives only. Both explicitly replace the two
resource members with the supplied files. The original-scene package removes all
2444 HD/Cartoon override PNGs and keeps the HD scale2 manifest. The isolation
package removes only the two018 override PNGs. All other retained payloads are
exact. The existing observer binary and C driver are reused by hash.

`capture.py` is a separate scoped parser, leaving previous parsers unchanged.
It checks the diagnostic load paths and requires actual API/path/draw/wait/display
transcripts to equal the bound current Front turn. Both package smokes pass before
their full and fresh-repeat routes,36 displays/3400ms each. `check_capture.py`
executes two altered-input controls. `check_review.py` runs browser smoke before
exact pixel crops, served-file identities and full-island expand/collapse checks.

The current page is `http://127.0.0.1:8932/cartoon-contact018-v1/review.html`.
Its four immutable served files, native reports/logs, source package hashes and
local/served browser results are retained in `evidence-v1`.

Replay needs the pinned skin-tone candidate-v2 ZIP, earlier unchanged native
observer and its build/source bindings, supplied original resources, host Pillow
and Playwright, and the pinned Linux image listed in evidence commands. Recreate
scratch inputs before `prepare.py`; commands intentionally refuse existing output
directories. Do not rerun `preserve.py` into the retained evidence or overwrite
the existing publication. Exact command order is in `evidence-v1/evidence.json`.

The separately attributed `source-audit-v1.json` retains the independent reviewer's
source-index audit and foot measurements. Excluding the original gray shadow,
the smaller original foot ends at doubled row143 versus Cartoon row131; the
larger-foot comparison is147 versus141. These are screen-space observations,
not anatomical left/right labels. The source audit also records why both private
packages use the supplied resource pair: bundled resources have minor contact
shadow differences. The frozen evidence predates this explanatory sidecar and
remains unchanged.
