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
#include "walk.h"

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
    if (recording) printf("TURN WAIT: ticks=%u logical_ms=%llu\n", delay, logical_ms);
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
        fatalError("TURN OBSERVER: invalid capture surface");
    char name[64];
    snprintf(name, sizeof(name), "display-%03u.ppm", ++display_count);
    FILE *file = safe_fopen(name, "wb");
    if (fprintf(file, "P6\n%d %d\n255\n", width, height) < 0)
        fatalError("TURN OBSERVER: capture header failed");
    unsigned char row[1280 * 3];
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            const uint8 *p = pixels + y * pitch + x * 4;
            row[x * 3] = p[2];
            row[x * 3 + 1] = p[1];
            row[x * 3 + 2] = p[0];
        }
        if (fwrite(row, sizeof(row), 1, file) != 1)
            fatalError("TURN OBSERVER: capture pixels failed");
    }
    if (fclose(file)) fatalError("TURN OBSERVER: capture close failed");
    printf("TURN DISPLAY: %u logical_ms=%llu file=%s\n", display_count, logical_ms, name);
    fflush(stdout);
}


/* Observe actual draw dispatch and returned delays, without changing their arguments. */
void __real_grDrawSprite(PlatformSurface *, struct TTtmSlot *, int, int, uint16, uint16);
void __wrap_grDrawSprite(PlatformSurface *sfc, struct TTtmSlot *slot, int x, int y, uint16 sprite, uint16 image)
{
    __real_grDrawSprite(sfc, slot, x, y, sprite, image);
    if (recording && image < MAX_BMP_SLOTS && slot->bmpNames[image] && !strcmp(slot->bmpNames[image], "JOHNWALK.BMP"))
        printf("TURN DRAW: flip=0 x=%d y=%d frame=%u\n", x, y, sprite);
}

void __real_grDrawSpriteFlip(PlatformSurface *, struct TTtmSlot *, int, int, uint16, uint16);
void __wrap_grDrawSpriteFlip(PlatformSurface *sfc, struct TTtmSlot *slot, int x, int y, uint16 sprite, uint16 image)
{
    __real_grDrawSpriteFlip(sfc, slot, x, y, sprite, image);
    if (recording && image < MAX_BMP_SLOTS && slot->bmpNames[image] && !strcmp(slot->bmpNames[image], "JOHNWALK.BMP"))
        printf("TURN DRAW: flip=1 x=%d y=%d frame=%u\n", x, y, sprite);
}

uint16 __real_walkAnimate(struct TTtmThread *, struct TTtmSlot *);
uint16 __wrap_walkAnimate(struct TTtmThread *thread, struct TTtmSlot *background)
{
    uint16 delay = __real_walkAnimate(thread, background);
    if (recording) printf("TURN ANIMATE: delay_ticks=%u\n", delay);
    return delay;
}

static void play_native_segment(const char *name, int a, int ah, int b, int bh)
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
    static const int prime0[4] = {5, 6, 5, 6};
    static const int travel0[4] = {5, 6, 2, 6};
    if (!strcmp(argv[3], "right")) { prime = prime0; travel = travel0; }
    static const int prime1[4] = {2, 2, 2, 2};
    static const int travel1[4] = {2, 2, 0, 2};
    if (!strcmp(argv[3], "left")) { prime = prime1; travel = travel1; }
    static const int prime2[4] = {5, 7, 5, 7};
    static const int travel2[4] = {5, 7, 2, 6};
    if (!strcmp(argv[3], "right_boundary")) { prime = prime2; travel = travel2; }
    static const int prime3[4] = {2, 3, 2, 3};
    static const int travel3[4] = {2, 3, 0, 2};
    if (!strcmp(argv[3], "left_boundary")) { prime = prime3; travel = travel3; }
    if (!prime || !travel) return 2;
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
