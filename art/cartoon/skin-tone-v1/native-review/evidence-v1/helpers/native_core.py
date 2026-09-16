"""Reuse the pinned connecting observer compiler and protected-input checks."""
from legacy import load_previous

_previous = load_previous('native_core')
SOURCE = _previous.SOURCE
OUT = _previous.OUT
BASE = _previous.BASE
FORMAT = _previous.FORMAT
sha = _previous.sha
codec = _previous.codec
require = _previous.require
save = _previous.save
protected = _previous.protected
build = _previous.build
