"""One complete static ground sprite and nine ground-free animated foam sprites."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import sys
import zipfile

from PIL import Image

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SOURCE=HERE.parent/'smooth-shore-v3/raw.png'
SOURCE_SHA='19df1e01931cf746e88f6bf696b39e16f009ba7aa1b37f1f7c916b0949822732'
COMPARISON=HERE.parent/'smooth-shore-v3/comparison.json'
COMPARISON_SHA='be5889ac173e0881b948e656be288d7ac7f66cc593c589a6d2bf314431c726ff'
ARCHIVE=ROOT/'assets/scrantic_data.zip'
ARCHIVE_SHA='4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be'
FILTER=HERE.parent.parent/'seasonal-v1/export.py'
FILTER_SHA='7fe0e58d9a2522af71ddf696eccb1a76c6c5d293f71e0a3c8cab7282f336892d'
MASK=HERE.parent/'foam-contact-v2/export.py'
MASK_SHA='fae28aba1181761777ae4ed43e088fb6a1cc51b08f20db39135ac81fe4ae1445'
WORLD_BOX=[540,548,1180,728]
AUDIT_BOX=[530,400,1190,844]
AFFINE=[.41852117731514715,0,534.110911701364,0,.41852117731514715,409.6805455850682]
FAMILIES={3:[540,612,144,58],6:[728,638,320,50],9:[1036,606,144,64]}


def helpers():
    import hashlib
    loaded=[]
    for index,(path,digest) in enumerate(((FILTER,FILTER_SHA),(MASK,MASK_SHA))):
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:
            raise ValueError(path.name+': pinned helper differs')
        spec=importlib.util.spec_from_file_location(f'integrated_shore_helper_{index}',path)
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        loaded.append(module)
    return loaded


def prepared():
    base,mask=helpers()
    for path,digest in ((SOURCE,SOURCE_SHA),(COMPARISON,COMPARISON_SHA),(ARCHIVE,ARCHIVE_SHA)):
        base.require(base.sha(path.read_bytes())==digest,path.name+': source identity differs')
    comparison=json.loads(COMPARISON.read_bytes())
    base.require(comparison['draft']['display_affine']==[.8370423546302943,116.22182340272792,87.36109117013643],'comparison: approved display transform differs')
    with Image.open(SOURCE) as im:
        base.require(im.mode=='RGBA' and im.size==(1536,1024),'ground source: canvas/mode')
    rows=[{'frame':0,'path':'BMP/BACKGRND.BMP/000.png','role':'sole static ground owner','canvas':[640,180],
           'logical_origin_hd':[576,558],'asset_offset_hd':[-36,-10],'world_box':WORLD_BOX,
           'footprint':{'id':'cartoon-island-ground-v1','canvas':[640,180],'offset_hd':[-36,-10]}}]
    with zipfile.ZipFile(ARCHIVE) as archive:
        for frame in range(3,12):
            family=frame-frame%3
            x,y,w,h=FAMILIES[family]
            member=f'data/styles/cartoon/BMP/BACKGRND.BMP/{frame:03}.png'
            raw=archive.read(member)
            with Image.open(io.BytesIO(raw)) as im:
                base.require(im.size==(w,h),f'{frame:03}: original foam canvas')
            rows.append({'frame':frame,'path':f'BMP/BACKGRND.BMP/{frame:03}.png','role':'foam only; zero ground ownership',
                         'canvas':[w,h],'logical_origin_hd':[x,y],'asset_offset_hd':[0,0],
                         'world_box':[x,y,x+w,y+h],'source_member':member,'source_member_sha256':base.sha(raw)})
    return {'schema_version':1,'accepted':False,'scope':'Technical static-ground candidate; approved shape, native placement/foam motion still pending.',
            'source':SOURCE.relative_to(ROOT).as_posix(),'source_sha256':SOURCE_SHA,
            'comparison':COMPARISON.relative_to(ROOT).as_posix(),'comparison_sha256':COMPARISON_SHA,
            'archive':ARCHIVE.relative_to(ROOT).as_posix(),'archive_sha256':ARCHIVE_SHA,
            'filter':FILTER.relative_to(ROOT).as_posix(),'filter_sha256':FILTER_SHA,
            'mask_helper':MASK.relative_to(ROOT).as_posix(),'mask_helper_sha256':MASK_SHA,
            'pillow_version':base.PIL.__version__,'resampling':base.FILTERS,
            'source_to_world_affine':AFFINE,'static_world_box':WORLD_BOX,'audit_world_box':AUDIT_BOX,
            'ground_ownership':'All resampled ground in000 exactly once; no ground in003..011.',
            'foam_visibility':'Frozen V2 alpha visibility mask, RGB unchanged, original foam positions. Not exact global ground-over-foam compositing.',
            'frames':rows}


def stats(image):
    a=image.getchannel('A')
    values=list(a.get_flattened_data())
    return {'nonzero_pixels':sum(v>0 for v in values),'alpha8_pixels':sum(v>=8 for v in values),
            'alpha_sum':sum(values),'maximum_alpha':max(values,default=0),
            'nonzero_bounds':a.getbbox(),'alpha8_bounds':a.point(lambda v:255 if v>=8 else 0).getbbox()}


def validate_foam_only(foam,retained,label):
    base,_=helpers()
    original=list(foam.get_flattened_data())
    actual=list(retained.get_flattened_data())
    base.require(all(a[:3]==b[:3] for a,b in zip(original,actual)),label+': foam RGB changed')
    base.require(all(a[3] or not b[3] for a,b in zip(original,actual)),label+': foam-only output introduced alpha outside source foam')
    base.require(all(not a[3] or b[3]<=a[3] for a,b in zip(original,actual)),label+': existing foam alpha increased')


def render(recipe):
    base,mask=helpers()
    base.require(recipe==prepared(),'recipe: static ownership/source/registration differs')
    source=Image.open(SOURCE).convert('RGBA')
    ax,ay,ar,ab=AUDIT_BOX
    forward=[AFFINE[0],0,AFFINE[2]-ax,0,AFFINE[4],AFFINE[5]-ay]
    padded=base.resample(source,[ar-ax,ab-ay],forward)
    audit=padded.crop((base.PAD,base.PAD,base.PAD+ar-ax,base.PAD+ab-ay))
    sx,sy,sr,sb=WORLD_BOX
    ground=audit.crop((sx-ax,sy-ay,sr-ax,sb-ay))
    outside=audit.copy()
    outside.paste((0,0,0,0),(sx-ax,sy-ay,sr-ax,sb-ay))
    outside_stats=stats(outside)
    base.require(outside_stats['nonzero_pixels']==0,'000: static extent crops filtered ground alpha')
    padded_outside=padded.copy()
    padded_outside.paste((0,0,0,0),(base.PAD,base.PAD,base.PAD+ar-ax,base.PAD+ab-ay))
    base.require(stats(padded_outside)['nonzero_pixels']==0,'audit: resample extent crops filtered source alpha')
    raw_out=[]
    for y in range(source.height):
        for x in range(source.width):
            wx,wy=(x+.5)*AFFINE[0]+AFFINE[2],(y+.5)*AFFINE[4]+AFFINE[5]
            if not (sx<=wx<sr and sy<=wy<sb):
                raw_out.append(source.getpixel((x,y))[3])
    outputs={'ground-audit.png':base.png(audit),'ground-padded.png':base.png(padded),
             'BMP/BACKGRND.BMP/000.png':base.png(ground)}
    rows=[{**recipe['frames'][0],'sha256':base.sha(outputs['BMP/BACKGRND.BMP/000.png']),'coverage':stats(ground)}]
    with zipfile.ZipFile(ARCHIVE) as archive:
        for row in recipe['frames'][1:]:
            foam=Image.open(io.BytesIO(archive.read(row['source_member']))).convert('RGBA')
            retained,measure=mask.occlude(foam,ground,row['logical_origin_hd'],WORLD_BOX)
            validate_foam_only(foam,retained,f"{row['frame']:03}")
            outputs[row['path']]=base.png(retained)
            rows.append({**row,'sha256':base.sha(outputs[row['path']]),'source_coverage':stats(foam),
                         'retained_coverage':stats(retained),'visibility_measurements':measure})
    report={'schema_version':1,'status':'DIAGNOSTIC_EXPORTED','accepted':False,'scope':recipe['scope'],
            'exporter_sha256':base.sha(Path(__file__).read_bytes()),'recipe_sha256':base.sha(base.encode(recipe)),
            'source_sha256':SOURCE_SHA,'uniform_resample_count':1,'ground_owner_frames':[0],
            'logical_offset_hd':[-36,-10],'static_world_box':WORLD_BOX,'static_extent_cropped_filtered_alpha':outside_stats,
            'audit_extent_cropped_filtered_alpha':stats(padded_outside),
            'raw_alpha_outside_static_extent_before_uniform_filter':{'nonzero_pixels':sum(v>0 for v in raw_out),
                'alpha8_pixels':sum(v>=8 for v in raw_out),'maximum_alpha':max(raw_out,default=0),'alpha_sum':sum(raw_out)},
            'noise_note':'Raw faint source alpha outside the static box is measured separately. One uniform filter rounds that faint material away; no alpha cutoff or manual cleanup is applied. Static640x180 retains every nonzero filtered pixel, including the two black alpha1 pixels atworld1114,725 and1114,726.',
            'blend_limit':recipe['foam_visibility'],'frames':rows,
            'outputs_sha256':{name:base.sha(raw) for name,raw in outputs.items()}}
    return outputs,report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare',action='store_true')
    parser.add_argument('--recipe',type=Path,default=HERE/'recipe-v1.json')
    parser.add_argument('--output',type=Path,default=HERE/'candidates/v1')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    base,_=helpers()
    print('WITNESS integrated-shore '+base.sha(Path(__file__).read_bytes()))
    try:
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
        if args.prepare:
            args.recipe.write_bytes(base.encode(recipe))
        print('PASS '+json.dumps({'ground_canvas':[640,180],'ground_offset':[-36,-10],'ground_owners':[0],'cropped_filtered_pixels':outside_count(report)}))
        return 0
    except (ValueError,OSError,KeyError,TypeError) as exc:
        print('FAIL '+str(exc),file=sys.stderr)
        return 1


def outside_count(report):
    return report['static_extent_cropped_filtered_alpha']['nonzero_pixels']


if __name__=='__main__':
    raise SystemExit(main())
