"""Publish a fresh local inspection page after exact browser smoke."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def publish(review, destination, url):
    smoke=json.loads((review/'browser-smoke.json').read_bytes())
    manifest=json.loads((review/'manifest.json').read_bytes())
    assert smoke['status']=='PASS'
    assert smoke['html_sha256']==sha(review/'review.html') and smoke['manifest_sha256']==sha(review/'manifest.json')
    assert not destination.exists(), 'immutable publication slug already exists'
    destination.mkdir(parents=True)
    files={}
    for name in ('review.html','manifest.json','build.json',*manifest['atlases']):
        shutil.copyfile(review/name,destination/name)
        expected=sha(review/name)
        assert sha(destination/name)==expected
        with urllib.request.urlopen(url.rsplit('/',1)[0]+'/'+name) as response:
            assert hashlib.sha256(response.read()).hexdigest()==expected, 'served identity: '+name
        files[name]=expected
    result={'status':'PUBLISHED_FOR_INSPECTION','url':url,'files_sha256':files,
            'smoke_sha256':sha(review/'browser-smoke.json'),'publisher_sha256':sha(Path(__file__)),
            'scope':'Root layout approved; human placement approval separate. Full regression result is retained separately.'}
    (review/'publication.json').write_text(json.dumps(result,indent=2)+'\n')
    print(url,sha(review/'publication.json'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--review',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--url',required=True)
    a=p.parse_args();publish(a.review.resolve(),a.destination.resolve(),a.url)
