"""Run authoring smoke before guarded-input regressions and source mutations.

All mutations run in an isolated copied authoring folder under --output.
The normal-mode positive control uses synthetic rectangles, not modified art.
"""
import argparse,hashlib,importlib.util,json,shutil,subprocess,sys,tempfile
from pathlib import Path
from PIL import Image,ImageDraw

HERE=Path(__file__).resolve().parent
def sha(data): return hashlib.sha256(data).hexdigest()
def execute(script,recipe,output,preview=True):
    command=[sys.executable,"-B",str(script),"--recipe",str(recipe),"--output",str(output)]
    if preview: command.append("--preview-only")
    result=subprocess.run(command,capture_output=True,text=True)
    assert "WITNESS export.py SHA256="+sha(script.read_bytes()) in result.stdout,"export.py: execution witness"
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--recipe",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    recipe=json.loads(args.recipe.read_text())
    baseline=args.output/"baseline"
    r=execute(HERE/"export.py",args.recipe,baseline)
    assert r.returncode==0 and "PREVIEW ONLY" in r.stdout,r.stderr
    assert len(list((baseline/"padded").glob("*.png")))==6 and not (baseline/"BMP").exists()
    print("SMOKE PASS exact six-source padded preview; no runtime sprites",flush=True)
    report=json.loads((baseline/"export-report.json").read_text())
    assert all(row["affine_forward"][0]==.1 and row["affine_forward"][4]==.1 for row in report["frames"])
    assert report["runtime_fit_all_source_centers"] is False
    assert [row["frame"] for row in report["frames"] if not row["source_centers_fit_runtime"]]==[22]
    print("SMOKE PASS common scale and measured022 overhang",flush=True)
    results=[];mutants=[]
    with tempfile.TemporaryDirectory(prefix="export-probe-",dir=args.output) as temp:
        root=Path(temp);copy=root/"authoring";copy.mkdir();(copy/"reference").mkdir()
        for name in ("export.py",):shutil.copyfile(HERE/name,copy/name)
        shutil.copyfile(HERE/"reference/metadata.json",copy/"reference/metadata.json")
        for row in recipe["frames"]:shutil.copyfile(HERE/row["source"],copy/row["source"])
        recipe_path=copy/"recipe.json"
        def write_recipe(value):recipe_path.write_text(json.dumps(value),encoding="utf-8")
        write_recipe(recipe)
        r=execute(copy/"export.py",recipe_path,root/"reproduced")
        assert r.returncode==0,r.stderr
        for frame in [11,19,20,21,22,23]:
            assert (baseline/"padded"/f"{frame:03}.png").read_bytes()==(root/"reproduced/padded"/f"{frame:03}.png").read_bytes()
        results.append("six-padded-PNG-byte-reproduction")
        # A real normal-mode positive control, independent of any art bounds.
        sources={}
        for frame in [11,19,20,21,22,23]:
            im=Image.new("RGBA",(1024,1536));ImageDraw.Draw(im).rectangle((320,45,500,1430),fill=(160,80,30,255))
            name=f"synthetic-{frame}.png";im.save(copy/name);sources[frame]=name
        spec=importlib.util.spec_from_file_location("probe_export",copy/"export.py")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        synthetic=module.prepare(sources);write_recipe(synthetic)
        r=execute(copy/"export.py",recipe_path,root/"normal-control",False)
        assert r.returncode==0,r.stderr
        for row in synthetic["frames"]:
            im=Image.open(root/"normal-control/BMP/JOHNWALK.BMP"/f"{row['frame']:03}.png")
            assert list(im.size)==row["runtime_canvas"] and im.getchannel("A").getextrema()[1]>200
        results.append("six-synthetic-fitting-normal-exports")
        original=(copy/"export.py").read_text(encoding="utf-8")
        cases=[
          ("reference-identity",lambda d:d.update(reference_sha256="0"*64),
           'require(recipe["reference_sha256"]==sha(raw),"reference-identity")','require(True,"reference-identity")'),
          ("family-render-contract",lambda d:d["scale_exact"].update(denominator=11),
           'require(recipe["scale_exact"]=={"numerator":1,"denominator":10} and recipe["normalization"]=="none" and\n            recipe["padding_hd"]==PAD and recipe["resampling"]==FILTERS and recipe["pillow_version"]==PIL.__version__,"family-render-contract")',
           'require(True,"family-render-contract")'),
          ("six-source-family",lambda d:d["frames"].pop(),
           'require([item["frame"] for item in recipe["frames"]]==FRAMES,"six-source-family")','require(True,"six-source-family")'),
          ("source-identity:011",lambda d:d["frames"][0].update(source_sha256="0"*64),
           'require(sha(data)==item["source_sha256"],f"source-identity:{frame:03}")','require(True,f"source-identity:{frame:03}")'),
          ("source-canvas:011",lambda d:d["frames"][0].update(generated_canvas=[1024,1535]),
           'require(source.mode=="RGBA" and source.size==(1024,1536) and item["generated_canvas"]==[1024,1536],f"source-canvas:{frame:03}")',
           'require(True,f"source-canvas:{frame:03}")'),
          ("fixed-registration:011",lambda d:d["frames"][0]["affine_forward"].__setitem__(1,.01),
           'require(item["cap_raw"]==cap and item["cap_target_hd"]==TARGET and recipe["cap_target_hd"]==TARGET and\n                    len(item["affine_forward"])==6 and all(math.isclose(a,b,rel_tol=0,abs_tol=1e-12) for a,b in zip(item["affine_forward"],expected)),f"fixed-registration:{frame:03}")',
           'require(True,f"fixed-registration:{frame:03}")'),
          ("runtime-canvas:011",lambda d:d["frames"][0].update(runtime_canvas=[65,156]),
           'require(item["runtime_canvas"]==canvas,f"runtime-canvas:{frame:03}")','require(True,f"runtime-canvas:{frame:03}")'),
          ("runtime-overhang:022",lambda d:None,
           'require(preview_only or fits,f"runtime-overhang:{frame:03}")','require(True,f"runtime-overhang:{frame:03}")')]
        for index,(label,change,old,new) in enumerate(cases):
            bad=json.loads(json.dumps(recipe));change(bad);write_recipe(bad)
            preview=not label.startswith("runtime-overhang")
            output=root/f"bad{index}"
            r=execute(copy/"export.py",recipe_path,output,preview)
            assert r.returncode==1 and r.stderr.strip()=="FAIL "+label and not output.exists(),label+": expected refusal"
            results.append(label+"-refused-before-output")
            assert original.count(old)==1,label+": mutant anchor"
            mutant=original.replace(old,new)
            (copy/"export.py").write_text(mutant,encoding="utf-8",newline="\n")
            r=execute(copy/"export.py",recipe_path,root/f"mutant{index}",preview)
            assert r.returncode==0,label+": mutant did not accept targeted wrong input: "+r.stderr
            mutants.append({"label":"export.py: "+label+"-refused-before-output","result":"FIRED","failure_count":1,
                            "executed_mutant_sha256":sha((copy/"export.py").read_bytes()),"witness":"fresh python -B child prints exact source SHA"})
            (copy/"export.py").write_text(original,encoding="utf-8",newline="\n")
        write_recipe(recipe)
        r=execute(copy/"export.py",recipe_path,root/"restored")
        assert r.returncode==0 and all((root/"restored/padded"/f"{f:03}.png").read_bytes()==(baseline/"padded"/f"{f:03}.png").read_bytes() for f in [11,19,20,21,22,23])
        results.append("restored-source-six-PNG-reproduction")
    evidence={"export_source_sha256":sha((HERE/"export.py").read_bytes()),"test_sha256":sha(Path(__file__).read_bytes()),
              "recipe_sha256":sha(args.recipe.read_bytes()),"smoke_passed":2,"regressions":results,"mutations":mutants,
              "limit":"Authoring-only Python checks; synthetic rectangles prove fitting normal-mode behavior, not anatomical correctness."}
    (args.output/"verification.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"PASS {len(results)} regressions; {len(mutants)} executed-source mutations FIRED")

if __name__=="__main__":main()
