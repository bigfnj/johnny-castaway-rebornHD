"""Append corrected source annotations without altering captured inputs or pixels."""
import copy
import hashlib
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
SHORE = HERE.parents[2]
PACKAGE = ROOT/'build/shoreline-repair-v1/side-clean-selected-v2'
BASE = ROOT/'build/shoreline-repair-v1/offshore-selected-v1/candidate.zip'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin(path):
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}


def main():
    original = PACKAGE/'export-report.json'
    historical = json.loads(original.read_bytes())
    corrected = copy.deepcopy(historical)
    corrected['schema_version'] = 2
    corrected['kind'] = 'metadata-clarification-only'
    corrected['captured_selection'] = pin(original)
    corrected['captured_preparation'] = pin(PACKAGE/'preparation.json')
    corrected['candidate_archive'] = pin(PACKAGE/'candidate.zip')
    corrected['scope'] = 'Corrected raw ancestry/identity annotations for integration. Exact captured runtime payloads and package unchanged; human approval pending.'
    source_proofs = []
    with zipfile.ZipFile(BASE) as before, zipfile.ZipFile(PACKAGE/'candidate.zip') as after, zipfile.ZipFile(ROOT/'assets/scrantic_data.zip') as production:
        for row in corrected['frames']:
            f = row['frame']
            member = 'data/styles/cartoon/'+row['path']
            old_sha = hashlib.sha256(before.read(member)).hexdigest()
            new_sha = hashlib.sha256(after.read(member)).hexdigest()
            assert row['sha256'] == new_sha and sha(ROOT/row['source_path']) == new_sha
            assert row['previous_selected_png_sha256'] == old_sha
            row['byte_identical_to_selected'] = old_sha == new_sha
            assert row['byte_identical_to_selected'] == (f in (0,6,8))
            if f in (3,4,5,9,10,11):
                recipe = SHORE/'side-fit-v1/recipe-v1.json'
                report = SHORE/'side-fit-v1/candidates/v1/export-report.json'
                assert hashlib.sha256(production.read(row['source_member'])).hexdigest() == row['source_member_sha256']
                source = {'archive':pin(ROOT/'assets/scrantic_data.zip'),'member':row['source_member'],'sha256':row['source_member_sha256']}
            else:
                folder = SHORE/'foam-shading-v1' if f == 7 else SHORE/'foam-refresh-v1' if f in (6,8) else SHORE
                recipe = folder/('recipe-v2.json' if f in (6,8) else 'recipe-v1.json')
                report = folder/('candidates/v2/export-report.json' if f in (6,8) else 'candidates/v1/export-report.json')
                recipe_data = json.loads(recipe.read_bytes())
                if f == 0:
                    row['source'],row['source_sha256'] = recipe_data['source'],recipe_data['source_sha256']
                elif f == 7:
                    row['source'] = (SHORE/'foam-shading-v1/007-raw-v1.png').relative_to(ROOT).as_posix()
                    row['source_sha256'] = 'bccf1e15c476c78ed7ffb6f842eaa001c763eff4209c63b3d47162097c5fa8f2'
                assert sha(ROOT/row['source']) == row['source_sha256']
                source = {'path':row['source'],'sha256':row['source_sha256']}
            row['authoring_recipe'] = pin(recipe)
            row['authoring_report'] = pin(report)
            source_proofs.append({'frame':f,'source':source,'runtime_sha256':new_sha,'baseline_sha256':old_sha,
                                  'byte_identical_to_selected':row['byte_identical_to_selected'],'result':'PASS'})
    destination = HERE/'corrected-selection-v2.json'
    assert not destination.exists()
    destination.write_text(json.dumps(corrected,indent=2)+'\n',encoding='utf-8',newline='\n')
    record = {'schema_version':1,'status':'PASS','captured_selection':pin(original),'corrected_selection':pin(destination),
              'helper_sha256':sha(Path(__file__)),'correction':'007 raw path/hash now bind foam-shading-v1; identity flag false. Explicit identity flags for all ten rows: seven changed, three unchanged.',
              'pixel_and_package_changes':0,'frames':source_proofs,
              'historical_issue':'Captured row007 inherited the preceding raw path/hash and true identity annotation even though runtime/source_path and package/output checks bound the correct new007.'}
    (HERE/'metadata-clarification.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    assert sha(original) == record['captured_selection']['sha256']
    print(json.dumps({'status':'PASS','corrected_selection_sha256':sha(destination),'clarification_sha256':sha(HERE/'metadata-clarification.json')}))


if __name__ == '__main__':
    main()
