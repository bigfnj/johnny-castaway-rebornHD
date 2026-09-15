/* Test-only driver. Calls the real engine API, not shipped CLI scheduling.
 * Usage: jc_island_probe hd|cartoon none|de|ed frame_budget capture.ppm
 * Budget0 runs the finite walk to completion with normal API cleanup.
 */
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

static int checkAtopClipping(void)
{
    struct TTtmSlot slot = {0};
    PlatformSurface *source = platformCreateSurface(4, 4);
    PlatformSurface *dest = platformCreateSurface(8, 8);
    slot.numSprites[0] = 1;
    slot.sprites[0][0] = source;
    platformFillRect(source, NULL, 255, 0, 0, 128);
    platformFillRect(dest, NULL, 0, 0, 255, 128);
    grScale = 2;
    grDx = grDy = 1;
    PlatformRect clip = {3, 3, 2, 2};
    platformSetClipRect(dest, &clip);
    grDrawSpriteAtop(dest, &slot, 0, 0, 0, 0);
    int ok = 1;
    const uint8 *pixels = platformGetSurfacePixels(dest);
    int pitch = platformGetSurfacePitch(dest);
    for (int y = 0; y < 8; y++) {
        for (int x = 0; x < 8; x++) {
            const uint8 *p = pixels + y * pitch + x * 4;
            int changed = x >= 3 && x < 5 && y >= 3 && y < 5;
            if (p[0] != (changed ? 64 : 128) || p[1] != 0 ||
                p[2] != (changed ? 64 : 0) || p[3] != 128) ok = 0;
        }
    }
    /* Negative destination clips the source origin too; only its bottom-right
     * quarter reaches the surface, with destination alpha unchanged. */
    platformFillRect(dest, NULL, 0, 0, 255, 128);
    platformSetClipRect(dest, NULL);
    grDrawSpriteAtop(dest, &slot, -2, -2, 0, 0);
    for (int y = 0; y < 8; y++) {
        for (int x = 0; x < 8; x++) {
            const uint8 *p = pixels + y * pitch + x * 4;
            int changed = x < 2 && y < 2;
            if (p[0] != (changed ? 64 : 128) || p[1] != 0 ||
                p[2] != (changed ? 64 : 0) || p[3] != 128) ok = 0;
        }
    }
    platformFreeSurface(dest);
    platformFreeSurface(source);
    printf("ATOP clipped scaled offset and negative origin: %s\n", ok ? "PASS" : "FAIL");
    return ok ? 0 : 1;
}

int main(int argc, char **argv)
{
    if (argc == 2 && !strcmp(argv[1], "atop-clipping")) return checkAtopClipping();
    if (argc != 5 || !artStyleSelect(argv[1])) return 2;
    int from = 3, to = 4, heading = 2;
    int backgroundOnly = !strcmp(argv[2], "none");
    if (!strcmp(argv[2], "ed")) { from = 4; to = 3; heading = 6; }
    else if (!backgroundOnly && strcmp(argv[2], "de")) return 2;
    debugMode = 1;
    grWindowed = 1;
    grForcedSeed = 9;
    grCapturePath = argv[4];
    evStartAtMaxSpeed = 1;
    evHotKeysEnabled = 1;
    evMaxFrames = (uint32)strtoul(argv[3], NULL, 10);
    soundDisabled = 1;
    zipvfs_init("scrantic_data.zip");
    parseResourceFiles("data/RESOURCE.MAP");
    graphicsInit();
    soundInit();
    adsInit();
    adsInitIsland();
    printf("API HARNESS: highTide=%d offset=%d,%d raft=%d route=%s\n",
           !islandState.lowTide, islandState.xPos, islandState.yPos, islandState.raft, argv[2]);
    if (backgroundOnly) {
        struct TTtmThread empty[MAX_TTM_THREADS] = {{0}};
        struct TTtmThread background = {0};
        background.isRunning = TTM_STATIC_LAYER;
        background.ttmLayer = grBackgroundSfc;
        grUpdateDisplay(&background, empty, NULL, NULL);
    } else {
        /* Select an existing direct path through the real calcPath routine.
         * This changes only the test's path RNG seed after island setup. */
        unsigned seed;
        debugMode = 0;
        for (seed = 0; seed < 2000; seed++) {
            srand(seed);
            int *path = calcPath(from, to);
            if (path[0] == from && path[1] == to && path[2] == UNDEF_NODE) break;
        }
        if (seed == 2000) fatalError("API harness: no direct D/E path found");
        debugMode = 1;
        srand(seed);
        printf("API HARNESS: direct-path RNG seed=%u; executing unchanged adsPlayWalk\n", seed);
        adsPlayWalk(from, heading, to, heading);
    }
    adsReleaseIsland();
    soundEnd();
    graphicsEnd();
    zipvfs_shutdown();
    printf("API HARNESS: finite route returned and cleanup completed\n");
    return 0;
}
