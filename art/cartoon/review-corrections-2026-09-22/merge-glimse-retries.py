"""Merge the named retry entry while preserving every other manifest row."""
import copy
import json
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
path=HERE/"glimse/manifest.json"
manifest=json.loads(path.read_text(encoding="utf-8-sig"))
before=copy.deepcopy(manifest)
replacements={}
for name in (sys.argv[1:] or ["013-entry-v3.json"]):
    entry=json.loads((HERE/"glimse"/name).read_text(encoding="utf-8-sig"))
    assert entry["frame"] in ("013","014") and not entry.get("appearance_approval")
    replacements[entry["frame"]]=entry
for index,entry in enumerate(manifest["entries"]):
    if entry["frame"] in replacements:
        manifest["entries"][index]=replacements[entry["frame"]]
    else:
        assert entry==before["entries"][index]
path.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"updated_frames":sorted(replacements),"other_entries_unchanged":True,"retry_approvals":None}))
