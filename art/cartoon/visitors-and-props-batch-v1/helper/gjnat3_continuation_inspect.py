from pathlib import Path
import json
from PIL import Image, ImageDraw
here=Path(__file__).resolve().parent.parent
root=here.parents[2]
out=root/'build/visitors-continuation'
out.mkdir(parents=True,exist_ok=True)
frames=[f'{i:03}' for i in range(19,32)]+['050','051']
rows=[]
for page in range(3):
    sheet=Image.new('RGB',(1000,1250),'#e5e8eb')
    d=ImageDraw.Draw(sheet)
    for n,f in enumerate(frames[page*5:page*5+5]):
        v=2 if f=='031' else 1
        for col,p in enumerate([here/'reference/nearest8/GJNAT3.BMP'/f'{f}.png',here/'generation/GJNAT3.BMP'/f'{f}-generated-v{v}.png']):
            im=Image.open(p).convert('RGBA')
            im.thumbnail((470,220),Image.Resampling.NEAREST if col==0 else Image.Resampling.LANCZOS)
            sheet.paste(im,(col*500+(500-im.width)//2,n*250+25+(220-im.height)//2),im)
            d.text((col*500+10,n*250+6),f+' original' if col==0 else f+' draft v'+str(v),fill='black')
    sheet.save(out/f'contact-{page+1}.png')
for f in frames:
    v=2 if f=='031' else 1
    rec=json.loads((here/'generation/GJNAT3.BMP'/f'{f}-record-v{v}.json').read_text())
    rows.append({'frame':f,'version':v,'output':rec['output'],'image':rec['image']})
(out/'summary.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
