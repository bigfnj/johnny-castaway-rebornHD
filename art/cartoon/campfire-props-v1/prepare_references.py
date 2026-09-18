"""Retain exact FIRE2/FIRE5 source images and diagnostic reference views."""
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
RESOURCES = {"FIRE2.BMP": 25, "FIRE5.BMP": 3, "SRAFT.BMP": 2}
PRESERVED = {("FIRE2.BMP", n) for n in (0, 3, 8)}
DEFERRED_GRIPS = {("FIRE2.BMP", n) for n in (10, 11)}


def ident(path):
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    original_zip = INVENTORY / "reference-originals.zip"
    runtime_zip = ROOT / "assets/scrantic_data.zip"
    index_path = INVENTORY / "source/frame-index.json"
    index = json.loads(index_path.read_text(encoding="utf-8-sig"))
    indexed = {(r["resource"], r["frame"]): r for r in index["frames"]}
    entries = []
    with ZipFile(original_zip) as originals, ZipFile(runtime_zip) as runtime:
        for resource, count in RESOURCES.items():
            for folder in ("original", "hd", "nearest8"):
                (OUT / folder / resource).mkdir(parents=True, exist_ok=True)
            sheets = [Image.new("RGB", (1280, 1050), "#293e4c") for _ in range((count+11)//12)]
            for n in range(count):
                member = f"native/BMP/{resource}/{n:03}.png"
                hd_member = f"data/hd/BMP/{resource}/{n:03}.png"
                data = originals.read(member)
                original_path = OUT / "original" / resource / f"{n:03}.png"
                hd_path = OUT / "hd" / resource / f"{n:03}.png"
                original_path.write_bytes(data)
                hd_path.write_bytes(runtime.read(hd_member))
                with Image.open(io.BytesIO(data)) as source:
                    im = source.convert("RGBA")
                guide = OUT / "nearest8" / resource / f"{n:03}.png"
                im.resize((im.width*8, im.height*8), Image.Resampling.NEAREST).save(guide)
                i = n % 12
                x, y = (i % 4)*320, (i//4)*350
                scale = min(8, 290/im.width, 285/im.height)
                diagnostic = im.resize((round(im.width*scale), round(im.height*scale)), Image.Resampling.NEAREST)
                sheet = sheets[n//12]
                sheet.paste(diagnostic, (x+15, y+50), diagnostic)
                ImageDraw.Draw(sheet).text((x+15, y+12), f"{resource} {n:03} {im.size}", fill="white")
                preserved = (resource, n) in PRESERVED
                entry = dict(resource=resource, frame=n, source_preserved=preserved,
                             deferred_character_overlay=(resource,n) in DEFERRED_GRIPS,
                             original={**ident(original_path), "member": member, "canvas": list(im.size),
                                       "matches_inventory": hashlib.sha256(data).hexdigest()==indexed[(resource,n)]["png_sha256"]},
                             hd={**ident(hd_path), "member": hd_member}, nearest8=ident(guide))
                if preserved:
                    dest = HERE / "source-preserved" / resource / f"{n:03}.png"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(data)
                    entry["preserved_file"] = ident(dest)
                entries.append(entry)
            for page, sheet in enumerate(sheets):
                sheet.save(OUT / f"{resource}-contact-{page+1}.png")
    record = dict(schema_version=1, resources=RESOURCES, frames=entries,
                  sources=[ident(p) for p in (original_zip,runtime_zip,index_path,Path(__file__))],
                  palette_limit=index["palette_limit"], original_bytes_preserved=True,
                  scope="Exact reference extraction and technical nearest-neighbor views; no art generation or runtime modifications.")
    (OUT / "source.json").write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(dict(slots=len(entries), preserved=sum(e["source_preserved"] for e in entries),
                          identities_match=all(e["original"]["matches_inventory"] for e in entries))))


if __name__ == "__main__":
    main()
