"""Freeze compact native comparison evidence; images/ZIPs/executables stay local."""
import json
from pathlib import Path
import shutil
import zipfile
from capture import ROOT,HERE,sha,save,require,member

RUNS={
 'initial-static':ROOT/'build/shoreline-repair-v1/integrated-native-v1',
 'original':ROOT/'build/shoreline-repair-v1/original-cycle-v1',
 'offshore':ROOT/'build/shoreline-repair-v1/offshore-cycle-v1',
 'wash':ROOT/'build/shoreline-repair-v1/wash-cycle-v1'}

def main():
    target=HERE/'evidence'
    require(not target.exists(),'fresh durable evidence directory')
    target.mkdir();copied={};origins={}
    def copy(source,relative):
        destination=target/relative;destination.parent.mkdir(parents=True,exist_ok=True)
        raw=source.read_bytes();destination.write_bytes(raw);copied[relative]=sha(raw);origins[relative]=source.relative_to(ROOT).as_posix()
    for label,folder in RUNS.items():
        require(json.loads((folder/'captures/summary.json').read_bytes())['status']=='PASS','completed native evidence:'+label)
        for name in ('launch.json','launch.log'):copy(folder/name,label+'/'+name)
        for p in (folder/'captures').rglob('*'):
            if p.is_file() and p.suffix in ('.json','.log','.txt','.py','.c'):
                copy(p,label+'/captures/'+p.relative_to(folder/'captures').as_posix())
        if (folder/'helper-snapshot').is_dir():
            for p in (folder/'helper-snapshot').iterdir():copy(p,label+'/helper-snapshot/'+p.name)
    for label,folder in (('initial-static','integrated-selected-v1'),('offshore','offshore-selected-v1'),('wash','wash-selected-v1')):
        copy(ROOT/'build/shoreline-repair-v1'/folder/'preparation.json',label+'/preparation.json')
    control=ROOT/'build/shoreline-repair-v1/offshore-preparation-controls-v1'
    for p in control.rglob('*'):
        if p.is_file() and p.suffix in ('.json','.txt') and 'runtime' not in p.parts:
            copy(p,'preparation-controls/'+p.relative_to(control).as_posix())
    for p in HERE.iterdir():
        if p.is_file() and p.suffix in ('.py','.c','.md'):copy(p,'current-helpers/'+p.name)
    # Preserve the exact historical exception, found in a retained test source
    # copy. Its neighboring mutated files are deliberately not copied.
    historical=ROOT/'build/shoreline-repair-v1/footprint-tests/regression/mutant-draw-normal/source/src/engine/art_style.c'
    original_inputs=json.loads((RUNS['original']/'captures/inputs.json').read_bytes())
    require(sha(historical.read_bytes())==original_inputs['protected_sha256']['src/engine/art_style.c'],'exact historical original-capture source')
    copy(historical,'runtime-source/original-art_style.c')
    for name in ('src/engine/art_style.c','src/engine/art_style.h','src/engine/graphics.c','src/engine/island.c'):
        copy(ROOT/name,'runtime-source/current/'+name)
    reports={label:json.loads((folder/('captures/smoke/report.json' if label=='original' else 'captures/motion/high_clover/candidate/smoke/report.json')).read_bytes()) for label,folder in RUNS.items() if label!='initial-static'}
    keys=('ordinal','time_ms','segment','phases','johnny')
    traces={label:[[row[k] for k in keys] for row in report['displays']] for label,report in reports.items()}
    require(traces['original']==traces['offshore']==traces['wash'],'three-way native timelines exact')
    require(reports['original']['native_calls']==reports['offshore']['native_calls']==reports['wash']['native_calls'],'three-way public calls exact')
    archives={label:ROOT/'build/shoreline-repair-v1'/f'{label}-selected-v1/candidate.zip' for label in ('offshore','wash')}
    payloads={}
    for label,path in archives.items():
        with zipfile.ZipFile(path) as z:payloads[label]={n:sha(z.read(n)) for n in z.namelist()}
    require(set(payloads['offshore'])==set(payloads['wash']),'comparison archive members exact')
    changed=[n for n in payloads['offshore'] if payloads['offshore'][n]!=payloads['wash'][n]]
    require(set(changed)=={member(i) for i in (6,7,8)},'only center foam differs across Cartoon panels')
    # Full images are reproducible local products; their expected hashes remain
    # in the retained reports and the parent browser bundle, not in files_sha256.
    source_bindings={}
    for label,folder in RUNS.items():
        source_bindings[label]={'launch':folder.relative_to(ROOT).as_posix(),
          'summary_sha256':sha((folder/'captures/summary.json').read_bytes()),
          'images_binaries_archives_local_only':True}
    comparison={'status':'PASS','displays_per_panel':51,'duration_ms':2400,'real_wave_period_ms':1440,
      'timing_phase_johnny_calls_equal':True,'Cartoon_member_count':len(payloads['offshore']),
      'unchanged_Cartoon_members':len(payloads['offshore'])-len(changed),'changed_Cartoon_members':sorted(changed),
      'archives_sha256':{label:sha(path.read_bytes()) for label,path in archives.items()},
      'report_sha256':{label:sha((folder/('captures/smoke/report.json' if label=='original' else 'captures/motion/high_clover/candidate/smoke/report.json')).read_bytes()) for label,folder in RUNS.items() if label!='initial-static'}}
    save(target/'comparison.json',comparison);copied['comparison.json']=sha((target/'comparison.json').read_bytes())
    text='''# Native comparison verification

The original, offshore-ripple and wash-over-sand clips each retain 51 actual native display records over 2400 ms. Their display times, phase tuples, Johnny records and twenty public same-heading wait calls are identical. A complete wave cycle returns to its initial tuple at 1440 ms. No wave counters, timing holds, sprite coordinates or display pixels were invented.

Original source smoke and fresh-process repeat passed. Three deliberately damaged native logs failed the intended checks: missing phase 008, changed clover origin and changed display timing. The original package contains the supplied original resource pair, no replacement PNGs, and original clovers. HD selection provides nearest-neighbor 2x rendering through the port. Colors are diagnostic. This is not original-executable palette or timing proof.

Each Cartoon cycle passed smoke before a fresh-process exact repeat, plus six executed native controls: actual ground offset, actual center offset, initial phase tuple, observed time, an out-of-scope pixel and missing full-cycle phase coverage. Both archives keep the exact approved static ground and full-size V5 props. Their 2,598 named payloads differ only at 006/007/008; 2,595 payloads are identical. Two fresh Python preparation controls rejected a substitution of frame 008 for 006, which has the same canvas, and a changed ground PNG even after its local report hash was updated. These checks establish technical identity and capture behavior, not artistic approval.

The earlier initial-static checkpoint is retained as a smoke-only diagnostic of the approved island shape with old masked foam. Its center frame 008 had no pixels with alpha at least 8. It is not evidence of complete animation or tide compatibility. No low-tide, night/shift, all-holiday motion or walking regression matrix was run after the user requested the three-way high-tide comparison.

## Retained evidence and reconstruction

`evidence.json` binds only the files physically copied below this directory. Native full PNG/PPM collections, private ZIPs and compiled executables remain local under the recorded build roots. Captured image hashes stay in each report; the parent review page separately preserves its displayed image sources/crops. This avoids treating ignored scratch images as durable Git members.

The original and initial-static observer snapshots are retained separately from current helpers. Original capture used one earlier art_style.c version; its exact hash-matching historical source is retained in runtime-source/original-art_style.c. The other original protected source inputs still matched the current worktree when this record was written. Current runtime source snapshots contain the final registered static-ground and center-wave placement contracts. Inputs/build records identify every source/header hash and the actual compiler command. These are current-code port checks, not an unchanged original binary.

Reconstruction requires a scratch checkout with matching source bytes, the pinned production archive 4c8085be, the exact full-size V5 baseline archive 3d619201, and the bound runtime export inputs. Restore pinned production data in that scratch checkout before using the preserved helpers; they deliberately refuse a later production package. Recreate private Cartoon ZIPs with the bound prepare.py command and selected export-report.json, then run the observer with --phase cycle into a fresh output directory. Preserve the real directory depth and frozen helper import paths. Do not run these preservation writers again over this evidence directory.

For the original reference, recreate the source-only package using seasonal-v1/island-footprint-v1/REPRODUCE.md and the supplied resource pair, verify archive 4301aad9, then run the original_cycle.py observer with its frozen helper and historical art_style.c in an isolated scratch checkout. The adapted observer source is copied verbatim in original/captures/observer/driver.c. Docker/Xvfb is pinned by image ID in launch records. Every task container was removed and its absence checked; no workstation window was opened.
'''
    (target/'README.md').write_text(text,encoding='utf-8',newline='\n');copied['README.md']=sha((target/'README.md').read_bytes())
    save(target/'evidence.json',{'schema_version':1,'status':'PASS','accepted':False,
      'files_sha256':copied,'copied_from':origins,'local_only_capture_roots':source_bindings,
      'scope':'Compact technical native comparison proof. Human art choice remains separate. No production writes, no full tide/night/Johnny matrix claim.'})
    require(all(sha((target/name).read_bytes())==digest for name,digest in copied.items()),'durable native byte readback')
    save(target/'readback.json',{'status':'PASS','file_count':len(copied),'bytes':sum((target/name).stat().st_size for name in copied),
      'evidence_sha256':sha((target/'evidence.json').read_bytes()),'method':'Every copied durable file hashed after write; no external scratch image asserted as tracked evidence.'})
    print(json.dumps({'files':len(copied),'bytes':sum((target/name).stat().st_size for name in copied),'evidence_sha256':sha((target/'evidence.json').read_bytes()),'path':target.relative_to(ROOT).as_posix()}))
if __name__=='__main__':main()
