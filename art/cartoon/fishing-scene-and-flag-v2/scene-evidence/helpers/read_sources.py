import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'tools'))
import inventory_scenes as parser

probe = Path('D:/.ai-work/projects/johnny-castaway-rebornHD/build/Release/jc_uncompress_test.exe')
archive = ROOT/'assets/scrantic_data.zip'
with zipfile.ZipFile(archive) as z:
    mapping = z.read('data/RESOURCE.MAP')
    volume = z.read('data/RESOURCE.001')
_, resources = parser.resource_catalog(mapping, volume)
result = {'archive_sha256': parser.digest(archive.read_bytes()), 'map_sha256': parser.digest(mapping), 'volume_sha256': parser.digest(volume), 'probe_sha256': parser.digest(probe.read_bytes()), 'resources': {}}
for name in ['MJFISH.TTM', 'MJFISHC.TTM', 'FISHING.ADS']:
    r = resources[name]
    parser.metadata(r)
    parser.decode(r, probe)
    result['resources'][name] = {k: v for k, v in r.items() if not k.startswith('_')}
    result['resources'][name]['commands'] = r['_commands']
result['palettes'] = [{'name': r['name'], 'payload_sha256': r['payload_sha256'], 'payload_hex': r['_payload'].hex()} for r in resources.values() if r['type']=='PAL']
out = Path(__file__).with_name('source-scene.json')
out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(out)
for name, r in result['resources'].items():
    wanted = [26, 29] if name=='MJFISH.TTM' else [49] if name=='MJFISHC.TTM' else list(range(1,9))
    print(name, r['decoded_sha256'])
    for c in r['commands']:
        if c['tag'] in wanted and (name.endswith('ADS') or c['command'] in ['SET_DELAY','TIMER','PURGE','GOTO_TAG','SET_COLORS','SET_PALETTE_SLOT','LOAD_PALETTE']):
            print(c)
print('PALETTES', result['palettes'])
