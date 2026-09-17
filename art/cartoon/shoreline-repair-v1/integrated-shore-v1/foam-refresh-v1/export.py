"""Offshore comparison only: three generated phases at common fixed registration."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import sys

from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
PARENT=HERE.parent/'export.py'
PARENT_SHA='7b9071272c7cee320fcc7c2a38167510313c8475cd4e3215bdb70752779c7fcf'
OLD=HERE.parent/'candidates/v1'
OLD_REPORT_SHA='9a09c9fd870f150499726b3eb5f17b2f22f391949b3f58cbce1fe3d236f638a4'
SOURCES={6:('006-raw.png','be78ddda6468fdd3d00c20589e700a50fbb6150157591eb1070eeb718e87c5bd'),
         7:('007-v2-raw.png','c97a2e468a854296fadb787d4b9ff30833bd8e46d3b1c4d17dc8cb965ddbd0d4'),
         8:('008-raw.png','ae9e3795f81be28436ebff6a7c90b19c8998377d0754e4e8ed990ed46bfca2a8')}
WORLD=[712,638,1068,740]
AUDIT=[692,544,1084,808]
FOOTPRINT={'id':'cartoon-island-center-foam-v1','canvas':[356,102],'offset_hd':[-16,0]}


def helpers():
    import hashlib
    if hashlib.sha256(PARENT.read_bytes()).hexdigest()!=PARENT_SHA:
        raise ValueError('integrated-shore export.py: frozen helper differs')
    spec=importlib.util.spec_from_file_location('frozen_integrated_shore',PARENT)
    parent=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parent)
    base,mask=parent.helpers()
    return parent,base,mask


def inputs():
    parent,base,mask=helpers()
    report_raw=(OLD/'export-report.json').read_bytes()
    base.require(base.sha(report_raw)==OLD_REPORT_SHA,'static/side input report differs')
    report=json.loads(report_raw)
    for name,digest in report['outputs_sha256'].items():
        base.require(base.sha((OLD/name).read_bytes())==digest,name+': prior output changed')
    for name,digest in (('context-source.json','8c93f6a72f33a353384377802dc74fa68f1ccbae001abd355178c493aa0bcee0'),
                        ('reference-source.json','73e231aed6c1da51a1078e1afa97cb4eb9c5cf9f31441a2dd54127c5a54e49cb')):
        base.require(base.sha((HERE/name).read_bytes())==digest,name+': reference changed')
    ground=Image.open(OLD/'BMP/BACKGRND.BMP/000.png').convert('RGBA')
    return parent,base,mask,report,ground


def source_row(frame):
    _,base,_=helpers()
    name,digest=SOURCES[frame]
    base.require(digest is not None,f'{frame:03}: final raw selection pending')
    base.require(base.sha((HERE/name).read_bytes())==digest,f'{frame:03}: selected raw identity differs')
    with Image.open(HERE/name) as im:
        base.require(im.mode=='RGBA' and im.size==(1536,1024),f'{frame:03}: raw canvas/mode')
    return {'frame':frame,'path':f'BMP/BACKGRND.BMP/{frame:03}.png','role':'generated center foam only',
            'source':(HERE/name).relative_to(ROOT).as_posix(),'source_sha256':digest,
            'canvas':[356,102],'logical_origin_hd':[728,638],'asset_offset_hd':[-16,0],
            'world_box':WORLD,'footprint':FOOTPRINT}


def prepared():
    parent,base,_,prior,_=inputs()
    frames=[source_row(row['frame']) if row['frame'] in SOURCES else {k:v for k,v in row.items() if k not in ('coverage','retained_coverage','source_coverage','visibility_measurements')} for row in prior['frames']]
    return {'schema_version':1,'accepted':False,'scope':'Offshore approach retained only for the requested three-way comparison. Not selected for production; incoming wash artwork is a separate direction.',
            'parent_exporter':PARENT.relative_to(ROOT).as_posix(),'parent_exporter_sha256':PARENT_SHA,
            'parent_report_sha256':OLD_REPORT_SHA,'filter_sha256':parent.FILTER_SHA,'mask_sha256':parent.MASK_SHA,
            'pillow_version':base.PIL.__version__,'source_to_world_affine':[.25,0,696,0,.25,548],
            'world_box':WORLD,'audit_world_box':AUDIT,'footprint':FOOTPRINT,
            'policy':'One common transform; no per-phase fit, translation or shrink. Ground visibility mask preserves RGB and changes only foam alpha at overlap. All ground remains in000.',
            'frames':frames}


def render_frame(frame):
    parent,base,mask,_,ground=inputs()
    row=source_row(frame)
    source=Image.open(ROOT/row['source']).convert('RGBA')
    # One filter call over the complete source extent; runtime is an exact crop.
    padded=base.resample(source,[392,264],[.25,0,4,0,.25,4])
    audit=padded.crop((32,32,424,296))
    foam=audit.crop((20,94,376,196))
    outside=audit.copy()
    outside.paste((0,0,0,0),(20,94,376,196))
    crop_stats=parent.stats(outside)
    base.require(crop_stats['nonzero_pixels']==0,f'{frame:03}: footprint crops filtered foam alpha')
    audit_outside=padded.copy()
    audit_outside.paste((0,0,0,0),(32,32,424,296))
    base.require(parent.stats(audit_outside)['nonzero_pixels']==0,f'{frame:03}: audit crops filtered raw alpha')
    retained,visibility=mask.occlude(foam,ground,WORLD[:2],parent.WORLD_BOX)
    parent.validate_foam_only(foam,retained,f'{frame:03}')
    raw_out=source.getchannel('A').copy()
    raw_out.paste(0,(64,360,1488,768))
    raw_values=list(raw_out.get_flattened_data())
    return {'runtime':base.png(retained),'unmasked':base.png(foam),'padded':base.png(padded),'audit':base.png(audit)}, {
        **row,'sha256':base.sha(base.png(retained)),'uniform_resample_count':1,
        'raw_alpha8_bounds':source.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox(),
        'raw_alpha_outside_footprint':{'nonzero_pixels':sum(a>0 for a in raw_values),'alpha8_pixels':sum(a>=8 for a in raw_values),'max_alpha':max(raw_values),'alpha_sum':sum(raw_values)},
        'cropped_filtered_alpha':crop_stats,'source_coverage':parent.stats(foam),'retained_coverage':parent.stats(retained),
        'visibility_measurements':visibility}


def render(recipe):
    _,base,_,prior,_=inputs()
    base.require(recipe==prepared(),'recipe: common source/registration contract differs')
    outputs,rows={},[]
    for row in recipe['frames']:
        frame=row['frame']
        if frame in SOURCES:
            data,report=render_frame(frame)
            outputs[row['path']]=data['runtime']
            for kind in ('unmasked','padded','audit'):
                outputs[f'audit/{frame:03}-{kind}.png']=data[kind]
            rows.append(report)
        else:
            raw=(OLD/row['path']).read_bytes()
            outputs[row['path']]=raw
            rows.append({**row,'sha256':base.sha(raw),'byte_identical_to_parent':True})
    report={'schema_version':1,'status':'DIAGNOSTIC_EXPORTED','accepted':False,
            'exporter_sha256':base.sha(Path(__file__).read_bytes()),'recipe_sha256':base.sha(base.encode(recipe)),
            'changed_frames':[6,7,8],'retained_frames':[0,3,4,5,9,10,11],
            'uniform_resamples':3,'ground_owner_frames':[0],'footprint':FOOTPRINT,
            'scope':recipe['scope'],'policy':recipe['policy'],'frames':rows,
            'outputs_sha256':{name:base.sha(raw) for name,raw in outputs.items()}}
    return outputs,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--recipe',type=Path,default=HERE/'recipe-v1.json')
    parser.add_argument('--output',type=Path,default=HERE/'candidates/v1')
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--preview-frame',type=int,choices=(6,7,8))
    args=parser.parse_args()
    _,base,_=helpers()
    print('WITNESS center-foam '+base.sha(Path(__file__).read_bytes()))
    try:
        if args.preview_frame is not None:
            data,report=render_frame(args.preview_frame)
            outputs={f'{args.preview_frame:03}-{kind}.png':raw for kind,raw in data.items()}
            outputs['preview-report.json']=base.encode(report)
        else:
            if args.prepare:
                base.require(not args.recipe.exists(),'recipe: refusing overwrite')
            recipe=prepared() if args.prepare else json.loads(args.recipe.read_bytes())
            outputs,report=render(recipe)
            outputs['export-report.json']=base.encode(report)
        if not args.check:
            base.require(not args.output.exists(),'output: refusing overwrite')
            args.output.mkdir(parents=True)
        for name,raw in outputs.items():
            path=args.output/name
            if args.check:
                base.require(path.read_bytes()==raw,name+': reproduced bytes differ')
            else:
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(raw)
        if args.prepare and args.preview_frame is None:
            args.recipe.write_bytes(base.encode(recipe))
        print('PASS '+json.dumps({'files':len(outputs),'footprint':FOOTPRINT}))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('FAIL '+str(exc),file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
