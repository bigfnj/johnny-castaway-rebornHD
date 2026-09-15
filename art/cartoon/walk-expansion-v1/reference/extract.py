"""Recreate technical JOHNWALK references from the identified original dump.

Run from any directory with --dump-root <directory containing report.json/dump>
and --output <local output directory>. Requires the repository and Pillow.
This applies the port dump palette and index-0 transparency, not verified
original-executable palette/compositing. No artistic resampling is performed.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
from art_review_metadata import text_fingerprint, xpm_facts
from PIL import Image, ImageDraw


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(ok, label):
    if not ok:
        raise ValueError(label)


def prepare(dump_root, table_bytes, expected):
    """Validate every input before creating output directories or images."""
    report = json.loads((dump_root / "report.json").read_text(encoding="utf-8"))
    require(report.get("input_sha256") == expected["resource_sha256"] and
            report.get("engine_sha256") == expected["dump_engine_sha256"] and
            report.get("exit_code") == 0, "original-source-identity")
    require(text_fingerprint(table_bytes) == expected["walk_table_lf_sha256"], "walk-table-identity")
    inputs = {}
    for frame, digest in expected["xpm_sha256"].items():
        data = (dump_root / "dump/BMP" / f"JOHNWALK.BMP.{frame}.xpm").read_bytes()
        require(sha(data) == digest, f"original-frame-identity:{frame}")
        inputs[int(frame)] = data
    images, facts = {}, []
    for frame, data in inputs.items():
        fact = xpm_facts(data, f"JOHNWALK.BMP.{frame:03}", True)
        strings = re.findall(r'^"([^"\\]*)"(?:,|\};?)?\r?$', data.decode("ascii"), re.M)
        palette = {s[0]: bytes.fromhex(s[5:]) for s in strings[1:17]}
        rgba = b"".join(bytes(4) if c == "0" else palette[c] + b"\xff"
                        for row in strings[17:] for c in row)
        image = Image.frombytes("RGBA", tuple(fact["canvas"]), rgba)
        images[frame] = image
        row0 = [x for x in range(image.width) if image.getpixel((x, 0))[3]]
        facts.append({"frame": frame, "resource": "JOHNWALK.BMP", **fact,
                      "first_row_visible_span_x_exclusive": [min(row0), max(row0)+1] if row0 else None,
                      "landmark_limit": "Visible bounds include original shadow; first-row extent is a measured pixel feature, not an engine or anatomical anchor."})
    groups, rows = [], []
    for line_number, line in enumerate(table_bytes.decode("utf-8").splitlines(), 1):
        match = re.fullmatch(r"\s*\{\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\},\s*(?://\s*(.*))?", line)
        if not match:
            continue
        flip, x, y, frame = map(int, match.groups()[:4])
        if match[5]:
            groups.append({"label": match[5], "first_row": len(rows), "source_line": line_number, "draws": []})
        row = {"row": len(rows), "source_line": line_number, "flip_x": bool(flip),
               "stored_x": x, "draw_x": x-1, "draw_y": y, "frame": frame}
        rows.append(row)
        if x:
            groups[-1]["draws"].append(row)
    for fact in facts:
        fact["encoded_uses"] = [{"group": g["label"], "draw_count": sum(r["frame"] == fact["frame"] for r in g["draws"]),
                                  "flip_x": sorted({r["flip_x"] for r in g["draws"] if r["frame"] == fact["frame"]})}
                                 for g in groups if any(r["frame"] == fact["frame"] for r in g["draws"])]
    route = next(g for g in groups if g["label"] == "B to A")
    for n, row in enumerate(route["draws"]):
        row["nominal_start_ms"] = n*120
        row["nominal_duration_ms"] = 120
    metadata = {"schema_version": 1, "source": "source.json", "reference_pixels": "supplied-original-version",
        "palette_compositing_limit": "Original indices use the port dump palette and index-0 transparency; original executable palette/compositing is not verified.",
        "frame_count": len(facts), "walk_table_rows_including_sentinels": len(rows), "frames": facts,
        "families": expected["family_observations"], "recommended_anchor": 11,
        "selected_route": {"from_node": 1, "to_node": 0, "from_label": "B", "to_label": "A", "heading": 3,
            **route, "coordinate_units": "logical/native pixels before island offset; HD scale2 multiplies both placement and canvas by2",
            "timing_basis": "walk.c ordinary delay6; events.c20ms per tick. Original executable timing unmeasured. Each pose may span multiple background-update displays.",
            "end_behavior": "After these23 route draws, actual adsPlayWalk transitions to heading3 waiting frame018 with delay80(1600ms). That frame is outside this six-frame artwork family.",
            "capture_recommendation": "Use unchanged adsPlayWalk(1,3,0,3) in an isolated test API driver. Choose/record a calcPath RNG seed that produces direct B,A,UNDEF. CLI ads/ttm does not directly call this route API. Native output remains to be captured for this family."},
        "registration_observation": {"frames": [11,19,20,21,22,23], "basis": "measured-supplied-original-pixels",
            "shared_top_row_extent": [6,0,11,1], "meaning": "Cap outline occupies native x6..10 at y0 in each frame. Pixel-edge midpoint8.5 is an observation, not a prescribed generated-art anchor.",
            "head_yaw": "Visual rear-oblique view toward screen-left. No exact anatomical left/right limb identity has been assigned. Top20 rows are not byte-identical, so constant head pixels are not asserted."}}
    return images, metadata


def render(images, metadata, output):
    output.mkdir(parents=True, exist_ok=True)
    for dirname in ("native", "nearest8"):
        (output / dirname).mkdir(exist_ok=True)
    for frame, im in images.items():
        im.save(output / "native" / f"{frame:03}.png")
        im.resize((im.width*8, im.height*8), Image.Resampling.NEAREST).save(output / "nearest8" / f"{frame:03}.png")
    for name, ids in (("all-000-017", range(18)), ("all-018-035", range(18,36)), ("next-six-011-019-023", [11,19,20,21,22,23])):
        sheet = Image.new("RGB", (1440, 70+365*((len(ids)+5)//6)), "#d9e0e5")
        draw = ImageDraw.Draw(sheet)
        draw.text((12,10), "Supplied-original JOHNWALK indices; 4x nearest; port palette/index0 transparency.", fill="black")
        draw.text((12,30), "Original executable color/compositing parity is not established.", fill="black")
        for n, frame in enumerate(ids):
            x,y = (n%6)*240,70+(n//6)*365
            im = images[frame]
            draw.text((x+12,y+8), f"{frame:03} | native {im.width}x{im.height}", fill="black")
            tile = im.resize((im.width*4,im.height*4), Image.Resampling.NEAREST)
            sheet.paste(tile,(x+(240-tile.width)//2,y+36),tile)
        sheet.save(output / (name+".png"))
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dump-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    expected = json.loads((HERE / "source.json").read_text(encoding="utf-8"))
    print("WITNESS extract.py SHA256="+sha(Path(__file__).read_bytes()), flush=True)
    try:
        images, metadata = prepare(args.dump_root, (ROOT/"src/data/walk_data.h").read_bytes(), expected)
        render(images, metadata, args.output)
    except (ValueError, OSError) as error:
        print("FAIL "+str(error), file=sys.stderr)
        return 1
    print("PASS original-reference36; output="+str(args.output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
