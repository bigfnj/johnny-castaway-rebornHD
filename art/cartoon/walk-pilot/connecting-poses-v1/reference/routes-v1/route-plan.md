# Connecting poses009/010/012: native review plan

Read-only source investigation on branch `art/cartoon-connecting-poses`, based
on main `3af0242`. Exact commit and source fingerprints are in
`route-analysis.json`. No native capture, historical helper, asset edit or
production change was run. The small source interpreter in `analyze.py`
matched all116 preserved actual-C draw/delay cases from the arrival trace.
Its proposed new clips still need the usual independently compiled C observer
and actual display/timestamp capture before any visual result is claimed.

## What these assets do

| Asset | Table use | Relationship to approved poses |
|---|---|---|
|009|Ordinary turn heading1/SW with flip1, heading7/SE with flip0 at every A-F spot; also four travel rows across three routes|Arms-free counterpart to waiting017. Links front-oblique and profile motion|
|010|Ordinary turn heading0/S, flip0 at every spot; no travel row|Arms-free counterpart to waiting016; lies between the two orientations of009|
|012|Ordinary turn heading4/N, flip0 at every spot; no travel row|Arms-free counterpart to waiting015; lies between ordinary023 and its mirror|

The complete ordinary ring is `010,009m,003m,023,012,023m,003,009` for
headings0-7. The waiting ring instead uses `016,017m,000m,018,015,018m,000,017`.
Here `m` denotes the existing full-canvas horizontal flip, not anatomical
left/right. Same-spot `adsPlayWalk` calls use the waiting ring and therefore
cannot validate these three new assets. Ordinary poses appear during departure
or an intermediate waypoint, before the final hands-in-pockets arrival.

The ordinary turn tables begin at source lines104/A,158/B,273/C,327/D,
418/E and484/F in `src/data/walk_data.h`. JSON includes every target row and
origin. The renderer uses `(stored_x-1, stored_y)` then island offset and scale2.
Mirror the full original-derived canvas around `(width-1)/2`; never center a
pose using its visible-alpha bounds. `currentHdg` during travel is engine
state, not a reliable per-frame facing label; the actual frame and flip govern
the drawing.

## Smallest focused native checkpoint

The first two clips are the smallest useful pair covering all three poses,
including both orientations of009 and accepted neighbors. Add CB and EC to
cover009's distinct travel entry/exit and front-to-profile connector roles.
All four clips use only already approved neighboring walk/wait assets.

Every row requires its own real same-heading priming call and
`srand(2)` immediately before both the prime and travel calls. Names below
use A=0 through F=5, headings as above. `adsPlayWalk` takes the four listed
arguments. Durations include the real120ms prime, all ordinary/travel poses
at120ms each, and the actual1600ms final arrival. They are source-derived
budgets, not newly captured display counts.

|Purpose|Prime|Travel|Assert selected path|Critical sequence|Total|
|---|---|---|---|---|---|
|Front ordinary arc, decreasing headings|`(3,3,3,3)`|`(3,3,2,7)`|DC|approved018,003m,009m,010,009, then DC028m onward, approved017|3400ms|
|Rear ordinary arc, decreasing headings|`(3,6,3,6)`|`(3,6,4,2)`|DE|approved000,023m,012,023,003m, then DE004m onward, approved000m|3640ms|
|009 as travel entry and exit|`(2,1,2,1)`|`(2,1,1,1)`|CB|approved017m,009m,028...027,009m,approved017m|3400ms|
|009 inside front-to-profile travel|`(4,7,4,7)`|`(4,7,2,6)`|EC|approved017,028m...025m,009,003,004...008,approved000|4600ms|

The first front arc's exact ordinary placements are003m(464,217),
009m(472,220),010(479,219),009(479,220), followed by028m(480,218).
The rear arc's critical placements are023m(479,215),012(476,217),
023(478,216),003m(464,217), followed by004m(458,218).
Those intentionally different origins must remain; do not remove them as
alignment noise.

Two additional clips exercise natural intermediate waypoints and also cover
the increasing-heading direction without another static turn montage:

|Purpose|Prime|Travel|Selected path|Critical boundary|Total|
|---|---|---|---|---|---|
|Front waypoint at C, increasing headings7-to2|`(3,7,3,7)`|`(3,7,5,3)`|DCF|DC025m(520,232) to010(521,233),009m(514,234),CF004m(501,232)|4840ms|
|Rear waypoint at A, increasing headings3-to5|`(1,3,1,3)`|`(1,3,4,5)`|BAE|BA022(302,244) to012(296,241),AE019m(305,238)|6520ms|

Recommendation: build the four focused clips plus these two waypoint clips in
one selector. This gives both rotation directions and distinct ordinary/travel
roles in six short actual native clips. It avoids a large invented turn ring.
If an even smaller first visual checkpoint is preferred, show the first two
arcs and keep the other four as subsequent checks.

Alternative positive-direction departures are D7-toE2 (`DE`,3400ms) for
`017,010,009m,004m...`, and F3-toC6 (`FC`,3520ms) for
`018,012,023m,003...`. They are redundant once the natural waypoint clips
above are shown. Their full predictions are retained in JSON, not required as
extra human-review clips.

##009 travel rows and all waypoint families

