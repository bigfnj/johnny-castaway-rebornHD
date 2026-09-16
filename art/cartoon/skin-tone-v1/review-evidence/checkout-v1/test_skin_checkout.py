import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[2]
bundle=root/'art/cartoon/skin-tone-v1'
source=(bundle/'correct.py').read_bytes()
name='art/cartoon/skin-tone-v1/correct.py'
results=[]
def git(repo,*args):
    result=subprocess.run(['git','-C',str(repo),'-c','core.autocrlf=true',*args],capture_output=True)
    assert result.returncode==0,result.stderr
    return result
for protected in (True,False,True):
    with tempfile.TemporaryDirectory(prefix='johnny-skin-checkout-') as directory:
        repo=Path(directory)/'repo';repo.mkdir()
        git(repo,'init','--quiet')
        path=repo/name;path.parent.mkdir(parents=True);path.write_bytes(source)
        attrs='* text=auto\n'
        if protected:attrs+='art/cartoon/skin-tone-v1/** -text whitespace=cr-at-eol\n'
        (repo/'.gitattributes').write_text(attrs,encoding='utf-8')
        git(repo,'add','--','.gitattributes',name)
        destination=Path(directory)/'fresh';destination.mkdir()
        git(repo,'checkout-index','--all','--prefix='+destination.as_posix()+'/')
        actual=(destination/name).read_bytes()
        equal=actual==source
        assert equal==protected, (protected,equal)
        results.append({'capability':'fresh Windows autocrlf checkout preserves hashed corrector','protection_present':protected,'status':'PASS' if equal else 'FIRED','file':name,'source_sha256':hashlib.sha256(source).hexdigest(),'checkout_sha256':hashlib.sha256(actual).hexdigest(),'failure':None if equal else name+': byte identity changed'})
out=bundle/'review-evidence/checkout-v1'
out.mkdir(parents=True,exist_ok=False)
(out/'report.json').write_text(json.dumps({'status':'PASS','cases':results},indent=2)+'\n',encoding='utf-8')
(out/'test_skin_checkout.py').write_bytes(Path(__file__).read_bytes())
print('PASS protected checkout; FIRED removed attribute; PASS restored checkout')
