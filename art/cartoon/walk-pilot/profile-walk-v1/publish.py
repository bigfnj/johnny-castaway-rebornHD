"""Copy the portable checkpoint into the existing local review server."""
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

HERE = Path(__file__).resolve().parent
REVIEW = HERE / "review-evidence/pose-check-v1"
DEST = Path(r"D:\.ai-work\worktrees\johnny-art-metadata\build\art-review\profile-walk-key-v1")
URL = "http://127.0.0.1:8932/profile-walk-key-v1/review.html"


def main():
    data = (REVIEW / "review.html").read_bytes()
    DEST.mkdir(parents=True, exist_ok=True)
    target = DEST / "review.html"
    if target.exists() and target.read_bytes() != data:
        raise ValueError("Existing published review differs; choose a new versioned destination.")
    target.write_bytes(data)
    with urlopen(URL, timeout=10) as response:
        served = response.read()
    if served != data:
        raise ValueError("Served review differs from the preserved review.")
    record = {"url": URL, "destination": str(target), "html_sha256": hashlib.sha256(data).hexdigest(),
              "served_bytes_identical": True, "scope": "Static two-pose draft; human review pending."}
    (REVIEW / "publication.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
