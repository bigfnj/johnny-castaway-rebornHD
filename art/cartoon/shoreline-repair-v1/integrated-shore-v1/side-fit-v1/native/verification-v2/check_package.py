"""Bounded seven-member package replay and an executed007 payload guard mutation."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
NATIVE = HERE.parent
ROOT = next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
sys.path.insert(0,str(NATIVE))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    spec = importlib.util.spec_from_file_location('executed_combined',path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute(module, baseline, candidate):
    print('WITNESS combined-package '+sha(module),flush=True)
    result = load(module).package_pair(baseline,candidate)
    print('PASS combined-package '+result['candidate_sha256'],flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--preparation',type=Path)
    p.add_argument('--work',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--execute-module',type=Path)
    a = p.parse_args()
    if a.execute_module:
        execute(a.execute_module,a.baseline,a.candidate)
        return
    assert a.preparation and a.work and a.output
    assert not a.work.exists() and not a.output.exists()
    a.work.mkdir(parents=True)
    module = NATIVE/'combined.py'
    source_hash = sha(module)
    c = load(module)
    record = json.loads(a.preparation.read_bytes())
    assert c.package_pair(a.baseline,a.candidate) == record['package_pair']
    assert c.center_support(a.baseline,a.candidate) == json.loads((ROOT/record['center_support']['path']).read_bytes())
    rows = []

    def run(name, script, archive, expected_error=None):
        command = [sys.executable,'-B',str(Path(__file__)), '--execute-module',str(script),
                   '--baseline',str(a.baseline),'--candidate',str(archive)]
        result = subprocess.run(command,capture_output=True,text=True)
        witness = 'WITNESS combined-package '+sha(script)
        assert witness in result.stdout, name+' executed source witness'
        if expected_error:
            assert result.returncode != 0 and result.stderr.count(expected_error) == 1, name+' named refusal'
        else:
            assert result.returncode == 0 and 'PASS combined-package ' in result.stdout, name+' positive acceptance'
        rows.append({'name':name,'executed_source_sha256':sha(script),'candidate_sha256':sha(archive),
                     'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr,
                     'result':'FIRED' if expected_error else 'PASS'})

    run('positive_before',module,a.candidate)
    from PIL import Image
    altered = a.work/'wrong007.zip'
    with zipfile.ZipFile(a.candidate) as z:
        original = z.read(c.member(7))
        image = Image.open(io.BytesIO(original)).convert('RGBA')
        xy = next((x,y) for y in range(image.height) for x in range(image.width) if image.getpixel((x,y))[3] > 0)
        pixel = image.getpixel(xy)
        image.putpixel(xy,(pixel[0]^1,*pixel[1:]))
        buffer = io.BytesIO();image.save(buffer,format='PNG',compress_level=9)
        with zipfile.ZipFile(altered,'w') as out:
            for info in z.infolist():
                out.writestr(info,buffer.getvalue() if info.filename == c.member(7) else z.read(info.filename))
    run('changed007_refused',module,altered,'ValueError: side native: 007 combined selected export payload')
    source = module.read_text()
    guard = "require(after[member(f)] == row['sha256'], f'{f:03} combined selected export payload')"
    assert source.count(guard) == 1
    mutated = source.replace(guard,"require(True, f'{f:03} combined selected export payload')")
    mutant = a.work/'combined_guard_disabled.py'
    mutant.write_text(mutated,encoding='utf-8',newline='\n')
    run('guard_disabled_corrupt007_accepted',mutant,altered)
    run('restored_positive',module,a.candidate)
    assert sha(module) == source_hash
    output = {'schema_version':1,'status':'PASS','phase':'regression','package_pair':record['package_pair'],
              'source_sha256':source_hash,'harness_sha256':sha(Path(__file__)),
              'exact_center_support_replay':'PASS','runs':rows,
              'mutation':{'guard':guard,'mutant_sha256':sha(mutant),'corrupt_archive_sha256':sha(altered),
                          'pixel':list(xy),'before_rgba':list(pixel),'after_rgba':list(image.getpixel(xy))},
              'scope':'Fresh processes execute exact source digests. Corrupt007 retains all membership and canvases; sole payload guard removal admits it; restored source accepts the selected archive.'}
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8',newline='\n')
    (a.output.parent/'combined_guard_disabled.py').write_bytes(mutant.read_bytes())
    print('PASS four fresh-process package checks and exact support replay')


if __name__ == '__main__':
    main()
