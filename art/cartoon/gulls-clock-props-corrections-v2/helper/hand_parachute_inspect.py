from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
root=Path(__file__).resolve().parents[4]
old=root/'art/cartoon/gulls-clock-props-batch-v1'
new=root/'art/cartoon/gulls-clock-props-corrections-v2'
out=root/'build/clock-parachute-corrections'
out.mkdir(parents=True,exist_ok=True)
rows=[('THEEND1.BMP',f) for f in ['006','008','009']]
sheet=Image.new('RGB',(1200,900),'#dddddd')
d=ImageDraw.Draw(sheet)
for n,(res,f) in enumerate(rows):
    for col,path in enumerate([old/'reference/nearest8'/res/(f+'.png'),old/'generation'/res/(f+'-generated-v1.png')]):
        im=Image.open(path).convert('RGBA')
        im.thumbnail((570,250),Image.Resampling.NEAREST if col==0 else Image.Resampling.LANCZOS)
        x=col*600+(600-im.width)//2;y=n*300+35+(250-im.height)//2
        sheet.paste(im,(x,y),im)
        d.text((col*600+12,n*300+10),res+' '+f+(' original' if col==0 else ' prior'),fill='black')
sheet.save(out/'parachute-before.png')
rows=[('MEANWHIL.BMP',f) for f in ['013','014','015','016']]+[('THEEND1.BMP',f) for f in ['006','008','009']]
for page in range(2):
    subset=rows[page*4:(page+1)*4]
    sheet=Image.new('RGB',(1200,300*len(subset)),'#dddddd')
    d=ImageDraw.Draw(sheet)
    for n,(res,f) in enumerate(subset):
        for col,base in enumerate([old,new]):
            im=Image.open(base/'generation'/res/(f+'-generated-v1.png')).convert('RGBA')
            im.thumbnail((570,250),Image.Resampling.LANCZOS)
            x=col*600+(600-im.width)//2;y=n*300+35+(250-im.height)//2
            sheet.paste(im,(x,y),im)
            d.text((col*600+12,n*300+10),res+' '+f+(' prior' if col==0 else ' corrected'),fill='black')
    sheet.save(out/('correction-'+str(page+1)+'.png'))
