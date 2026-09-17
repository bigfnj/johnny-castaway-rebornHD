# Moving cloud lessons

The user accepted the reviewed clouds with "Yes, keep these clouds". See the
[authoring record](../art/cartoon/clouds-v1/README.md) and
[delivery verification](cartoon-clouds-verification.md). Earlier draft and
native-run records retain their original pending status.

## Identify the active resource first

Ordinary island clouds are `BACKGRND.BMP015-017`. The separate resource named
`CLOUDS.BMP` has four drawings, but neither its filename nor its presence in the
archive proves runtime use. The source selector and recorded script map are the
authority for deciding a delivery family. Frame 015 was already approved; only
016/017 need new drawings to complete this particular family.

## Separate original geometry from approved style

The reference export verifies the supplied-original resource pair, decoded
index-plane identities, archived PNGs and enlarged nearest-neighbor guides.
The diagnostic palette does not establish the original executable's night
colors. Existing HD PNGs are useful comparisons but differ from exact doubling
of the original pixels. Keep the original guide and accepted Cartoon style
image as separately identified inputs in each generation prompt.

The first drafts exceeded the available height. Targeted image-tool edits made
them shallower. A numeric bounding box in a prompt is guidance, not a geometric
guarantee: the second 016 draft became lower than requested. It fits cleanly but
has about 89 percent of the original silhouette area; the user accepted that
shape in the native comparison. The second 017 draft retains its distinctive trailing
cloudlet and lower opening. No Python drawing or silhouette painting was used.

## Inspect alpha and actual presentation

Generated outputs, like the approved cloud, have interior alpha 254 and sparse
very low alpha values outside the useful outline. The dark image-tool preview
can expose hidden RGB and suggest a halo that needs checking in an actual alpha
composite. Do not turn a diagnostic alpha threshold into an export threshold.
Use premultiplied filtering and record the fixed uniform scale and translation.

The engine mirrors the complete canvas when the wind reverses. Empty margins
and translations therefore need review in both directions. A static image of
one cloud does not establish scheduler behavior or screen-edge wrapping.

Night selects a different background, but the PNG cloud colors are not tinted
by that switch. Review brightness and fringes on the actual night background.
An explicitly forced cloud state exercises known source-valid cases; it is not
evidence that a particular seed naturally reaches all of them. Compare the
candidate against the exact current production archive so earlier island and
wave approvals remain present in the review.

The pack builder replaces the entire Cartoon prefix. A review candidate that
adds only two drawings must preserve all existing 61 approved payloads. The
two-file scope does not authorize replacing the production ledger with two rows.

## Keep prompt history portable without rewriting it

The exact image-tool requests retain the absolute paths actually supplied to
the tool. Reproduction must resolve their recorded batch-relative suffixes
under the current checkout. Reading the historical absolute paths directly
would keep a hidden dependency on the author's worktree after a merge or move.
The exporter was corrected and replayed from a fresh different checkout layout;
the PNGs and private archive stayed byte exact. Historical requests were kept
unchanged, and invalid references outside this batch were rejected.
