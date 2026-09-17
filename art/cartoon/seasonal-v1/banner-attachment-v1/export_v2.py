"""Selected attachment registration: V5 plus (+2, -0.3) HD, scale unchanged.

Reuse the pinned trial adapter and its pinned original premultiplied filter.
The rejected fixed-registration V1/V2 artifacts remain unchanged.
"""
import hashlib
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ADAPTER_SHA = '749823dcd4a31ec352ce35e45cae72412807eabe4e9fafb7d258e7c245df400c'
RAW_SHA = 'd55a08ac62755c3ad3c13c72ca6bfed8fcd0fc6b000c9f12d798f60948744d84'
assert hashlib.sha256((HERE / 'export.py').read_bytes()).hexdigest() == ADAPTER_SHA
spec = importlib.util.spec_from_file_location('banner_attachment_fixed_trial', HERE / 'export.py')
trial = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trial)
original_prepare, original_render = trial.prepare, trial.render


def prepare(source):
    base = trial.load_base()
    base.require(source.resolve() == (HERE / 'raw-v2.png').resolve()
                 and trial.sha(source.read_bytes()) == RAW_SHA,
                 '003: selected attachment V2 source differs')
    recipe = original_prepare(source)
    row = recipe['frames'][0]
    row['affine_forward'][2] += 2
    row['affine_forward'][5] -= .3
    row['target_anchor'][0] += 2
    row['target_anchor'][1] -= .3
    recipe['scope'] = 'Attachment registration at unchanged scale; pending human native scene review.'
    recipe['registration_variant'] = {
        'delta_hd_vs_v5': [2, -.3], 'scale_unchanged': .23,
        'basis': 'V2 fixed placement clips 16 meaningful pixels left and 9 below. A 2 HD right shift and 0.3 HD upward shift retain meaningful alpha without shrinking.',
        'source_alpha8_center_valid_y_delta_hd': [-.655, -.265],
        'valid_y_interval': 'lower inclusive, upper exclusive',
        'filter_limit': 'Retain padded fringe; runtime permits only reported alpha below 8 outside.'}
    return recipe


def render(recipe, preview_only):
    outputs, report = original_render(recipe, preview_only)
    report['exporter_sha256'] = trial.sha(Path(__file__).read_bytes())
    report['reused_trial_exporter_sha256'] = ADAPTER_SHA
    report['registration_variant'] = recipe['registration_variant']
    return outputs, report


trial.prepare, trial.render = prepare, render

if __name__ == '__main__':
    print('WITNESS banner-registration ' + trial.sha(Path(__file__).read_bytes()))
    raise SystemExit(trial.main())
