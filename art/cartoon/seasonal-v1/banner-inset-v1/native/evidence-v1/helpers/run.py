"""Reuse the frozen windowless Docker launcher with this versioned adapter."""
import hashlib
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
ANCESTOR=HERE.parents[1]/'banner-attachment-v1/native/run.py'
if __name__=='__main__':
    assert hashlib.sha256(ANCESTOR.read_bytes()).hexdigest()=='3626a129badb60ed2422f0c84bf9d0ee278eecf169141ee17e2009d4643e3055','frozen banner Docker launcher'
    spec=importlib.util.spec_from_file_location('inset_launcher',ANCESTOR);legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    legacy.HERE=HERE;legacy.main()
