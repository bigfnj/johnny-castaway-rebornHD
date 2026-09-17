"""Package pending artwork for native review and assemble its static review page.

This only writes diagnostic outputs. It never changes the production archive or
the accepted-art ledger. native/capture.py independently verifies ZIP retention,
canvas dimensions, selected payloads, draw origins and captured pixel boundaries.
"""
import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = [
    ("000", "halloween", "Halloween pumpkin", (80, 68), (580, 400, 1100, 752),
     "Revised pumpkin: glowing red eyes and a sharp-toothed evil grin. Check how the approved face reads at game size."),
    ("001", "stpatricks", "St. Patrick's clovers", (240, 94), (580, 400, 1100, 752),
     "Check the spacing between the clovers and where their stems meet the sand."),
    ("002", "christmas", "Christmas tree", (112, 130), (580, 400, 1100, 752),
     "Check the tree's size, ornaments and base at the island's edge."),
    ("003", "newyear", "New Year banner", (304, 94), (580, 160, 1100, 512),
     "Check the banner's lettering, curved shape and placement beneath the palm."),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def package(output, version):
    source = ROOT / "assets/scrantic_data.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    added = {}
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(output, "x") as result:
        for member in original.infolist():
            result.writestr(member, original.read(member.filename))
        for frame, *_ in ASSETS:
            path = HERE / f"candidates/{version}/BMP/HOLIDAY.BMP/{frame}.png"
            member = f"data/styles/cartoon/BMP/HOLIDAY.BMP/{frame}.png"
            info = zipfile.ZipInfo(member, date_time=(2026, 9, 16, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            result.writestr(info, path.read_bytes())
            added[member] = sha(path)
    save(output.with_suffix(".json"), {
        "status": "diagnostic only; pending human visual approval",
        "candidate_version": version,
        "production_archive_sha256": sha(source),
        "draft_archive_sha256": sha(output),
        "added_members_sha256": added,
    })
    print(f"Draft archive: {output}")


def review(baseline, candidate, version):
    entries = []
    evidence = {"status": "pending human visual approval", "candidate_version": version, "native_runs": {}}
    for label, run in (("before", baseline), ("after", candidate)):
        summary = run / "captures/summary.json"
        evidence["native_runs"][label] = {
            "path": run.relative_to(ROOT).as_posix(),
            "summary_sha256": sha(summary),
            "result": json.loads(summary.read_text(encoding="utf-8")),
        }
    files = {}
    for frame, key, name, canvas, crop, description in ASSETS:
        entry = {"name": name, "description": description,
                 "runtime_canvas": canvas, "crop": crop,
                 "original": f"reference/{frame}-original-native.png",
                 "hd": f"reference/{frame}-hd-native.png",
                 "candidate": f"candidates/{version}/BMP/HOLIDAY.BMP/{frame}.png"}
        for label, run in (("before", baseline), ("after", candidate)):
            source = run / f"captures/day/{key}/smoke/final.png"
            relative = f"review-evidence/{version}/{frame}-{label}.png"
            destination = HERE / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            entry[label] = relative
            close = f"review-evidence/{version}/{frame}-{label}-close.png"
            with Image.open(source) as image:
                image.crop(crop).save(HERE / close)
            entry[label + "_close"] = close
            files[relative] = sha(destination)
            files[close] = sha(HERE / close)
        entries.append(entry)
    save(HERE / "review-data.json", {
        "sprite_zoom": 2,
        "capture_note": "Both sides are native Linux captures using the same Cartoon island, approved Johnny pose and fixed scene state. The only changes are the four holiday drawings. The existing cloud still uses HD artwork. These are static decoration checks; story trigger dates and cargo-scene suppression are outside this preview.",
        "assets": entries,
    })
    evidence["review_files_sha256"] = files
    save(HERE / f"review-evidence/{version}/source.json", evidence)
    print(f"Review ready: {HERE / 'review.html'}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    pack = commands.add_parser("package")
    pack.add_argument("--output", type=Path, required=True)
    pack.add_argument("--version", choices=("v1", "v2", "v3"), required=True)
    page = commands.add_parser("review")
    page.add_argument("--baseline", type=Path, required=True)
    page.add_argument("--candidate", type=Path, required=True)
    page.add_argument("--version", choices=("v1", "v2", "v3"), required=True)
    args = parser.parse_args()
    if args.command == "package":
        package(args.output.resolve(), args.version)
    else:
        review(args.baseline.resolve(), args.candidate.resolve(), args.version)


if __name__ == "__main__":
    main()
