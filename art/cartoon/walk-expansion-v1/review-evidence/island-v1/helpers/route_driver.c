/* Scratch observation driver. All engine calls and archive bytes are unchanged. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ads.h"
#include "art_style.h"
#include "calcpath.h"
#include "calcpath_data.h"
#include "events.h"
#include "graphics.h"
#include "island.h"
#include "resource.h"
#include "sound.h"
#include "utils.h"
#include "zipvfs.h"

static int recording;
static int after_tick;
static unsigned display_count;
static unsigned long long logical_ms;

void __real_eventsWaitTick(uint16 delay);
void __wrap_eventsWaitTick(uint16 delay)
{
    if (recording) logical_ms += (unsigned long long)delay * 20u;
    after_tick = 0;
    __real_eventsWaitTick(delay);
    after_tick = recording;
}

void __real_platformUpdateWindow(PlatformWindow *window);
void __wrap_platformUpdateWindow(PlatformWindow *window)
{
    __real_platformUpdateWindow(window);
    if (!recording || !after_tick) return;
    after_tick = 0;
    PlatformSurface *surface = platformGetWindowSurface(window);
    int width = platformGetSurfaceWidth(surface);
    int height = platformGetSurfaceHeight(surface);
    int pitch = platformGetSurfacePitch(surface);
    const uint8 *pixels = platformGetSurfacePixels(surface);
    if (!pixels || width != 1280 || height != 960 || pitch < width * 4)
        fatalError("REAR OBSERVER: invalid capture surface");
    char name[64];
    snprintf(name, sizeof(name), "display-%03u.ppm", ++display_count);
    FILE *file = safe_fopen(name, "wb");
    if (fprintf(file, "P6\n%d %d\n255\n", width, height) < 0)
        fatalError("REAR OBSERVER: capture header failed");
    unsigned char row[1280 * 3];
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const uint8 *p = pixels + y * pitch + x * 4;
            row[x * 3] = p[2];
            row[x * 3 + 1] = p[1];
            row[x * 3 + 2] = p[0];
        }
        if (fwrite(row, sizeof(row), 1, file) != 1)
            fatalError("REAR OBSERVER: capture pixels failed");
    }
    if (fclose(file)) fatalError("REAR OBSERVER: capture close failed");
    printf("REAR DISPLAY: %u logical_ms=%llu file=%s\n", display_count, logical_ms, name);
    fflush(stdout);
}

int main(int argc, char **argv)
{
    UNUSED(walkMatrix); /* Header supplies the original node/sentinel constants. */
    if (argc != 3 || !artStyleSelect(argv[1])) return 2;
    if (strcmp(argv[2], "smoke") && strcmp(argv[2], "full")) return 2;
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
    unsigned seed;
    debugMode = 0;
    for (seed = 0; seed < 2000; ++seed) {
        srand(seed);
        int *path = calcPath(1, 0);
        if (path[0] == 1 && path[1] == 0 && path[2] == UNDEF_NODE) break;
    }
    if (seed == 2000) fatalError("REAR DRIVER: no direct B,A,UNDEF path");
    debugMode = 1;
    srand(seed);
    printf("REAR DRIVER: island_seed=11 path_seed=%u route=B,A,UNDEF api=adsPlayWalk(1,3,0,3) style=%s\n", seed, argv[1]);
    printf("REAR ISLAND: highTide=%d offset=%d,%d raft=%d night=%d holiday=%d\n",
           !islandState.lowTide, islandState.xPos, islandState.yPos,
           islandState.raft, islandState.night, islandState.holiday);
    recording = 1;
    adsPlayWalk(1, 3, 0, 3);
    recording = 0;
    adsReleaseIsland();
    soundEnd();
    graphicsEnd();
    zipvfs_shutdown();
    printf("REAR DRIVER: finite route returned; cleanup complete; displays=%u logical_ms=%llu\n",
           display_count, logical_ms);
    return 0;
}
