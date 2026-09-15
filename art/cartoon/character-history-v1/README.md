# Early character design history

This record preserves the five design passes that led to the approved
[canonical v5 character](../johnny-character-v5.png). The user responded
"nailed it, perfect." and "Yes, use this design" to v5. That decision concerns
the character reference sheet. Later walking and scene approvals have their
own records.

`source-images.zip` contains the unchanged v1-v4 generated sheets, totaling
5,233,048 compressed bytes. All five sheets are 1536 x 1024 RGB images. V5 is
already tracked separately and is not duplicated here. Each saved character
image, including canonical v5, was compared byte-for-byte against its actual
inline imagegen response. No artwork was edited during recovery.

| Pass | Direction and result |
| --- | --- |
| v1 | The user liked the drawing style and ragged shorts, but the character felt wrong. |
| v2 | A leaner body and closer facial expressions improved the identity; the beard still read as stubble. |
| v3 | A fuller beard and earlier sailor-cap form were restored while retaining the lean body and expressions. |
| v4 | The beard became longer and scruffier. The cap followed a bowl-rim interpretation that the next user reference replaced. |
| v5 | The attached cap supplied the projecting dark brim. The user approved this version as the character design. |

`provenance.json` preserves the exact prompt strings, their semantic UTF-8
hashes, actual explicit reference order, generated source hashes and the
specific human revision decisions. The files in `prompts/` contain the same
decoded tool strings. Prompt hashes describe the string itself, independent
of JSON or text-file line-ending conventions. The first prompt was recovered
from the exact direct storage call before generation; later similarly named
variables and prompt readers were excluded.

The explicit reference chain is recorded without collapsing distinct roles.
V1 used the two original walking poses. V2 used v1 followed by original walking
and telephone poses. V3 used v2 as its edit target, v1 for the cap, and an
original walking pose for beard identity. V5 used v4 followed by the user's
attached cap. These direct original inputs are small PNGs in `references/`.
The preserved user cap was compared with the actual attached temporary file
and matches its bytes exactly.

V4 used `num_last_images_to_include: 4`, rather than explicit image paths.
Its prompt declared a browser screenshot of a cap, the cartoon sheet to edit,
and two original sprite contact sheets. Those intended roles and the exact
selection mechanism are retained. The record does not invent an explicit
ordered path list for that call or claim the older external browser screenshot
can be reconstructed from a URL. The actual later attached cap is available.

The useful lesson is to name which reference controls each feature and carry
forward the features the user has already approved. A prompt asking for small
changes still needs visual review. Here, the ragged shorts, lean body and face
were accepted before the beard and cap direction settled. The final attached
reference resolved the projecting brim more clearly than the earlier verbal
cap descriptions. Keep concept approval separate from approval of independently
generated animation frames and their behavior in a full scene.

Only relevant art requests, image bytes, direct inputs and revision decisions
were recovered. No general task transcript is included. Historical local paths
identify the original tool inputs and outputs; all stored references and the
canonical character have portable paths within the repository. No new exporter
or production archive update is needed for these historical direction sheets.
