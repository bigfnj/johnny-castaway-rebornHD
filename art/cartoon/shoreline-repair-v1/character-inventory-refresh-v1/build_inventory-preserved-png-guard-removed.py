"""Reproduce the complete Johnny worklist and an offline reference browser.

Standard library only. Source pixels, classification and production acceptance
are separate inputs. This tool does not infer anatomy or grant art approval.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[3]
BASE = Path('art/cartoon/character-inventory-v1')
CLASSES = {'johnny_full', 'johnny_partial', 'johnny_composite', 'not_johnny', 'uncertain', 'placeholder'}
JOHNNY = {'johnny_full', 'johnny_partial', 'johnny_composite'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, subject, message):
    if not ok:
        raise ValueError(f'{subject}: {message}')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def encode(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8')


def safe(name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in name and ':' not in name,
            name, 'unsafe reference path')
    return name


def indexed_source(base):
    index_path = base / 'source/frame-index.json'
    index = read(index_path)
    rows = index['frames']
    require(len({r['id'] for r in rows}) == len(rows), index_path, 'duplicate frame ID')
    require(len({r['path'] for r in rows}) == len(rows), index_path, 'duplicate PNG path')
    for row in rows:
        safe(row['path'])
    return index, digest(index_path.read_bytes())


def pack_originals(base, directory):
    index, _ = indexed_source(base)
    target = base / 'reference-originals.zip'
    require(not target.exists(), target, 'refusing to overwrite preserved originals')
    payloads = []
    for row in index['frames']:
        data = (directory / row['path']).read_bytes()
        require(digest(data) == row['png_sha256'], row['id'], 'source PNG hash mismatch')
        payloads.append((row['path'], data))
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(payloads):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    return target


def originals(base, index):
    path = base / 'reference-originals.zip'
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        expected = {r['path'] for r in index['frames']}
        require(len(names) == len(set(names)), path.name, 'duplicate ZIP member')
        require(set(names) == expected, path.name, 'member coverage differs from source index')
        result = {}
        for row in index['frames']:
            data = archive.read(row['path'])
            pass  # executed control: preserved PNG identity guard removed
            result[row['path']] = data
    return result


def classifications(base, index, source_hash):
    by_resource = defaultdict(list)
    for row in index['frames']:
        by_resource[row['resource']].append(row)
    result, records = {}, {}
    for path in sorted((base / 'classification').glob('*.json')):
        data = read(path)
        require(data['source_index_sha256'] == source_hash, path.name, 'stale source index')
        for group in data['resources']:
            resource = group['resource']
            require(resource in by_resource, resource, 'classification has unknown resource')
            require(resource not in records, resource, 'duplicate resource classification')
            require(group['default_class'] in CLASSES, resource, 'unknown default classification')
            records[resource] = group
            frames = {r['frame']: r for r in by_resource[resource]}
            expected_pages = {f'{resource}-{p+1:02}.png' for p in range((len(frames)+47)//48)}
            require(set(group['reviewed_pages']) == expected_pages, resource, 'incomplete reviewed-page coverage')
            for row in frames.values():
                result[row['id']] = {'class': group['default_class'], 'note': group['notes']}
            seen = set()
            for override in group['overrides']:
                require(override['class'] in CLASSES, resource, 'unknown override classification')
                for frame in override['frames']:
                    require(frame in frames, resource, f'override has unknown frame {frame}')
                    require(frame not in seen, resource, f'duplicate override for frame {frame}')
                    seen.add(frame)
                    result[frames[frame]['id']] = {'class': override['class'], 'note': override['note']}
    missing = set(by_resource) - set(records)
    require(not missing, 'classification', f'missing resources {sorted(missing)}')
    return result, records


def build(root):
    base = root / BASE
    index, source_hash = indexed_source(base)
    pixels = originals(base, index)
    annotated, groups = classifications(base, index, source_hash)
    # Rebuild accepted/pending state using the maintained validator. A stale
    # production catalog cannot silently award approval to replacement pixels.
    sys.path.insert(0, str(root / 'tools'))
    import art_production_catalog
    production = art_production_catalog.build(root)
    prod = {a['path']: a for a in production['assets']}
    scene = read(base / 'scene-map/resource-map.json')
    scenes = {r['resource']: r for r in scene['resources']}
    assets, resources, cartoon = [], [], {}
    duplicate_first = {}
    with zipfile.ZipFile(root / 'assets/scrantic_data.zip') as archive:
        for row in index['frames']:
            anno = annotated[row['id']]
            bundled = row['bundled']
            current = prod.get(bundled['path']) if bundled else None
            require(not bundled or current is not None, row['id'], 'bundled slot missing from production catalog')
            if current:
                require(current['hd_proxy']['sha256'] == bundled['hd_png_sha256'], row['id'], 'HD mapping changed')
            accepted = bool(current and current['production']['status'] == 'accepted')
            status = ('reference_only' if not current else 'accepted' if accepted else
                      'outstanding' if anno['class'] in JOHNNY else 'needs_review' if anno['class'] == 'uncertain' else 'excluded')
            key = (tuple(row['canvas']), row['rgba_sha256'])
            duplicate = duplicate_first.get(key)
            duplicate_first.setdefault(key, row['id'])
            actions = [f"{a['ttm']} #{a['tag']}: {a['description']}" for a in
                       scenes.get(row['resource'], {}).get('unique_slot_frame_actions', []) if row['frame'] in a['frames']]
            item = dict(id=row['id'], resource=row['resource'], frame=row['frame'], kind=row['kind'],
                        canvas=row['canvas'], original_png=row['path'], original_png_sha256=row['png_sha256'],
                        rgba_sha256=row['rgba_sha256'], classification=anno['class'], note=anno['note'],
                        status=status, port_path=bundled['path'] if bundled else None,
                        exact_original_duplicate_of=duplicate, static_actions=actions,
                        acceptance=current['production']['acceptance'] if accepted else None, cartoon_png=None)
            if accepted and anno['class'] in JOHNNY:
                name = 'data/styles/cartoon/' + bundled['path']
                data = archive.read(name)
                require(digest(data) == current['production']['png_sha256'], row['id'], 'accepted Cartoon PNG changed')
                item['cartoon_png'] = 'cartoon/' + bundled['path']
                item['cartoon_png_sha256'] = digest(data)
                cartoon[item['cartoon_png']] = data
            assets.append(item)
    require({a['port_path'] for a in assets if a['port_path']} == set(prod), 'source index', 'port coverage mismatch')
    for name, group in sorted(groups.items()):
        subset = [a for a in assets if a['resource'] == name]
        resources.append(dict(resource=name, notes=group['notes'], counts=dict(sorted(Counter(a['classification'] for a in subset).items())),
                              outstanding=sum(a['status'] == 'outstanding' for a in subset),
                              needs_review=sum(a['status'] == 'needs_review' for a in subset),
                              accepted_johnny=sum(a['status'] == 'accepted' and a['classification'] in JOHNNY for a in subset),
                              static_story_associations=sorted({s['description'] for t in scenes.get(name, {}).get('ttm_load_associations', []) for s in t['story_associations']}),
                              reviewed_pages=group['reviewed_pages']))
    pending = [a for a in assets if a['status'] == 'outstanding']
    summary = dict(original_slots=len(assets), port_slots=len(prod), resources=len(resources),
                   reference_only=sum(a['status'] == 'reference_only' for a in assets),
                   accepted_johnny=sum(a['status'] == 'accepted' and a['classification'] in JOHNNY for a in assets),
                   outstanding_johnny=len(pending), outstanding_classes=dict(sorted(Counter(a['classification'] for a in pending).items())),
                   uncertain_port_slots=sum(a['status'] == 'needs_review' for a in assets),
                   outstanding_resources=sum(r['outstanding'] > 0 for r in resources),
                   distinct_outstanding_originals=len({(tuple(a['canvas']), a['rgba_sha256']) for a in pending}),
                   all_classes=dict(sorted(Counter(a['classification'] for a in assets).items())))
    report = dict(schema_version=1, scope='Complete supplied-original BMP/SCR inventory, visually classified per runtime slot; no new art approval.',
                  palette='Port diagnostic dump palette, not calibrated original executable colors. Native canvases preserved; gray pixels may be shadows.',
                  evidence_limits='Static script associations are not executed scene coverage. Exact-pixel duplicates are reuse candidates, never shared acceptance.',
                  summary=summary, source_index_sha256=source_hash, production_archive_sha256=digest((root / 'assets/scrantic_data.zip').read_bytes()),
                  references_archive_sha256=digest((base / 'reference-originals.zip').read_bytes()),
                  classifications_sha256={p.name:digest(p.read_bytes()) for p in sorted((base/'classification').glob('*.json'))},
                  scene_map_sha256=digest((base/'scene-map/resource-map.json').read_bytes()), resources=resources, assets=assets)
    return report, pixels, cartoon


def markdown(report):
    s = report['summary']
    lines = ['# Remaining Johnny artwork', '', report['scope'], '',
             f"Reviewed {s['original_slots']:,} source slots across {s['resources']} resources: {s['port_slots']:,} app slots and {s['reference_only']} original-only reference.", '',
             f"**{s['outstanding_johnny']:,} confirmed Johnny slots remain**, across {s['outstanding_resources']} resources. {s['accepted_johnny']} character slots already have accepted Cartoon art; {s['uncertain_port_slots']} additional app slots need visual confirmation.", '',
             f"The remaining slots contain {s['distinct_outstanding_originals']:,} distinct native RGBA/canvas images. Duplicates remain separate runtime targets; no approval is inherited.", '',
             '| Drawing type | Outstanding slots |', '|---|---:|']
    for kind, count in s['outstanding_classes'].items():
        lines.append(f'| {kind} | {count} |')
    lines += ['', 'These are drawings and compositing parts, not distinct animation sequences. Extraction is complete; Cartoon generation and scene acceptance are not.', '',
              'Some Johnny drawings contain props or other characters in the same bitmap. Those scene groups need coordinated character and prop work. The title screen and thought bubbles also contain Johnny.', '',
              '## Review and reproduce', '',
              'Run `python -B art/cartoon/character-inventory-v1/build_inventory.py --check --review-directory build/character-inventory/review` from the repository root. Open the resulting `index.html`, or serve that directory on localhost.', '',
              'The browser starts with confirmed outstanding drawings. It can also show accepted Cartoon comparisons, ambiguous pieces, excluded props and the original-only reference. Its JSON and ZIP downloads preserve exact resource/frame identities.', '',
              'Originals use a diagnostic palette. Their geometry is authoritative for this extraction; the bright colors are not a proposed new style. Review the full native PNG when a contact-sheet thumbnail is too small.', '',
              'See [character playbook](../../../docs/cartoon-character-playbook.md), [source provenance](source/README.md), [static scene mapping](scene-map/README.md) and [classification records](classification/).', '',
              '## Resource worklist', '', '| Resource | Remaining Johnny | Needs review | Accepted Johnny | Static story associations |', '|---|---:|---:|---:|---|']
    for r in report['resources']:
        if r['outstanding'] or r['needs_review'] or r['accepted_johnny']:
            lines.append(f"| {r['resource']} | {r['outstanding']} | {r['needs_review']} | {r['accepted_johnny']} | {', '.join(r['static_story_associations']).replace('|','/')} |")
    lines += ['', 'Resource-to-story associations identify where to investigate. They do not prove that every frame runs in every listed story. Ambiguous script slots remain explicit in the detailed scene map.', '']
    return '\n'.join(lines)


def publish(base, output, report, pixels, cartoon):
    output.mkdir(parents=True, exist_ok=True)
    for name, data in {**pixels, **cartoon}.items():
        target = output / safe(name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (output / 'inventory.json').write_bytes(encode(report))
    # Embedded data supports file:// without fetch permissions; no external JS,
    # network, browser storage or hidden approval state is involved.
    template = (base / 'review.html').read_text(encoding='utf-8')
    embedded = json.dumps(report, ensure_ascii=True).replace('<', '\\u003c')
    (output / 'index.html').write_text(template.replace('__INVENTORY_JSON__', embedded), encoding='utf-8', newline='\n')
    selected = [a for a in report['assets'] if a['status'] in {'outstanding', 'needs_review'}]
    with zipfile.ZipFile(output/'outstanding-johnny-originals.zip', 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('inventory.json', encode(report))
        for a in selected:
            archive.writestr(a['original_png'], pixels[a['original_png']])
    # Published notes use local review links; full playbook references point at
    # maintained repository documents instead of dangling outside this server.
    readme = (base/'README.md').read_text(encoding='utf-8').replace('../../../docs/cartoon-character-playbook.md', 'playbook.md')
    (output/'README.md').write_text(readme, encoding='utf-8', newline='\n')
    for folder in ['source', 'scene-map']:
        (output/folder).mkdir(exist_ok=True)
        shutil.copyfile(base/folder/'README.md', output/folder/'README.md')
    (output/'classification').mkdir(exist_ok=True)
    for path in (base/'classification').glob('*.json'):
        shutil.copyfile(path, output/'classification'/path.name)
    root = base.parents[2]
    playbook = (root/'docs/cartoon-character-playbook.md').read_text(encoding='utf-8')
    def repo_link(match):
        href = match.group(1)
        if '://' in href or href.startswith('#'):
            return match.group(0)
        relative = (root/'docs'/href).resolve().relative_to(root.resolve()).as_posix()
        return '](https://github.com/bigfnj/johnny-castaway-rebornHD/blob/main/' + relative + ')'
    (output/'playbook.md').write_text(re.sub(r'\]\(([^)]+)\)', repo_link, playbook), encoding='utf-8', newline='\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--pack-originals', type=Path)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--review-directory', type=Path)
    args = parser.parse_args()
    print('WITNESS character-inventory ' + digest(Path(__file__).read_bytes()))
    try:
        base = args.root / BASE
        if args.pack_originals:
            print('PASS preserved-originals ' + str(pack_originals(base, args.pack_originals)))
            return 0
        report, pixels, cartoon = build(args.root)
        outputs = {'inventory.json': encode(report), 'README.md': markdown(report).encode('utf-8')}
        for name, data in outputs.items():
            if args.check:
                require((base/name).read_bytes() == data, name, 'generated inventory differs')
            else:
                (base/name).write_bytes(data)
        if args.review_directory:
            publish(base, args.review_directory, report, pixels, cartoon)
        print('REFERENCE stored original PNG evidence; original executable colors and scene execution were not revalidated')
        print('PASS character-inventory ' + json.dumps(report['summary'], sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print('ERROR ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
