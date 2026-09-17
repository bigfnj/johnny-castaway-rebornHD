import hashlib,importlib.util
from pathlib import Path
root=next(p for p in Path(__file__).resolve().parents if (p/"CMakeLists.txt").is_file())
path=root/'art/cartoon/seasonal-v1/banner-attachment-v1/export_v2.py'
s=importlib.util.spec_from_file_location("selected",path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
raw=(Path(__file__).parent/"mutant_render.py").read_bytes()
print("EXECUTED_MUTANT_SHA256="+hashlib.sha256(raw).hexdigest())
exec(compile(raw,"mutant_render.py","exec"),m.trial.__dict__)
m.original_render=m.trial.render; m.trial.render=m.render
print("WITNESS banner-registration "+m.trial.sha(path.read_bytes()))
raise SystemExit(m.trial.main())
