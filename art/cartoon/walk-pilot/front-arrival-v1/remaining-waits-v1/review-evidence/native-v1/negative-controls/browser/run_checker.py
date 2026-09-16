import hashlib, runpy
from pathlib import Path
p=Path(__file__).parent/'check_review.py'
print('WITNESS exact executed checker SHA256='+hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)
runpy.run_path(str(p),run_name='__main__')
