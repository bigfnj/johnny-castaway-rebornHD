"""Save the real native background immediately after low-tide rock 002 draws."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import traceback

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('candidate_adapter', HERE / 'capture.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
c = a.c

HOOK = r'''
static int prewave_saved;
static void save_prewave(void)
{
    PlatformSurface *s=grBackgroundSfc;
    int w=platformGetSurfaceWidth(s),h=platformGetSurfaceHeight(s),pitch=platformGetSurfacePitch(s);
    const unsigned char *pixels=platformGetSurfacePixels(s);
    if(prewave_saved || capture_enabled || phases[0]!=-1 || phases[1]!=-1 || phases[2]!=-1 || phases[3]!=-1) exit(80);
    if(w!=1280 || h!=960 || platformGetSurfaceBytesPerPixel(s)!=4) exit(81);
    FILE *file=fopen("prewave.ppm","wb"); if(!file) exit(82);
    if(fprintf(file,"P6\n%d %d\n255\n",w,h)<0) exit(83);
    unsigned char row[1280*3];
    for(int y=0;y<h;y++) {
        const unsigned char *p=pixels+(size_t)y*pitch;
        for(int x=0;x<w;x++) {row[x*3]=p[x*4+2];row[x*3+1]=p[x*4+1];row[x*3+2]=p[x*4];}
        if(fwrite(row,3,w,file)!=(size_t)w) exit(84);
    }
    if(fclose(file)) exit(85);
    prewave_saved=1;
    puts("PREWAVE: actual grBackgroundSfc after BACKGRND002; phases=-1,-1,-1,-1; display_capture=0");
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--candidate-sha256', required=True)
    args = parser.parse_args()
    out = Path('/out/prewave-v1')
    c.require(not out.exists(), 'fresh pre-wave output')
    c.require(c.sha(args.candidate.read_bytes()) == args.candidate_sha256, 'explicit candidate SHA256')
    c.require(c.sha(a.PRODUCTION.read_bytes()) == a.BASE_SHA, 'current production identity')
    out.mkdir()
    try:
        observer = c.load_observer()
        observer.verify_log = c.verify_log
        protected = observer.legacy.protected()
        before, after = c.archive(a.PRODUCTION), c.archive(args.candidate)
        a.packages(before, after)
        source = c.OBSERVER.parent / 'driver.c'
        text = source.read_text()
        marker = 'void __real_grDrawSprite(PlatformSurface *,struct TTtmSlot *,int,int,uint16,uint16);'
        c.require(text.count(marker) == 1, 'unique pre-wave helper insertion')
        text = text.replace(marker, HOOK + '\n' + marker)
        marker = '    observe(slot,x,y,frame,image,0);'
        c.require(text.count(marker) == 1, 'unique post-draw observation insertion')
        text = text.replace(marker, marker + '\n    if (image<MAX_BMP_SLOTS && slot->bmpNames[image] &&\n'
                            '        !strcmp(slot->bmpNames[image],"BACKGRND.BMP") && frame==2) save_prewave();')
        driver = out / 'observer-source'
        driver.mkdir()
        (driver / 'driver.c').write_bytes(text.encode())
        observer.HERE = driver
        exe = observer.build(out)
        canvases = {str(f): after[c.member(f)]['canvas'] for f in c.FRAMES}
        rows = {}
        for name, archive in (('baseline', a.PRODUCTION), ('candidate', args.candidate)):
            folder = out / name
            report = observer.one(exe, archive, folder, [0, 0, 0, 0, 1, 0, 1], True, canvases)
            log = (folder / 'capture.log').read_text()
            witness = 'PREWAVE: actual grBackgroundSfc after BACKGRND002; phases=-1,-1,-1,-1; display_capture=0'
            c.require(log.count(witness) == 1, 'executed pre-wave witness ' + name)
            first_wave = re.search(r'BG DRAW: frame=(3[0-9]|4[01]) ', log)
            c.require(first_wave is not None and log.index('BG DRAW: frame=2 ') < log.index(witness) < first_wave.start(),
                      'pre-wave capture order ' + name)
            pixels = observer.codec.ppm(folder / 'prewave.ppm')
            png = observer.codec.png_bytes(pixels)
            (folder / 'prewave.png').write_bytes(png)
            frozen_folder = a.BASE / 'none/smoke' if name == 'baseline' else HERE / 'captures-v1/none/smoke'
            frozen = json.loads((frozen_folder / 'report.json').read_bytes())
            keys = (*c.TIMING, 'pixels_sha256', 'png_sha256')
            c.require([[d[k] for k in keys] for d in report['displays']] ==
                      [[d[k] for k in keys] for d in frozen['displays'][:len(report['displays'])]],
                      'passive observer displayed prefix ' + name)
            rows[name] = {'archive_sha256': c.sha(archive.read_bytes()), 'prewave_png_sha256': c.sha(png),
                          'prewave_pixels_sha256': c.sha(pixels), 'report_sha256': c.sha((folder / 'report.json').read_bytes()),
                          'log_sha256': c.sha((folder / 'capture.log').read_bytes()),
                          'matched_unmodified_observer_displays': len(report['displays']),
                          'reference_report_sha256': c.sha((frozen_folder / 'report.json').read_bytes())}
            print('READY ' + str(folder / 'prewave.png'), flush=True)
        changed = a.scoped_pixels(observer.codec.ppm(out / 'baseline/prewave.ppm'),
                                  observer.codec.ppm(out / 'candidate/prewave.ppm'))
        c.require(changed > 0, 'pre-wave beach/rock change visible')
        c.require(protected == observer.legacy.protected(), 'pre-wave protected inputs stable')
        c.save(out / 'summary.json', {'status': 'PASS', 'cases': rows, 'changed_pixels': changed,
            'outside_001_002_pixels': 'EXACT', 'base_driver_sha256': c.sha(source.read_bytes()),
            'adapter_sha256': c.sha(Path(__file__).read_bytes()), 'modified_driver_sha256': c.sha((driver / 'driver.c').read_bytes()),
            'build_sha256': c.sha((out / 'build.json').read_bytes()), 'protected_sha256': protected,
            'scope': 'Real native grBackgroundSfc after BACKGRND002 before any wave draw, observed without changing native rendering. Initialization background only: no clouds, holiday or Johnny. Not a normal displayed full scene.'})
    except Exception:
        c.save(out / 'failure.json', {'traceback': traceback.format_exc()})
        raise


if __name__ == '__main__':
    main()
