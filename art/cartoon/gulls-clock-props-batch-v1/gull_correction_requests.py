"""Persist narrowly scoped visual corrections before built-in edits."""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
NOTES = {
 ('GJGULL1A.BMP','029'): 'Make only this anatomical correction to the existing sprite: its far orange webbed foot at lower-right is floating disconnected. Connect that existing foot to the underside of the bird with one short thin orange leg, originating anatomically beneath the rear body, just like the other connected foot. Keep exactly two feet total. Preserve the foot positions, raised V wings, body, face, book, all colors and transparent canvas. Do not add another foot or change the pose.',
 ('GJGULL1A.BMP','030'): 'Correct the standing sprite in the FIRST image to follow the grounded pose in the SECOND pixel source. The near wing is wrongly stretched DOWN to the ground: fold and tuck that wing horizontally snugly along the bird side, with its tip trailing RIGHT beside the tail, as in a standing gull. The book must remain upright at beak front-left. Keep face, book, body and feet locations as stable as possible. Remove the tiny pure-red patch just behind the book and left of the visible orange leg; it is a diagnostic-color artifact, not clothing or anatomy. Preserve one bird, ordinary yellow-orange beak and two feet with hidden parts naturally occluded. Do not add any red checker patterns, dangling objects or ribbons. Transparent background, same crisp cartoon styling and comfortable margins.',
 ('GJGULL3A.BMP','042'): 'Make only these anatomical cleanup corrections to this flying gull. The two orange webbed feet currently float disconnected below the body: connect EACH existing foot to the underside of the body with a short thin orange leg, exactly two connected legs and feet total. Remove BOTH small yellow detached teardrop blobs in front of the open beak; they are erroneous fragments, not spit or food. Keep the complete open beak, tongue and face, wings raised V, tail, colors, linework, shape, placement and transparent canvas unchanged. Do not add anything else.'
}
def main():
 resource, frame = sys.argv[1:]
 folder = HERE / 'generation' / resource
 refs = [folder / f'{frame}-generated-v1.png']
 if frame == '030': refs.append(HERE / 'reference/nearest8' / resource / f'{frame}.png')
 spec={'schema_version':1,'tool':'image_gen.imagegen','mode':'built-in','arguments':{'prompt':NOTES[(resource,frame)]+' Return one isolated genuinely transparent RGBA sprite. No artistic changes beyond the stated correction.','referenced_image_paths':[str(x) for x in refs]}}
 dest=folder / f'{frame}-v2-request.json'
 assert not dest.exists()
 dest.write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(spec['arguments']))
if __name__ == '__main__': main()
