"""Bounded smoke, reproduction checks and executed-source guard mutations.

Requires --dump-root and --output (ignored test evidence directory). All changes
are isolated copies beneath output; production inputs and artwork remain read-only.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(script, dump, output):
    proc = subprocess.run([sys.executable, "-B", str(script), "--dump-root", str(dump),
                           "--output", str(output)], capture_output=True, text=True)
    witness = "WITNESS extract.py SHA256="+sha(script.read_bytes())
    assert witness in proc.stdout, "executed-source-witness"
    return proc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dump-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    expected = json.loads((HERE/"metadata.json").read_text(encoding="utf-8"))
    baseline = args.output/"baseline"
    proc = run(HERE/"extract.py", args.dump_root, baseline)
    assert proc.returncode == 0 and "PASS original-reference36" in proc.stdout, proc.stderr
    print("SMOKE PASS extract.py full36 real source", flush=True)
    small = Image.open(baseline/"native/011.png").convert("RGBA")
    large = Image.open(baseline/"nearest8/011.png").convert("RGBA")
    assert small.size == (32,78) and large.size == (256,624)
    assert sha(small.tobytes()) == "ce1dac4cbd7b20fa35807655c9cb69c7e24e50afce7c674d1db2842d783bb504"
    assert all(large.getpixel((x,y)) == small.getpixel((x//8,y//8))
               for y in range(large.height) for x in range(large.width))
    print("SMOKE PASS original011 exact pixels and integer nearest8", flush=True)
    results = []
    actual = json.loads((baseline/"metadata.json").read_text(encoding="utf-8"))
    assert actual == expected, "full36-metadata-reproduction"
    for frame in expected["frames"]:
        im = Image.open(baseline/"native"/f"{frame['frame']:03}.png").convert("RGBA")
        assert list(im.size) == frame["canvas"] and sha(im.tobytes()) == frame["rgba_sha256"]
    results.append("full36-metadata-canvas-and-RGBA-reproduction")
    for sub, tracked in (("native/011.png","011-native.png"),("nearest8/011.png","011-nearest8.png")):
        assert (baseline/sub).read_bytes() == (HERE/tracked).read_bytes(), tracked
    results.append("selected011-PNG-byte-reproduction")
    mutations=[]
    with tempfile.TemporaryDirectory(prefix="reference-probe-", dir=args.output) as temporary:
        sandbox = Path(temporary)
        repo = sandbox/"repo"
        ref = repo/"art/cartoon/walk-expansion-v1/reference"
        ref.mkdir(parents=True)
        for name in ("extract.py","source.json"):
            shutil.copyfile(HERE/name,ref/name)
        (repo/"tools").mkdir()
        for name in ("art_review_metadata.py","art_common.py","inventory_scenes.py"):
            shutil.copyfile(ROOT/"tools"/name,repo/"tools"/name)
        (repo/"src/data").mkdir(parents=True)
        table=(ROOT/"src/data/walk_data.h").read_bytes()
        table_path=repo/"src/data/walk_data.h"
        table_path.write_bytes(table)
        dump=sandbox/"dump-input"
        (dump/"dump/BMP").mkdir(parents=True)
        report=(args.dump_root/"report.json").read_bytes()
        (dump/"report.json").write_bytes(report)
        for frame in range(36):
            name=f"JOHNWALK.BMP.{frame:03}.xpm"
            shutil.copyfile(args.dump_root/"dump/BMP"/name,dump/"dump/BMP"/name)
        table_lf=table.decode("utf-8").replace("\r\n","\n").replace("\r","\n")
        for name,newline in (("lf","\n"),("crlf","\r\n"),("cr","\r")):
            table_path.write_bytes(table_lf.replace("\n",newline).encode("utf-8"))
            out=sandbox/("table-"+name)
            r=run(ref/"extract.py",dump,out)
            assert r.returncode == 0 and json.loads((out/"metadata.json").read_text()) == expected, name
            results.append("table-text-normalization-"+name)
        table_path.write_bytes(table)
        original_script=(ref/"extract.py").read_text(encoding="utf-8")
        cases=[
          ("original-source-identity", "report", "pair",
           'require(report.get("input_sha256") == expected["resource_sha256"] and\n            report.get("engine_sha256") == expected["dump_engine_sha256"] and\n            report.get("exit_code") == 0, "original-source-identity")',
           'require(True, "original-source-identity")'),
          ("original-frame-identity:019", "frame", "pixel",
           'require(sha(data) == digest, f"original-frame-identity:{frame}")',
           'require(True, f"original-frame-identity:{frame}")'),
          ("walk-table-identity", "table", "coordinate",
           'require(text_fingerprint(table_bytes) == expected["walk_table_lf_sha256"], "walk-table-identity")',
           'require(True, "walk-table-identity")')]
        frame_path=dump/"dump/BMP/JOHNWALK.BMP.019.xpm"
        original_frame=frame_path.read_bytes()
        def refuse(label, out):
            r=run(ref/"extract.py",dump,out)
            ok=r.returncode == 1 and r.stderr.strip() == "FAIL "+label and not out.exists()
            return ok,r
        for index,(label,target,axis,old,new) in enumerate(cases):
            if target == "report":
                bad=json.loads(report); bad["input_sha256"]["RESOURCE.MAP"]="0"*64
                (dump/"report.json").write_text(json.dumps(bad),encoding="utf-8")
            elif target == "frame":
                frame_path.write_bytes(original_frame.replace(b'"00000055555',b'"10000055555',1))
                assert frame_path.read_bytes() != original_frame
            else:
                changed=table.replace(b"{ 0, 446, 252, 11 }",b"{ 0, 445, 252, 11 }",1)
                assert changed != table
                table_path.write_bytes(changed)
            ok,r=refuse(label,sandbox/f"bad-{index}")
            assert ok, label+": refusal missing: "+r.stderr
            results.append(label+"-bad-input-refused-before-output")
            assert original_script.count(old) == 1, label+": mutant anchor"
            mutant=original_script.replace(old,new)
            (ref/"extract.py").write_text(mutant,encoding="utf-8",newline="\n")
            ok,r=refuse(label,sandbox/f"mutant-{index}")
            assert not ok and r.returncode == 0 and "PASS original-reference36" in r.stdout, label+": mutant did not execute omitted guard"
            mutations.append({"guard":label,"axis":axis,"mutant_source_sha256":sha((ref/"extract.py").read_bytes()),
                              "witness":"exact source SHA printed by fresh python -B subprocess",
                              "result":"FIRED","named_failure":label+"-bad-input-refused-before-output",
                              "failure_count":1,"observed_mutant_behavior":"accepted the deliberately wrong input"})
            (ref/"extract.py").write_text(original_script,encoding="utf-8",newline="\n")
            (dump/"report.json").write_bytes(report)
            frame_path.write_bytes(original_frame)
            table_path.write_bytes(table)
        # Raw XPM identity deliberately has no line-ending normalization.
        frame_lf=original_frame.replace(b"\r\n",b"\n")
        changed=frame_lf if original_frame != frame_lf else frame_lf.replace(b"\n",b"\r\n")
        frame_path.write_bytes(changed)
        ok,r=refuse("original-frame-identity:019",sandbox/"changed-xpm-newlines")
        assert ok, "raw-XPM-byte-identity"
        results.append("raw-XPM-newline-change-refused")
        frame_path.write_bytes(original_frame)
        restored=run(ref/"extract.py",dump,sandbox/"restored")
        assert restored.returncode == 0 and json.loads((sandbox/"restored/metadata.json").read_text()) == expected
        results.append("restored-source-positive-reproduction")
    final={"source_sha256":sha((HERE/"extract.py").read_bytes()),"test_sha256":sha(Path(__file__).read_bytes()),
           "smoke_passed":2,"regressions":results,"mutations":mutations,
           "scope":"Authoring reference only. No runtime build or GUI capture. Python mutants run in fresh -B subprocesses and emit their exact source SHA.",
           "mutation_storage":"Temporary copied repository beneath the requested output directory."}
    (args.output/"verification.json").write_text(json.dumps(final,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"PASS {len(results)} regression checks; {len(mutations)} executed-source mutations FIRED",flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
