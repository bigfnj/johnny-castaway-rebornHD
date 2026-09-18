"""Copy exact FIRE1 references; enlarge only diagnostic reference views."""
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = HERE / "reference"
INVENTORY = ROOT / "art/cartoon/character-inventory-v1"

def ident(path):
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest())

def main():
    original_zip = INVENTORY / "reference-originals.zip"
    runtime_zip = ROOT / "assets/scrantic_data.zip"
    index_path = INVENTORY / "source/frame-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8-sig"))
    frames = {r["frame"]: r for r in index["frames"] if r["resource"] == "FIRE1.BMP"}
    for folder in ("original", "hd", "nearest8"):
        (OUT / folder).mkdir(parents=True, exist_ok=True)
    entries = []
    sheets = [Image.new("RGB", (1280, 1320), "#293e4c") for _ in range(2)]
    with ZipFile(original_zip) as originals, ZipFile(runtime_zip) as runtime:
        for n in range(28):
            member = f"native/BMP/FIRE1.BMP/{n:03}.png"
            hd_member = f"data/hd/BMP/FIRE1.BMP/{n:03}.png"
            data, hd = originals.read(member), runtime.read(hd_member)
            original_path = OUT / "original" / f"{n:03}.png"
            hd_path = OUT / "hd" / f"{n:03}.png"
            original_path.write_bytes(data)
            hd_path.write_bytes(hd)
            with Image.open(io.BytesIO(data)) as source:
                im = source.convert("RGBA")
            guide = OUT / "nearest8" / f"{n:03}.png"
            im.resize((im.width * 8, im.height * 8), Image.Resampling.NEAREST).save(guide)
            i = n % 14
            x, y = (i % 4) * 320, (i // 4) * 330
            diagnostic = im.resize((im.width * 6, im.height * 6), Image.Resampling.NEAREST)
            sheets[n // 14].paste(diagnostic, (x + 20, y + 42), diagnostic)
            ImageDraw.Draw(sheets[n // 14]).text((x + 20, y + 12), f"FIRE1 {n:03} {im.size} / original NN x6", fill="white")
            entries.append(dict(frame=n, original={**ident(original_path), "member": member, "canvas": list(im.size), "matches_inventory": hashlib.sha256(data).hexdigest() == frames[n]["png_sha256"]}, hd={**ident(hd_path), "member": hd_member}, nearest8=ident(guide)))
    for i, sheet in enumerate(sheets):
        sheet.save(OUT / f"original-contact-{i + 1}.png")
    record = dict(schema_version=1, resource="FIRE1.BMP", frames=entries, sources=[ident(p) for p in (original_zip, runtime_zip, index_path, Path(__file__))], palette_limit=index["palette_limit"], scope="Exact source copies and diagnostic full-canvas nearest-neighbor reference views only. No generated-art edits, runtime exports or native validation.")
    (OUT / "source.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(dict(frames=len(entries), exact_original_identities=all(e["original"]["matches_inventory"] for e in entries), source=ident(OUT / "source.json"))))

if __name__ == "__main__":
    main()
