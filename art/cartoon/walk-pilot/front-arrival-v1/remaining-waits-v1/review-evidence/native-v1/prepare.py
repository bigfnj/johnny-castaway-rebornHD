"""Stage an unchanged approved ring baseline and explicit native call driver."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

import config

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT / 'build/front-arrival/front-turn-v1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    assert all(not (OUT / name).exists() for name in ('baseline-pack.zip', 'native_core.py', 'route_driver.c', 'preparation.json')), 'preserve prepared ring outputs'
    source_zip = ROOT / 'assets/scrantic_data.zip'
    assert sha(source_zip.read_bytes()) == config.PRODUCTION_SHA, 'production archive identity'
    additions = {}
    for frame, approved in config.APPROVED.items():
        raw = (ROOT / approved['path']).read_bytes()
        assert sha(raw) == approved['sha256'], 'approved runtime identity:' + str(frame)
        additions[f'data/styles/cartoon/BMP/JOHNWALK.BMP/{frame:03}.png'] = raw
    with zipfile.ZipFile(source_zip) as archive:
        names = archive.namelist()
        assert len(names) == len(set(names)) and not (set(additions) & set(names)), 'unique untouched production members'
        hashes = {name: sha(archive.read(name)) for name in names}
        with zipfile.ZipFile(OUT / 'baseline-pack.zip', 'x') as output:
            output.comment = archive.comment
            for info in archive.infolist():
                output.writestr(copy.copy(info), archive.read(info.filename))
            for member, raw in additions.items():
                frame = member.rsplit('/', 1)[1]
                info = copy.copy(archive.getinfo('data/hd/BMP/JOHNWALK.BMP/' + frame))
                info.filename = info.orig_filename = member
                output.writestr(info, raw)
    with zipfile.ZipFile(OUT / 'baseline-pack.zip') as packed:
        assert packed.namelist() == names + list(additions)
        assert all(sha(packed.read(name)) == digest for name, digest in hashes.items()), 'all production members retained'
        assert all(packed.read(name) == raw for name, raw in additions.items()), 'only approved016017 added'
        assert 'data/styles/cartoon/BMP/JOHNWALK.BMP/018.png' in packed.namelist(), 'existing approved018 retained'
    # Reuse the existing observation wrappers byte-for-byte; TURN is their log
    # prefix, not a claim that the clip contains only one two-pose turn.
    prior_driver = (PRIOR / 'route_driver.c').read_text()
    assert prior_driver.count('int main(int argc, char **argv)') == 1
    driver = prior_driver.split('int main(int argc, char **argv)')[0]
    options = '\n'.join(f'    {"if" if i == 0 else "else if"} (!strcmp(argv[3], "{name}")) step = {row["step"]};' for i, (name, row) in enumerate(config.CLIPS.items()))
    driver += r'''static void play_native_segment(const char *name, int from, int to)
{
    srand(2);
    printf("TURN SEGMENT: %s api=adsPlayWalk(0,%d,0,%d) start_ms=%llu\n", name, from, to, logical_ms);
    adsPlayWalk(0, from, 0, to);
    printf("TURN SEGMENT END: %s end_ms=%llu\n", name, logical_ms);
}

int main(int argc, char **argv)
{
    UNUSED(walkMatrix);
    if (argc != 4 || !artStyleSelect(argv[1])) return 2;
    if (strcmp(argv[2], "smoke") && strcmp(argv[2], "full")) return 2;
    int step;
''' + options + r'''
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
           !islandState.lowTide, islandState.xPos, islandState.yPos, islandState.raft, islandState.night, islandState.holiday);
    recording = 1;
    play_native_segment("prime", 0, 0);
    int current = 0;
    for (int i = 1; i <= 8; i++) {
        int next = (current + step) & 7;
        char name[16];
        snprintf(name, sizeof(name), "turn%02d", i);
        play_native_segment(name, current, next);
        current = next;
    }
    recording = 0;
    adsReleaseIsland();
    soundEnd();
    graphicsEnd();
    zipvfs_shutdown();
    printf("TURN DRIVER: finite clips returned; cleanup complete; displays=%u logical_ms=%llu\n", display_count, logical_ms);
    return 0;
}
'''
    (OUT / 'route_driver.c').write_text(driver, encoding='utf-8', newline='\n')
    # Reuse only five generic functions, using AST source spans rather than
    # broad replacements of the old route's assumptions. Contract comes from
    # the shared explicit ring configuration above.
    text = (PRIOR / 'capture.py').read_text()
    functions = {node.name: ast.get_source_segment(text, node) for node in ast.parse(text).body if isinstance(node, ast.FunctionDef)}
    header = '''import hashlib\nimport importlib.util\nimport json\nfrom pathlib import Path\nimport subprocess\nimport time\nfrom config import contract\nSOURCE = Path('/source')\nOUT = Path('/out')\nBASE = OUT / 'baseline-v1'\nFORMAT = SOURCE / 'art/cartoon/arrival-pilot-v1/review-evidence/native-v1/helpers/capture_format.py'\nspec = importlib.util.spec_from_file_location('ring_codec', FORMAT)\ncodec = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(codec)\n\n'''
    body = '\n\n'.join(functions[name] for name in ('sha', 'require', 'save', 'protected', 'build'))
    assert body.count("exe = BASE / 'front_turn_probe'") == 1
    body = body.replace("exe = BASE / 'front_turn_probe'", "exe = BASE / 'waiting_ring_probe'")
    (OUT / 'native_core.py').write_text(header + body + '\n', encoding='utf-8', newline='\n')
    record = {'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
              'image_id': 'sha256:c648e362c0fa184b745cc54efc05792d54596ef23e5a34b1376d98e62af39a72',
              'production_archive_sha256': config.PRODUCTION_SHA, 'baseline_pack_sha256': sha((OUT / 'baseline-pack.zip').read_bytes()),
              'adapted_driver_sha256': sha((OUT / 'route_driver.c').read_bytes()),
              'native_core_sha256': sha((OUT / 'native_core.py').read_bytes()), 'config_sha256': sha((OUT / 'config.py').read_bytes()),
              'prior_driver_sha256': sha((PRIOR / 'route_driver.c').read_bytes()), 'prior_capture_sha256': sha((PRIOR / 'capture.py').read_bytes()),
              'approved_assets': config.APPROVED, 'production_members_preserved': len(names),
              'scope': 'Eight adjacent-heading native calls in each direction plus actual native priming. Prior approved016017 and production018 retained; no new000015 artwork or production writes.'}
    (OUT / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS shared ring config, approved private baseline and actual native driver prepared')


if __name__ == '__main__':
    main()
