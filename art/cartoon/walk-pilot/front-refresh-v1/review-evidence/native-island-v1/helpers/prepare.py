"""Adapt the preserved arrival observer into a new, isolated front-route observer."""
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
PRIOR = ROOT / 'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    raw = (PRIOR / 'route_driver.c').read_bytes()
    text = raw.decode('utf-8').replace('\r\n', '\n')
    text = text.replace('REAR', 'FRONT')
    changes = [
        ('calcPath(1, 0)', 'calcPath(4, 0)'),
        ('path[0] == 1', 'path[0] == 4'),
        ('route=B,A,UNDEF api=adsPlayWalk(1,3,0,3)', 'route=E,A,UNDEF api=adsPlayWalk(4,1,0,1)'),
        ('no direct B,A,UNDEF path', 'no direct E,A,UNDEF path'),
        ('adsPlayWalk(1, 3, 0, 3);', 'adsPlayWalk(4, 1, 0, 1);'),
        ('#include "zipvfs.h"', '#include "zipvfs.h"\n#include "walk.h"'),
        ('    after_tick = recording;',
         '    after_tick = recording;\n    if (recording) printf("FRONT WAIT: ticks=%u logical_ms=%llu\\n", delay, logical_ms);'),
    ]
    for old, new in changes:
        if text.count(old) != 1:
            raise ValueError('prepare.py: unique adaptation anchor:' + old)
        text = text.replace(old, new)
    observer = '''
/* Observe actual draw dispatch and returned delays, without changing their arguments. */
void __real_grDrawSprite(PlatformSurface *, struct TTtmSlot *, int, int, uint16, uint16);
void __wrap_grDrawSprite(PlatformSurface *sfc, struct TTtmSlot *slot, int x, int y, uint16 sprite, uint16 image)
{
    __real_grDrawSprite(sfc, slot, x, y, sprite, image);
    if (recording && image < MAX_BMP_SLOTS && slot->bmpNames[image] && !strcmp(slot->bmpNames[image], "JOHNWALK.BMP"))
        printf("FRONT DRAW: flip=0 x=%d y=%d frame=%u\\n", x, y, sprite);
}

void __real_grDrawSpriteFlip(PlatformSurface *, struct TTtmSlot *, int, int, uint16, uint16);
void __wrap_grDrawSpriteFlip(PlatformSurface *sfc, struct TTtmSlot *slot, int x, int y, uint16 sprite, uint16 image)
{
    __real_grDrawSpriteFlip(sfc, slot, x, y, sprite, image);
    if (recording && image < MAX_BMP_SLOTS && slot->bmpNames[image] && !strcmp(slot->bmpNames[image], "JOHNWALK.BMP"))
        printf("FRONT DRAW: flip=1 x=%d y=%d frame=%u\\n", x, y, sprite);
}

uint16 __real_walkAnimate(struct TTtmThread *, struct TTtmSlot *);
uint16 __wrap_walkAnimate(struct TTtmThread *thread, struct TTtmSlot *background)
{
    uint16 delay = __real_walkAnimate(thread, background);
    if (recording) printf("FRONT ANIMATE: delay_ticks=%u\\n", delay);
    return delay;
}

'''
    if text.count('int main(int argc, char **argv)') != 1:
        raise ValueError('prepare.py: unique main insertion')
    text = text.replace('int main(int argc, char **argv)', observer + 'int main(int argc, char **argv)')
    target = OUT / 'route_driver.c'
    if target.exists():
        raise ValueError('prepare.py: preserve existing route driver')
    target.write_text(text, encoding='utf-8', newline='\n')
    evidence = {
        'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
        'image_id': 'sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72',
        'source_driver': str((PRIOR / 'route_driver.c').relative_to(ROOT)),
        'source_driver_sha256': sha(raw), 'adapted_driver_sha256': sha(target.read_bytes()),
        'prepare_sha256': sha(Path(__file__).read_bytes()),
        'adaptations': ['REAR labels become FRONT', 'direct E-to-A route and headings 1/1',
                        'observe completed waits, actual sprite draw dispatch and walk delay return values'],
        'scope': 'New observation-only linker wrapper; original archived helper and production sources unchanged.'
    }
    (OUT / 'preparation.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print('PASS front observer prepared; prior driver bytes and production inputs untouched')


if __name__ == '__main__':
    main()
