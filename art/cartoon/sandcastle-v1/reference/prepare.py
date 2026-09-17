"""Extract exact sandcastle references and diagnostic nearest-neighbor guides.

Reference preparation only. Does not run the game, change art, or validate a pack.
Run from any directory: toolbox Python reference/prepare.py
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "CMakeLists.txt").is_file())
INVENTORY = ROOT / "art/cartoon/character-inventory-v1"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def record(path: Path) -> dict:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha(path.read_bytes())}


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def main():
    index_path = INVENTORY / "source/frame-index.json"
    map_path = INVENTORY / "scene-map/resource-map.json"
    sites_path = INVENTORY / "scene-map/static-draw-sites.json"
    classification_path = INVENTORY / "classification/s-family.json"
    original_zip = INVENTORY / "reference-originals.zip"
    assets_zip = ROOT / "assets/scrantic_data.zip"
    index = read(index_path)
    frames = sorted((f for f in index["frames"] if f["resource"] == "SANDCAST.BMP"), key=lambda f: f["frame"])
    resource = next(r for r in read(map_path)["resources"] if r["resource"] == "SANDCAST.BMP")
    sites = read(sites_path)
    draws = [dict(zip(sites["draw_site_columns"], row)) for row in sites["draw_sites"]]
    draws = [row for row in draws if row["resource"] == "SANDCAST.BMP"]
    classification = next(r for r in read(classification_path)["resources"] if r["resource"] == "SANDCAST.BMP")
    actions = {
        "schema_version": 1,
        "scope": "Copied static attribution, not executed scene order, timing, or reachability proof.",
        "resource": "SANDCAST.BMP",
        "classification": classification,
        "source_files": [record(p) for p in (map_path, sites_path, classification_path)],
        "story_associations": [{"ttm": a["resource"], "decoded_sha256": a["decoded_sha256"], "stories": [{k: s[k] for k in ("scene", "description", "source")} for s in a["story_associations"]]} for a in resource["ttm_load_associations"]],
        "frame_actions": resource["unique_slot_frame_actions"],
        "draw_argument_order": ["x", "y", "frame", "slot"],
        "draw_sites": draws,
        "frames_without_unique_slot_draw_attribution": sorted(set(range(15)) - {row["draw"][2] for row in draws}),
        "runtime_reachability_proven": False,
    }
    write_json(HERE / "static-actions.json", actions)
    for directory in ("original", "hd", "nearest8"):
        (HERE / directory).mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (1920, 840), (46, 55, 65))
    label = ImageDraw.Draw(sheet)
    rows = []
    with ZipFile(original_zip) as originals, ZipFile(assets_zip) as assets:
        for row in frames:
            n = row["frame"]
            original_member = f"native/BMP/SANDCAST.BMP/{n:03}.png"
            hd_member = f"data/hd/BMP/SANDCAST.BMP/{n:03}.png"
            data = originals.read(original_member)
            hd_data = assets.read(hd_member)
            # Copy source bytes, including the complete original canvas.
            original_path = HERE / "original" / f"{n:03}.png"
            hd_path = HERE / "hd" / f"{n:03}.png"
            original_path.write_bytes(data)
            hd_path.write_bytes(hd_data)
            image = Image.open(io.BytesIO(data)).convert("RGBA")
            hd_image = Image.open(io.BytesIO(hd_data))
            nearest_path = HERE / "nearest8" / f"{n:03}.png"
            image.resize((image.width * 8, image.height * 8), Image.Resampling.NEAREST).save(nearest_path)
            diagnostic = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)
            x, y = (n % 5) * 384, (n // 5) * 280
            sheet.paste(diagnostic, (x + 16, y + 48), diagnostic)
            label.text((x + 16, y + 14), f"{n:03}  {image.size}  NN x2", fill="white")
            rows.append({
                "frame": n,
                "original": {**record(original_path), "member": original_member, "canvas": list(image.size), "matches_inventory_sha256": sha(data) == row["png_sha256"], "visible_bounds_exclusive": row["visible_bounds_exclusive"]},
                "hd": {**record(hd_path), "member": hd_member, "canvas": list(hd_image.size), "matches_inventory_hd_sha256": sha(hd_data) == row["bundled"]["hd_png_sha256"]},
                "nearest8": {**record(nearest_path), "canvas": [image.width * 8, image.height * 8], "method": "full original canvas, nearest-neighbor x8"},
            })
        style_member = "data/styles/cartoon/BMP/BACKGRND.BMP/000.png"
        style_path = HERE / "approved-island-000.png"
        style_path.write_bytes(assets.read(style_member))
    sheet.save(HERE / "original-contact.png")
    aliases = [record(HERE / name) for name in ("original-000.png", "approved-island000-runtime.png") if (HERE / name).is_file()]
    source = {
        "schema_version": 1,
        "purpose": "Reference preparation for 15 sandcastle drawings; no new art or runtime claim.",
        "inputs": [record(p) for p in (original_zip, assets_zip, index_path, map_path, sites_path, classification_path, Path(__file__))],
        "supplied_original_resource_sha256": index["source"]["resource_sha256"],
        "palette_limit": index["palette_limit"],
        "original_executable_color_parity": False,
        "frames": rows,
        "approved_cartoon_style": {**record(style_path), "member": style_member, "canvas": list(Image.open(style_path).size), "use": "Sand color, shading, and outline style only; do not inherit this island's shape or canvas."},
        "root_owned_reference_aliases": aliases,
        "contact_sheet": {**record(HERE / "original-contact.png"), "method": "Full original canvases nearest-neighbor x2, diagnostic dark backdrop and labels; no sprite pixels repainted."},
        "static_actions": record(HERE / "static-actions.json"),
        "complete_key_frame": 0,
        "review_groups_of_five": [
            {"frames": [0, 1, 2, 3, 4], "description": "Completed castle and upper construction stages"},
            {"frames": [5, 6, 7, 8, 9], "description": "Lowest standing wall and four airborne sand effects"},
            {"frames": [10, 11, 12, 13, 14], "description": "Wilting castle, dissolving piles, and collapse variants"},
        ],
        "parallel_generation_after_key": {"key": [0], "construction": [1, 2, 3, 4, 5], "effects_and_first_collapse": [6, 7, 8, 9, 10], "remaining_collapse": [11, 12, 13, 14]},
    }
    write_json(HERE / "source.json", source)
    print(json.dumps({"reference": str(HERE), "frames": len(rows), "source_sha256": sha((HERE / "source.json").read_bytes()), "all_original_copy_identities": all(r["original"]["matches_inventory_sha256"] for r in rows), "all_hd_copy_identities": all(r["hd"]["matches_inventory_hd_sha256"] for r in rows)}, indent=2))


if __name__ == "__main__":
    main()
