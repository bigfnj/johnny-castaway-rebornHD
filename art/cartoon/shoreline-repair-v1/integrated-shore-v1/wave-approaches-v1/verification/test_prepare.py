"""Fresh isolated packer checks; never run the historical writer on its live output."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from PIL import Image

HERE = Path(__file__).resolve().parent
BUNDLE = HERE.parent
ROOT = BUNDLE.parents[4]
BUILDER = BUNDLE / 'prepare.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=('smoke', 'regression'), required=True)
    args = parser.parse_args()
    output = HERE / (args.phase+'.json')
    require(not output.exists(), 'verification output already exists')
    manifest = json.loads((BUNDLE/'manifest.json').read_bytes())
    require(manifest['builder_sha256'] == sha(BUILDER), 'published builder identity differs')
    source = BUILDER.read_text(encoding='utf-8')
    records, repeats, folders = {}, {}, {}
    result = {'schema_version':1,'phase':args.phase,'status':'RUNNING','test_sha256':sha(Path(__file__)),
              'builder_sha256':sha(BUILDER),'published_manifest_sha256':sha(BUNDLE/'manifest.json'),
              'scope':'Isolated writer reproduction and actual guard-removal controls; no native recaptures.',
              'checks':[],'executions':[],'negative_controls':[]}
    count = 0
    for key, panel in manifest['panels'].items():
        report_path = ROOT/panel['native_report']
        require(sha(report_path) == panel['native_report_sha256'], key+': source report hash')
        folder = report_path.parent
        repeated = folder.parent/'repeat/report.json'
        require(sha(repeated) == panel['fresh_repeat_report_sha256'], key+': repeat report hash')
        records[key] = json.loads(report_path.read_bytes())
        repeats[key] = json.loads(repeated.read_bytes())
        folders[key] = folder
        for name, record in panel['images'].items():
            require(sha(folder/name) == record['source_sha256'], key+'/'+name+': native PNG digest')
            require(sha(BUNDLE/key/name) == record['crop_sha256'], key+'/'+name+': crop PNG digest')
            native = Image.open(folder/name).convert('RGBA')
            crop = Image.open(BUNDLE/key/name).convert('RGBA')
            require(native.crop((520,470,1200,750)).tobytes() == crop.tobytes(), key+'/'+name+': exact cropped pixels')
            count += 1
    result['checks'] += [f'All {count} unique published PNG crops preserve native pixels exactly', 'All three report/repeat/source/crop hashes match current manifest']
    if args.phase == 'regression':
        smoke = json.loads((HERE/'smoke.json').read_bytes())
        require(smoke['status'] == 'PASS' and smoke['builder_sha256'] == sha(BUILDER), 'smoke must pass first on current builder')
        result['smoke_sha256'] = sha(HERE/'smoke.json')
        scratch = ROOT/'build/shoreline-repair-v1/review-packer-controls'
        scratch.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='run-',dir=scratch) as temp:
            work = Path(temp)
            launcher = work/'launch.py'
            launcher.write_text("import hashlib,importlib.util,json,sys\nfrom pathlib import Path\np=Path(sys.argv[1]); out=Path(sys.argv[2]); root=Path(sys.argv[3]); inputs=json.loads(Path(sys.argv[4]).read_bytes())\ns=importlib.util.spec_from_file_location('executed_packer',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)\nm.HERE=out; m.ROOT=root; out.mkdir(parents=True)\nprint('WITNESS packer '+hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)\nm.prepare({k:Path(v) for k,v in inputs.items()})\n",encoding='utf-8')

            def fixture(label, changed=None):
                case = work/label
                case.mkdir()
                current, repeated = copy.deepcopy(records), copy.deepcopy(repeats)
                if changed:
                    changed(current,repeated)
                inputs = {}
                for key, report in current.items():
                    folder = case/key/'smoke'
                    folder.mkdir(parents=True)
                    (folder.parent/'repeat').mkdir()
                    inputs[key] = str(folder)
                    if report == records[key]:
                        shutil.copyfile(folders[key]/'report.json',folder/'report.json')
                    else:
                        write_json(folder/'report.json',report)
                    if repeated[key] == repeats[key]:
                        shutil.copyfile(folders[key].parent/'repeat/report.json',folder.parent/'repeat/report.json')
                    else:
                        write_json(folder.parent/'repeat/report.json',repeated[key])
                    for name in manifest['panels'][key]['images']:
                        shutil.copyfile(folders[key]/name,folder/name)
                path = case/'inputs.json'
                write_json(path,inputs)
                return case,path,current,repeated

            def execute(label, script, inputs, out, expected):
                command = [sys.executable,'-B',str(launcher),str(script),str(out),str(ROOT),str(inputs)]
                proc = subprocess.run(command,cwd=ROOT,text=True,capture_output=True)
                record = {'label':label,'executed_script_sha256':sha(script),'returncode':proc.returncode,
                          'stdout':proc.stdout,'stderr':proc.stderr.replace(str(work),'<scratch>').replace(str(ROOT),'<repo>')}
                result['executions'].append(record)
                require('WITNESS packer '+sha(script) in proc.stdout,label+': executed digest absent')
                require(proc.returncode == expected,label+': unexpected exit')
                return proc

            def positive(label):
                case,inputs,_,_ = fixture(label)
                execute(label,BUILDER,inputs,case/'out',0)
                reproduced = json.loads((case/'out/manifest.json').read_bytes())
                for key in reproduced['panels']:
                    reproduced['panels'][key]['native_report'] = manifest['panels'][key]['native_report']
                require(reproduced == manifest,label+': manifest content differs beyond redirected source paths')
                for key,panel in manifest['panels'].items():
                    for name in panel['images']:
                        require((case/'out'/key/name).read_bytes() == (BUNDLE/key/name).read_bytes(),label+': PNG bytes differ')
                return sha(case/'out/manifest.json')

            positive('positive-before')
            result['checks'].append('Fresh writer reproduces all crop bytes and manifest fields except explicit scratch source locations')

            def timing(a,b):
                a['offshore']['displays'][1]['time_ms'] += 1
                b['offshore']['displays'] = copy.deepcopy(a['offshore']['displays'])

            def phases(a,b):
                for key in a:
                    for row in a[key]['displays']:
                        row['phases'] = [7 if f == 8 else f for f in row['phases']]
                    b[key]['displays'] = copy.deepcopy(a[key]['displays'])

            def repeat_rows(a,b):
                b['original']['displays'][1]['time_ms'] += 1

            def repeat_status(a,b):
                b['original']['status'] = 'FAIL'

            def loop(a,b):
                initial = a['original']['displays'][0]['phases']
                for key in a:
                    rows = [r for r in a[key]['displays'] if r['time_ms'] == 1440]
                    require(bool(rows),'loop control needs actual1440 row')
                    rows[-1]['phases'] = list(initial)
                    rows[-1]['phases'][0] = 6 + (initial[0]-6+1)%3
                    b[key]['displays'] = copy.deepcopy(a[key]['displays'])

            controls = [
                ('timing',timing,'offshore: native timing or poses differ',"        elif schedule != current:\n            raise ValueError(key + ': native timing or poses differ')"),
                ('phase-omission',phases,'original: wave phases missing',"        if {f for r in rows for f in r['phases'] if f >= 0} != set(range(3, 12)):\n            raise ValueError(key + ': wave phases missing')"),
                ('repeat-row',repeat_rows,'original: fresh native repeat differs',"        if rows != repeat_report['displays']:\n            raise ValueError(key + ': fresh native repeat differs')"),
                ('repeat-status',repeat_status,'original: fresh native repeat did not pass',"        if repeat_report['status'] != 'PASS':\n            raise ValueError(key + ': fresh native repeat did not pass')"),
                ('png-digest',None,None,"            if sha(image_raw) != row['png_sha256']:\n                raise ValueError(key + '/' + name + ': source PNG hash differs')"),
                ('loop-closure',loop,'original: 1440 ms does not close the observed wave cycle',"    if not at_loop or at_loop[-1]['phases'] != initial:\n        raise ValueError('original: 1440 ms does not close the observed wave cycle')")]
            for label,change,message,guard in controls:
                case,inputs,current,repeated = fixture(label,change)
                if label == 'png-digest':
                    name = current['original']['displays'][0]['file']
                    target = case/'original/smoke'/name
                    image = Image.open(target).convert('RGBA')
                    pixel = image.getpixel((600,600))
                    image.putpixel((600,600),((pixel[0]+1)%256,*pixel[1:]))
                    image.save(target)
                    message = 'original/'+name+': source PNG hash differs'
                proc = execute(label+'-guarded',BUILDER,inputs,case/'refused',1)
                require(proc.stderr.count('ValueError: ') == 1 and proc.stderr.rstrip().endswith('ValueError: '+message),label+': wrong named failure')
                require(source.count(guard) == 1,label+': guard occurrence')
                indent = guard[:len(guard)-len(guard.lstrip())]
                replacement = indent+'# Executed isolated '+label+' guard-removal control\n'+indent+'pass'
                # elif cannot become a standalone pass between if branches.
                if label == 'timing':
                    replacement = "        elif schedule != current:\n            pass  # Executed isolated timing guard-removal control"
                mutant = case/'mutant.py'
                mutant.write_text(source.replace(guard,replacement),encoding='utf-8')
                execute(label+'-guard-removed',mutant,inputs,case/'accepted',0)
                require((case/'accepted/manifest.json').exists(),label+': mutant did not package')
                result['negative_controls'].append({'name':label,'result':'FIRED','named_failure':message,
                    'removed_guard':guard,'mutant_sha256':sha(mutant),'accepted_manifest_sha256':sha(case/'accepted/manifest.json'),
                    'input_report_sha256':{k:sha(case/k/'smoke/report.json') for k in current},
                    'repeat_report_sha256':{k:sha(case/k/'repeat/report.json') for k in current},
                    'proof':'Actual original fails once; actual guard-removed copied source emits its digest and accepts the same corrupted fixture.'})
            positive('positive-after')
            result['checks'].append('Original positive reproduction restored after all six isolated guard removals')
    result['status'] = 'PASS'
    write_json(output,result)
    print(json.dumps({'status':'PASS','phase':args.phase,'checks':len(result['checks']),'controls':len(result['negative_controls']),'sha256':sha(output)}))


if __name__ == '__main__':
    main()
