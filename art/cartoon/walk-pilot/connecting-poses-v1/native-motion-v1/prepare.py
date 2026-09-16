"""Prepare a byte-exact current production baseline and explicit route observer."""
import ast
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
import config

ROOT, OUT, sha = config.ROOT, config.OUT, config.sha
PRIOR = ROOT / 'art/cartoon/walk-pilot/front-arrival-v1/remaining-waits-v1/review-evidence/native-v1'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assert not any((OUT / p).exists() for p in ('preparation.json', 'baseline-pack.zip', 'route_driver.c')), 'preserve preparation outputs'
    archive = ROOT / 'assets/scrantic_data.zip'
    assert sha(archive.read_bytes()) == config.PRODUCTION_SHA, 'current production ZIP identity'
    with zipfile.ZipFile(archive) as packed:
        names = packed.namelist()
        assert len(names) == len(set(names)), 'unique production members'
        hashes = {name: sha(packed.read(name)) for name in names}
        accepted = [name for name in names if name.startswith('data/styles/cartoon/') and name.endswith('.png')]
        assert len(accepted) == 40, '40 accepted Cartoon PNGs retained'
        assert all(f'data/styles/cartoon/BMP/JOHNWALK.BMP/{i:03}.png' not in names for i in config.CANDIDATE_FRAMES), 'connecting poses remain HD baseline'
    shutil.copyfile(archive, OUT / 'baseline-pack.zip')
    prior_driver = (PRIOR / 'route_driver.c').read_text()
    marker = 'static void play_native_segment('
    assert prior_driver.count(marker) == 1, 'unique prior observer boundary'
    driver = prior_driver.split(marker)[0]
    driver += r'''static void play_native_segment(const char *name, int a, int ah, int b, int bh)
{
    srand(2);
    printf("TURN SEGMENT: %s api=adsPlayWalk(%d,%d,%d,%d) start_ms=%llu\n", name, a, ah, b, bh, logical_ms);
    adsPlayWalk(a, ah, b, bh);
    printf("TURN SEGMENT END: %s end_ms=%llu\n", name, logical_ms);
}

int main(int argc, char **argv)
{
    UNUSED(walkMatrix);
    if (argc != 4 || !artStyleSelect(argv[1])) return 2;
    if (strcmp(argv[2], "smoke") && strcmp(argv[2], "full")) return 2;
    const int *prime = NULL, *travel = NULL;
'''
    for i, (name, clip) in enumerate(config.CLIPS.items()):
        driver += f'    static const int prime{i}[4] = {{{", ".join(map(str, clip["prime"]))}}};\n'
        driver += f'    static const int travel{i}[4] = {{{", ".join(map(str, clip["travel"]))}}};\n'
        driver += f'    if (!strcmp(argv[3], "{name}")) {{ prime = prime{i}; travel = travel{i}; }}\n'
    driver += r'''    if (!prime || !travel) return 2;
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
    graphicsInit(); soundInit(); adsInit(); adsInitIsland();
    printf("TURN DRIVER: island_seed=11 path_seed=2 clip=%s style=%s\n", argv[3], argv[1]);
    printf("TURN ISLAND: highTide=%d offset=%d,%d raft=%d night=%d holiday=%d\n", !islandState.lowTide, islandState.xPos, islandState.yPos, islandState.raft, islandState.night, islandState.holiday);
    recording = 1;
    play_native_segment("prime", prime[0], prime[1], prime[2], prime[3]);
    play_native_segment("travel", travel[0], travel[1], travel[2], travel[3]);
    recording = 0;
    adsReleaseIsland(); soundEnd(); graphicsEnd(); zipvfs_shutdown();
    printf("TURN DRIVER: finite clips returned; cleanup complete; displays=%u logical_ms=%llu\n", display_count, logical_ms);
    return 0;
}
'''
    (OUT / 'route_driver.c').write_text(driver, encoding='utf-8', newline='\n')
    trace_path = ROOT / 'art/cartoon/walk-pilot/front-arrival-v1/trace/trace.py'
    tree = ast.parse(trace_path.read_text())
    glue = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'GLUE' for t in node.targets))
    (OUT / 'trace_driver.c').write_text(glue, encoding='utf-8', newline='\n')
    helpers = {p.name: sha(p.read_bytes()) for p in config.HERE.glob('*.py')}
    record = {'source_commit': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
              'image_id': config.IMAGE_ID, 'production_archive_sha256': config.PRODUCTION_SHA,
              'baseline_pack_sha256': sha((OUT / 'baseline-pack.zip').read_bytes()),
              'adapted_driver_sha256': sha((OUT / 'route_driver.c').read_bytes()), 'trace_driver_sha256': sha((OUT / 'trace_driver.c').read_bytes()),
              'prior_driver_path': (PRIOR / 'route_driver.c').relative_to(ROOT).as_posix(), 'prior_driver_sha256': sha((PRIOR / 'route_driver.c').read_bytes()),
              'prior_trace_path': trace_path.relative_to(ROOT).as_posix(), 'prior_trace_sha256': sha(trace_path.read_bytes()),
              'helper_sha256': helpers, 'production_members_sha256': hashes, 'accepted_cartoon_pngs': accepted,
              'scope': 'Byte-exact current40-asset production baseline; six actual connecting route clips; no candidate or production changes.'}
    (OUT / 'preparation.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print('PASS prepared exact production baseline, explicit observer and independent C trace helper')


if __name__ == '__main__':
    main()
