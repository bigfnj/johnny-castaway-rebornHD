"""Comparison-only offshore phases on the common complete-source footprint."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

from PIL import Image

HERE = Path(__file__).resolve().parent
ANCESTOR = HERE / 'export.py'
ANCESTOR_SHA = 'b4f3e3c8f79a22977da78051b89d34fd4201f4fae1f137007523aa23543b2bd5'
WORLD = [696, 548, 1080, 804]
FOOTPRINT = {'id': 'cartoon-island-center-foam-v1', 'canvas': [384, 256], 'offset_hd': [-32, -90]}


def load():
    if hashlib.sha256(ANCESTOR.read_bytes()).hexdigest() != ANCESTOR_SHA:
        raise ValueError('export.py: frozen comparison ancestor differs')
    spec = importlib.util.spec_from_file_location('offshore_comparison_ancestor', ANCESTOR)
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    prior.WORLD = WORLD
    prior.FOOTPRINT = FOOTPRINT
    original_source_row = prior.source_row

    def source_row(frame):
        row = original_source_row(frame)
        row.update(canvas=FOOTPRINT['canvas'], asset_offset_hd=FOOTPRINT['offset_hd'])
        return row

    def render_frame(frame):
        parent, base, mask, _, ground = prior.inputs()
        row = source_row(frame)
        source = Image.open(prior.ROOT / row['source']).convert('RGBA')
        # Same complete-source audit and single frozen filter call as v1.
        padded = base.resample(source, [392, 264], [.25, 0, 4, 0, .25, 4])
        audit = padded.crop((32, 32, 424, 296))
        foam = audit.crop((4, 4, 388, 260))
        outside = audit.copy()
        outside.paste((0, 0, 0, 0), (4, 4, 388, 260))
        crop_stats = parent.stats(outside)
        base.require(crop_stats['nonzero_pixels'] == 0, f'{frame:03}: footprint crops filtered foam alpha')
        audit_outside = padded.copy()
        audit_outside.paste((0, 0, 0, 0), (32, 32, 424, 296))
        base.require(parent.stats(audit_outside)['nonzero_pixels'] == 0, f'{frame:03}: audit crops filtered raw alpha')
        retained, visibility = mask.occlude(foam, ground, WORLD[:2], parent.WORLD_BOX)
        parent.validate_foam_only(foam, retained, f'{frame:03}')
        return {'runtime': base.png(retained), 'unmasked': base.png(foam),
                'padded': base.png(padded), 'audit': base.png(audit)}, {
            **row, 'sha256': base.sha(base.png(retained)), 'uniform_resample_count': 1,
            'raw_alpha8_bounds': source.getchannel('A').point(lambda a: 255 if a >= 8 else 0).getbbox(),
            'raw_alpha_outside_footprint': {'nonzero_pixels': 0, 'alpha8_pixels': 0, 'max_alpha': 0, 'alpha_sum': 0},
            'cropped_filtered_alpha': crop_stats, 'source_coverage': parent.stats(foam),
            'retained_coverage': parent.stats(retained), 'visibility_measurements': visibility}

    prior.source_row = source_row
    prior.render_frame = render_frame
    return prior


def prepared(prior):
    recipe = prior.prepared()
    recipe.update(comparison_exporter_ancestor_sha256=ANCESTOR_SHA,
                  source_window=[0, 0, 1536, 1024],
                  extent_reason='Common full-source footprint for both offshore and incoming-wash comparisons; prior 356x102 result remains historical.')
    return recipe


def render(recipe):
    prior = load()
    _, base, _ = prior.helpers()
    base.require(recipe == prepared(prior), 'recipe: full-source common footprint contract differs')
    # Reuse the frozen output assembly with its own narrow recipe contract.
    outputs, report = prior.render(prior.prepared())
    report.update(exporter_sha256=base.sha(Path(__file__).read_bytes()),
                  comparison_exporter_ancestor_sha256=ANCESTOR_SHA,
                  recipe_sha256=base.sha(base.encode(recipe)))
    return outputs, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare', action='store_true')
    parser.add_argument('--recipe', type=Path, default=HERE / 'recipe-v2.json')
    parser.add_argument('--output', type=Path, default=HERE / 'candidates/v2')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print('WITNESS offshore-full-source ' + hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    try:
        prior = load()
        _, base, _ = prior.helpers()
        if args.prepare:
            base.require(not args.recipe.exists(), 'recipe: refusing overwrite')
        recipe = prepared(prior) if args.prepare else json.loads(args.recipe.read_bytes())
        outputs, report = render(recipe)
        outputs['export-report.json'] = base.encode(report)
        if not args.check:
            base.require(not args.output.exists(), 'output: refusing overwrite')
            args.output.mkdir(parents=True)
        for name, raw in outputs.items():
            path = args.output / name
            if args.check:
                base.require(path.read_bytes() == raw, name + ': reproduced bytes differ')
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
        if args.prepare:
            args.recipe.write_bytes(base.encode(recipe))
        print('PASS ' + json.dumps({'files': len(outputs), 'footprint': FOOTPRINT}))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print('FAIL ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
