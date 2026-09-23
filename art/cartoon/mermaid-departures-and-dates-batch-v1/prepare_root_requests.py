"""Save exact built-in requests for date components and departure dives."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ART = HERE.parent
identity = ART / 'mermaid-expression-corrections-v1/generation/SMGIFT.BMP/000-generated-v1.png'
tail = ART / 'workers-and-mermaids-batch-v1/generation/SBREAKUP.BMP/019-generated-v1.png'
fin = ART / 'mermaid-expression-corrections-v1/generation/SMGFTWAV.BMP/007-generated-v2.png'
poses = {
    'SMDATE6.BMP': {
        0: 'Full adult mermaid in right-facing profile, upright seated torso, forearms held forward at waist level. Long green fish tail folds back left at the hips, bends diagonally down-left, then sweeps horizontally right to the two-lobed fin. Preserve this seated zigzag tail, the hair shape and modest relaxed expression. No water or chair is present.',
        1: 'Only the head and cropped torso component of an adult mermaid, right-facing profile, chin slightly lowered, golden hair hanging behind at left, green swimsuit top, bare midriff clipped at the original horizontal lower edge. Arms and lower tail are separate sprites: do not add them. Preserve the partial component as clean animation artwork.',
        2: 'Only the lower body and tail animation component. A small skin-colored waist joins the green tail at upper left. The broad upper tail goes right, bends sharply diagonally down-left, then sweeps right along the lower edge into a two-lobed fin at far right. Keep this exact zigzag silhouette. Do not add a head, torso, arms, water or rock.',
        3: 'Only a detached arm animation component. Smooth tan shoulder attachment on left, arm curves downward into a shallow elbow, then extends nearly horizontally to the right with a small relaxed hand at the end. No body, head, jewelry, water or other elements. This is an ordinary animation layer with no injury detail.',
        4: 'Only a detached bent arm animation component raising a small upright stemmed glass with magenta-pink drink. Shoulder attachment at lower left, elbow low, forearm rises toward upper right, fingers hold the thin stem under the glass bowl. Match exact source angle and silhouette, no body or head. Ordinary uninjured animation layer.',
        5: 'Only a detached bent arm animation component raising a small stemmed glass with magenta-pink drink. Rounded shoulder attachment at left, elbow near lower middle, forearm angles upward right, fingers hold the stem. Keep the wide V arm silhouette and glass orientation of the original. No body or head. Ordinary uninjured animation layer.',
        6: 'Adult mermaid upper-body animation component in right-facing profile, torso and face leaning back, chin raised, eyes following the raised small stemmed glass with pink drink at her lips. Golden hair falls left. One bent arm raises the glass. Green swimsuit top and cropped midriff, no lower tail, no legs, no water. Preserve the original drinking gesture.',
        18: 'Adult mermaid cropped upper body in right-facing profile, looking forward, holding the small green food item across both palms low in front of her torso. Preserve the original green prop shape: thicker leafy end toward the left and a small tapered forked extension at the right. Both forearms and the object remain below chest level. Preserve the exact silhouette and crop at waist; no lower tail or water.',
        19: 'Adult mermaid cropped upper body in right-facing profile, head slightly lowered toward the small green food item held across both palms low in front of her torso. Preserve original green prop shape and tiny hand/finger differences, its thicker end left and tapered forked extension right. Both forearms stay below chest level. No lower tail or water.',
        20: 'Adult mermaid cropped upper body, right-facing profile, leaning her face down slightly while lifting the small green food item with both hands toward her mouth. Match the bent elbows, green leaflike shape of the prop, and its hanging pointed right end. Keep original waist crop and head direction. No tail or water.',
        21: 'Adult mermaid cropped upper body in right-facing profile, leaned forward with a green leafy food item held at her open mouth by both hands as she takes a bite. Match the original food silhouette and arm overlaps exactly, with forearms angled across her torso. Golden hair behind, green swimsuit top. No lower tail or water.',
        27: 'Adult mermaid cropped upper body, right-facing profile, with two empty forearms held forward as in the original: upper forearm reaches right horizontally with fingertips extended, lower forearm bends outward beneath it. Her head inclines down a little toward the hands. No food prop, no lower tail or water. Preserve natural human arm proportions and the original crop.',
        28: 'Adult mermaid cropped upper body, right-facing profile with chin lowered and shoulders slightly hunched forward. Both hands are near each other in front of the chest, fingers curled gently downward as in the original. No food prop, no lower tail or water. Keep exact source arm positions, head angle and crop.',
        31: 'Adult mermaid cropped upper body in right-facing profile, head tipped back a little, nose and chin pointing slightly upward. Elbows bent; one forearm rests across lower torso while the forward hand rises to the right at chest height with loosely curled fingers. Match source posture and crop. No food prop, no tail or water.',
    },
    'SMDATE10.BMP': {
        4: 'Full adult mermaid diving diagonally down-left, viewed slightly from behind. Both arms reach together ahead toward lower left, face points down-left and is partly hidden, golden hair fans up behind her. Long green tail curves from waist across to far right and hooks down at its far tip. Preserve the broad horizontal diving silhouette and overlapping hands. No ocean backdrop.',
        5: 'Full adult mermaid in a steeper headfirst dive down-left. Hands together at lower left, arms straight ahead of head, golden hair streaming behind. Torso near left-middle, green tail rises diagonally up-right and ends in a small sideways fin at the far upper-right. Preserve this long diagonal shape and partly obscured downward face. No ocean backdrop.',
        6: 'Only the upraised green mermaid tail entering water, its body disappearing into a splash at lower left. Long thin tail rises with an S bend toward upper right and ends in two sharply tapered fin lobes. White splash arcs with cyan edges fan around the submerged base. No head, torso, arms or extra person. Keep exact original tail curve and splash extent.',
    },
    'SMDATE11.BMP': {
        4: 'Only a partial green mermaid tail protruding above a tiny water ripple. Tail stalk begins at lower left, sweeps up-right, then splits into two curling flukes at upper right seen in narrow side perspective. Match the original asymmetric arching shape, do not make the symmetric frontal fin from the style reference. Tiny white-cyan ripple at bottom left only. No body or head.',
    },
}
requests = []
for resource, frames in poses.items():
    for frame, pose in frames.items():
        source = HERE / f'reference/nearest8/{resource}/{frame:03}.png'
        refs = [source, identity]
        if resource != 'SMDATE6.BMP' or frame in (0, 2):
            refs.append(tail)
        if resource == 'SMDATE11.BMP':
            refs.append(fin)
        prompt = ('Use case: style-transfer. Create one polished cartoon game sprite on a real transparent RGBA background. '
                  'Image 1 is the exact original pose and component boundary: preserve its silhouette, facing direction, overlaps, eye visibility and prop placement. '
                  'Remaining images are established character and material style references only, not pose references. '
                  f'This asset is {resource} {frame:03}. Specific pose: {pose} '
                  'Match the approved clean bold black outlines, smooth cel shading, golden-yellow hair with cyan headband, warm tan skin and green swimsuit top and emerald-green fish tail wherever those parts occur in the original. '
                  'Use ordinary adult proportions. Red-white source pixels mean smooth skin, not a checker pattern. '
                  'Cleanly redraw the pixelated contours as fluid curves. Keep only this source component; do not complete hidden or absent anatomy. '
                  'Center the entire asset with transparent margins; no clipping, checkerboard, background scenery, captions, border, watermark or extra objects.')
        args = {'prompt': prompt, 'referenced_image_paths': [p.as_posix() for p in refs]}
        spec = {'schema_version': 1, 'tool': 'image_gen.imagegen', 'resource': resource, 'frame': f'{frame:03}', 'version': 1, 'arguments': args}
        destination = HERE / f'generation/{resource}/{frame:03}-v1-request.json'
        destination.parent.mkdir(parents=True, exist_ok=True)
        assert not destination.exists(), destination
        destination.write_text(json.dumps(spec, indent=2) + '\n', encoding='utf-8')
        requests.append(spec)
print(json.dumps(requests))
