# Reproduce the approved43-asset Cartoon package

This integration accepts28Johnny assets and inherits only15unchanged island
assets.27Johnny use the approved `skin-tone-v1/exports-v2` recipe. Standing018
uses the later `standing018-proportions-v1/color/evidence-foot-v5` recipe and
the separately accepted foot correction. The original28-pose color recipe,
old018 studies, raw drawings and older human records remain unchanged.

`production-acceptance.json` is in the parent directory. `prior-pack.json` and
`integrated-pack.json` are frozen ledger snapshots. `inputs.json` pins all
selected recipes, artwork, approvals and maintained tool source identities;
maintained Python source uses LF-normalized hashes for checkout portability.
The runtime_sources record lists the exact28selected PNGs.

Use Python3.11.15 and Pillow12.3.0 with NumPy2.4.6, from this repository's root.
Recover the prior production ZIP from commit
`3af0242a74f234aab231d9203b48f78ca8e5c1b4:assets/scrantic_data.zip` into a separate
file. Its required SHA256 is
`1649218b32a4d11595806f8680e351a4f47950fcefbafdf8de758c2d225913db`.
For example, use Python subprocess with binary stdout to avoid shell newline
conversion:

```python
import subprocess
from pathlib import Path
raw = subprocess.run(["git", "show", "3af0242a74f234aab231d9203b48f78ca8e5c1b4:assets/scrantic_data.zip"], check=True, capture_output=True).stdout
target = Path("build/prior-cartoon1649218b.zip")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(raw)
```

Use a fresh output directory below this repository's `build/`, because the
unchanged standing exporter staging adapter deliberately requires that scope:

```text
python -B art/cartoon/skin-tone-v1/integration-v1/integrate.py --repo . --baseline build/prior-cartoon1649218b.zip --output build/skin-tone/reproduction-fresh
```

If the local approved private candidate remains available, include
`--private-candidate build/standing018-proportions/foot-v5-motion/scrantic_data.zip`.
Its hash is `561edb2c9b4b4857b723af1505ce8d2654616aae2942325389604a4d88804521`.
When absent, the helper explicitly reports that independent private-ZIP
comparison was not rerun. It still checks the pinned baseline and all approved
member identities. The default command does not modify the production ZIP or
pack. `--promote` is the explicit integration operation and requires the active
production files still to match the prior baseline; it is not needed for replay.

The helper first reproduces canonical029, then all27retained raw ancestors as
decoded RGBA. Historical024–027 filter directly to their canvas; the other
ancestors retain their recorded padding. It next reproduces a changed024 and
unchanged029 color smoke, all27retained color outputs, and raw018-foot-v5 through
the unchanged fixed exporter and its new color adapter. Final PNGs are exact
byte comparisons. Legacy raw reconstruction does not claim identical re-encoded
PNG envelopes. New scratch paths can change018's recipe JSON paths without
changing its pixels or masks.

All43assets are staged together. Standard `tools/art_pack.py validate` runs
before `build`. The result must contain2594members:3new009/010/012,24changed
existingJohnny and2567unchanged prior payloads.029and all15island assets remain
byte-identical. Existing HD proxy `source_sha256` values keep their original
meaning; they do not refer to generated raw sources or corrected PNGs.

The independent regression compares every named member. A fresh subprocess
rejects a corrupted018member with exactly one named failure. A separate source
copy removes that audit condition and is actually executed against the damaged
archive, proving that the removed condition was responsible for the rejection.
The restored helper then accepts the undamaged candidate. Both helper execution
hashes and output witnesses are preserved. The corrupt ZIP remains ignored
scratch evidence and is never promoted.

The executed standard build is
`4c8085beeb71c2ddf071c32be0a741d4ec2327446cce45eb97addc8af1e233be`.
Its entire2594-member payload map equals the approved private candidate. The
ZIP envelope differs because standard packaging controls its own member
metadata. `verification.json`, `source-replay.json`, command stdout/stderr and
`evidence.json` preserve the completed run. The `controls/` copy is the executed
guard-removal artifact, not a maintained replacement for `integrate.py`.

Production promotion checks both active inputs again, replaces the ZIP and
ledger from verified bytes, and reads them back. A write failure restores both
prior byte sequences. Metadata regeneration, platform gates and post-merge
audits belong to separate delivery records. The new human acceptance covers
the presented palette and foot/contact checkpoint, not every story placement
or original-executable parity.
