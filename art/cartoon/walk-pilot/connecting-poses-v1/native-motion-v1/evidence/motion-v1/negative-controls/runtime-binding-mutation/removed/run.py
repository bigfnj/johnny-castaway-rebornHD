import hashlib
from pathlib import Path
import config
import prepare_candidate
import check_selection
config.OUT = Path(__file__).resolve().parent / "output"
config.OUT.mkdir()
print("WITNESS executed validator SHA256=" + hashlib.sha256(Path(prepare_candidate.__file__).read_bytes()).hexdigest(), flush=True)
check_selection.main()
