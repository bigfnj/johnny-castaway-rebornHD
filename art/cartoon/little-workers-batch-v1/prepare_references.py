"""Prepare exact little-worker drawings and enlarged inspection copies."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INV = HERE.parent / 'character-inventory-v1'
GROUPS = json.loads((HERE / 'selection.json').read_text(encoding='utf-8'))
COUNT = sum(map(len, GROUPS.values()))

def pin(path):
    return {'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')

def main():
    archive = INV / 'reference-originals.zip'
    index_path = INV / 'source/frame-index.json'
    map_path = INV / 'scene-map/resource-map.json'
    index = json.loads(index_path.read_text(encoding='utf-8'))
    mapping = json.loads(map_path.read_text(encoding='utf-8'))
    lookup = {(r['resource'], r['frame']): r for r in index['frames']}
    resources = {r['resource']: r for r in mapping['resources']}
    rows, contacts = [], []
    with zipfile.ZipFile(archive) as zipped:
        for resource, frames in GROUPS.items():
            group_rows = []
            for frame in frames:
                source = lookup[(resource, frame)]
                raw = zipped.read(source['path'])
                assert hashlib.sha256(raw).hexdigest() == source['png_sha256'], source['id']
                original = HERE / f'reference/original/{resource}/{frame:03}.png'
                nearest = HERE / f'reference/nearest8/{resource}/{frame:03}.png'
                original.parent.mkdir(parents=True, exist_ok=True)
                nearest.parent.mkdir(parents=True, exist_ok=True)
                original.write_bytes(raw)
                with Image.open(io.BytesIO(raw)) as im:
                    im.resize((im.width*8, im.height*8), Image.Resampling.NEAREST).save(nearest)
                actions = [{k:a[k] for k in ('ttm','tag','description','scope')}
                           for a in resources[resource]['unique_slot_frame_actions'] if frame in a['frames']]
                row = {'id': source['id'], 'resource':resource, 'frame':f'{frame:03}',
                       'canvas':source['canvas'], 'archive_member':source['path'],
                       'original':pin(original), 'nearest8':pin(nearest),
                       'source_rgba_sha256':source['rgba_sha256'],
                       'static_frame_attribution':actions}
                rows.append(row)
                group_rows.append(row)
            for page, start in enumerate(range(0, len(group_rows), 12), 1):
                subset = group_rows[start:start+12]
                sheet = Image.new('RGB', (1200, ((len(subset)+3)//4)*250), '#dfe7ec')
                draw = ImageDraw.Draw(sheet)
                for n, row in enumerate(subset):
                    with Image.open(ROOT / row['original']['path']) as im:
                        im = im.convert('RGBA')
                        scale = max(1, min(8, 280//im.width, 210//im.height))
                        im = im.resize((im.width*scale, im.height*scale), Image.Resampling.NEAREST)
                        sheet.paste(im, (n%4*300+(300-im.width)//2, n//4*250+30+(210-im.height)//2), im)
                    draw.text((n%4*300+8,n//4*250+8), f"{resource} {row['frame']}", fill='black')
                dest = HERE / f'reference/{resource}-contact-{page:02}.png'
                sheet.save(dest)
                contacts.append(pin(dest))
    assert len(rows) == COUNT
    provenance = {'archive':pin(archive), 'frame_index':pin(index_path),
                  'scene_map':pin(map_path), 'preparation':pin(Path(__file__))}
    source = {'schema_version':1, 'count':COUNT, 'scope':'Exact source drawings for a new appearance review',
              'palette_limit':index['palette_limit'], **provenance, 'contacts':contacts, 'assets':rows}
    save(HERE / 'reference/source.json', source)
    plan = {'schema_version':1, 'target_new_drawings':COUNT, 'user_batch_default':[60,72],
            'resources':GROUPS, 'source_record':pin(HERE/'reference/source.json'),
            'groups':GROUPS,
            'excluded':'Later LILIPUTS 072-101 are deferred to keep this review at72. No selected exact/mirror duplicates were found. See source notes.',
            'art_direction':'Exact original silhouettes, eye visibility, orientation, overlaps and prop placement govern each pose. Shared Cartoon keys control material identity only.',
            'approval':None, 'native_validation':False,
            'workflow':'Built-in image generation, one call per drawing, exact saved requests and untouched raw outputs. Appearance review now; native placement and bulk testing later.',
            'attribution_limit':'Static source associations do not establish native timing. No consecutive-frame animation is fabricated.'}
    save(HERE/'batch-plan.json', plan)
    print(f'Prepared {COUNT} exact source drawings and inspection copies.')

if __name__ == '__main__':
    main()
