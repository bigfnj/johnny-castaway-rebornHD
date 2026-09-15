"""Frozen accepted pilot bytes for historical tests, independent of production."""
from contextlib import contextmanager
import copy
import json
from pathlib import Path
from unittest.mock import patch
import zipfile

FIXTURE = Path(__file__).resolve().parent / "fixtures/cartoon-pilot-v1.zip"


@contextmanager
def legacy_pilot(root):
    """Substitute only the historical ledger and its exact accepted PNG bytes.

    All original resources, HD proxies, raw image bundles and acceptance records
    still come from the repository and are validated by the real metadata tool.
    Saved PNGs avoid a dependency on old Git commits or a Pillow renderer.
    """
    read_file, read_zip = Path.read_bytes, zipfile.ZipFile.read
    with zipfile.ZipFile(FIXTURE) as frozen:
        pack = read_zip(frozen, "pack.json")
        names = set(frozen.namelist()) - {"pack.json"}

        def file_bytes(path):
            return pack if path == root / "art/cartoon/pack.json" else read_file(path)

        def zip_bytes(archive, name, *args, **kwargs):
            if Path(archive.filename) == root / "assets/scrantic_data.zip" and name in names:
                return read_zip(frozen, name, *args, **kwargs)
            return read_zip(archive, name, *args, **kwargs)

        with patch.object(Path, "read_bytes", file_bytes), patch.object(zipfile.ZipFile, "read", zip_bytes):
            yield


@contextmanager
def promoted_pilot(root, module):
    """Expose a future 028 promotion through real build() I/O, without writes."""
    asset, control = "BMP/JOHNWALK.BMP/028.png", "BMP/JOHNWALK.BMP/027.png"
    new = "art/cartoon/future-history-fixture/production-acceptance.json"
    recipe_path = "art/cartoon/future-history-fixture/recipe.json"
    pack = json.loads((root / module.PACK).read_bytes())
    previous = pack["acceptance_record"]
    prior_hash = module.digest((root / previous).read_bytes())
    replacements = set(pack.get("pilot_history", {}).get("replaced_assets", [])) | {asset}
    target = next(row for row in pack["assets"] if row["path"] == asset)
    other = next(row for row in pack["assets"] if row["path"] == control)
    target.update(sha256=other["sha256"], recipe=recipe_path, review=new)
    pack["acceptance_record"] = new
    pack["pilot_history"] = {"acceptance_record": module.ACCEPTANCE,
        "sha256": module.digest((root / module.ACCEPTANCE).read_bytes()), "replaced_assets": sorted(replacements)}
    old_recipe = json.loads((root / module.RECIPES[0]).read_bytes())
    row = copy.deepcopy(next(row for row in old_recipe["frames"] if row["path"] == asset))
    row["candidate_png_sha256"] = other["sha256"]
    records = {module.PACK: pack, recipe_path: {"frames": [row], "required_assets": [asset]},
        new: {"accepted": True, "accepted_assets": [
            {key: row[key] for key in ("path", "sha256", "recipe")} for row in pack["assets"]],
            "newly_accepted_assets": [asset], "inherited_acceptances": [{"path": previous,
                "sha256": prior_hash, "asset_paths": [row["path"] for row in pack["assets"] if row["path"] != asset]}]}}
    virtual = {path: (json.dumps(value, indent=2) + "\n").encode("utf-8") for path, value in records.items()}
    read_file, read_zip, read_text = Path.read_bytes, zipfile.ZipFile.read, Path.read_text

    def file_bytes(path):
        relative = path.relative_to(root).as_posix() if path.is_relative_to(root) else ""
        return virtual[relative] if relative in virtual else read_file(path)

    def file_text(path, *args, **kwargs):
        relative = path.relative_to(root).as_posix() if path.is_relative_to(root) else ""
        return virtual[relative].decode("utf-8") if relative in virtual else read_text(path, *args, **kwargs)

    def zip_bytes(archive, name, *args, **kwargs):
        if Path(archive.filename) == root / "assets/scrantic_data.zip" and name == "data/styles/cartoon/" + asset:
            name = "data/styles/cartoon/" + control
        return read_zip(archive, name, *args, **kwargs)

    with patch.object(Path, "read_bytes", file_bytes), patch.object(Path, "read_text", file_text), patch.object(zipfile.ZipFile, "read", zip_bytes):
        report = module.build(root)
        virtual[module.OUTPUT + ".json"] = (json.dumps(report, indent=2) + "\n").encode("utf-8")
        virtual[module.OUTPUT + ".md"] = module.markdown(report).encode("utf-8")
        yield report