|Route|Table row/source line|Frame/flip/native origin|Immediate travel relationship|
|---|---|---|---|
|C-toB entry|196/209|009m(514,235)|followed by028(521,233)|
|C-toB exit|209/222|009m(446,256)|preceded by027(456,255); final heading1 arrival is017m(447,257)|
|D-toF entry|302/315|009m(472,220)|followed by028(478,217)|
|E-toC connector|366/379|009(434,229)|between025m(433,226) and003(439,226)|

D-toF's local009m-to028 pair is the same pose relationship as CB entry at a
different spot. The specified seed2 D-toF call selects DCF, so it is not a
direct-DF fixture. Do not label that detour as validation of DF's stored009
row. Add a seed-selected direct DF capture later only if placement inspection
shows a reason; do not alter the route algorithm to force it.

The permitted intermediate triples which draw at least one target ordinary
pose are ACD,BAE,BCD,CAE,DCA,DCB,DCF,DEA,EAB,EAC,EDC,FCD,FEA. Exact heading
changes and row sequences are retained in JSON.010 and009m occur at C after
DC in DCA/DCF;012 occurs at A in BAE/CAE and at C in ACD/BCD/FCD.009 also
occurs in the other listed transitions. These are permitted table/graph
contexts, not a claim that each is selected by the same seed.

## Timing and route-choice traps

`walk.c:109` uses unsigned modulo heading distance, so positive adjacent turns
can skip their ordinary final heading while negative turns may draw it.
Waypoint entry at `walk.c:163-180` advances heading once before the normal
turn loop. Keep the actual asymmetric sequence, including repeated poses.
`walk.c:211-215` returns6 ticks for ordinary movement and80 for final arrival;
`events.c:209` converts ticks to20ms. `ads.c:1110` initializes the first timer
to6 even when the first draw returns80. Thus a same-heading prime is120ms,
not an invented1600ms hold. Background/cloud scheduling can add display events
and zero-duration boundaries; retain every observed timestamp.

The retained glibc seed2 first `rand()` is1505335290. The graph and route
enumeration order are unchanged from the retained actual-C trace. Priming also
consumes RNG, so seed immediately before each call. Assert the chosen-path log
on the pinned Linux image before capture. Do not assume libc equivalence on
Windows or macOS.

The historical case named A-toE, arguments(0,1,4,5), actually selects ABCDE
with seed2. The historical E-toF case selects EDCF. Endpoint names are not
proof of direct routing. `calcpath.c:86` also explicitly disclaims exact
original path-selection reconstruction.

## TTM is a separate use surface

The preserved trace inventories15 statically attributed scripted draws:

|Asset|Scripted sites|Preceding linear delay information|
|---|---|---|
|009, five draws|MJFIRE tags140 and139; GJDIVE13; MJDIVE1; GJGULIVR11|8,8,unknown,unknown,11 ticks|
|010, eight draws|SJMSSGE28; MJCOCO1 tag24; MJCOCO23; five draws in MJDIVE2|7,15,15 and10 ticks respectively|
|012, two draws|GJVIS5 tag10; SJLEAVES3|9 and122 ticks respectively|

All15 statically attributed draws use unmirrored DRAW_SPRITE. These are
shared JOHNWALK references; replacing a PNG changes them too. Their TTM
coordinates are passed directly in `ttm.c:437-454`, unlike walk tablex-minus1.
The old trace matched all41 decoded TTM resources for both original and port
inventories; current RESOURCE.MAP/001 hashes still match those preserved
inputs. This is slot/tag/command attribution, not execution of every branch or
measured scene timing. Cross-tag image bindings can matter. SJLEAVES original
also has an extra SET_DELAY0, so its122-tick linear attribution is particularly
unsuitable as a fabricated review hold.

Native walk approval must not be described as whole-scene TTM parity. Preserve
these sites in the metadata and spot-check actual scripted scenes after the
connecting family is visually accepted.

## Minimal capture adaptation

Reuse the preserved profile native observer/review architecture as a reference,
without running its historical helpers against the new production pack:
`art/cartoon/walk-pilot/profile-walk-v1/native-motion-v1/`.

1. New config pins current40-asset production ZIP
   `1649218b32a4d11595806f8680e351a4f47950fcefbafdf8de758c2d225913db`,
   candidates009/010/012 only, and the six explicit call/path contracts above.
2. Replace the profile-only one-prefix/one-travel-bookmark contract with exact
   expected draw rows and roles across multiple path legs. Keep prime,
   departure, travel, waypoint and final-wait roles distinct.
3. Independently compile unchanged walk/calcpath with the existing draw-call
   observer pattern for the proposed cases before native capture. Then capture
   actual public adsPlayWalk displays and timestamps in Linux/Xvfb.
4. Keep a fixed route-wide shared camera. Candidate differences may occur only
   within the placed009/010/012 canvases. Preserve every already approved PNG
   and all other archive members byte-for-byte.
5. Keep Normal/Slow, step/replay, resource-ID stepping and a "Show connecting
   pose" selector. Do not synthesize extra animation holds. The two waypoint
   clips provide opposite turn direction naturally.

Original supplied-binary comparison previously established489 matching table
rows at offset0x188EA. This supports table geometry/frame identity. It does not
prove original-binary route choice, timing, or every TTM outcome.
