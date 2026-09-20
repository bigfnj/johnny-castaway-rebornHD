# Pose and action lessons for future art packs

The user requested these notes after approving the [18 worker corrections](../art/cartoon/little-workers-pose-corrections-v2/README.md): "approved, take notes so the next art pack is accurate and continue". Apply the lessons during source reading, prompting and visual review. They are an authoring reference, not a substitute for checking each drawing.

## Read the action before drawing the pose

Inspect the exact source beside its neighboring phases. Identify what is moving, which body part owns each visible shape, and what is hidden. A repeated attractive standing pose does not reproduce a walk, a reach or a reaction. Shared Cartoon references control identity and materials; the individual original controls geometry unless the user explicitly overrides its interpretation.

For each character prompt, state camera direction, gaze, near/far limb ownership, joint path and occlusion. Trace each visible arm from shoulder through elbow to hand and each leg from hip through knee to foot. Two visible hands alone do not rule out an extra sleeve or disconnected third arm. Do not expose an anatomically present limb that the source hides.

## Worker walking and gestures

For the right-facing worker in the approved correction set, the nearer leg and arm are his anatomical right; the farther limbs are his left. Identify them by hip and shoulder connections, not simply by which shoe or hand is on the left side of the image. Recoloring a leg without changing its pelvis overlap does not change the leading leg. Flipping the entire character changes facing and is not a leg swap.

002 alternates from001's right-foot lead to a left-foot lead. 013/014 advance the left leg, with014 extending the step. 016 starts the right foot's low forward swing and017 completes that step. 020 finishes the stride from018/019 rather than crossing raised shins. 021 needs a forward torso lean because he is starting to run. Preserve these phase relationships when drawing analogous actions.

026's far arm is fully hidden. In029, the nearer/right arm reaches image-left while the far/left arm is slightly forward. In036 the far arm crosses the front and partly covers the face; in037 it crosses the chest while the near arm hangs at his side. 039 also crosses in front, and040 brings the far arm forward. 046/047 need a slight near-elbow bend, and054's far arm reaches farther forward than the near arm. In063 the head looks right while both arms gesture behind toward image-left. Gaze and gesture direction can differ.

## Earlier corrections that must carry forward

| Subject | What the user's feedback established |
| --- | --- |
| Gull carrying a book | GJGULL1A026–030 carry the book in the beak. The upper beak is visible and the lower section is hidden by the book. Preserve the attachment and overlap. |
| Gull disturbing pages | The book is full length, leaning or lying as the original shows, with one binding. Pages become increasingly ruffled or torn. Keep feet hidden behind the book when only legs are visible; do not stand the gull on a tidy open book by default. |
| Facing and wing use | GJDIVE027–029 face forward with the chest in front. Both wings act like hands holding the card. Rear-facing gulls hide their eyes; deleting one pupil does not fix a front-facing body. |
| Eye visibility and accessories | Include partly occluded far eyes where visible, such as GJDIVE025. Sunglasses are frame-specific; GJNAT3009/010 have none. |
| Human contact and torso direction | Both hands must touch a camera that is held with two hands. Read belly angle, body turn and gaze independently. GJNAT3016 faces front looking down, not back. The user's final choice retained the previous Cartoon versions of012–014. |
| Hand orientation | MEANWHIL013–016 expose the inverted hand orientation: the back of the hand is at the bottom. A familiar pointing-hand template can reverse this. |
| Spinning machinery | GJVIS3007–009 depict a continuous, fast blurred propeller. Circular fragments are motion marks, not broken blades. The small lower rotors in010/011 also need blurred spinning blades. |
| Empty parachutes | THEEND1006/008/009 are used, empty and collapsing. Show sagging fabric and slack, irregular cords wherever visible. Do not invent a suspended load or taut symmetrical rigging. |
| Hanging cloth | GJBIPLAN021 is the long flag from022 draped down from its attachment, not fabric fixed along the entire pole. |
| Palette uncertainty | The darker MJFISH3008–010 source appearance was reviewed in scene and the v2 colors approved. Diagnostic source colors alone do not establish scene lighting. |

## Apply the notes in the next batch

Write specific source notes before generating each frame. Use a nearby approved drawing only for identity, and name any pose differences explicitly. For props, describe the grip, binding, hinge, string or other attachment and which part occludes it. Preserve deliberate partial silhouettes, debris and motion blur instead of completing or cleaning them into ordinary static objects.

After generation, inspect each drawing against its original and nearby action phases. Check the joint connections and silhouettes, not just the number of limbs or a bounding-box ratio. View actual alpha on light and dark backgrounds before treating hidden RGB as a halo. Retain targeted revisions and exact prompts; select the corrected version explicitly.

Use 60–72 new drawings for ordinary reviews, with targeted corrections separate. Source-canvas placement and native timing remain later integration work under the [art-first workflow](cartoon-art-build-workflow.md). Do not invent an animation by looping consecutive filenames.
