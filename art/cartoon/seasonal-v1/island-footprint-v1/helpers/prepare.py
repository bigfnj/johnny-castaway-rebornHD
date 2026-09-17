from pathlib import Path
import copy
import hashlib
import io
import json
import zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sha=lambda raw:hashlib.sha256(raw).hexdigest()
source=ROOT/'assets/scrantic_data.zip'
assert sha(source.read_bytes())=='4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'
pair=json.loads((ROOT/'art/cartoon/character-inventory-v1/source/source.json').read_bytes())['source']['resource_sha256']
original=Path('C:/JohnCast/SIERRA/SCRANTIC')
replacements={'data/'+name:(original/name).read_bytes() for name in pair}
assert all(sha(replacements['data/'+name])==digest for name,digest in pair.items())
assert not (OUT/'original-full.zip').exists()
with zipfile.ZipFile(source) as z,zipfile.ZipFile(OUT/'original-full.zip','w',compression=zipfile.ZIP_DEFLATED) as target:
    kept={};removed=[]
    for entry in z.infolist():
        name=entry.filename
        if name.endswith('.png') and (name.startswith('data/hd/') or name.startswith('data/styles/')):
            removed.append(name)
            continue
        raw=replacements.get(name,z.read(name))
        target.writestr(copy.copy(entry),raw)
        kept[name]=sha(raw)
images=OUT/'images'
images.mkdir()
reference=ROOT/'art/cartoon/character-inventory-v1/reference-originals.zip'
with zipfile.ZipFile(reference) as z,zipfile.ZipFile(source) as current:
    for i in [0,1,2,3,4,5,6,7,8,9,10,11,30,31,32,33,34,35,36,37,38,39,40,41]:
        name=f'BACKGRND.BMP/{i:03}.png'
        raw=z.read('native/BMP/'+name)
        (images/f'original-BACKGRND-{i:03}.png').write_bytes(raw)
        (images/f'hd-BACKGRND-{i:03}.png').write_bytes(current.read('data/hd/BMP/'+name))
        member='data/styles/cartoon/BMP/'+name
        if member in current.namelist():
            (images/f'cartoon-BACKGRND-{i:03}.png').write_bytes(current.read(member))
    for i in range(4):
        name=f'HOLIDAY.BMP/{i:03}.png'
        (images/f'original-HOLIDAY-{i:03}.png').write_bytes(z.read('native/BMP/'+name))
        (images/f'hd-HOLIDAY-{i:03}.png').write_bytes(current.read('data/hd/BMP/'+name))
driver=(ROOT/'art/cartoon/seasonal-v1/native/driver.c').read_text()
for before,after in [('argc != 5 || !artStyleSelect("cartoon")','argc != 7 || !artStyleSelect(argv[5])'),
                     ('    islandState.holiday = holiday;','    islandState.lowTide = atoi(argv[6]);\n    islandState.holiday = holiday;')]:
    assert driver.count(before)==1
    driver=driver.replace(before,after)
(OUT/'driver.c').write_text(driver,encoding='utf-8',newline='\n')
report={'production_sha256':sha(source.read_bytes()),'original_full_sha256':sha((OUT/'original-full.zip').read_bytes()),
        'supplied_resource_pair_sha256':pair,'removed_pngs':len(removed),'retained_members_sha256':kept,
        'driver_sha256':sha((OUT/'driver.c').read_bytes()),'source_driver_sha256':sha((ROOT/'art/cartoon/seasonal-v1/native/driver.c').read_bytes()),
        'scope':'Scratch-only original-art package: supplied resource pair, all override PNGs absent. HD manifest retained to render source pixels at2x. Unchanged native renderer, not original executable or palette-parity proof.'}
(OUT/'preparation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS supplied-original package prepared; all overrides removed; source images extracted')
