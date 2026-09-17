"""Unpainted geometry references for the low-tide rock ripple ring."""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / 'rock-waves-v1/reference'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    rows = []
    for frame in range(39, 42):
        source = HERE / f'reference/original-{frame:03}.png'
        image = Image.open(source).convert('RGBA')
        guide = Image.new('RGBA', (1536, 1024))
        guide.alpha_composite(image.resize((1248, 348), Image.Resampling.NEAREST), (144, 338))
        path = OUT / f'original-{frame:03}-guide.png'
        guide.save(path, compress_level=9)
        rows.append({'path':path.name, 'source':source.relative_to(ROOT).as_posix(),
                     'source_sha256':sha(source), 'sha256':sha(path)})
    rock_source = HERE / 'static-v2/BMP/BACKGRND.BMP/002.png'
    rock = Image.open(rock_source).convert('RGBA')
    guide = Image.new('RGBA', (1536, 1024))
    # Ring origin258,680; rock300,656; native HD mapping6x plus144,338.
    guide.alpha_composite(rock.resize((768, 360), Image.Resampling.NEAREST), (396, 194))
    path = OUT / 'approved-rock-position.png'
    guide.save(path, compress_level=9)
    rows.append({'path':path.name, 'source':rock_source.relative_to(ROOT).as_posix(),
                 'source_sha256':sha(rock_source), 'sha256':sha(path)})
    style = ROOT / 'art/cartoon/shoreline-repair-v1/integrated-shore-v1/foam-refresh-v1/006-raw.png'
    rows.append({'role':'approved white ripple style, use original file as reference',
                 'source':style.relative_to(ROOT).as_posix(),'sha256':sha(style)})
    record = {'reference_only':True, 'mapping':{'runtime_scale':6,'paste':[144,338],
              'ring_canvas_hd':[208,58],'ring_world_origin_hd':[258,680]},
              'files':rows, 'scope':'Nearest-neighbor source/rock reference placement only. No art painted.'}
    (OUT / 'source.json').write_bytes((json.dumps(record,indent=2)+'\n').encode())
    approval = {'human_response':'looks good', 'review_url':'http://127.0.0.1:8936/review.html',
                'review_html_sha256':sha(HERE/'review/review.html'),
                'scope':'Static low-tide beach001 and rock002 appearance. Wave artwork and combined motion remain pending.',
                'approved_assets': [{'path':f'BMP/BACKGRND.BMP/{i:03}.png',
                                     'sha256':sha(HERE/f'static-v2/BMP/BACKGRND.BMP/{i:03}.png')} for i in [1,2]],
                'subsequent_direction':'Reuse the already approved new white wave artwork for the island and rock where possible; do not confuse legacy low-tide fallback with approved high-tide waves.'}
    (HERE/'static-shape-approval.json').write_bytes((json.dumps(approval,indent=2)+'\n').encode())
    print('Preserved static approval and four unpainted ring references.')


if __name__ == '__main__':
    main()
