"""Build the portable, static two-pose checkpoint from exact export bytes."""
import base64
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main():
    print("WITNESS build_review.py SHA256=" + hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), flush=True)
    files = {}

    def png(path):
        data = path.read_bytes()
        files[path.relative_to(ROOT).as_posix()] = hashlib.sha256(data).hexdigest()
        return "data:image/png;base64," + base64.b64encode(data).decode("ascii")

    data = {"frames": {}}
    for frame, version in [(1, 2), (3, 1)]:
        export = ROOT / "build/profile-walk" / f"export{frame:03}-v{version}"
        canonical = HERE / "exports" / f"{frame:03}-v{version}"
        if (export / "recipe.json").read_bytes() != (canonical / "recipe.json").read_bytes():
            raise ValueError(f"candidate-recipe:{frame:03}")
        expected = json.loads((canonical / "export-report.json").read_bytes())["outputs_sha256"]
        member = f"BMP/JOHNWALK.BMP/{frame:03}.png"
        if hashlib.sha256((export / member).read_bytes()).hexdigest() != expected[member]:
            raise ValueError(f"candidate-png:{frame:03}")
        recipe = json.loads((export / "recipe.json").read_bytes())
        data["frames"][f"{frame:03}"] = {
            "canvas": recipe["frames"][0]["runtime_canvas"], "version": f"v{version}",
            "original": png(HERE / "reference" / f"{frame:03}-original-native.png"),
            "candidate": png(export / f"BMP/JOHNWALK.BMP/{frame:03}.png"),
        }
        for name in ["recipe.json", "export-report.json"]:
            path = export / name
            files[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    import zipfile
    with zipfile.ZipFile(ROOT / "assets/scrantic_data.zip") as archive:
        standing = archive.read("data/styles/cartoon/BMP/JOHNWALK.BMP/000.png")
    data["identity"] = "data:image/png;base64," + base64.b64encode(standing).decode("ascii")
    template = (HERE / "review-template.html").read_text(encoding="utf-8")
    assert template.count("__REVIEW_DATA__") == 1
    html = template.replace("__REVIEW_DATA__", json.dumps(data)).encode("utf-8")
    output = HERE / "review-evidence/pose-check-v1"
    output.mkdir(parents=True, exist_ok=True)
    (output / "review.html").write_bytes(html)
    record = {"schema_version": 1, "scope": "Static pose review only; no native motion or human acceptance.",
              "selected": {"001": "001-profile-v2.png", "003": "003-profile-v1.png"}, "inputs_sha256": files,
              "standing000_runtime_sha256": hashlib.sha256(standing).hexdigest(),
              "review_html_sha256": hashlib.sha256(html).hexdigest(),
              "template_sha256": hashlib.sha256((HERE / "review-template.html").read_bytes()).hexdigest(),
              "production_archive_sha256": hashlib.sha256((ROOT / "assets/scrantic_data.zip").read_bytes()).hexdigest()}
    (output / "review-record.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "PASS", "output": str(output), "review_html_sha256": record["review_html_sha256"]}))


if __name__ == "__main__":
    main()
