"""New immutable inset review using the frozen banner pixels/timing pipeline."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ANCESTOR=HERE.parents[1]/'banner-attachment-v1/review/build_review.py'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')

def build(captures,output):
    assert sha(ANCESTOR)=='029d83ab8bdd36d1c4485130a288780ac9b0ae9e79adfcc0a7543e654798cd04','frozen banner review builder'
    spec=importlib.util.spec_from_file_location('inset_review',ANCESTOR);legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    legacy.build(captures,output)
    page=output/'review.html';text=page.read_text(encoding='utf-8')
    changes={
      'Please check whether both ends of the revised banner visibly attach to the palm fronds. The island, waves, palm and other artwork are identical on both sides.':'Please check whether both upper cloth corners of the inset banner meet the green palm fronds. It is slightly smaller and has no added ties. The palm, island and waves are unchanged.',
      '<h2>Current banner</h2>':'<h2>Previous tied draft</h2>',
      '<h2>Revised attachment</h2>':'<h2>Inset banner</h2>',
      'aria-label="Current banner scene"':'aria-label="Previous tied draft scene"',
      'aria-label="Revised attachment scene"':'aria-label="Inset banner scene"',
      'This comparison changes only the banner; shoreline and wave placement remain a separate review.':'This comparison changes only the banner and retains the previous waves. The wave correction will be reviewed separately.'}
    for before,after in changes.items():
        assert text.count(before)==1,'one exact UI label: '+before
        text=text.replace(before,after)
    page.write_text(text,encoding='utf-8')
    manifest=json.loads((output/'manifest.json').read_bytes());manifest['labels']=['Previous tied draft','Inset banner']
    manifest['scope']='Clean-source 8% inset supersedes tie-only approach. Only banner003 differs; attachment and separate wave-placement judgment remain open.'
    manifest['banner_recipe']={'path':(HERE.parent/'recipe-v1.json').relative_to(legacy.ROOT).as_posix(),'sha256':sha(HERE.parent/'recipe-v1.json')}
    save(output/'manifest.json',manifest)
    record=json.loads((output/'build.json').read_bytes());record.update(builder_sha256=sha(Path(__file__)),ancestor_builder_sha256=sha(ANCESTOR),
        html_sha256=sha(page),manifest_sha256=sha(output/'manifest.json'),scope=manifest['scope'])
    save(output/'build.json',record);print('PASS inset review built',record['html_sha256'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--captures',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    build(a.captures.resolve(),a.output.resolve())
