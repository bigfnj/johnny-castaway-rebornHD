"""Two bounded altered-input controls for the diagnostic-only transcript/load checks."""
import json
from pathlib import Path
import capture as c

def main():
    out=c.OUT/'parser-controls.json'
    assert not out.exists(), 'preserve parser controls'
    prep=json.loads((c.OUT/'preparation.json').read_bytes())
    folder=c.OUT/'original_johnny/full'
    text=(folder/'capture.log').read_text()
    ref=(c.OUT/'current/full/capture.log').read_text()
    report=json.loads((folder/'report.json').read_bytes())
    expected=report['loaded_art']
    c.validate(text,ref,'cartoon','original_johnny',expected)
    old='TURN DRAW: flip=0 x=478 y=216 frame=18'
    assert text.count(old)==1, 'single intended initial018 draw witness'
    cases=[('wrong018-origin',text.replace(old,old.replace('x=478','x=479')),'unchanged native path/draw/timing transcript:original_johnny'),
           ('loaded018-override',text+'\nArt asset: data/styles/cartoon/BMP/JOHNWALK.BMP/018.png\n','exact diagnostic PNG-load set:original_johnny')]
    results=[]
    for name,altered,wanted in cases:
        try:c.validate(altered,ref,'cartoon','original_johnny',expected)
        except AssertionError as e:
            assert str(e)==wanted, 'specific failure identity:'+name
            results.append({'name':name,'status':'FIRED','message':str(e),'altered_log_sha256':c.sha(altered.encode())})
        else:raise AssertionError('SURVIVED:'+name)
    c.validate(text,ref,'cartoon','original_johnny',expected)
    c.save(out,{'status':'PASS','positive_before_after':True,'controls':results,
        'executed_capture_sha256':c.sha(Path(c.__file__).read_bytes()),'checker_sha256':c.sha(Path(__file__).read_bytes()),
        'original_log_sha256':c.sha((folder/'capture.log').read_bytes()),'scope':'Two parser input mutations; no capture file or runtime source changed.'})
    print('PASS original control; wrong018 origin and restored018 override each rejected by exact named guard; restored positive')

if __name__=='__main__':main()
