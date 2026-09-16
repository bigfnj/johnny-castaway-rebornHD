"""Read-only imports of pinned native helpers; their config is this review's."""
import importlib.util
import config

PRIOR = config.ROOT / 'art/cartoon/walk-pilot/connecting-poses-v1/native-motion-v1'
PINS = {
    "native_core.py": "996e60eb4e64d98ce0107d68db9f2cffb9229189eafbd9befdfaa61dafe2472e",
    "capture.py": "c9c5008f3dc3efe5ddefd02522f6621e744e8c61e6b3a85fd48d5f0c6b589bec"
}


def load_previous(name):
    filename = name + '.py'
    path = PRIOR / filename
    assert config.sha(path.read_bytes()) == PINS[filename], 'immutable native helper:' + filename
    spec = importlib.util.spec_from_file_location('skin_previous_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
