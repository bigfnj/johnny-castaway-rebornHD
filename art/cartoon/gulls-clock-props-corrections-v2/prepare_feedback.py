"""Retain this correction request and bind each prior drawing to its source."""
import hashlib
import json
import shutil
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PRIOR=ROOT/'art/cartoon/gulls-clock-props-batch-v1'

def pin(path):
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    request=json.loads((HERE/'request-input.json').read_text(encoding='utf-8'))
    prior=json.loads((PRIOR/'review-data.json').read_text(encoding='utf-8'))
    index={row['key']:row for row in prior['assets']}
    attachments=[]
    for i,source in enumerate(request['attachments'],1):
        dest=HERE/'feedback'/f'annotation-{i:02}.png'
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest)
        attachments.append(pin(dest))
    frames=[]
    for item in request['frames']:
        key=f"{item['resource']}-{item['frame']}"
        old=index[key]
        frames.append({**item,'key':key,'original':old['original_reference'],'prior_raw':old['selected_raw'],'prior_record':old['generation_record'],'prior_request':old['request']})
    data={'schema_version':1,'date':'2026-09-20','user_request':request['user_request'],'reviewed_url':request['reviewed_url'],'attachments':attachments,'frames':frames,'scope':'24 targeted corrections; unmentioned drawings receive no implied approval','prior_review':pin(PRIOR/'review-record.json')}
    (HERE/'feedback.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    assert len(frames)==24
    print('Prepared 24 corrections and retained 12 annotations')

if __name__=='__main__':main()
