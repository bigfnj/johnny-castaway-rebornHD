"""Build non-destructive source/candidate contact sheets for visual inspection."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / 'review-data.json').read_text(encoding='utf-8'))
groups = {}
for row in data['assets']:
    groups.setdefault(row['resource'], []).append(row)
output = HERE / 'inspection'
output.mkdir(exist_ok=True)
for resource, rows in groups.items():
    for page, first in enumerate(range(0, len(rows), 12), 1):
        subset = rows[first:first + 12]
        sheet = Image.new('RGB', (1600, ((len(subset) + 3) // 4) * 430), '#e5e1d8')
        draw = ImageDraw.Draw(sheet)
        for index, row in enumerate(subset):
            x, y = index % 4 * 400, index // 4 * 430
            draw.rectangle((x, y, x + 399, y + 429), outline='#61737c')
            draw.text((x + 10, y + 8), row['key'] + ' v' + str(row['version']), fill='#142c3a')
            for kind, box in [('url', (x + 15, y + 30, 370, 280)), ('original_url', (x + 15, y + 325, 370, 90))]:
                if not row[kind]:
                    continue
                with Image.open(HERE / row[kind]) as opened:
                    im = opened.convert('RGBA')
                    bounds = im.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()
                    im = im.crop(bounds)
                    factor = min(box[2] / im.width, box[3] / im.height)
                    im = im.resize((max(1, round(im.width * factor)), max(1, round(im.height * factor))), Image.Resampling.LANCZOS if kind == 'url' else Image.Resampling.NEAREST)
                    sheet.paste(im, (box[0] + (box[2] - im.width) // 2, box[1] + (box[3] - im.height) // 2), im)
        destination = output / f'{resource}-{page:02}.png'
        sheet.save(destination)
        print(destination.name)
