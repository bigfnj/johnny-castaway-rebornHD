"""Render diagnostic composites only; raw generated assets stay unchanged."""
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
BATCH = HERE.parents[1]
VERSIONS = {8: 2} if HERE.name == 'SMDATE4.BMP' else {}
COUNT = 9 if HERE.name == 'SMDATE4.BMP' else 12

for tone, color in [('light', '#eeeae2'), ('dark', '#18303b')]:
    for start in [0, 8]:
        sheet = Image.new('RGBA', (1600, 880), color)
        draw = ImageDraw.Draw(sheet)
        for n in range(start, min(COUNT, start + 8)):
            version = VERSIONS.get(n, 1)
            col, row = (n-start) % 4, (n-start) // 4
            x, y = col * 400, row * 440
            draw.text((x+10,y+8), f'{HERE.name} {n:03} v{version}', fill='black' if tone == 'light' else 'white')
            with Image.open(HERE / f'{n:03}-generated-v{version}.png') as im:
                tile = im.convert('RGBA')
                bounds = tile.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox()
                tile = tile.crop(bounds)
                tile.thumbnail((250, 395), Image.Resampling.LANCZOS)
                sheet.alpha_composite(tile, (x+5+(250-tile.width)//2, y+30+(395-tile.height)//2))
            with Image.open(BATCH / 'reference/original' / HERE.name / f'{n:03}.png') as im:
                tile = im.convert('RGBA')
                tile.thumbnail((130, 240), Image.Resampling.NEAREST)
                scale = min(130/tile.width, 240/tile.height)
                tile = tile.resize((int(tile.width*scale),int(tile.height*scale)),Image.Resampling.NEAREST)
                sheet.alpha_composite(tile, (x+262, y+50+(330-tile.height)//2))
        out = HERE / f'inspection-{tone}-{start:03}.png'
        sheet.convert('RGB').save(out)
        print(out)
