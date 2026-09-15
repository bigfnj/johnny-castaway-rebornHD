"""Rebuild the exact accepted historical HTML from the preserved repo PNGs.

This creates a padded browser preview, never runtime sprites. Historical page
captions remain unchanged so its bytes match the page the user reviewed.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path


def build(output):
    here = Path(__file__).resolve().parent
    art = here.parent
    acceptance = json.loads((art / "standalone-motion-acceptance.json").read_text(encoding="utf-8"))
    data = json.loads((here / "standalone-walk-data.json").read_text(encoding="utf-8"))
    template = (here / "standalone-walk-template.html").read_bytes().decode("utf-8")
    sources = {item["frame"]: item for item in acceptance["source_frames"]}
    for item in data["images"]:
        source = sources[item["frame"]]
        path = art / source["file"]
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != source["sha256"]:
            raise ValueError("source PNG identity mismatch: " + source["file"])
        item["data"] = "data:image/png;base64," + base64.b64encode(raw).decode("ascii")
    encoded = json.dumps(data, separators=(",", ":")).replace("<", "\\u003c")
    html = template.replace("__STANDALONE_WALK_DATA__", encoded).encode("utf-8")
    if hashlib.sha256(html).hexdigest() != acceptance["reviewed_html"]["sha256"]:
        raise ValueError("reviewed HTML identity mismatch: standalone-walk.html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(html)
    print(f"Reproduced {output} ({len(html)} bytes; SHA-256 {hashlib.sha256(html).hexdigest()})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    build(parser.parse_args().output)
