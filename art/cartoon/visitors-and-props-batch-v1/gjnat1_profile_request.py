"""One focused profile correction; preserve the first generated drawing."""
import json
from pathlib import Path

here = Path(__file__).resolve().parent
folder = here / 'generation/GJNAT1.BMP'
spec = {
    'schema_version': 1, 'tool': 'image_gen.imagegen', 'mode': 'built-in',
    'arguments': {
        'prompt': 'Edit image1 only with a narrow correction to the yellow mask facing. Keep the entire tan body, both arms/hands, raised right knee, supporting leg, both feet, green wrap, hair, shading, linework, arrangement and transparent canvas unchanged. The exact original frame022 in image2 faces RIGHT IN PROFILE. Image1 accidentally turned the mask toward the viewer and shows a second red eye slit. Turn ONLY the yellow mask to a narrow strict RIGHT-facing profile, as in image2 and the same performer profile in image3. One visible red eye slit only, with the far slit fully hidden; preserve the long yellow mask shape and red lower marks with appropriate profile foreshortening. Do not invent a visible human face, nose or teeth. The mask stays in the same head position and keeps the same tilt. Keep the rest of image1 byte-visually equivalent, no pose redesign. Smooth flowing outlined cel-shaded cartoon, no pixel steps. Genuine RGBA transparent background, safe transparent padding. No floor, no cast shadow, no glow, no added objects. One sprite only.',
        'referenced_image_paths': [str(folder / '022-generated-v1.png'), str(here / 'reference/nearest8/GJNAT1.BMP/022.png'), str(folder / '020-generated-v1.png')],
    }
}
dest = folder / '022-v2-request.json'
assert not dest.exists()
dest.write_text(json.dumps(spec, indent=2) + '\n', encoding='utf-8')
print(json.dumps(spec))
