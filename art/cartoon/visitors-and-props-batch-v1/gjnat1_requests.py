"""Save exact built-in image requests for the GJNAT1 performer drawings."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
POSES = {
    1: 'Low three-quarter frontal crouch. The arm on image left reaches horizontally left with open hand; image-right arm bends back at waist. Both knees deeply folded, narrow asymmetric crouched silhouette. Preserve source silhouette and mask tilt.',
    2: 'Frontal airborne small leap. Both arms extend outward slightly upward, elbows gently bent. Both knees bend outward and both bare feet are off the ground, dangling at unequal angles. No contact shadow.',
    3: 'Frontal low squat, both arms raised high outward into a broad V, bent knees apart, feet spread. Image-left knee bends sharply inward at calf while image-right foot plants outward. Broad source silhouette.',
    4: 'Frontal crouch with both elbows lifted sideways and both forearms bent upward. Bent knees apart and both feet turned outward. Preserve the source asymmetry and lower squat.',
    5: 'Frontal standing pose, both arms out and upward in a shallow V with open hands, both legs almost straight and feet spaced apart. Preserve the long mask and narrow torso proportions exactly.',
    6: 'Frontal upright stance, both arms raised high diagonally, fingers open, feet spaced apart. Taller V-shaped arm arrangement than frame005. Both bare legs nearly straight.',
    7: 'Frontal deep bent-knee stance, both upper arms angle out, elbows low, forearms upright with closed hands. Feet apart and turned outward. Mask remains frontal.',
    8: 'Frontal dancing balance on the straight leg at image left; other knee lifted high toward image right with its lower leg dropping vertically. Both elbows bent with closed hands raised beside chest. Preserve source leg laterality.',
    9: 'Frontal dance step on the leg at image left, other leg at image right kicks outward with toes lifted. Both arms lowered diagonally outward. Preserve narrow frontal long mask.',
    10: 'Frontal hopping balance on image-right leg, image-left knee lifts outward and bends, foot hanging inward. Both arms angle outward and down. Keep correct raised-leg side.',
    11: 'Frontal dance step with image-left leg kicked outward low and heel leading; image-right leg supports body. Both bent arms extended outward at waist/chest level, palms up. Keep exact source laterality.',
    12: 'Frontal energetic high-knee twist, image-left knee raised sharply toward torso, image-right supporting leg slants diagonally to bottom center. Broad elbows thrust sideways and forearms bend down. The large long mask leans with torso as in source.',
    13: 'Frontal small upright jump with legs crossed at calves, two feet tucked closely together underneath. Both arms lowered diagonally. Keep thin crossed-leg silhouette and both feet off the ground.',
    14: 'Frontal leap with arms high into wide V, image-right knee lifted outward at waist height, other leg pointing downward with pointed foot. Preserve clear separation of limbs and airborne pose.',
    15: 'Frontal low airborne crouch, both elbows out and wrists downward, both knees raised and bent with separated dangling feet. Wide squat in air, no ground shadow.',
    16: 'Right-facing three-quarter profile in a deep crouched jump, both hands lifted beside and in front of head. Mask projects toward image right, black shaggy hair visible behind to image left. Legs deeply bent, feet angled right and separated; green wrap trails left.',
    17: 'Strict right-facing profile, deep knee-bend crouch with both arms stretched diagonally upward in front of the face and hands together/overlapping near top right. Long mask projects right. Preserve paired arms and crouched legs as source.',
    18: 'Strict right-facing upright standing stretch, arms raised above and forward of head, one forearm almost vertical and other diagonally up-right. Legs nearly straight, two feet close below body at slightly staggered levels. This is an upright planted stance, NOT a tucked airborne jump. Tall source silhouette, long yellow mask seen edge-on.',
    19: 'Strict right-facing bent-knee standing stance, two forearms reaching forward/up at different heights. The knees bend modestly forward, lower legs return back down, and the two feet are close together underneath. Preserve distinct elbow bends, mask in narrow profile. NOT a knees-up airborne jump.',
    20: 'Right-facing high-knee running/dance profile, forward knee lifts horizontally right while other leg extends downward and slightly back. One arm reaches forward right, other bent back near torso. Source pose is compact and tilted forward.',
    21: 'Right-facing low squat, both knees bend deeply, chest leaning forward. Both bent arms gather in front at chest level, one hand nearer the mask and the other lower. Feet staggered, not a standing pose.',
    22: 'Right-facing raised-knee running profile. One knee projects forward right and folds down, rear leg bent behind. One arm extends diagonally upward in front of mask while the other is lower. Preserve exact source arm/leg positions.',
    23: 'Right-facing forward-leaning dance step. The leg at image left supports the body with a modest knee bend; the nearer image-right knee lifts forward and its lower leg drops to a raised foot. One arm extends forward at chest level toward image right; the other elbow bends back/up near the rear shoulder with its hand beside the back of the mask. Preserve the exact original separate arm shapes, raised foot and hunched right-profile posture, not a symmetric deep squat.'
}

def main():
    frame = int(sys.argv[1])
    out = HERE / 'generation' / 'GJNAT1.BMP' / f'{frame:03}-v1-request.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    refs = [str(HERE / 'reference' / 'nearest8' / 'GJNAT1.BMP' / f'{frame:03}.png')]
    if frame != 5:
        refs.append(str(HERE / 'generation' / 'GJNAT1.BMP' / '005-generated-v1.png'))
    prompt = (
        'Create ONE clean hand-drawn cel-shaded Cartoon game sprite on a genuinely transparent RGBA background. '
        'Image 1 is the exact original pose and silhouette authority, not a color/texture template. '
        + ('Image 2 is the same performer identity/material/style key ONLY; do not copy its pose. ' if frame != 5 else '')
        + 'Subject: an adult costumed performer with a very long yellow costume mask, shaggy black hair behind it, plain warm tan skin, a simple bright green ragged waist wrap, bare arms, legs and feet. '
        'The yellow mask has simple red narrow slanted eye slits and three short red vertical lower marks/cuts, with the same outline as the source. Keep it a flat costume mask, no invented visible face, no nose or teeth, no extra symbols. '
        'The red-and-white pixel stipple on the source limbs and torso is only a diagnostic palette: render smooth plain tan skin, NOT checked clothing, NOT red skin. '
        'Pose for this exact frame: ' + POSES[frame] + ' '
        'Faithfully keep source facing, the silhouette and relative proportions of mask/body, raised versus supporting leg, hand direction, limb overlap and green-wrap shape. Exactly two arms, two hands, two legs and two bare feet. '
        'Style: crisp flowing dark ink contours, restrained warm cel shading, readable clean shapes, polished classic 2D cartoon adventure-game artwork. Upper-left light. No pixel stairs or stippling. '
        'Isolated full source figure centered with generous clear transparent padding on ALL sides. No scenery, no ground, no platform, no gray cast/contact shadow, no glow, no motion blur, no border or labels. The original gray floor shadow is not part of this new sprite. '
        'Render one pose only, not a sprite sheet. Preserve actual alpha transparency.'
    )
    spec = {'schema_version': 1, 'tool': 'image_gen.imagegen', 'mode': 'built-in', 'arguments': {'prompt': prompt, 'referenced_image_paths': refs}}
    assert not out.exists(), out
    out.write_text(json.dumps(spec, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(spec))

if __name__ == '__main__':
    main()
