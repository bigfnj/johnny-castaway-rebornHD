"""Frozen banner capture, with only the explicitly selected baseline changed."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ANCESTOR=HERE.parents[1]/'banner-attachment-v1/native/capture.py'
BASE_SHA='507dac5b524b08450d14119443f19a370b790e1bcd198ec6144563ef2a7f2233'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

if __name__=='__main__':
    assert sha(ANCESTOR)=='848f9faa6e7d74482f7662791614aff74a84be8d7688a359eb816ba53ac63844','frozen banner native adapter'
    spec=importlib.util.spec_from_file_location('inset_native',ANCESTOR);legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    legacy.BASE_SHA=BASE_SHA;legacy.main()
    output=Path(sys.argv[sys.argv.index('--output')+1])
    (output/'adapter-config.json').write_text(json.dumps({'wrapper_sha256':sha(Path(__file__)),'ancestor_sha256':sha(ANCESTOR),
        'baseline_sha256':BASE_SHA,'change':'Only package baseline selection. Same native observer, cases, timing, canvas comparison and controls.'},indent=2)+'\n')
