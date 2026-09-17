from pathlib import Path
import hashlib
root=next(p for p in Path(__file__).resolve().parents if (p/"CMakeLists.txt").is_file())
helper=root/'art/cartoon/shoreline-repair-v1/integrated-shore-v1/side-fit-v1/export.py'
raw=(Path(__file__).parent/"mutant_export.py").read_bytes()
print("EXECUTED_MUTANT_SHA256="+hashlib.sha256(raw).hexdigest())
exec(compile(raw,str(helper),"exec"),{"__name__":"__main__","__file__":str(helper)})
