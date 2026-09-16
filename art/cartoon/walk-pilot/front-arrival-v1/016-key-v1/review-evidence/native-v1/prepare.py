"""Prepare actual same-spot turns with a native approved017 priming call."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'build/front-arrival/native'
ZIP_SHA = '1da6ddba0f22d679193fc35b824b975b62dc9ca1966f312d91649f18d8793b63'
PNG_SHA = '60e3a77a64620502d2b5198911a7805e19aaedf07801c7a00a92c030b4924de1'
MEMBER017 = 'data/styles/cartoon/BMP/JOHNWALK.BMP/017.png'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    outputs = ['route_driver.c', 'baseline-pack.zip', 'preparation.json']
    if any((OUT / name).exists() for name in outputs):
        raise ValueError('preserve existing turn preparation')
    source_zip = ROOT / 'assets/scrantic_data.zip'
    png = ROOT / 'build/front-arrival/export-v3/BMP/JOHNWALK.BMP/017.png'
    assert sha(source_zip.read_bytes()) == ZIP_SHA, 'production archive identity'
    assert sha(png.read_bytes()) == PNG_SHA, 'approved017 runtime identity'
    with zipfile.ZipFile(source_zip) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)) and MEMBER017 not in names, 'unique production baseline'
        hashes = {name: sha(archive.read(name)) for name in names}
        with zipfile.ZipFile(OUT / 'baseline-pack.zip', 'x') as output:
            output.comment = archive.comment
            for info in archive.infolist():
                output.writestr(copy.copy(info), archive.read(info.filename))
            info = copy.copy(archive.getinfo('data/hd/BMP/JOHNWALK.BMP/017.png'))
            info.filename = info.orig_filename = MEMBER017
            output.writestr(info, png.read_bytes())
    with zipfile.ZipFile(OUT / 'baseline-pack.zip') as output:
        assert output.namelist() == names + [MEMBER017], 'only approved017 addition'
        assert all(sha(output.read(name)) == digest for name, digest in hashes.items()), 'all production members unchanged'
    previous = (PRIOR / 'route_driver.c').read_text(encoding='utf-8')
    assert previous.count('int main(int argc, char **argv)') == 1
    text = previous.split('int main(int argc, char **argv)')[0].replace('FRONT', 'TURN')
    text += r'''int main(int argc, char **argv)
{
    UNUSED(walkMatrix);
    if (argc != 4 || !artStyleSelect(argv[1])) return 2;
    if (strcmp(argv[2], "smoke") && strcmp(argv[2], "full")) return 2;
    int from, to;
    if (!strcmp(argv[3], "A1-to-A7")) { from = 1; to = 7; }
    else if (!strcmp(argv[3], "A7-to-A1")) { from = 7; to = 1; }
    else return 2;
    debugMode = 1;
    grWindowed = 1;
    grForcedSeed = 11;
    grCapturePath = "final.ppm";
    evStartAtMaxSpeed = 1;
    evHotKeysEnabled = 1;
    evMaxFrames = !strcmp(argv[2], "smoke") ? 1 : 0;
    soundDisabled = 1;
    zipvfs_init("scrantic_data.zip");
    parseResourceFiles("data/RESOURCE.MAP");
    graphicsInit();
    soundInit();
    adsInit();
    adsInitIsland();
    printf("TURN DRIVER: island_seed=11 path_seed=2 clip=%s style=%s\n", argv[3], argv[1]);
    printf("TURN ISLAND: highTide=%d offset=%d,%d raft=%d night=%d holiday=%d\n",
           !islandState.lowTide, islandState.xPos, islandState.yPos,
           islandState.raft, islandState.night, islandState.holiday);
    srand(2);
    recording = 1;
    printf("TURN SEGMENT: prime api=adsPlayWalk(0,%d,0,%d) start_ms=%llu\n", from, from, logical_ms);
    adsPlayWalk(0, from, 0, from);
    printf("TURN SEGMENT END: prime end_ms=%llu\n", logical_ms);
    srand(2);
    printf("TURN SEGMENT: turn api=adsPlayWalk(0,%d,0,%d) start_ms=%llu\n", from, to, logical_ms);
    adsPlayWalk(0, from, 0, to);
    printf("TURN SEGMENT END: turn end_ms=%llu\n", logical_ms);
    recording = 0;
    adsReleaseIsland();
    soundEnd();
    graphicsEnd();
    zipvfs_shutdown();
    printf("TURN DRIVER: finite clips returned; cleanup complete; displays=%u logical_ms=%llu\n", display_count, logical_ms);
    return 0;
}
'''
    (OUT / 'route_driver.c').write_text(text, encoding='utf-8', newline='\n')
    record = {'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
              'image_id': 'sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72',
              'production_archive_sha256': ZIP_SHA, 'baseline_pack_sha256': sha((OUT / 'baseline-pack.zip').read_bytes()),
              'approved017_sha256': PNG_SHA, 'production_members_preserved': len(names),
              'adapted_driver_sha256': sha((OUT / 'route_driver.c').read_bytes()),
              'prior_driver_sha256': sha((PRIOR / 'route_driver.c').read_bytes()),
              'scope': 'Native same-spot turn baseline with approved017 private addition; existing HD016. Separate native priming call preserves observed starting017 duration. No candidate016 or production edits.'}
    (OUT / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS turn observer prepared; approved017 only, all production members preserved')


if __name__ == '__main__':
    main()
