"""Replay completed native reports with bounded pixel/timestamp corruptions."""
import argparse
import copy
import io
import json
from pathlib import Path
import zipfile
from PIL import Image
import config
import native_core as core
import capture_candidate
import skin_compare


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate-version', type=int, default=1)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    target = config.OUT / f'candidate-v{args.candidate_version}'
    prep, masks = capture_candidate.verify_prepared(target)
    folder, prior = target / 'front_arc/full', core.BASE / 'front_arc/full'
    observed = config.load_json(folder / 'report.json')
    expected = config.load_json(prior / 'report.json')
    witness = {'checker_sha256':core.sha(Path(__file__).read_bytes()),
               'comparison_helper_sha256':core.sha(Path(skin_compare.__file__).read_bytes()),
               'candidate_archive_sha256':prep['archive_sha256'],'recipe_sha256':prep['recipe_sha256']}
    print('WITNESS native mask controls ' + json.dumps(witness,sort_keys=True),flush=True)
    def compare(value):
        return skin_compare.compare_reports(value,expected,prep,folder,prior,masks)
    compare(copy.deepcopy(observed))
    controls=[]
    bad=copy.deepcopy(observed)
    bad['displays'][0]['logical_ms'] += 1
    try:
        compare(bad)
    except ValueError as error:
        core.require(str(error)=='connecting capture: identical native display logical_ms','named timestamp refusal')
        controls.append({'case':'changed-display-timestamp','status':'FIRED','failure':str(error)})
    else:
        raise ValueError('timestamp control survived')

    original_ppm = core.codec.ppm
    for case in ('outside-skin','outside-canvas','unchanged029'):
        bad=copy.deepcopy(observed)
        display=next(d for d in bad['displays'] if d['actual_draw'][3]==29) if case=='unchanged029' else bad['displays'][0]
        flip,x,y,frame=display['actual_draw']
        raw=bytearray(original_ppm(folder/display['ppm']))
        if case=='outside-canvas':
            px,py=0,0
            label=f'connecting capture: outside skin canvas:{frame:03}'
        else:
            mask=masks[frame]; weights=mask.tobytes()
            with zipfile.ZipFile(target/'scrantic_data.zip') as packed:
                sprite=Image.open(io.BytesIO(packed.read(f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'))).convert('RGBA')
            alpha=sprite.getchannel('A').tobytes()
            choose=(lambda i: weights[i]>0 and alpha[i]>=250) if case=='unchanged029' else (lambda i: weights[i]==0 and alpha[i]>=250)
            at=next(i for i in range(len(weights)) if choose(i))
            sx,sy=at%mask.width,at//mask.width
            px=x*2+(mask.width-1-sx if flip else sx);py=y*2+sy
            label=f'connecting capture: unchanged reference pixels:{frame:03}' if case=='unchanged029' else f'connecting capture: outside transformed skin mask:{frame:03}'
        offset=(py*1280+px)*3
        raw[offset]=(raw[offset]+1)%256
        modified=bytes(raw)
        display['pixels_sha256']=core.sha(modified)
        selected=(folder/display['ppm']).resolve()
        def injected(path):
            return modified if Path(path).resolve()==selected else original_ppm(path)
        try:
            core.codec.ppm=injected
            try:
                compare(bad)
            except ValueError as error:
                core.require(str(error)==label,'named '+case+' refusal')
                controls.append({'case':case,'frame':frame,'scene_pixel':[px,py],'status':'FIRED','failure':str(error)})
            else:
                raise ValueError(case+' control survived')
        finally:
            core.codec.ppm=original_ppm
    compare(copy.deepcopy(observed))
    core.require(not args.report.exists(),'preserve native control evidence')
    args.report.parent.mkdir(parents=True,exist_ok=True)
    core.save(args.report,{'status':'PASS',**witness,'candidate_version':args.candidate_version,
              'positive_before_and_after':True,'original_files_modified':False,
              'inputs':{'candidate_report_sha256':core.sha((folder/'report.json').read_bytes()),
                        'baseline_report_sha256':core.sha((prior/'report.json').read_bytes())},
              'controls':controls,
              'method':'Actual completed native reports and PPM reader; one timestamp or one in-memory pixel changed. Candidate pixel hash updated so pixel controls reach the placement/mask/reference guards, rather than failing a hash check.'})
    print('PASS four actual-report controls; unmodified positive replay restored',flush=True)


if __name__ == '__main__':
    main()
