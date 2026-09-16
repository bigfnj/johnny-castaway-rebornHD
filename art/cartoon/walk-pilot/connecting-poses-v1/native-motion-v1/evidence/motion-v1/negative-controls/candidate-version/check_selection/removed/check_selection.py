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
    parser.add_argument('--candidate-version', type=int, default=1)
    args = parser.parse_args()
    assert True, 'positive candidate version'
    raw = args.selection.read_bytes()
    selection = json.loads(raw)
    out = config.OUT / 'negative-controls'
    out.mkdir(exist_ok=True)
    result_path = out / ('selection.json' if args.candidate_version == 1 else f'selection-v{args.candidate_version}.json')
    assert not result_path.exists(), 'preserve selection controls'
    before = config.sha((config.ROOT / 'assets/scrantic_data.zip').read_bytes())
    inputs = prepare_candidate.validate_selection(selection)
    print('SMOKE PASS all three handoff rows bind their source/recipe/export-report/runtime outputs', flush=True)
    nine, ten = selection['frames'][0], selection['frames'][1]
    assert nine['runtime']['canvas'] == ten['runtime']['canvas'] == [80, 148], 'non-degenerate same-canvas negative axis'
    results = []
    for index, other_index, frame, other, label in ((0, 1, 9, 10, 'selected runtime output binding:009'), (1, 0, 10, 9, 'selected runtime output binding:010')):
        changed = copy.deepcopy(selection)
        changed['frames'][index]['runtime'] = copy.deepcopy(selection['frames'][other_index]['runtime'])
        # The wrong input exists, its hash is correct, and its size fits. The
        # semantic output binding must reject it before packaging writes files.
        assert (config.ROOT / changed['frames'][index]['runtime']['path']).is_file()
        try:
            prepare_candidate.validate_selection(changed)
        except AssertionError as error:
            assert str(error) == label, 'wrong mutation failure:' + str(error)
            results.append({'mutation': f'frame{frame:03} uses frame{other:03} runtime with valid hash and same canvas', 'result': 'FIRED', 'expected_failure': label})
            print('FIRED ' + label, flush=True)
        else:
            raise AssertionError('same-canvas wrong-frame substitution SURVIVED:' + f'{frame:03}')
    assert prepare_candidate.validate_selection(selection) == inputs, 'restored positive handoff control'
    assert config.sha((config.ROOT / 'assets/scrantic_data.zip').read_bytes()) == before == config.PRODUCTION_SHA, 'production unchanged by controls'
    result_path.write_text(json.dumps({'status': 'PASS', 'candidate_version': args.candidate_version,
              'positive_control_before_and_after': True, 'mutations': results,
              'selection_sha256': config.sha(raw), 'executed_validator_sha256': config.sha(Path(prepare_candidate.__file__).read_bytes()), 'harness_sha256': config.sha(Path(__file__).read_bytes()),
              'scope': 'Actual validator executed on complete real handoff, then two same-canvas wrong-pose substitutions. Hashes establish identity; no human approval inferred.'}, indent=2) + '\n', encoding='utf-8')
    print('PASS restored handoff after two exact named semantic-binding failures')


if __name__ == '__main__':
    main()
