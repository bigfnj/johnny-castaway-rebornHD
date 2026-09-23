"""Verify the completed delegated date assets and retain their alpha statistics."""
import hashlib
import json
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
assigned = {"SMDATE1.BMP": list(range(17)), "SMDATE10.BMP": [4,5,6], "SMDATE11.BMP": [4]}
entries = []
for resource, frames in assigned.items():
    for number in frames:
        frame = f"{number:03}"
        versions = [1,2] if resource == "SMDATE1.BMP" and number in [2,3] else [1]
        for version in versions:
            folder = HERE / "generation" / resource
            record_path = folder / f"{frame}-record-v{version}.json"
            record = json.loads(record_path.read_text(encoding="utf-8"))
            output = ROOT / record["output"]["path"]
            raw = Path(record["raw_tool_output"])
            digest = hashlib.sha256(output.read_bytes()).hexdigest()
            assert output.read_bytes() == raw.read_bytes(), str(output)
            assert digest == record["output"]["sha256"], str(output)
            request = ROOT / record["request"]["path"]
            assert hashlib.sha256(request.read_bytes()).hexdigest() == record["request"]["sha256"], str(request)
            for reference in record["references"]:
                ref = ROOT / reference["path"]
                assert hashlib.sha256(ref.read_bytes()).hexdigest() == reference["sha256"], str(ref)
            with Image.open(output) as im:
                assert im.mode == "RGBA", str(output)
                assert im.getchannel("A").getextrema() == (0,255), str(output)
            entries.append({"resource":resource,"frame":frame,"version":version,"sha256":digest,"image":record["image"]})
report = {"assigned_slots":21,"completed_slots":sum(len(v) for v in assigned.values()),
          "saved_versions":len(entries),"all_raw_copies_byte_exact":True,
          "all_request_and_reference_hashes_match":True,"all_rgba_with_transparency":True,
          "selected_corrections":{"SMDATE1.BMP-002":2,"SMDATE1.BMP-003":2},
          "appearance_approval":None,"production_integrated":False,"entries":entries}
(HERE/"SMDATE1-10-11-inspection.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps({k:v for k,v in report.items() if k != "entries"},indent=2))
