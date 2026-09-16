"""Prepare two private original-art diagnostics; never change production assets."""
import hashlib
import copy
import json
from pathlib import Path
import shutil
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'assets/scrantic_data.zip').is_file())
OUT = ROOT/'build/skin-tone/contact018-review-v1'
OLD = ROOT/'build/skin-tone/native-review'
BASE_SHA = 'bdc62b0c34835196e6dfa6541ee54f9c72f9824a0c24a0beab4bee3a33393eaf'
sha = lambda b: hashlib.sha256(b).hexdigest()
save = lambda p, o: p.write_text(json.dumps(o, indent=2)+'\n', encoding='utf-8')

def main():
    assert not OUT.exists(), 'preserve existing contact018 diagnostic'
    source = OLD/'candidate-v2/scrantic_data.zip'
    assert sha(source.read_bytes()) == BASE_SHA, 'corrected private source archive'
    build = json.loads((OLD/'baseline-v1/build.json').read_bytes())
    exe = OLD/'baseline-v1/connecting_walk_probe'
    assert sha(exe.read_bytes()) == build['executable_sha256'], 'unchanged native observer executable'
    for path, digest in build['protected_sha256'].items():
        assert sha((ROOT/path).read_bytes()) == digest, 'protected original source:' + path
    OUT.mkdir(parents=True)
    shutil.copyfile(exe, OUT/'connecting_walk_probe')
    shutil.copyfile(OLD/'route_driver.c', OUT/'route_driver.c')
    shutil.copyfile(OLD/'baseline-v1/build.json', OUT/'original-build.json')
    packages = {}
    supplied = {f'data/{name}': (Path('C:/JohnCast/SIERRA/SCRANTIC')/name).read_bytes() for name in ('RESOURCE.MAP','RESOURCE.001')}
    omitted018 = {f'data/{root}/BMP/JOHNWALK.BMP/018.png' for root in ('hd','styles/cartoon')}
    with zipfile.ZipFile(source) as base:
        names = base.namelist()
        assert len(names) == len(set(names)) == 2594, 'unique corrected archive members'
        for kind in ('original_scene', 'original_johnny'):
            removed = sorted(n for n in names if n.lower().endswith('.png') and n.startswith(('data/hd/','data/styles/'))) if kind == 'original_scene' else sorted(omitted018)
            assert set(removed) <= set(names), 'existing diagnostic removals'
            path = OUT/(kind+'.zip')
            with zipfile.ZipFile(path, 'w') as output:
                for info in base.infolist():
                    if info.filename not in removed:
                        output.writestr(copy.copy(info), supplied.get(info.filename, base.read(info.filename)))
            with zipfile.ZipFile(path) as result:
                retained = {n: sha(result.read(n)) for n in result.namelist()}
                assert set(retained) == set(names)-set(removed), 'exact removal-only member set'
                assert all(result.read(n) == supplied.get(n, base.read(n)) for n in retained), 'every retained payload unchanged except explicit supplied resources'
                assert json.loads(result.read('data/hd/manifest.json'))['scale'] == 2, 'original fallback retains native2x scale'
                if kind == 'original_scene':
                    assert not any(n.lower().endswith('.png') and n.startswith(('data/hd/','data/styles/')) for n in retained), 'no raster overrides remain'
                else:
                    assert not (omitted018 & set(retained)), 'both018 override paths absent'
            packages[kind] = {'archive_sha256': sha(path.read_bytes()), 'style': 'hd' if kind=='original_scene' else 'cartoon',
                              'removed_members': removed, 'retained_members_sha256': retained,
                              'supplied_resource_replacements_sha256': {n:sha(b) for n,b in supplied.items()}}
    refs = {}
    for phase in ('smoke','full'):
        folder = OUT/'current'/phase
        folder.mkdir(parents=True)
        original = OLD/'candidate-v2/front_arc'/phase
        for name in ('report.json','capture.log'):
            shutil.copyfile(original/name, folder/name)
        refs[phase] = {name: sha((folder/name).read_bytes()) for name in ('report.json','capture.log')}
    save(OUT/'preparation.json', {'status':'PASS','source_archive':source.relative_to(ROOT).as_posix(),'source_archive_sha256':BASE_SHA,
        'packages':packages,'executable_sha256':build['executable_sha256'],'driver_sha256':sha((OUT/'route_driver.c').read_bytes()),
        'original_build_sha256':sha((OUT/'original-build.json').read_bytes()),'reference_capture_sha256':refs,
        'protected_sha256':build['protected_sha256'],'prepare_sha256':sha(Path(__file__).read_bytes()),
        'scope':'Supplied original RESOURCE.MAP/.001 rendered by the port at2x, not DOSBox or original-executable parity; private override removals and exactly two original-resource replacements.'})
    print('PASS two private fallback packages, all retained payloads exact, unchanged observer and source')

if __name__ == '__main__':
    main()
