"""Actual master reconstruction, partial-alpha ownership and fresh CLI witnesses."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from PIL import Image

HERE = Path(__file__).resolve().parent
HELPER = HERE/'export.py'
SAVED = HERE/'candidates/v1'
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def reconstruct(adapter, outputs, recipe, lossless=False):
    wx,wy,_,_ = recipe['world_crop']
    width,height = recipe['master_canvas']
    reconstructed = Image.new('RGBA',(width,height))
    for group,box in adapter.BOXES.items():
        layer = Image.open(io.BytesIO(outputs[f'ground/{group:03}.png'])).convert('RGBA')
        if lossless:
            for rect in adapter.OWNERSHIP[group]:
                x0,y0,x1,y1 = max(wx,rect[0]),max(wy,rect[1]),min(wx+width,rect[2]),min(wy+height,rect[3])
                reconstructed.paste(layer.crop((x0-box[0],y0-box[1],x1-box[0],y1-box[1])),(x0-wx,y0-wy))
        else:
            x0,y0,x1,y1 = max(wx,box[0]),max(wy,box[1]),min(wx+width,box[2]),min(wy+height,box[3])
            reconstructed.alpha_composite(layer.crop((x0-box[0],y0-box[1],x1-box[0],y1-box[1])),(x0-wx,y0-wy))
    return reconstructed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=('smoke','regression'),required=True)
    args = parser.parse_args()
    helper = HELPER.read_bytes()
    recipe_raw = (HERE/'recipe-v1.json').read_bytes()
    recipe = json.loads(recipe_raw)
    report_raw = (SAVED/'export-report.json').read_bytes()
    selected = json.loads(report_raw)
    runs = []

    def run(label,options=(),failure=None,script=HELPER,mutant=None):
        result = subprocess.run([sys.executable,'-B',str(script),*map(str,options)],capture_output=True,text=True,encoding='utf-8',timeout=90)
        assert result.returncode == (1 if failure else 0),(label,result.stdout,result.stderr)
        assert 'WITNESS shared-ground '+sha(helper) in result.stdout
        assert result.stderr.strip() == ('FAIL '+failure if failure else ''),(label,result.stderr)
        assert failure or 'DIAGNOSTIC ' in result.stdout
        assert not mutant or 'EXECUTED_MUTANT_SHA256='+mutant in result.stdout
        runs.append({'name':label,'result':'FIRED' if failure else 'PASS','stdout':result.stdout,'stderr':result.stderr})

    run('selected_smoke_readback',['--check'])
    evidence = {'status':'PASS','phase':args.phase,'scope':'Export integrity and representable ground ownership only; reported crop/uncovered alpha is not waived.',
                'exporter_sha256':sha(helper),'test_sha256':sha(Path(__file__).read_bytes()),
                'recipe_sha256':sha(recipe_raw),'export_report_sha256':sha(report_raw)}
    if args.phase == 'regression':
        spec = importlib.util.spec_from_file_location('shared_ground_checked',HELPER)
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        real_resample = adapter.base.resample
        calls = []

        def counted(*values):
            calls.append(values[1:])
            return real_resample(*values)

        adapter.base.resample = counted
        actual,actual_report = adapter.render(recipe)
        adapter.base.resample = real_resample
        assert len(calls)==1
        for name,data in actual.items():
            assert data == (SAVED/name).read_bytes(),name
        master = Image.open(io.BytesIO(actual['master-ground.png'])).convert('RGBA')
        restored = reconstruct(adapter,actual,recipe,lossless=True)
        composited = reconstruct(adapter,actual,recipe)
        wx,wy,_,_ = recipe['world_crop']
        missing = []
        owned_count = 0
        transparent_rgb_normalized = 0
        for y in range(master.height):
            for x in range(master.width):
                covered = any(adapter.inside(x+wx,y+wy,box) for box in adapter.BOXES.values())
                if covered:
                    assert restored.getpixel((x,y)) == master.getpixel((x,y)),(x,y)
                    observed = composited.getpixel((x,y))
                    expected = master.getpixel((x,y))
                    assert observed[3] == expected[3]
                    if expected[3]:
                        assert observed == expected,(x,y)
                    elif observed != expected:
                        transparent_rgb_normalized += 1
                    owned_count += 1
                else:
                    assert restored.getpixel((x,y))[3] == 0
                    if master.getpixel((x,y))[3]:
                        missing.append({'world_xy':[x+wx,y+wy],'rgba':list(master.getpixel((x,y)))})
        evidence['actual_reconstruction'] = {'covered_pixels_rgba_exact':owned_count,'unrepresentable_nonzero_pixels':missing,
                                             'full_master_exact':not missing,'actual_resample_calls':len(calls),
                                             'source_over_nonzero_rgba_and_all_alpha_exact':True,
                                             'zero_alpha_hidden_rgb_normalized_by_source_over':transparent_rgb_normalized}
        # Exercise the SAME render/crop implementation with partially transparent
        # master pixels at both overlapping rectangle boundaries. No output files
        # are replaced; the synthetic source is confined to this test call.
        synthetic = Image.new('RGBA',(master.width,master.height))
        witness_points = [(860,650),(1040,666)]
        for x,y in witness_points:
            synthetic.putpixel((x-wx,y-wy),(90,140,210,128))
        synthetic.putpixel((850-wx,650-wy),(90,140,210,255))
        padded = Image.new('RGBA',(master.width+64,master.height+64))
        padded.paste(synthetic,(32,32))
        adapter.base.resample = lambda *unused:padded.copy()
        try:
            witness_outputs,_ = adapter.render(recipe)
        finally:
            adapter.base.resample = real_resample
        witness_result = reconstruct(adapter,witness_outputs,recipe)
        assert witness_result.tobytes() == synthetic.tobytes()
        duplicated = Image.alpha_composite(Image.new('RGBA',(1,1),(90,140,210,128)),Image.new('RGBA',(1,1),(90,140,210,128)))
        assert duplicated.getpixel((0,0))[3] == 192
        evidence['partial_alpha_witness'] = {'world_points':[list(p) for p in witness_points],
            'input_alpha':128,'actual_reconstructed_alpha':[witness_result.getpixel((x-wx,y-wy))[3] for x,y in witness_points],
            'duplicate_crop_control_alpha':192,'opaque_and_transparent_controls_exact':True}
        with tempfile.TemporaryDirectory(prefix='replay-',dir=HERE) as temporary:
            work = Path(temporary).resolve()
            assert work.is_relative_to(HERE.resolve())
            run('fresh_selected_replay',['--output',work/'replay'])
            for name in [*selected['outputs_sha256'],'export-report.json']:
                assert (SAVED/name).read_bytes() == (work/'replay'/name).read_bytes(),name

            def execute_variant(label,text,failure=None):
                data = text.encode('utf-8')
                path = work/(label+'.py')
                path.write_bytes(data)
                driver = work/(label+'-run.py')
                driver.write_text('from pathlib import Path\nimport hashlib\nraw=Path('+repr(str(path))+').read_bytes()\n'
                                  +"print('EXECUTED_MUTANT_SHA256='+hashlib.sha256(raw).hexdigest())\n"
                                  +'exec(compile(raw,'+repr(str(HELPER))+',"exec"),{"__name__":"__main__","__file__":'+repr(str(HELPER))+'})\n',encoding='utf-8')
                output = work/label
                run(label,['--prepare','--recipe',work/(label+'.json'),'--output',output],failure,driver,sha(data))
                return output,sha(data)

            text = helper.decode('utf-8')
            original = '6: [(728,662,1048,688)]'
            assert text.count(original)==1
            dropped = text.replace(original,'6: [(728,663,1048,688)]',1)
            execute_variant('missing_center_ground_row_rejected',dropped,'master: ground ownership differs from original-canvas union')
            statement = "    base.require(all(bool(n)==covered for n,covered in zip(count,expected)), 'master: ground ownership differs from original-canvas union')"
            assert dropped.count(statement)==1
            removed = dropped.replace(statement,'    pass  # executed control: ownership union check removed',1)
            wrong,mutant_sha = execute_variant('missing_row_accepted_only_without_guard',removed)
            assert (wrong/'BMP/BACKGRND.BMP/006.png').read_bytes() != (SAVED/'BMP/BACKGRND.BMP/006.png').read_bytes()
            wrong_report = json.loads((wrong/'export-report.json').read_bytes())
            assert wrong_report['master_alpha_outside_original_canvas_union']['alpha8_pixels'] > selected['master_alpha_outside_original_canvas_union']['alpha8_pixels']
            evidence['guard_removal'] = {'mutant_sha256':mutant_sha,'removed_statement':statement,
                'actually_changed_006_png_sha256':sha((wrong/'BMP/BACKGRND.BMP/006.png').read_bytes()),
                'wrong_uncovered_alpha':wrong_report['master_alpha_outside_original_canvas_union']}
            original = '(1048,662,1136,670)'
            assert text.count(original)==1
            execute_variant('duplicate_overlap_ground_rejected',text.replace(original,'(1036,662,1136,670)',1),'master: duplicate ground ownership')
        run('restored_selected_positive',['--check'])
        assert HELPER.read_bytes()==helper and (HERE/'recipe-v1.json').read_bytes()==recipe_raw
        assert (SAVED/'export-report.json').read_bytes()==report_raw
    evidence['runs'] = runs
    (HERE/('verification-'+args.phase+'.json')).write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('PASS shared-ground '+args.phase)


if __name__=='__main__':
    main()
