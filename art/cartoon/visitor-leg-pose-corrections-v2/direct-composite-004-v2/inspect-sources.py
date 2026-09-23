from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ART = HERE.parents[1]
sources = {
    '004-upper': ART / 'mermaid-expression-corrections-v1/generation/SSUZY1.BMP/004-generated-v2.png',
    '003-lower': HERE.parent / 'generation/SSUZY1.BMP/003-generated-v2.png',
}
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 19)
for name, path in sources.items():
    source = Image.open(path).convert('RGBA')
    canvas = Image.new('RGBA', source.size, '#eeeae0')
    canvas.alpha_composite(source)
    draw = ImageDraw.Draw(canvas)
    for x in range(0, source.width, 100):
        draw.line((x, 0, x, source.height), fill=(0, 70, 130, 100), width=1)
        for y in range(100, source.height, 200):
            draw.text((x + 2, y + 2), f'{x},{y}', fill='#164771', font=font, stroke_width=1, stroke_fill='white')
    for y in range(0, source.height, 100):
        draw.line((0, y, source.width, y), fill=(0, 70, 130, 100), width=1)
    canvas.convert('RGB').save(HERE / f'{name}-grid.jpg')
