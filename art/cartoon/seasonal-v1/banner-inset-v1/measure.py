"""Read-only source/native geometry measurements; writes a new analysis record only."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'CMakeLists.txt').is_file())
RAW=ROOT/'art/cartoon/seasonal-v1/raw/003-v1.png'
NATIVE=ROOT/'build/shoreline-repair-v1/offshore-full-v1/captures/day/none/candidate/smoke'
RAW_SHA='8cada55c5d6156efcb5a2c29a49a56d8f2662ac31c3201662ec2f66456e7ab17'
ZIP_SHA='ab5c8094b461307b87d68d2bb148eae5b9ce56d93cb6b93805c27c7fbd8e24ac'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def measure(output):
    assert not output.exists(),'fresh measurement output required'
    report=json.loads((NATIVE/'report.json').read_bytes());frame=report['displays'][0];scene=NATIVE/frame['file']
    assert sha(RAW)==RAW_SHA and sha(scene)==frame['png_sha256'],'original raw/native scene identity'
    assert report['archive_sha256']==ZIP_SHA and report['args']==[0,0,0,0,0,0,1],'selected offshore no-decoration native case'
    with Image.open(RAW) as im:raw=im.convert('RGBA')
    with Image.open(scene) as im:background=im.convert('RGB')
    alpha=raw.getchannel('A');tips=[]
    for name,box in (('left',[110,300,190,370]),('right',[1370,300,1440,380])):
        rows=[(y,[x for x in range(box[0],box[2]) if alpha.getpixel((x,y))>=128]) for y in range(box[1],box[3])]
        y,xs=next((y,xs) for y,xs in rows if xs)
        tips.append({'side':name,'source_search_box':box,'alpha128_first_row':y,'span_inclusive':[min(xs),max(xs)],
                     'raw_pixel_edge_midpoint':[(min(xs)+max(xs)+1)/2,y+.5]})
    candidates=[]
    for reduction in (0,.05,.06,.08,.10,.12):
        scale=.23*(1-reduction);sides=[]
        for tip,cloth in zip(tips,([132,328],[1407,337])):
            x,y=tip['raw_pixel_edge_midpoint'];world=[874+scale*(x-770),310.08+scale*(y-322)]
            cx,cy=874+scale*(cloth[0]-770),310.08+scale*(cloth[1]-322)
            rounded=[round(cx),round(cy)]
            sides.append({'side':tip['side'],'tip_world_hd':world,'interior_cloth_raw':cloth,
                          'interior_cloth_rgba':raw.getpixel(tuple(cloth)),'interior_cloth_world_hd':[cx,cy],
                          'native_sample_pixel':rounded,'native_rgb':background.getpixel(tuple(rounded)),
                          'native_rgb_neighborhood3x3':[[background.getpixel((sx,sy)) for sx in range(rounded[0]-1,rounded[0]+2)] for sy in range(rounded[1]-1,rounded[1]+2)]})
        candidates.append({'reduction_fraction':reduction,'scale':scale,'sides':sides})
    scale=.2116;tx=152-770*scale;ty=.08-322*scale;bounds=alpha.point(lambda a:255 if a>=8 else 0).getbbox()
    result={'schema_version':1,'status':'MEASURED_PROPOSAL','accepted':False,
            'sources':{p.relative_to(ROOT).as_posix():sha(p) for p in (RAW,scene,NATIVE/'report.json',ROOT/'art/cartoon/seasonal-v1/recipe-v5.json')},
            'native_archive_sha256':ZIP_SHA,'native_logical_banner_origin':[361,155],'hd_banner_origin':[722,310],
            'runtime_canvas':[304,94],'raw_corner_measurements':tips,'candidates':candidates,
            'proposed':{'reduction_fraction':.08,'scale':scale,'raw_anchor':[770,322],'target_anchor':[152,.08],
                        'affine_forward':[scale,0,tx,0,scale,ty],'source_alpha8_bounds':bounds,
                        'source_alpha8_center_extents_hd':[(bounds[0]+.5)*scale+tx,(bounds[1]+.5)*scale+ty,(bounds[2]-.5)*scale+tx,(bounds[3]-.5)*scale+ty]},
            'observations':['At the 5% candidate, the left corner sample remains on the dark outside edge.',
                            'At the 8% candidate both interior white-cloth corner samples and their 3x3 neighborhoods lie within visually identified green fronds in the unoccluded native scene.',
                            'This measures the two upper cloth tips and nearby interior cloth, not added ties. The palm artwork is unchanged.'],
            'limits':'Proposal only; no runtime export, filtered overlap or final native banner capture yet. Recorded RGB neighborhoods support visual review, not a generic automated definition of leaf material.',
            'measurement_helper_sha256':sha(Path(__file__))}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('MEASURED',sha(output));print(json.dumps(result['proposed'],indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();measure(a.output.resolve())
