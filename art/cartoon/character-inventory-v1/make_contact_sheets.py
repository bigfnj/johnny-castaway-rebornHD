"""Make technical original-reference sheets without altering source PNG files."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

parser = argparse.ArgumentParser()
parser.add_argument('--originals', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
data = json.loads((args.originals / 'index.json').read_text(encoding='utf-8'))
args.output.mkdir(parents=True, exist_ok=False)
groups = {}
for row in data['frames']:
    groups.setdefault(row['resource'], []).append(row)
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 15)
small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 12)
title = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 20)
pages = []
for resource, rows in sorted(groups.items()):
    chunks = [rows[i:i+48] for i in range(0, len(rows), 48)]
    for page, chunk in enumerate(chunks):
        columns = min(8, len(chunk))
        cw, ch = 150, 205
        canvas = Image.new('RGB', (max(600, columns*cw), 70 + math.ceil(len(chunk)/columns)*ch), '#18222b')
        draw = ImageDraw.Draw(canvas)
        draw.text((12, 9), f'{resource} | original references | {page+1}/{len(chunks)}', font=title, fill='#edf5fb')
        draw.text((12, 38), 'Diagnostic palette; geometry only. Numbers are resource frame IDs. PNGs retain native canvases.', font=small, fill='#b9cbd7')
        for i, row in enumerate(chunk):
            x, y = (i%columns)*cw, 70+(i//columns)*ch
            path = args.originals / row['path']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == row['png_sha256'], row['id']
            im = Image.open(path).convert('RGBA')
            scale = min(4.0, 138/im.width, 163/im.height)
            size = (max(1,round(im.width*scale)),max(1,round(im.height*scale)))
            preview = im.resize(size, Image.Resampling.NEAREST)
            draw.rectangle((x+2,y+2,x+cw-3,y+ch-3), fill='#e5e5dd', outline='#6a737c')
            canvas.paste(preview,(x+(cw-size[0])//2,y+4+(165-size[1])//2),preview)
            label = f'{row["frame"]:03}' if row['frame'] is not None else 'screen'
            draw.text((x+8,y+169), f'{label}  {im.width}x{im.height}', font=font, fill='#15202a')
            draw.text((x+8,y+189), f'view x{scale:.2f}',font=small,fill='#34495a')
        filename = f'{resource}-{page+1:02}.png'
        canvas.save(args.output / filename)
        pages.append({'resource':resource,'page':page+1,'path':filename,'frames':[r['id'] for r in chunk],
                      'sha256':hashlib.sha256((args.output / filename).read_bytes()).hexdigest()})
(args.output/'index.json').write_text(json.dumps({'source_index_sha256':hashlib.sha256((args.originals/'index.json').read_bytes()).hexdigest(),'pages':pages},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'resources':len(groups),'pages':len(pages),'frames':len(data['frames'])}))
