"""Prepare a fresh current-main front-arrival observer without editing production."""
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'art/cartoon/walk-pilot/front-refresh-v1/review-evidence/native-island-v1/helpers'
EXPECTED_ZIP = '1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63'
IMAGE_ID = 'sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('prepare.py: unique adaptation anchor:' + old)
    return text.replace(old, new)


def main():
    if sha((ROOT / 'assets/scrantic_data.zip').read_bytes()) != EXPECTED_ZIP:
        raise ValueError('prepare.py: current approved production archive identity')
    if any((OUT / name).exists() for name in ('route_driver.c', 'capture.py', 'preparation.json')):
        raise ValueError('prepare.py: preserve existing prepared outputs')
    inputs = {name: sha((PRIOR / name).read_bytes()) for name in ('route_driver.c', 'capture.py')}
    driver = (PRIOR / 'route_driver.c').read_bytes()
    text = (PRIOR / 'capture.py').read_text(encoding='utf-8')
    text = replace_once(text, '0748676eb6ab0685abecfeb0bbfb8547d2050e6419bb1cad5f13ccc9f716fedd', EXPECTED_ZIP)
    text = replace_once(text, "def parse(folder, phase, expected):", "def parse(folder, phase, expected, candidate017=False):")
    old = """    require('data/hd/BMP/JOHNWALK.BMP/017.png' in loaded and 'data/styles/cartoon/BMP/JOHNWALK.BMP/017.png' not in loaded,
            phase + ': unchanged HD017 dependency')"""
    new = """    standing = 'data/styles/cartoon/BMP/JOHNWALK.BMP/017.png' if candidate017 else 'data/hd/BMP/JOHNWALK.BMP/017.png'
    excluded = 'data/hd/BMP/JOHNWALK.BMP/017.png' if candidate017 else 'data/styles/cartoon/BMP/JOHNWALK.BMP/017.png'
    require(standing in loaded and excluded not in loaded, phase + ': selected standing017 dependency')"""
    text = replace_once(text, old, new)
    text = replace_once(text, "'scope': 'Actual Linux production28 Cartoon walk/island and HD017 arrival. Native logical timing under maxspeed; no original-executable or wall-clock parity claim.'", "'scope': ('Actual Linux current approved Cartoon walk/island and private Cartoon017 arrival.' if candidate017 else 'Current Cartoon walk + HD standing017.') + ' Native logical timing under maxspeed; no original-executable or wall-clock parity claim.'")
    (OUT / 'route_driver.c').write_bytes(driver)
    (OUT / 'capture.py').write_text(text, encoding='utf-8', newline='\n')
    record = {
        'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'image_id': IMAGE_ID,
        'archive_sha256': EXPECTED_ZIP,
        'source_driver': (PRIOR / 'route_driver.c').relative_to(ROOT).as_posix(),
        'source_driver_sha256': inputs['route_driver.c'],
        'adapted_driver_sha256': sha(driver),
        'prepare_sha256': sha(Path(__file__).read_bytes()),
        'capture_sha256': sha((OUT / 'capture.py').read_bytes()),
        'retained_helper_sha256': inputs,
        'adaptations': ['Unchanged prior direct E-to-A observer', 'Bind newly approved production archive', 'Optional future candidate017 dependency check; disabled for baseline'],
        'scope': 'Current Cartoon walk + HD standing017. No candidate art, production edit, publication or human approval.'
    }
    (OUT / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS current-main observer prepared; prior driver bytes identical and production unchanged')


if __name__ == '__main__':
    main()
