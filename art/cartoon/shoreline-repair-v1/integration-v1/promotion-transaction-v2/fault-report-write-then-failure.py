import sys
from pathlib import Path
import promote_v2 as m
original = m.atomic_bytes
report = Path(sys.argv[sys.argv.index('--report')+1])
def fail(path, raw):
    if path == report:
        print('WITNESS both disposable production files changed', flush=True)
        assert m.ROOT.joinpath('assets/scrantic_data.zip').read_bytes() == Path(sys.argv[sys.argv.index('--candidate')+1]).read_bytes()
        assert m.ROOT.joinpath('art/cartoon/pack.json').read_bytes() == m.HERE.joinpath('integrated-pack.json').read_bytes()
        original(path, raw)
        raise OSError('injected report write failure')
    original(path, raw)
m.atomic_bytes = fail
try: m.main()
except OSError as error:
    print('FAIL '+str(error), file=sys.stderr)
    raise SystemExit(1)
