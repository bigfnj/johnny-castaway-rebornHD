/* Observation-only adaptation of seasonal-v1/native/driver.c; no phase forcing. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ads.h"
#include "art_style.h"
#include "events.h"
#include "graphics.h"
#include "island.h"
#include "resource.h"
#include "sound.h"
#include "utils.h"
#include "zipvfs.h"

void __real_grDrawSprite(PlatformSurface *, struct TTtmSlot *, int, int, uint16, uint16);
void __wrap_grDrawSprite(PlatformSurface *s, struct TTtmSlot *slot,
                         int x, int y, uint16 frame, uint16 image)
{
    __real_grDrawSprite(s, slot, x, y, frame, image);
    if (image >= MAX_BMP_SLOTS || !slot->bmpNames[image]) return;
    PlatformSurface *sprite = slot->sprites[image][frame];
    if (!strcmp(slot->bmpNames[image], "HOLIDAY.BMP"))
        printf("SEASONAL DRAW: frame=%u x=%d y=%d dx=%d dy=%d scale=%d canvas=%dx%d\n",
               frame, x, y, grDx, grDy, grScale,
               platformGetSurfaceWidth(sprite), platformGetSurfaceHeight(sprite));
    if (!strcmp(slot->bmpNames[image], "BACKGRND.BMP"))
        printf("SHORE DRAW: frame=%u x=%d y=%d dx=%d dy=%d scale=%d canvas=%dx%d\n",
               frame, x, y, grDx, grDy, grScale,
               platformGetSurfaceWidth(sprite), platformGetSurfaceHeight(sprite));
}

int main(int argc, char **argv)
{
    if (argc != 5 || !artStyleSelect("cartoon")) return 2;
    int holiday = atoi(argv[1]), night = atoi(argv[2]);
    int x = atoi(argv[3]), y = atoi(argv[4]);
    if (holiday < 0 || holiday > 4 || (night != 0 && night != 1)) return 2;
    debugMode = 1;
    grWindowed = 1;
    grForcedSeed = 11;
    grCapturePath = "final.ppm";
    evStartAtMaxSpeed = 1;
    evHotKeysEnabled = 1;
    soundDisabled = 1;
    zipvfs_init("scrantic_data.zip");
    parseResourceFiles("data/RESOURCE.MAP");
    graphicsInit();
    soundInit();
    adsInit();
    islandState.holiday = holiday;
    islandState.night = night;
    islandState.xPos = x;
    islandState.yPos = y;
    puts("SHORE STAGE: init");
    adsInitIsland();
    printf("SEASONAL STATE: seed=11 holiday=%d night=%d offset=%d,%d lowTide=%d raft=%d render=%dx%d\n",
           holiday, night, x, y, islandState.lowTide, islandState.raft,
           grRenderWidth, grRenderHeight);
    puts("SHORE STAGE: native same-heading wait");
    adsPlayWalk(0, 0, 0, 0);
    puts("SHORE STAGE: native wait returned");
    adsReleaseIsland();
    soundEnd();
    graphicsEnd();
    zipvfs_shutdown();
    puts("SEASONAL DONE: finite native wait returned; cleanup complete");
    return 0;
}
