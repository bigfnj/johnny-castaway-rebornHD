"""Prepare exact original shark references for a 39-drawing visual draft batch.

Run with TOOLBOX_PYTHON -B art/cartoon/sharks-batch-v1/prepare_references.py.
This copies source bytes and creates nearest-neighbor viewing aids only.
"""
import hashlib
import io
import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INVENTORY = HERE.parent / "character-inventory-v1"
GROUPS = {
    "GJFFFOOD.BMP": [5, 6, 8, 15, 17] + list(range(19, 37)) + [44, 45, 48],
    "SHARK.BMP": list(range(25, 38)),
}
POSES = {
    "GJFFFOOD.BMP": {
        5: "Rounded shark head/body emerging low through white water; snout left, one eye visible. Keep the short submerged silhouette and surrounding splash.",
        6: "Near-vertical rising shark with snout angled up-left and open mouth; preserve the narrow angled body and visible side fins.",
        8: "Strongly arched shark over water, open mouth at lower-left and body/tail curving across the top toward the right; retain attached splash.",
        15: "Head-first downward shark with head at lower-left and tail high above/right; preserve the inverted curved silhouette.",
        17: "Descending curved shark, snout lower-left and tail curling high to the right; distinct from015, with its own fin placement.",
        19: "Broad low left-facing shark profile; complete body, tail to the right and short pectoral fins. Recommended shared material/identity key.",
        20: "Low left-facing profile with a different flattened body/tail curve from019; preserve the original fin and tail angles.",
        21: "Left-facing body beginning to rise, dorsal fin above and long tail trailing right; do not substitute019's lower profile.",
        22: "More upright left-facing shark, arched neck/back and low trailing tail right; preserve the rising posture.",
        23: "Upright seated left-facing shark with low tail curled right and small side fins; retain its compact expression.",
        24: "Upright left-facing shark with open mouth and visible colored mouth interior; low tail to the right.",
        25: "Upright left-facing shark with toothy mouth, lowered side fins and thin tail along the bottom-right.",
        26: "Large upright left-facing head and front-body emerging from the water, mouth open; no full lower body should be invented.",
        27: "Upright front/three-quarter reaction with bulging eye and mouth open toward the left; preserve attached waterline.",
        28: "Upright three-quarter head/body with two visible white eyes and dark pupils, including a small far eye, and a cheek/mouth reaction toward the left; retain the source gaze and waterline.",
        29: "Upright open-eyed reaction with mouth left, small lower side fin and waterline; separate expression from027/028.",
        30: "Tall left-facing head/neck at the waterline; pointed snout, small side fin and submerged lower edge.",
        31: "Rear-facing upright shark, back of the head and dorsal silhouette toward viewer. No visible front eye should be invented.",
        32: "Upright left-profile head/neck turning back into view, one visible eye; retain rearward fin and submerged lower edge.",
        33: "Left-facing shark rising/slanting out of water with open mouth and narrow lower body ending at the waterline.",
        34: "Shark diving leftward into a large splash; the arched back and tail remain above water. Preserve visible water as part of this drawing.",
        35: "Low diving arc across a wide splash, head submerged on the left and tail high/right; retain the submerged omission.",
        36: "Tail/body disappearing toward the left with a curved back and large attached splash on the right; do not fill in hidden anatomy.",
        44: "Upright head tilted sharply up-left with mouth open and one eye; keep the original eye direction and short visible front-body.",
        45: "Upright left-facing head with closed eye and open mouth; expression differs from044 and048.",
        48: "Upright left-facing head with closed eye and a small red tongue/food-like protrusion at the mouth. Preserve the visible component without inventing its runtime role.",
    },
    "SHARK.BMP": {
        25: "Open-jawed shark head breaching nearly vertically, mouth turned toward upper-right, teeth and colored mouth interior exposed; retain white water at base.",
        26: "Right-facing shark head/upper body at the waterline, open mouth and low horizontal snout; no lower body below the source water.",
        27: "Upright right-facing three-quarter shark with broad grin and colored mouth interior; preserve attached waterline.",
        28: "Similar upright right-facing reaction with its own mouth/tongue shape and eye; keep this phase distinct from027.",
        29: "Right-facing head/upper-body reaction with a different open mouth and colored inner shape; preserve phase-specific eye and cheek.",
        30: "Right-facing shark head with small tongue-like protrusion extending toward the right; maintain the original mouth and waterline.",
        31: "Right-facing shark with larger projecting colored mouth/tongue shape; keep it attached and do not replace with a generic grin.",
        32: "Upright right-facing head with the colored tongue-like shape brought up across the snout/cheek; preserve that contour and eye.",
        33: "Near-frontal upward-looking shark with snout tipped up-left and mouth open; preserve two-dimensional source view rather than mirroring a profile.",
        34: "Left-facing shark rising out of the water, narrow almost vertical body with visible pectoral fins and splash at base.",
        35: "Whole airborne shark arched leftward, snout down-left, tail right and pectoral fins below; keep complete curved body.",
        36: "Leftward diving shark with head submerged on the left, back arcing above the white splash and tail toward the right.",
        37: "Final submerging tail and body fragment with wide white splash; preserve hidden head/body rather than completing a whole animal.",
    },
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def ident(path):
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": digest(path.read_bytes())}

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")

def main():
    index_path = INVENTORY / "source/frame-index.json"
    map_path = INVENTORY / "scene-map/resource-map.json"
    archive = INVENTORY / "reference-originals.zip"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    mapping = json.loads(map_path.read_text(encoding="utf-8"))
    lookup = {(f["resource"], f["frame"]): f for f in index["frames"]}
    resource_lookup = {r["resource"]: r for r in mapping["resources"]}
    rows, crop_rows, sheets = [], [], []
    with zipfile.ZipFile(archive) as zipped:
        for resource, frames in GROUPS.items():
            resource_rows = []
            for number in frames:
                item = lookup[(resource, number)]
                raw = zipped.read(item["path"])
                if digest(raw) != item["png_sha256"]:
                    raise ValueError("Original PNG hash differs: " + item["id"])
                original = HERE / f"reference/original/{resource}/{number:03}.png"
                nearest = HERE / f"reference/nearest8/{resource}/{number:03}.png"
                original.parent.mkdir(parents=True, exist_ok=True)
                nearest.parent.mkdir(parents=True, exist_ok=True)
                original.write_bytes(raw)
                with Image.open(io.BytesIO(raw)) as source:
                    source.resize((source.width * 8, source.height * 8), Image.Resampling.NEAREST).save(nearest)
                    rgba = source.convert("RGBA")
                    bounds = rgba.getchannel("A").getbbox()
                    crop = rgba.crop(bounds)
                    crop_rows.append((item["id"], crop.size, crop.tobytes(), ImageOps.mirror(crop).tobytes()))
                action_rows = [
                    {"ttm": action["ttm"], "tag": action["tag"], "description": action["description"], "scope": action["scope"]}
                    for action in resource_lookup[resource]["unique_slot_frame_actions"]
                    if number in action["frames"]
                ]
                row = {
                    "id": item["id"], "resource": resource, "frame": f"{number:03}",
                    "canvas": item["canvas"], "visible_bounds_exclusive": item["visible_bounds_exclusive"],
                    "archive_member": item["path"], "original": ident(original), "nearest8": ident(nearest),
                    "source_rgba_sha256": item["rgba_sha256"], "source_index_plane_sha256": item["index_plane_sha256"],
                    "pose": POSES[resource][number], "body_count": 1,
                    "static_frame_attribution": action_rows,
                    "attribution_limit": "Static unique-script-slot attribution is not an executed sequence or exhaustive reachability proof.",
                }
                rows.append(row)
                resource_rows.append(row)
            for page, start in enumerate(range(0, len(resource_rows), 16), 1):
                page_rows = resource_rows[start:start + 16]
                sheet = Image.new("RGB", (1200, ((len(page_rows) + 3) // 4) * 200), (230, 230, 230))
                draw = ImageDraw.Draw(sheet)
                for n, row in enumerate(page_rows):
                    with Image.open(ROOT / row["original"]["path"]) as opened:
                        image = opened.convert("RGBA")
                        scale = max(1, min(8, 280 // image.width, 160 // image.height))
                        image = image.resize((image.width * scale, image.height * scale), Image.Resampling.NEAREST)
                        x = n % 4 * 300 + (300 - image.width) // 2
                        y = n // 4 * 200 + 30 + (160 - image.height) // 2
                        sheet.paste(image, (x, y), image)
                    draw.text((n % 4 * 300 + 8, n // 4 * 200 + 8), f"{resource} {row['frame']} {row['canvas']}", fill=(0, 0, 0))
                sheet_path = HERE / f"reference/{resource}-contact-{page:02}.png"
                sheet.save(sheet_path)
                sheets.append(ident(sheet_path))
    exact, mirrors = [], []
    for i, (name, size, data, flipped) in enumerate(crop_rows):
        for prior, prior_size, prior_data, _ in crop_rows[:i]:
            if size == prior_size and data == prior_data:
                exact.append([prior, name])
            elif size == prior_size and flipped == prior_data:
                mirrors.append([prior, name])
    duplicate_audit = {
        "scope": "All39 selected original drawings, comparing exact RGBA visible-bounds crops and exact horizontal mirrors after removing transparent canvas margins.",
        "selected_count": len(rows), "pair_comparisons": len(rows) * (len(rows) - 1) // 2,
        "exact_duplicate_pairs": exact, "exact_mirror_pairs": mirrors,
        "no_exact_or_mirror_duplicates_within_selection": not exact and not mirrors,
        "limits": "This is an internal source-pixel comparison, not a semantic uniqueness or worldwide duplicate claim. Similar animation poses intentionally remain separate drawings.",
    }
    shared = {
        "archive": ident(archive), "frame_index": ident(index_path), "scene_map": ident(map_path),
        "preparation": ident(Path(__file__)), "supplied_original_resource_sha256": index["source"]["resource_sha256"],
    }
    record = {
        "schema_version": 1, "scope": "39 authentic source drawings prepared for new Cartoon drafts; no generated artwork or approval",
        "count": len(rows), "palette_limit": index["palette_limit"], **shared,
        "duplicate_audit": duplicate_audit, "contacts": sheets, "assets": rows,
    }
    write_json(HERE / "reference/source.json", record)
    resources = []
    for resource, frames in GROUPS.items():
        source = resource_lookup[resource]
        resources.append({
            "resource": resource, "frames": frames, "count": len(frames),
            "original_resource_payload_sha256": source["original_payload_sha256"],
            "story_associations": source["ttm_load_associations"],
        })
    plan = {
        "schema_version": 1, "status": "reference preparation only; generation and human review pending",
        "target_new_drawings": 39, "user_batch_default": [36, 48], "resources": resources,
        "source_record": ident(HERE / "reference/source.json"), **shared,
        "shared_style_key": {"resource": "GJFFFOOD.BMP", "frame": "019", "reason": "Broad complete left profile exposes head, eye, dorsal and pectoral fins, body and tail without attached splash.", "status": "proposed, not generated or approved"},
        "constraints": [
            "One shark per selected drawing; no Johnny, other people or uncertain occupants in this selection.",
            "Exact originals govern head direction, eye visibility, mouth expression, body bends and phase silhouettes.",
            "Preserve attached source water and omitted submerged anatomy. Do not paint a full lower body onto a head/water fragment.",
            "GJFFFOOD031 is a rear view with no visible front eye; do not convert it to a front or side view.",
            "Use shared generated key for consistent material and line style, not to override individual pose geometry.",
            "Diagnostic gray/blue/magenta/red source colors establish shapes and components, not original-executable palette parity.",
        ],
        "attribution_limit": "Existing source-map associations are static. They do not establish timing, actual execution or exhaustive original-program parity. GJFFFOOD048 has no unique-slot frame attribution in this map; it remains a clear original drawing and is not declared unused.",
        "duplicate_audit": duplicate_audit,
        "assets": rows,
        "workflow": "One built-in image generation call per drawing after original inspection. Save exact requests and untouched raw outputs. Collect all39 new drafts in one visual review; exports/native testing remain deferred to the agreed integration milestone.",
        "approval": None,
    }
    write_json(HERE / "batch-plan.json", plan)
    print(f"Prepared {len(rows)} exact originals, {len(rows)} nearest8 references and {len(sheets)} contact sheets.")
    print(json.dumps(duplicate_audit))

if __name__ == "__main__":
    main()
