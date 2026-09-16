"""Check published input identities on copies before freezing motion evidence."""
import json
from pathlib import Path
import shutil
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'assets/scrantic_data.zip').is_file())
HERE = ROOT / 'art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1'
sys.path.insert(0, str(HERE))
import config
import preserve_motion

publication = config.load_json(config.OUT / 'publication.json')
preserve_motion.checkpoint_identity(config.OUT, publication)
print('SMOKE PASS published HTML, selection and all full reports match checked identities')
out = config.OUT / 'negative-controls/preservation-readback'
out.mkdir(parents=True, exist_ok=False)
fixture = out / 'fixture'
review, candidate = publication['review_directory'], publication['candidate_directory']
names = [f'{review}/review.html', f'{review}/review-record.json', f'{review}/browser-validation.json',
         f'{candidate}/preparation.json', f'{candidate}/candidate-selection.json']
names += [f'{base}/{clip}/full/report.json' for base in ('baseline-v1', candidate) for clip in config.CLIPS]
for name in names:
    target = fixture / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config.OUT / name, target)
preserve_motion.checkpoint_identity(fixture, publication)
results = []
cases = [(f'{review}/review.html', 'preserve published HTML identity'),
         (f'{candidate}/candidate-selection.json', 'preserve captured selection identity'),
         (f'{candidate}/front_arc/full/report.json', 'preserve captured full report:candidate:front_arc')]
for index, (name, witness) in enumerate(cases):
    path = fixture / name
    original = path.read_bytes()
    if path.suffix == '.html':
        changed = original + b' '
    else:
        record = json.loads(original)
        record['audit_mutation'] = 'valid JSON, deliberately different exact bytes'
        changed = (json.dumps(record, indent=2) + '\n').encode()
    path.write_bytes(changed)
    (out / ('changed-' + str(index) + path.suffix)).write_bytes(changed)
    try:
        preserve_motion.checkpoint_identity(fixture, publication)
    except AssertionError as error:
        assert str(error) == witness, str(error)
        results.append({'input': name, 'result': 'FIRED', 'expected_failure': witness, 'mutated_sha256': config.sha(changed)})
        print('FIRED ' + witness)
    else:
        raise AssertionError('published input alteration SURVIVED:' + name)
    path.write_bytes(original)
    preserve_motion.checkpoint_identity(fixture, publication)
preserve_motion.checkpoint_identity(config.OUT, publication)
record = {'status': 'PASS', 'smoke_passed': 1, 'mutations': results, 'restored_positives': 3,
          'publication_sha256': config.sha((config.OUT / 'publication.json').read_bytes()),
          'executed_preserver_sha256': config.sha((HERE / 'preserve_motion.py').read_bytes()),
          'harness_sha256': config.sha(Path(__file__).read_bytes()),
          'original_inputs_sha256': {name: config.sha((config.OUT / name).read_bytes()) for name in names},
          'scope': 'Actual preservation identity checker executed on published inputs and isolated copies. Changed valid HTML/selection/report bytes fail named checks, each restored positive passes. No actual review, publication, candidate or historical evidence edited.'}
(out / 'result.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8', newline='\n')
print('PASS final published readback; ' + config.sha((out / 'result.json').read_bytes()))
