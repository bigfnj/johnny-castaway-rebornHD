"""Ordered single-frame checks with data controls and an executed source guard mutant."""
import argparse
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from PIL import Image

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('shading_export', HERE / 'export.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
ROOT = e.ROOT
OUT = HERE / 'candidates/v1'

def require(value, message):
    if not value:
        raise AssertionError(message)

def rgba(raw):
    with Image.open(io.BytesIO(raw)) as im:
        return im.convert('RGBA')

def check_output(outputs, report):
    require(set(outputs) == set(report['outputs_sha256']), 'output set differs')
    for name, raw in outputs.items():
        require(e.sha(raw) == report['outputs_sha256'][name], name + ': output identity differs')
    im = rgba(outputs['BMP/BACKGRND.BMP/007.png'])
    require(im.size == (384, 256), '007: canvas differs')
    require(e.shading(im)['alpha8_dark_max_rgb_lt100'] == 0, '007: visible dark fringe')

def refuse(call, message):
    try:
        call()
    except (ValueError, AssertionError) as exc:
        require(message in str(exc), 'wrong failure: ' + str(exc))
        return str(exc)
    raise AssertionError('damaged input survived: ' + message)

def run(phase):
    report = json.loads((OUT / 'export-report.json').read_bytes())
    recipe = json.loads((HERE / 'recipe-v1.json').read_bytes())
    outputs = {name: (OUT / name).read_bytes() for name in report['outputs_sha256']}
    rows = []
    def passed(name, detail=None):
        rows.append({'name': name, 'status': 'PASS', 'detail': detail})
    source = e.source(e.SOURCE.read_bytes())
    require(source.size == (1536, 1024), 'source canvas')
    passed('pinned-source-canvas')
    require(recipe == e.prepared(), 'recipe binding')
    check_output(outputs, report)
    passed('recipe-runtime-identities')
    require(report['cropped_filtered_alpha']['nonzero_pixels'] == 0 and
            report['audit_cropped_filtered_alpha']['nonzero_pixels'] == 0, 'filtered crop')
    require(report['uniform_resample_count'] == 1 and report['changed_frames'] == [7], 'scope')
    passed('complete-source-fit-and-single-frame-scope')
    if phase == 'regression':
        replay, replay_report = e.render(recipe)
        require(replay == outputs and e.encode(replay_report) == (OUT / 'export-report.json').read_bytes(), 'exact replay')
        passed('exact-output-report-replay')
        # Verify this adapter against the old selected source, including all four PNGs.
        old_source = e.FROZEN.parent / '007-v2-raw.png'
        with Image.open(old_source) as old:
            old_outputs, _ = e.render_source(old.convert('RGBA'))
        require(all(raw == (e.OLD / name).read_bytes() for name, raw in old_outputs.items()), 'ancestor transform parity')
        passed('old-source-exact-transform-parity-four-pngs')
        dark = {}
        for key, path in [('old007', old_source), ('new007', e.SOURCE),
                          ('neighbor006', e.FROZEN.parent / '006-raw.png'),
                          ('neighbor008', e.FROZEN.parent / '008-raw.png')]:
            with Image.open(path) as im:
                dark[key] = {'sha256': e.sha(path.read_bytes()), **e.shading(im.convert('RGBA'))}
        require(dark['old007']['alpha8_dark_max_rgb_lt100'] == 123597, 'old007 dark witness')
        require(all(dark[k]['alpha8_dark_max_rgb_lt100'] == 0 for k in ('new007', 'neighbor006', 'neighbor008')), 'new/neighbor dark witness')
        passed('independent-visible-dark-fringe-comparison', dark)
        parent, _, _, _, ground = e.helpers()
        unmasked = rgba(outputs['audit/007-unmasked.png'])
        actual = rgba(outputs['BMP/BACKGRND.BMP/007.png'])
        changed_alpha = 0
        for y in range(256):
            for x in range(384):
                before, after = unmasked.getpixel((x, y)), actual.getpixel((x, y))
                gx, gy = x + 696 - 540, y + 548 - 548
                ga = ground.getpixel((gx, gy))[3] if 0 <= gx < ground.width and 0 <= gy < ground.height else 0
                require(before[:3] == after[:3], 'mask changed RGB')
                require(after[3] == (before[3] * (255 - ga) + 127) // 255, 'world alpha mask mismatch')
                changed_alpha += before[3] != after[3]
        require(changed_alpha > 0, 'mask axis degenerate')
        passed('all-runtime-pixels-mask-rgb-and-nondegenerate-alpha', {'changed_alpha_pixels': changed_alpha})
        require(len(recipe['unchanged_sibling_pngs']) == 9, 'nine siblings')
        for name, digest in recipe['unchanged_sibling_pngs'].items():
            require(e.sha((e.OLD / name).read_bytes()) == digest, name + ' changed')
        passed('all-nine-sibling-pngs-unchanged')
        failures = []
        bad = source.copy()
        bad.putpixel((700, 550), (1, 2, 3, 255))
        buf = io.BytesIO()
        bad.save(buf, format='PNG')
        failures.append({'name': 'changed-source-rgba', 'failure': refuse(lambda: e.source(buf.getvalue()), 'selected raw identity differs')})
        for key, value in [('frame', 6), ('source_sha256', '0' * 64), ('source_to_world_affine', [.25, 0, 697, 0, .25, 548]),
                           ('footprint', {'id': 'cartoon-island-center-foam-v1', 'canvas': [384, 255], 'offset_hd': [-32, -90]})]:
            damaged = copy.deepcopy(recipe)
            damaged[key] = value
            failures.append({'name': 'changed-recipe-' + key, 'failure': refuse(lambda: e.render(damaged), 'source/registration contract differs')})
        for kind, pixel in [('rgb', (1, 2, 3, 255)), ('alpha', (255, 255, 255, 1))]:
            damaged = dict(outputs)
            im = actual.copy()
            im.putpixel((180, 145), pixel)
            buf = io.BytesIO()
            im.save(buf, format='PNG')
            damaged['BMP/BACKGRND.BMP/007.png'] = buf.getvalue()
            failures.append({'name': 'damaged-runtime-' + kind, 'failure': refuse(lambda: check_output(damaged, report), '007.png: output identity differs')})
        edge = Image.new('RGBA', (1536, 1024))
        edge.paste((255, 255, 255, 255), (0, 0, 24, 24))
        failures.append({'name': 'filtered-alpha-outside-complete-source-crop', 'failure': refuse(lambda: e.render_source(edge), 'footprint crops filtered foam alpha')})
        passed('eight-reachable-damaged-input-controls', failures)
        scratch_root = ROOT / 'build/shoreline-repair-v1/foam-shading-v1'
        scratch_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='guard-', dir=scratch_root) as folder:
            scratch = Path(folder)
            code = (HERE / 'export.py').read_text()
            guarded = "require(sha(raw) == SOURCE_SHA, '007: selected raw identity differs')"
            require(code.count(guarded) == 1, 'mutation location')
            mutant = scratch / 'mutant.py'
            mutant.write_text(code.replace(guarded, 'pass # deliberate source identity guard removal'), encoding='utf-8')
            damaged_path = scratch / 'damaged.png'
            damaged_path.write_bytes(buf.getvalue())
            # Use a valid full-size altered raw, not a canvas failure, to reach this guard.
            bad.save(damaged_path)
            witness = "import importlib.util,hashlib,pathlib,sys;s=importlib.util.spec_from_file_location('m',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);print('WITNESS '+hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest(),flush=True);m.source(pathlib.Path(sys.argv[2]).read_bytes());raise AssertionError('selected raw identity guard removed: damaged source survived')"
            result = subprocess.run([sys.executable, '-B', '-c', witness, str(mutant), str(damaged_path)], capture_output=True, text=True,
                                    creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=30)
            output = result.stdout + result.stderr
            require(result.returncode != 0 and 'WITNESS ' + e.sha(mutant.read_bytes()) in output and
                    'damaged source survived' in output, 'source mutant not reached')
            passed('fresh-process-source-guard-removal-fired', {'mutant_sha256': e.sha(mutant.read_bytes()), 'output': output})
        require(e.source(e.SOURCE.read_bytes()).size == (1536, 1024), 'restored source')
        check_output(outputs, report)
        passed('restored-source-and-output-positive')
    return {'schema_version': 1, 'phase': phase, 'status': 'PASS', 'checks': rows,
            'exporter_sha256': e.sha((HERE / 'export.py').read_bytes()),
            'harness_sha256': e.sha(Path(__file__).read_bytes()), 'recipe_sha256': e.sha((HERE / 'recipe-v1.json').read_bytes()),
            'report_sha256': e.sha((OUT / 'export-report.json').read_bytes()),
            'limits': 'Static source/export validation only. Image generation can change geometry; this does not assert alpha identity with the earlier drawing or native scene approval.'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['smoke', 'regression'], required=True)
    args = parser.parse_args()
    path = HERE / ('verification-' + args.phase + '.json')
    require(not path.exists(), 'verification: refusing overwrite')
    result = run(args.phase)
    path.write_bytes(e.encode(result))
    print('PASS ' + args.phase + ' ' + str(len(result['checks'])) + ' checks; ' + e.sha(path.read_bytes()))

if __name__ == '__main__':
    main()
