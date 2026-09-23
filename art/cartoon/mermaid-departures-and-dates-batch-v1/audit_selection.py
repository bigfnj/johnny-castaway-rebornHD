"""Compare source pixels for selected drawings against prior generated slots."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
ART = HERE.parent
ROOT = HERE.parents[2]
INV = ART / "character-inventory-v1"

def digest(im):
    return hashlib.sha256(str(im.size).encode() + im.tobytes()).hexdigest()

def main():
    inventory_path = INV / "inventory.json"
    archive_path = INV / "reference-originals.zip"
    selection_path = HERE / "selection.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selected_pairs = {(r, f) for r, frames in selection.items() for f in frames}
    generated_paths = [
        p for p in ART.glob("*/generation/*/*.png")
        if p.name[:3].isdigit() and HERE not in p.parents
    ]
    prior_pairs = {(p.parent.name, int(p.name[:3])) for p in generated_paths}
    prior = {x["id"] for x in inventory["assets"] if (x["resource"], x["frame"]) in prior_pairs}
    selected = {x["id"] for x in inventory["assets"] if (x["resource"], x["frame"]) in selected_pairs}
    hashes = {}
    with zipfile.ZipFile(archive_path) as archive:
        for asset in inventory["assets"]:
            with Image.open(io.BytesIO(archive.read(asset["original_png"]))) as src:
                im = src.convert("RGBA")
            bbox = im.getbbox()
            if bbox:
                im = im.crop(bbox)
            hashes[asset["id"]] = {digest(im), digest(ImageOps.mirror(im))}
    within = [[a, b] for a in sorted(selected) for b in sorted(selected)
              if a < b and hashes[a] & hashes[b]]
    earlier = [[a, b] for a in sorted(selected) for b in sorted(prior)
               if hashes[a] & hashes[b]]
    injected_slot = "BMP/SMDATE11.BMP/000"
    mutated_matches = [[a, b] for a in sorted(selected | {injected_slot}) for b in sorted(prior)
                       if hashes[a] & hashes[b]]
    guard_fired = False
    try:
        assert not mutated_matches, str(mutated_matches)
    except AssertionError:
        guard_fired = True
    assert guard_fired and mutated_matches == [[injected_slot, "BMP/SMGFTWAV.BMP/000"]]
    result = {
        "schema_version": 1,
        "method": "Exact RGBA after alpha-bounds crop, plus horizontal mirror; dimensions included in hash.",
        "scope": "Inventory original pixels, compared only against resource/frame pairs with PNG files in earlier top-level generation folders. New batch excluded.",
        "selected_resource_frame_count": len(selected_pairs),
        "selected_inventory_slots": len(selected),
        "prior_generated_resource_frame_pairs": len(prior_pairs),
        "prior_inventory_slots": len(prior),
        "within_selected_matches": within,
        "matches_against_prior_generated": earlier,
        "negative_control": {
            "mutation": "Add known already-drawn SMDATE11.BMP/000 to candidate selection in memory.",
            "guard_fired": guard_fired,
            "detected_matches": mutated_matches,
            "source_selection_file_modified": False,
        },
        "inputs": {
            str(p.relative_to(ROOT)).replace(chr(92), "/"): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (inventory_path, archive_path, selection_path, Path(__file__))
        },
        "limits": "Does not prove artwork acceptance, native integration, or visual equivalence beyond exact original pixels.",
    }
    (HERE / "duplicate-audit.json").write_text(json.dumps(result, indent=2) + chr(10), encoding="utf-8")
    print(json.dumps(result))
    assert len(selected) == len(selected_pairs)
    assert not within and not earlier

if __name__ == "__main__":
    main()
