"""Copy exact original frames and produce nearest-neighbor viewing references."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INVENTORY = HERE.parent / "character-inventory-v1"
GROUPS = {"GJGULL1.BMP": list(range(33)), "LILFISH.BMP": list(range(9))}

def ident(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

def main():
    index_path = INVENTORY / "source/frame-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    lookup = {(f["resource"], f["frame"]): f for f in index["frames"]}
    archive = INVENTORY / "reference-originals.zip"
    rows = []
    with zipfile.ZipFile(archive) as z:
        for resource, frames in GROUPS.items():
            for n in frames:
                item = lookup[(resource, n)]
                raw = z.read(item["path"])
                assert hashlib.sha256(raw).hexdigest() == item["png_sha256"], item["id"]
                original = HERE / f"reference/original/{resource}/{n:03}.png"
                nearest = HERE / f"reference/nearest8/{resource}/{n:03}.png"
                original.parent.mkdir(parents=True, exist_ok=True)
                nearest.parent.mkdir(parents=True, exist_ok=True)
                original.write_bytes(raw)
                with Image.open(io.BytesIO(raw)) as im:
                    im.resize((im.width * 8, im.height * 8), Image.Resampling.NEAREST).save(nearest)
                rows.append({"resource": resource, "frame": f"{n:03}", "canvas": item["canvas"],
                             "archive_member": item["path"], "original": ident(original), "nearest8": ident(nearest),
                             "source_rgba_sha256": item["rgba_sha256"]})
    record = {"schema_version": 1, "scope": "42 original source slots; no generated artwork approval", "count": len(rows),
              "palette_limit": index["palette_limit"], "archive": ident(archive), "frame_index": ident(index_path),
              "preparation": ident(Path(__file__)), "assets": rows}
    (HERE / "reference/source.json").write_text(json.dumps(record, indent=2) + '\n', encoding="utf-8")
    print(f"Prepared {len(rows)} exact originals and nearest8 references")

if __name__ == "__main__":
    main()
