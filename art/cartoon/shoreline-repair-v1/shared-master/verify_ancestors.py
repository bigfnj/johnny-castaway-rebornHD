"""Read back previously frozen export identities without running their writers."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
checked = {}


def check(relative, expected):
    actual = hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()
    assert actual == expected, relative + ': frozen bytes differ'
    checked[relative] = actual


prefix = 'art/cartoon/seasonal-v1/'
helpers = {'export.py':'7fe0e58d9a2522af71ddf696eccb1a76c6c5d293f71e0a3c8cab7282f336892d',
           'export_v2.py':'50aa0da6717af65bfe51593ac29da28ccb93d571d49ce0809031b0c89fb788e7',
           'export_v3.py':'261923eec27a9919a48384095246cb3fc122251ea27637bd50805ceb1c9ad024',
           'export_v4.py':'6a9959d7d97f86f5c2fcd0563b4d2ab71d651631dc679b9b870872ea25edcc82',
           'export_v5.py':'9ff87e42cb7433107ddb93d058f4e3725bf384764e729588bd17c5a29f073cb7'}
recipes = {1:'13a3363b72338c07bdb5d75d242a98a547bf688cf5daa676cc0a0ce0f3761d83',
           2:'68e8559a79a5abbf765d8cd6c8d9b7b1d45ff921a264e3aa174fed316ab57d38',
           3:'52baf948e79ff768627d37e5fce2de7a98db8d8c3c62d58c49e9a18a3019f139',
           4:'b3aadeabdce51590a0bc0414574dc285be59ab236d2aea7e12dee499ca2b82db',
           5:'5e60af35fd517663b4c0f3c4c26da97d61f81ccad807fadc5bb858c6ed3c848f'}
for name,checksum in helpers.items():
    check(prefix+name,checksum)
for version,checksum in recipes.items():
    recipe_path = prefix+f'recipe-v{version}.json'
    check(recipe_path,checksum)
    recipe = json.loads((ROOT/recipe_path).read_bytes())
    for row in recipe['frames']:
        check(prefix+row['source'],row['source_sha256'])
    report = json.loads((ROOT/prefix/f'candidates/v{version}/export-report.json').read_bytes())
    assert report['recipe_sha256'] == checksum
    helper = 'export.py' if version==1 else f'export_v{version}.py'
    assert report['exporter_sha256'] == helpers[helper]
    for name,digest in report['outputs_sha256'].items():
        check(prefix+f'candidates/v{version}/'+name,digest)

shore = 'art/cartoon/shoreline-repair-v1/'
check(shore+'export.py','f68a2869ff6519fe15f87e776f5c1b027270b4a5b979e9aaa94eccd154dbd264')
check(shore+'recipe-v1.json','c0b564613949ec1324b41dc15baceb7ce65d5606eeb21e2f6128e52278a29e62')
check(shore+'candidates/v1/export-report.json','2d152ba974242ff28332e9c438fa0e0a9629e94b88c856e896ffc5362127bda5')
aggregate = json.loads((ROOT/shore/'recipe-v1.json').read_bytes())
for row in aggregate['frames']:
    check(shore+row['recipe'],row['recipe_sha256'])
    check(shore+row['source'],row['source_sha256'])
    check(shore+row['export_report'],row['export_report_sha256'])
    report = json.loads((ROOT/shore/row['export_report']).read_bytes())
    output = Path(row['export_report']).parent.as_posix()+'/'
    for name,checksum in report['outputs_sha256'].items():
        check(shore+output+name,checksum)

new_recipe = json.loads((HERE/'recipe-v1.json').read_bytes())
for path_key,hash_key in [('source','source_sha256'),('reference','reference_sha256'),('archive','archive_sha256')]:
    check(new_recipe[path_key],new_recipe[hash_key])
report = {'status':'PASS','scope':'Exact readback of listed seasonal V1-V5 helpers, recipes, raw inputs and PNG outputs; frozen failed strip exports; selected master inputs and production archive. No historical writers executed and no whole-repository immutability claim.',
          'helper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'checked_files':len(checked),'files_sha256':dict(sorted(checked.items()))}
(HERE/'ancestor-verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'status':'PASS','checked_files':len(checked),'report_sha256':hashlib.sha256((HERE/'ancestor-verification.json').read_bytes()).hexdigest()}))
