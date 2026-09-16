"""Bind two scoped pixel controls to the actual final normalizedv5 capture buffers."""
import importlib.util
import json
from pathlib import Path
import capture_normalized as c

def main():
    output=c.OUT/'negative-controls.json';assert not output.exists(),'preserve normalizedv5 controls'
    summary=json.loads((c.OUT/'summary.json').read_bytes());prep=json.loads((c.OUT/'preparation.json').read_bytes())
    assert summary['status']=='PASS' and summary['runtime018_sha256']==c.RUNTIME_SHA and summary['archive_sha256']==prep['archive_sha256'],'complete selectedv5 native captures'
    codec=c.m.load_codec();cases=[];pins={}
    for clip,frame,wanted in [('waypoint_rear',18,'unchanged outside018 canvas'),('waypoint_front',23,'prior pose and scene pixel identity:23')]:
        folder=c.OUT/clip/'full';prior=c.BASELINES[clip]/'full'
        report=json.loads((folder/'report.json').read_bytes());baseline=json.loads((prior/'report.json').read_bytes())
        row=next(d for d in report['displays'] if d['actual_draw'][3]==frame and (frame!=18 or d['actual_draw'][0]==1))
        old=baseline['displays'][row['index']-1]
        before=codec.ppm(prior/old['ppm']);after=codec.ppm(folder/row['ppm'])
        assert c.m.sha(before)==old['pixels_sha256'] and c.m.sha(after)==row['pixels_sha256'],'exact tested final/native buffers'
        c.m.compare_scene(before,after,row['actual_draw'])
        flip,x,y,_=row['actual_draw'];px=x*2-1 if frame==18 else x*2+1;py=y*2+1
        changed=bytearray(after);changed[(py*1280+px)*3]^=1
        try:c.m.compare_scene(before,bytes(changed),row['actual_draw'])
        except AssertionError as error:
            assert str(error)==wanted,'exact intended scope failure'
            cases.append({'clip':clip,'display':row['index'],'frame':frame,'actual_draw':row['actual_draw'],'altered_pixel':[px,py],
                'result':'FIRED','exact_failure':str(error),'altered_rgb_sha256':c.m.sha(changed)})
        else:raise AssertionError('SURVIVED:'+clip+':'+str(frame))
        c.m.compare_scene(before,after,row['actual_draw'])
        pins[clip]={'baseline_report_sha256':c.m.sha((prior/'report.json').read_bytes()),'candidate_report_sha256':c.m.sha((folder/'report.json').read_bytes())}
    c.m.save(output,{'status':'PASS','controls':cases,'positive_before_after':True,'report_bindings':pins,
        'summary_sha256':c.m.sha((c.OUT/'summary.json').read_bytes()),'archive_sha256':prep['archive_sha256'],'runtime018_sha256':c.RUNTIME_SHA,
        'executed_comparison_helper_sha256':c.m.sha(Path(c.m.__file__).read_bytes()),'capture_helper_sha256':c.m.sha(Path(c.__file__).read_bytes()),
        'checker_sha256':c.m.sha(Path(__file__).read_bytes()),'scope':'Two memory-only altered actual final-native buffers; no image/capture/production changes.'})
    print('PASS finalv5 mirrored018 outside-canvas and retained023 guards; exact failures and restored positives')

if __name__=='__main__':main()
