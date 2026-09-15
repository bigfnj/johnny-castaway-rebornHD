"""Prepare or reproduce a fixed-scale technical walking review, without promotion.

--prepare accepts six explicit --source FRAME=FILENAME entries, relative to this
folder, and records their measured cap registration. The default reproduces a
saved recipe. --preview-only permits padded review of overhanging artwork and
never writes the runtime-canvas sprites. No source artwork is altered.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import PIL
from PIL import Image

HERE = Path(__file__).resolve().parent
FRAMES = [11,19,20,21,22,23]
SCALE = .1
PAD = 64
TARGET = [17,.25]
FILTERS = {"working_mode":"RGBa", "affine":"BICUBIC", "oversample":8,
           "downsample":"LANCZOS", "output_mode":"RGBA", "png_compress_level":9}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def png(image):
    output=io.BytesIO()
    image.save(output,format="PNG",compress_level=9)
    return output.getvalue()


def measure_cap(image):
    alpha=image.getchannel("A")
    bounds=alpha.point(lambda value:255 if value>=128 else 0).getbbox()
    require(bounds is not None and bounds[1]<300,"cap-outline-not-found")
    y=bounds[1]
    xs=[x for x in range(image.width) if alpha.getpixel((x,y))>=128]
    return [(min(xs)+max(xs)+1)/2,y]


def reference():
    raw=(HERE/"reference/metadata.json").read_bytes()
    value=json.loads(raw)
    return raw,value,{item["frame"]:item for item in value["frames"]}


def prepare(sources):
    raw,metadata,originals=reference()
    require(sorted(sources)==FRAMES,"six-source-family")
    recipe={"schema_version":1,"scope":"Technical review only; no runtime or motion approval is assigned by this recipe.",
            "reference":"reference/metadata.json","reference_sha256":sha(raw),
            "scale_exact":{"numerator":1,"denominator":10},"normalization":"none","padding_hd":PAD,
            "resampling":FILTERS,"pillow_version":PIL.__version__,
            "cap_measurement":"First row containing alpha>=128; horizontal pixel-edge midpoint of that row. Its y is the row top edge. Consistent outline observation, not an anatomical or engine anchor.",
            "cap_target_hd":TARGET,"target_basis":"Native original cap-top span x[6,11) has midpoint8.5, doubled to17HD. y0.25 is a deliberate small antialiasing margin.",
            "frames":[]}
    for frame in FRAMES:
        path=sources[frame]
        data=(HERE/path).read_bytes()
        with Image.open(io.BytesIO(data)) as image:
            require(image.mode=="RGBA" and image.size==(1024,1536),f"source-canvas:{frame:03}")
            cap=measure_cap(image)
        tx,ty=TARGET[0]-cap[0]*SCALE,TARGET[1]-cap[1]*SCALE
        recipe["frames"].append({"frame":frame,"source":path,"source_sha256":sha(data),"generated_canvas":[1024,1536],
            "runtime_canvas":[n*2 for n in originals[frame]["canvas"]],"cap_raw":cap,"cap_target_hd":TARGET,
            "affine_forward":[SCALE,0,tx,0,SCALE,ty]})
    return recipe


def render(recipe, preview_only):
    raw,metadata,originals=reference()
    require(recipe["reference_sha256"]==sha(raw),"reference-identity")
    require(recipe["scale_exact"]=={"numerator":1,"denominator":10} and recipe["normalization"]=="none" and
            recipe["padding_hd"]==PAD and recipe["resampling"]==FILTERS and recipe["pillow_version"]==PIL.__version__,"family-render-contract")
    require([item["frame"] for item in recipe["frames"]]==FRAMES,"six-source-family")
    rendered={}
    reports=[]
    for item in recipe["frames"]:
        frame=item["frame"]
        data=(HERE/item["source"]).read_bytes()
        require(sha(data)==item["source_sha256"],f"source-identity:{frame:03}")
        with Image.open(io.BytesIO(data)) as source:
            require(source.mode=="RGBA" and source.size==(1024,1536) and item["generated_canvas"]==[1024,1536],f"source-canvas:{frame:03}")
            cap=measure_cap(source)
            tx,ty=TARGET[0]-cap[0]*SCALE,TARGET[1]-cap[1]*SCALE
            expected=[SCALE,0,tx,0,SCALE,ty]
            require(item["cap_raw"]==cap and item["cap_target_hd"]==TARGET and recipe["cap_target_hd"]==TARGET and
                    len(item["affine_forward"])==6 and all(math.isclose(a,b,rel_tol=0,abs_tol=1e-12) for a,b in zip(item["affine_forward"],expected)),f"fixed-registration:{frame:03}")
            canvas=[n*2 for n in originals[frame]["canvas"]]
            require(item["runtime_canvas"]==canvas,f"runtime-canvas:{frame:03}")
            width,height=canvas
            bounds=source.getchannel("A").point(lambda value:255 if value>=8 else 0).getbbox()
            centers=[(bounds[0]+.5)*SCALE+tx,(bounds[1]+.5)*SCALE+ty,(bounds[2]-.5)*SCALE+tx,(bounds[3]-.5)*SCALE+ty]
            fits=centers[0]>=0 and centers[1]>=0 and centers[2]<width and centers[3]<height
            require(preview_only or fits,f"runtime-overhang:{frame:03}")
            size=(width+PAD*2,height+PAD*2)
            high=source.convert("RGBa").transform((size[0]*8,size[1]*8),Image.Transform.AFFINE,
                (1/(SCALE*8),0,-(tx+PAD)/SCALE,0,1/(SCALE*8),-(ty+PAD)/SCALE),
                resample=Image.Resampling.BICUBIC,fillcolor=(0,0,0,0))
            padded=high.resize(size,Image.Resampling.LANCZOS).convert("RGBA")
            filtered=padded.getchannel("A").point(lambda value:255 if value>=8 else 0).getbbox()
            padded_bytes=png(padded)
            rendered[f"padded/{frame:03}.png"]=padded_bytes
            fixed=padded.crop((PAD,PAD,PAD+width,PAD+height))
            if not preview_only:
                rendered[f"BMP/JOHNWALK.BMP/{frame:03}.png"]=png(fixed)
            reports.append({"frame":frame,"source":item["source"],"source_sha256":sha(data),"cap_raw":cap,
                "runtime_canvas":canvas,"affine_forward":expected,"alpha8_source_bounds":list(bounds),
                "alpha8_centers_hd":centers,"source_centers_fit_runtime":fits,
                "overhang_hd_left_top_right_bottom":[max(0,-centers[0]),max(0,-centers[1]),max(0,centers[2]-width),max(0,centers[3]-height)],
                "filtered_alpha8_bounds_hd_exclusive":[filtered[0]-PAD,filtered[1]-PAD,filtered[2]-PAD,filtered[3]-PAD],
                "padded_png_sha256":sha(padded_bytes),"padded_canvas":list(size)})
    return rendered,{"schema_version":1,"scope":"Diagnostic fixed-scale export. Not native capture or artistic acceptance.",
                    "preview_only":preview_only,"runtime_sprites_written":not preview_only,
                    "runtime_fit_all_source_centers":all(item["source_centers_fit_runtime"] for item in reports),
                    "padding_hd":PAD,"scale":SCALE,"reference_sha256":sha(raw),"frames":reports,
                    "filter_limit":"Source-center fit is separate from low-alpha filter fringes; padded images retain and report those fringes."}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare",action="store_true")
    parser.add_argument("--source",action="append",default=[],help="FRAME=FILENAME relative to this folder")
    parser.add_argument("--recipe",type=Path,default=HERE/"recipe.json")
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--preview-only",action="store_true")
    args=parser.parse_args()
    print("WITNESS export.py SHA256="+sha(Path(__file__).read_bytes()),flush=True)
    try:
        require(not args.output.exists(),"output-already-exists")
        if args.prepare:
            entries=[item.split("=",1) for item in args.source]
            require(len(entries)==6 and len({int(item[0]) for item in entries})==6,"six-source-family")
            recipe=prepare({int(frame):path for frame,path in entries})
        else:
            recipe=json.loads(args.recipe.read_text(encoding="utf-8"))
        images,report=render(recipe,args.preview_only)
        args.output.mkdir(parents=True,exist_ok=False)
        for name,data in images.items():
            dest=args.output/name
            dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(data)
        for name,value in (("recipe.json",recipe),("export-report.json",report)):
            (args.output/name).write_text(json.dumps(value,indent=2)+"\n",encoding="utf-8",newline="\n")
    except (ValueError,OSError,KeyError) as error:
        print("FAIL "+str(error),file=sys.stderr)
        return 1
    print("PASS six fixed-scale exports; "+("PREVIEW ONLY: runtime sprites not written" if args.preview_only else "runtime-canvas candidates written; not promoted"),flush=True)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
