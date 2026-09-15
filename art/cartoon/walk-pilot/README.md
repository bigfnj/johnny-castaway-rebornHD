# Walking review candidates

This directory's root recipe preserves the rejected profile-cycle candidates.
The later `direction-key-024` record holds the approved viewing direction and
leg-order key; `directional-cycle-v1` holds the subsequent six-pose E-to-A cycle
whose full motion the user approved with "looks good" on 2026-09-14. Its separate
`acceptance.json` records the exact approved export hashes. Production promotion
and broader scene contact remain pending.

This root recipe covers only `JOHNWALK.BMP` frames 024 through 029. Its images
are rejected review candidates. On 2026-09-14 the user replied "well done"
after the synchronized revision-3 motion comparison, then identified substantive
leg-order and viewing-angle defects: pose 3 / sprite 024 brings the opposite leg
forward, and the generated cycle stays in a fixed left profile rather than
following the original three-quarter movement. The earlier response must not be
treated as full motion approval.

For this root profile candidate, the approved decision is narrower: "The body pop looks resolved"
confirmed revision-2 upper-body registration. Preserve that alignment while
correcting pose geometry and direction. Character design approval is separate.

Frame 024 uses the third foot drawing, with its known canvas normalization.
The other five PNGs retain the revision-2 registration and bytes.
The source bundle retains nine generated images: the six final drawings and
the three earlier drawings used in their actual reference ancestry. It contains
no external cap reference and no complete game archive. Original pose references
remain in `assets/scrantic_data.zip`; the approved character reference is already
stored beside this directory.

`recipe.json` records source hashes, ordered image references, exact prompt
files, canvas dimensions and export transforms. Reference orders taken from
prompt roles are labeled as such; the two foot-edit reference lists were
confirmed against their calls. Image generation is not reproducible from these
prompts: no seed or model identifier was exposed. The preserved generated pixels
and recorded candidate PNG hashes are the authority.

All six frames use the same drawing scale, 137/1590, and the approved cap anchor
convention. Frame 024 first restores the known 929-by-1813 input canvas from the
898-by-1752 returned image using one uniform factor, 929/898. That factor is
recorded separately. It was checked against the head and torso; it is not a
general rule to resize future output, a body-bounds fit, or a limb warp.

The third foot drawing's sole lands near y142.69, compared with the original
black sole at y144-145. Source contact interpretation remains approximate by
about two HD pixels. This measurement does not establish correct anatomical
leg order or viewing angle. This profile candidate remains rejected; the later
directional cycle supplies the accepted replacement.

Recreate the six runtime PNGs with Python and Pillow 12.3.0. The exporter checks
every output against its recorded candidate hash before writing; it refuses an existing
output directory. These are authoring dependencies, not runtime dependencies.
From the repository root:

```text
python art/cartoon/walk-pilot/export.py --output build/art-work/restored-walk-pilot
python tools/art_pack.py build --archive assets/scrantic_data.zip --ledger art/cartoon/walk-pilot/pack.json --accepted build/art-work/restored-walk-pilot --output build/art-work/restored-walk-pilot.zip
```

On this Windows workspace, use the configured toolbox Python for its Pillow
installation. `pack.json` declares `coverage: partial` and exactly six required
assets. The full candidate archive stays under ignored `build/`; this authoring
record does not modify the production archive or the shipped story scripts.

The native review used 23 original E-to-A positions at 120 ms per pose and a
one-second endpoint hold. The diagnostic resource edits existed only in the
review archive. Compared with revision 2, revision 3 changed only frame 024.
Native captures loaded all six replacements, preserved pixels outside the
sprite canvases, retained all 2,550 original archive members, and matched all
2,452 golden dump hashes. These checks establish integration and preservation;
the user's review supplies the artistic decision. This root profile cycle remains
rejected. The later directional cycle has its own motion approval and does not
change this historical recipe or its recorded candidate bytes.
