"""Save reviewed source-pose requests before built-in image generation."""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
NOTES = {
 'GJGULL1A.BMP': {
 26: 'Flying LEFT with an upright open dark book held by the beak at the front-left. The book obscures the breast, not the eye. Preserve the broad gray cover panels, white page top edges and V hinge. Head above book faces left, tail right, near wing extends diagonally DOWN-RIGHT, other wing reaches left behind the book; preserve detached flight strokes. No ground shadow.',
 27: 'Flying LEFT carrying upright open book at beak, book front-left below face. Far wing rises vertically, near wing extends horizontally RIGHT, body and two small trailing legs right of book. Preserve each wing and leg, flight strokes. No ground shadow.',
 28: 'Flying LEFT carrying upright open book at beak in front-left. Head above cover. Near wing sweeps steeply DOWN-RIGHT; far wing extends horizontally LEFT behind book; tail trails right. Preserve flight strokes. No ground shadow.',
 29: 'Flying LEFT carrying upright open book at beak. Both wings raised in a wide V, book hangs front-left, two feet trail separately right of book, tail angles right. No ground shadow.',
 30: 'Standing LEFT with upright open book at beak covering breast/front-left. Folded wings form long body toward right; tail right. Preserve feet contact and small neutral gray contact shadow exactly as source. Book dark cover and light page edges.',
 31: 'Crouching LEFT to lower/open book onto ground. Book lies horizontally across front, several pages turn upward near beak, bird body lies low behind toward right, folded wing and tail right. Preserve small motion strokes above head and left of pages. Contact shadow only at source.',
 32: 'One gull faces LEFT while standing behind an open book. Neck bent down toward tall upward turning page at left; two broad white open page lobes below body, dark cover base. Folded wing and tail right. Preserve head, beak-to-page contact, feet/body separation. Paper lobes are pages, NOT a second gull.',
 33: 'One gull behind open book faces LEFT/down, beak slightly open above pages. Two feet visibly on right-hand pages. Short curved movement marks by head, open pages ruffled upward left. Folded wings and tail extend right. Preserve exact arrangement.',
 34: 'One gull crouches with head bent DOWN-LEFT into open book. Rump raised right, folded wing follows back, feet contact right page edge. Upright fluttering pages left; motion strokes above head. Do not confuse page edges with extra birds or wings.',
 35: 'One gull stands behind open book facing LEFT with upright long neck, one eye, beak pointed down-left. Folded wing and tail right, feet on or behind right page. Book lies broad and open below with slight ruffled pages. Preserve exact low body and book proportions.',
 36: 'One gull bends sharply DOWN-LEFT, beak touching low pages, head near left page, body and folded wing high right. Tail points upper-right. Short motion strokes above and left, open book base below. Preserve compact pecking anatomy, no second head.',
 37: 'One gull stands upright facing LEFT behind open book, on the right-hand page. Folded wing and downward-pointing tail right, head modestly raised, visible single eye. Book fills lower-left foreground. Preserve legs and contact, low open page shapes.',
 38: 'One gull upright facing LEFT, tall neck, feet at back/right of open book. Body compact almost vertical, folded wing crossing side, tail extends horizontally RIGHT. Broad open book below, ruffled white pages dark cover. Preserve source tall stance and book/body ratio.'},
 'GJGULL3.BMP': {
 17: 'Flying RIGHT in profile, near wing extends diagonally DOWN-RIGHT, far wing rises steeply UP-LEFT. Long narrow horizontal body with small head/right-facing closed beak; tail left and tucked orange feet. One visible eye only.',
 18: 'Flying RIGHT in profile, horizontal long body with small head at upper-right, near wing sweeps down into long bent elbow/pointed tip, other wing is partly visible behind/left. Preserve head/beak tiny relative to wings, two tucked feet only if visible.',
 19: 'REAR VIEW flying AWAY. Back of head and round rump centered, NO visible face, NO eyes, NO forward beak. Two wings descend diagonally outward then hang down at tips. Two tiny orange feet below rump. Preserve rear anatomy exactly; do not turn bird to face viewer.',
 20: 'REAR VIEW flying AWAY. Back of head and rump centered below raised wings in a wide V. NO face, NO eyes, NO visible beak. Two tiny orange feet below body. Preserve narrow tapered wings and rear-only view.',
 21: 'Flying LEFT in profile, far wing points steeply UP-RIGHT, near wing stretches diagonally DOWN-LEFT, body horizontal with left-facing beak and single eye. Tail and orange tucked feet trail right. Preserve rolled wing plane and source proportions.',
 22: 'Flying LEFT in profile, long horizontal body, single visible eye and beak at left. Two long downward wings: near wing sweeps down-left toward center bottom, far wing bends outward down-right. Tail horizontal right. Preserve exact downward wing pose.',
 23: 'FRONT VIEW flying TOWARD viewer. Two distinct eyes, orange central beak, centered round white chest and two separate orange feet below. Both long wings slope DOWN outward and bend vertically down at tips. Symmetric source front anatomy; not rear view.',
 24: 'FRONT VIEW flying TOWARD viewer. Two eyes, centered orange beak, small white body low center and two distinct orange feet beneath. Both long narrow wings rise outward in wide V. Preserve front view and source wing angles.'},
 'GJGULL3A.BMP': {
 42: 'Agitated gull flies RIGHT with open beak, head low right, both wings raised in V at different angles, two feet dangling separately and tail left. Preserve curved flight motion strokes around wing tips. Single eye, expressive strained brow, not an added face.',
 43: 'Agitated gull flies RIGHT, horizontal body, head front-right with open beak angled down, two feet below. Near wing is large sweeping DOWN-LEFT, far wing extends behind/up-left. Preserve horizontal short motion marks above and in front of head.',
 44: 'Agitated gull flies RIGHT with long nearly horizontal spread wings, elongated body, head right with open beak pointing down-right. Two feet below chest. Preserve especially wide/low silhouette and trailing near wing LEFT, source movement strokes.',
 45: 'Agitated gull flies RIGHT, horizontal body and open beak at right. Near wing sweeps down-left; other wing is tucked/foreshortened above back; tail at left. Two orange feet beneath and short motion marks above/right. Preserve source silhouette.',
 46: 'Agitated gull flies RIGHT with head at lower-right and open orange beak, single visible eye. Far wing rises almost vertically upper-right, near wing stretches diagonally upper-left; body low center, tail left, orange feet below. Preserve source short black flight strokes around wings.'}
}
def main():
 resource, frame = sys.argv[1:3]
 number = int(frame)
 original = HERE / 'reference' / 'nearest8' / resource / f'{number:03}.png'
 prior = ROOT / 'art/cartoon/gulls-fish-batch-v1/generation/GJGULL1.BMP/009-generated-v1.png'
 key = HERE / 'generation/GJGULL1A.BMP/026-generated-v1.png'
 refs = [original, prior if resource != 'GJGULL1A.BMP' or number == 26 else key]
 prompt = ('Create one clean high-resolution Cartoon game sprite based on the FIRST reference. The first image is authoritative for exact pose, silhouette, facing, limb positions, book placement if present, and isolated motion strokes. Smooth its pixel stair steps into clean curves; do not copy pixel blocks. The second reference provides ONLY consistent gull identity/materials/linework; NEVER transfer its pose, book, objects, or background unless the FIRST reference contains them. White and cool light-gray feathers, charcoal wing tips, warm yellow-orange beak and webbed feet, clear black contour, restrained cel shading, same friendly expressive proportions. '+NOTES[resource][number]+' Preserve original aspect ratio and relative component sizes. One bird only. Both wings and feet follow source visibility; no invented limbs, no humans, no letters or titles. Genuine transparent RGBA background including all gaps, comfortably padded on every side so no tips or strokes touch the canvas edge. No atmospheric glow, no backdrop, no scenery, no cast floor shadow for flying poses. Return only the isolated sprite, no reference panels, no labels.')
 folder = HERE / 'generation' / resource
 folder.mkdir(parents=True, exist_ok=True)
 dest = folder / f'{number:03}-v1-request.json'
 assert not dest.exists(), dest
 for ref in refs:
  assert ref.is_file(), ref
 spec = {'schema_version':1,'tool':'image_gen.imagegen','mode':'built-in','arguments':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs]}}
 dest.write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(spec['arguments']))
if __name__ == '__main__': main()
