"""Persist each requested book-grip correction before built-in imagegen."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'gulls-clock-props-batch-v1'
POSES = {
 26: 'Left-facing flight, near wing extended steeply down-right, far wing partly behind the book to the left, tail right. Preserve this exact downstroke.',
 27: 'Left-facing flight, far wing upright, near wing outstretched horizontally right, two trailing feet. Preserve this exact asymmetric wing phase.',
 28: 'Left-facing flight, near wing long and steeply down-right, far wing left behind book, tail right. Preserve this exact narrow downstroke and source proportions.',
 29: 'Left-facing flight, both wings raised in a wide V, two connected trailing legs and feet. Preserve all corrected anatomy.',
 30: 'Left-facing grounded gull, wings folded and tucked along side, feet behind/beside book. Preserve corrected folded-wing anatomy and grounded pose.',
}

def main():
 number = int(sys.argv[1])
 oldv = 2 if number in (29,30) else 1
 refs = [PRIOR / 'generation/GJGULL1A.BMP' / f'{number:03}-generated-v{oldv}.png', PRIOR / 'reference/nearest8/GJGULL1A.BMP' / f'{number:03}.png']
 if number <= 30:
  action = ('Change the beak-to-book contact so the bird is visibly CARRYING the heavy book clamped in its beak. The upper bill must visibly hook OVER the top edge of the cover/page block and press against the OUTSIDE FRONT face, while the ENTIRE lower bill is hidden BEHIND the book. Raise or locally reshape the book top edge/contact as needed to cover the lower mandible. There must be NO visible orange lower jaw, NO visible horizontal mouth seam below the upper bill, and NO open mouth hovering above pages. The book top edge enters the beak at its base and visibly occludes everything below the upper mandible. Read as biting and supporting the book weight, not reading or looking into it. Keep one large full-sized dark-gray hardcover book, with existing panel orientation, width/height and general location. It may remain slightly open as in the source but not presented for reading. '+POSES[number])
 else:
  action = ('The gull is FRANTICALLY turning and ruffling pages of ONE LARGE FULL-SIZED BOOK. The existing book has become a short tiny booklet; restore a large tall hardcover volume with long full-sized cover panels and many long pages, consistent with the large book carried in neighboring poses. The volume leans downward and is partly laid down on its bottom/front edge as in the pixel source, not a short low rectangular booklet. Gull bends its head downward and forward from the right, actively biting/pulling a lifted sheet near the center hinge; many pages fan and curl vigorously on the left with short clean motion strokes. Keep the folded-wing gull body, facing LEFT and source crouch/contact arrangement. Make the action urgent and physical, no calm reading pose. Use a dark-gray cover and ivory blank pages; no writing or extra objects. The whole large book and bird must remain comfortably inside the canvas.')
 prompt = ('Use case: precise-object-edit. Edit image 1, the current Cartoon gull sprite. Image 2 is the exact original pose/action reference, with diagnostic pixel colors only. User correction: '+action+' Preserve the bird identity, eye, white/light-gray feathers, charcoal tips, orange upper bill and feet, crisp black outlines and cel shading. Preserve wing/body phase, orientation and relative proportions except the stated contact/book correction. Do not copy red/yellow checker pixels as decorations. No human hands, ribbon, extra book, floor scenery, glow or shadow additions. Genuine transparent RGBA background and clear padding around every tip. Return only the corrected isolated sprite.')
 spec={'schema_version':1,'tool':'image_gen.imagegen','mode':'built-in','arguments':{'prompt':prompt,'referenced_image_paths':[str(x) for x in refs]}}
 folder=HERE/'generation/GJGULL1A.BMP'
 folder.mkdir(parents=True,exist_ok=True)
 dest=folder/f'{number:03}-v1-request.json'
 assert not dest.exists(),dest
 dest.write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(spec['arguments']))

if __name__ == '__main__': main()
