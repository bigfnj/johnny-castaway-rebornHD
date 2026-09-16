"""Focused altered-pixel controls against actual captured018 and retained023 displays."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('motion',HERE/'capture_motion.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def main():
    out=m.OUT/'negative-controls.json';assert not out.exists(),'preserve018 motion controls'
    summary=json.loads((m.OUT/'summary.json').read_bytes());assert summary['status']=='PASS','completed018 native clips'
    codec=m.load_codec();records=[];pins={}
    for clip,frame,wanted in [('waypoint_rear',18,'unchanged outside018 canvas'),('waypoint_front',23,'prior pose and scene pixel identity:23')]:
        folder=m.OUT/clip/'full';prior=m.BASE/'candidate-v2'/clip/'full'
        report=json.loads((folder/'report.json').read_bytes());baseline=json.loads((prior/'report.json').read_bytes())
        row=next(d for d in report['displays'] if d['actual_draw'][3]==frame and (frame!=18 or d['actual_draw'][0]==1))
        old=baseline['displays'][row['index']-1]
        before=codec.ppm(prior/old['ppm']);after=codec.ppm(folder/row['ppm'])
        assert m.sha(before)==old['pixels_sha256'] and m.sha(after)==row['pixels_sha256'],'bound actual motion pixels'
        m.compare_scene(before,after,row['actual_draw'])
        flip,x,y,_=row['actual_draw'];px=x*2-1 if frame==18 else x*2+1;py=y*2+1
        damaged=bytearray(after);damaged[(py*1280+px)*3]^=1
        try:m.compare_scene(before,bytes(damaged),row['actual_draw'])
        except AssertionError as e:
            assert str(e)==wanted,'single intended scene guard'
            records.append({'clip':clip,'display':row['index'],'frame':frame,'flip_x':flip,'altered_scene_pixel':[px,py],
                'result':'FIRED','exact_failure':str(e),'altered_rgb_sha256':m.sha(damaged)})
        else:raise AssertionError('SURVIVED:'+clip+':'+str(frame))
        m.compare_scene(before,after,row['actual_draw'])
        pins[clip]={'baseline_report_sha256':m.sha((prior/'report.json').read_bytes()),'candidate_report_sha256':m.sha((folder/'report.json').read_bytes())}
    m.save(out,{'status':'PASS','controls':records,'positive_before_and_after':True,'report_bindings':pins,
        'summary_sha256':m.sha((m.OUT/'summary.json').read_bytes()),'executed_comparer_sha256':m.sha(Path(m.__file__).read_bytes()),
        'checker_sha256':m.sha(Path(__file__).read_bytes()),'archive_sha256':m.PACKAGE_SHA,'runtime018_sha256':m.RUNTIME_SHA,
        'scope':'Two memory-only changed-pixel controls on bound actual full-capture buffers; no capture files, artwork or production mutations.'})
    print('PASS mirrored018 outside-canvas and retained023 altered-pixel controls; each exact named failure, restored positives pass')

if __name__=='__main__':main()
