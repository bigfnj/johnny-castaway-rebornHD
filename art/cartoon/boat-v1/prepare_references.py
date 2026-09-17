"""Copy exact boat references and record their source identities."""
from pathlib import Path
import hashlib
import io
import json
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "reference"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    originals = ROOT / "art/cartoon/character-inventory-v1/reference-originals.zip"
    runtime = ROOT / "assets/scrantic_data.zip"
    entries = []
    for archive, member, name, role in [
        (originals, "native/BMP/BOAT.BMP/000.png", "original-000.png", "original geometry"),
        (runtime, "data/hd/BMP/BOAT.BMP/000.png", "hd-000.png", "current HD proxy"),
        (runtime, "data/styles/cartoon/BMP/BACKGRND.BMP/012.png", "approved-palm012.png", "Cartoon outline and shading style"),
    ]:
        with zipfile.ZipFile(archive) as z:
            data = z.read(member)
        (OUT / name).write_bytes(data)
        with Image.open(io.BytesIO(data)) as im:
            entries.append(dict(file=name, role=role, source_archive=archive.relative_to(ROOT).as_posix(), source_member=member, sha256=sha(data), canvas=list(im.size), mode=im.mode))
    source_map = ROOT / "art/cartoon/character-inventory-v1/scene-map/resource-map.json"
    resource = next(r for r in json.loads(source_map.read_text())["resources"] if r["resource"] == "BOAT.BMP")
    record = dict(schema_version=1, resource="BOAT.BMP", frame=0,
        original_canvas=[248, 61], runtime_canvas=[496, 122],
        palette_limit="Original diagnostic palette establishes geometry, not original-executable color parity.",
        sources=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p.read_bytes())) for p in [originals, runtime, source_map]],
        images=entries, static_actions=resource["unique_slot_frame_actions"],
        scope="Static script attribution and reference extraction only; scene placement and native motion remain pending.")
    (OUT / "source.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(entries, indent=2))

if __name__ == "__main__":
    main()
