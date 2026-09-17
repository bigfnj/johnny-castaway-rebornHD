"""Only HOLIDAY003 changes over the reviewed tied-banner private package."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent/'banner-attachment-v1'
BASE_SHA='507dac5b524b08450d14119443f19a370b790e1bcd198ec6144563ef2a7f2233'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);p.add_argument('--runtime-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    ancestor=PARENT/'prepare.py';assert sha(ancestor)=='7981cbc0823de32fe6cb5a0abb36f79646774fe1d42a1f94aa84de406d4361b0','frozen package helper'
    spec=importlib.util.spec_from_file_location('inset_package',ancestor);legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    legacy.BASE_SHA=BASE_SHA;legacy.prepare(a.baseline.resolve(),a.runtime.resolve(),a.runtime_sha256,a.output.resolve())
    path=a.output/'preparation.json';record=json.loads(path.read_bytes())
    record.update(wrapper_sha256=sha(Path(__file__)),scope='Private clean-banner 8% inset versus tied draft; only HOLIDAY003 differs. Human attachment review pending.')
    path.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
