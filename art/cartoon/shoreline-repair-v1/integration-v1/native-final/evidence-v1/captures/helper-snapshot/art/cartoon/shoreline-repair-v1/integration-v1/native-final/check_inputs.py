"""Focused final-package smoke, damaged inputs and fresh executed guard witness."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import contract as canonical

def load(path):
    # The copied mutant keeps its original ROOT/HERE constants explicitly.
    spec=importlib.util.spec_from_file_location('checked_final_contract',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def negatives(c,before,after,fixtures):
    tests=[]
    for name,member in (('selected007',c.member(7)),('selected_banner','data/styles/cartoon/BMP/HOLIDAY.BMP/003.png')):
        damaged=copy.deepcopy(after);damaged[member]['sha256']='0'*64
        tests.append((name,damaged,'selected payload '+member))
    damaged=copy.deepcopy(after);damaged['data/styles/cartoon/BMP/HOLIDAY.BMP/003.png']['canvas']=[303,94]
    tests.append(('banner_canvas',damaged,'selected canvas data/styles/cartoon/BMP/HOLIDAY.BMP/003.png'))
    results=[]
    for name,damaged,expected in tests:
        try:c.validate_members(before,damaged,fixtures)
        except ValueError as error:
            c.require(str(error)=='final native: '+expected,'named package control '+name)
            results.append({'name':name,'failure':str(error),'status':'FIRED'})
        else:raise ValueError('final native: negative survived '+name)
    c.validate_members(before,after,fixtures)
    return results

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--candidate-sha256',required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--phase',choices=('smoke','regression','mutant-child'),required=True);p.add_argument('--contract',type=Path)
    a=p.parse_args();path=a.contract or Path(canonical.__file__);c=load(path)
    print('WITNESS executed contract '+c.sha(path.read_bytes()),flush=True)
    pair=c.package_pair(a.baseline,a.candidate,a.candidate_sha256)
    before,after=c.archive(a.baseline),c.archive(a.candidate);fixtures=c.fixtures()
    if a.phase=='smoke':
        c.require(not a.output.exists(),'fresh input-check output');a.output.mkdir(parents=True)
        c.save(a.output/'smoke.json',{'status':'PASS','contract_sha256':c.sha(path.read_bytes()),'package_pair':pair,'fixtures':14})
        print('PASS input smoke 14 selected fixtures');return
    if a.phase=='mutant-child':
        negatives(c,before,after,fixtures);return
    smoke=json.loads((a.output/'smoke.json').read_bytes())
    c.require(smoke['status']=='PASS' and smoke['package_pair']==pair and smoke['contract_sha256']==c.sha(path.read_bytes()),'matching package smoke first')
    results=negatives(c,before,after,fixtures)
    mutation=a.output/'mutation';mutation.mkdir()
    text=path.read_text();guard="require(after[name]['sha256']==row['sha256'],'selected payload '+name)"
    c.require(text.count(guard)==1,'unique selected-payload guard')
    text=text.replace(guard,"require(True,'selected payload '+name)")
    text=text.replace("HERE=Path(__file__).resolve().parent","HERE=Path("+repr(str(c.HERE))+ ")",1)
    mutant=mutation/'contract-guard-removed.py';mutant.write_text(text,encoding='utf-8',newline='\n')
    command=[sys.executable,'-B',str(Path(__file__).resolve()),'--baseline',str(a.baseline.resolve()),'--candidate',str(a.candidate.resolve()),
             '--candidate-sha256',a.candidate_sha256,'--output',str(a.output.resolve()),'--phase','mutant-child','--contract',str(mutant.resolve())]
    run=subprocess.run(command,capture_output=True,timeout=60)
    (mutation/'stdout.txt').write_bytes(run.stdout);(mutation/'stderr.txt').write_bytes(run.stderr)
    witness='WITNESS executed contract '+c.sha(mutant.read_bytes())
    c.require(witness in run.stdout.decode() and run.returncode!=0 and run.stderr.decode().count('ValueError: final native: negative survived selected007')==1,'executed selected-payload guard removal witness')
    c.validate_members(before,after,fixtures)
    c.save(a.output/'regression.json',{'status':'PASS','contract_sha256':c.sha(path.read_bytes()),'checker_sha256':c.sha(Path(__file__).read_bytes()),
      'package_pair':pair,'controls':results,'guard_removal':{'command':command,'mutant_sha256':c.sha(mutant.read_bytes()),'exit_code':run.returncode,
      'witness':witness,'failure':'negative survived selected007','stdout_sha256':c.sha(run.stdout),'stderr_sha256':c.sha(run.stderr)},'restored_positive':'PASS'})
    print('PASS input regression 3 damaged inputs, executed guard removal, restored positive')

if __name__=='__main__':main()
