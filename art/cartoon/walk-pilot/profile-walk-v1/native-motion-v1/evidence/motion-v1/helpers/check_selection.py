"""Positive handoff validation then executed same-canvas wrong-pose negatives."""
import argparse
import copy
import json
from pathlib import Path
import config
import prepare_candidate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--selection', type=Path, required=True)
    args = parser.parse_args()
    raw = args.selection.read_bytes()
    selection = json.loads(raw)
    out = config.OUT / 'negative-controls'
    out.mkdir(exist_ok=True)
    result_path = out / 'selection.json'
    assert not result_path.exists(), 'preserve selection controls'
    before = config.sha((config.ROOT / 'assets/scrantic_data.zip').read_bytes())
    inputs = prepare_candidate.validate_selection(selection)
    print('SMOKE PASS all eight handoff rows bind their source/recipe/export-report/runtime outputs', flush=True)
    one, five = selection['frames'][0], selection['frames'][4]
    assert one['runtime']['canvas'] == five['runtime']['canvas'] == [96, 144], 'non-degenerate same-canvas negative axis'
    results = []
    for frame, other, label in ((1, 5, 'selected runtime output binding:001'), (5, 1, 'selected runtime output binding:005')):
        changed = copy.deepcopy(selection)
        changed['frames'][frame - 1]['runtime'] = copy.deepcopy(selection['frames'][other - 1]['runtime'])
        # The wrong input exists, its hash is correct, and its size fits. The
        # semantic output binding must reject it before packaging writes files.
        assert (config.ROOT / changed['frames'][frame - 1]['runtime']['path']).is_file()
        try:
            prepare_candidate.validate_selection(changed)
        except AssertionError as error:
            assert str(error) == label, 'wrong mutation failure:' + str(error)
            results.append({'mutation': f'frame{frame:03} uses frame{other:03} runtime with valid hash and same canvas', 'result': 'FIRED', 'expected_failure': label})
            print('FIRED ' + label, flush=True)
        else:
            raise AssertionError('same-canvas wrong-frame substitution SURVIVED')
    assert prepare_candidate.validate_selection(selection) == inputs, 'restored positive handoff control'
    assert config.sha((config.ROOT / 'assets/scrantic_data.zip').read_bytes()) == before == config.PRODUCTION_SHA, 'production unchanged by controls'
    result_path.write_text(json.dumps({'status': 'PASS', 'positive_control_before_and_after': True, 'mutations': results,
              'selection_sha256': config.sha(raw), 'executed_validator_sha256': config.sha(Path(prepare_candidate.__file__).read_bytes()), 'harness_sha256': config.sha(Path(__file__).read_bytes()),
              'scope': 'Actual validator executed on complete real handoff, then two same-canvas wrong-pose substitutions. Hashes establish identity; no human approval inferred.'}, indent=2) + '\n', encoding='utf-8')
    print('PASS restored handoff after two exact named semantic-binding failures')


if __name__ == '__main__':
    main()
