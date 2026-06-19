/*
 *  This file is part of 'Johnny Reborn'
 *
 *  An open-source engine for the classic
 *  'Johnny Castaway' screensaver by Sierra.
 *
 *  Copyright (C) 2019 Jeremie GUILLAUME
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */

#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdio.h>
#include <ctype.h>
#include "platform.h"

#include "mytypes.h"
#include "utils.h"
#include "graphics.h"
#include "resource.h"
#include "events.h"
#include "zipvfs.h"


static PlatformWindow *platform_window;

static uint8 ttmPalette[16][4];

static PlatformSurface *grSavedZonesLayer = NULL;

static PlatformRect grScreenOrigin = { 0, 0, 0, 0 };   // TODO

PlatformSurface *grBackgroundSfc = NULL;

int grDx = 0;
int grDy = 0;
int grWindowed = 0;
uint16 grUpdateDelay = 0;

// HD / scaling support (logical coordinate space stays 640x480)
int grScale = 1;                 // 1 = original, 2 = 2x, etc.
int grRenderWidth = SCREEN_WIDTH;
int grRenderHeight = SCREEN_HEIGHT;
int grHdEnabled = 0;


static void grReleaseScreen(void)
{
    free(platformGetSurfacePixels(grBackgroundSfc));
    platformFreeSurface(grBackgroundSfc);
    grBackgroundSfc = NULL;
}


static void grReleaseSavedLayer(void)
{
    platformFreeSurface(grSavedZonesLayer);
    grSavedZonesLayer = NULL;
}



static void grPutPixel(PlatformSurface *sfc, int x, int y, uint8 color)
{
    // TODO: Implement Cohen-Sutherland clipping algorithm or such for
    // grDrawLine(), and another ad hoc algorithm for grDrawCircle()

    // Coordinates are in *logical* pixels (640x480). We write a grScale x grScale
    // block of real pixels to the render surface.
    if (x>=0 && y>=0 && x<SCREEN_WIDTH && y<SCREEN_HEIGHT && color < 16) {

        uint8 *base = platformGetSurfacePixels(sfc);
        int pitch = platformGetSurfacePitch(sfc);
        int bpp = platformGetSurfaceBytesPerPixel(sfc);

        int rx = x * grScale;
        int ry = y * grScale;

        for (int dy=0; dy < grScale; dy++) {
            uint8 *row = base + ((size_t)(ry + dy) * (size_t)pitch) + ((size_t)rx * (size_t)bpp);
            for (int dx=0; dx < grScale; dx++) {
                uint8 *pixel = row + ((size_t)dx * (size_t)bpp);
                pixel[0] = ttmPalette[color][0];
                pixel[1] = ttmPalette[color][1];
                pixel[2] = ttmPalette[color][2];
                pixel[3] = 255;
            }
        }
    }
}


static void grDrawHorizontalLine(PlatformSurface *sfc, int x1, int x2, int y, uint8 color)
{
    if (y < 0 || y > (SCREEN_HEIGHT - 1))
        return;

    x1 = x1 < 0   ? 0   : x1;
    x2 = x2 > (SCREEN_WIDTH - 1) ? (SCREEN_WIDTH - 1) : x2;

    for (int x=x1; x<=x2; x++)
        grPutPixel(sfc, x, y, color);
}


void grLoadPalette(struct TPalResource *palResource)
{
    if (palResource == NULL)
        fatalError("NULL palette\n");

    for (int i=0; i < 16; i++) {
        ttmPalette[i][0] = (uint8)(palResource->colors[i].b << 2);
        ttmPalette[i][1] = (uint8)(palResource->colors[i].g << 2);
        ttmPalette[i][2] = (uint8)(palResource->colors[i].r << 2);
        ttmPalette[i][3] = 255;
    }
}



static void grDetectHDAssets(void)
{
    grScale = 1;
    grHdEnabled = 0;

    // If this file exists in the zip, we assume the HD PNG pack is present.
    const char *manifestPath = "data/hd/manifest.json";

    size_t manifestSize = 0;
    uint8 *manifestData = zipvfs_read(manifestPath, &manifestSize);
    if (!manifestData) {
        grRenderWidth = SCREEN_WIDTH;
        grRenderHeight = SCREEN_HEIGHT;
        return;
    }

    char buf[4096 + 1];
    size_t n = manifestSize < sizeof(buf) - 1 ? manifestSize : sizeof(buf) - 1;
    memcpy(buf, manifestData, n);
    free(manifestData);
    buf[n] = '\0';

    // Very small / very dumb JSON parsing: look for "scale": <int>
    char *p = strstr(buf, "\"scale\"");
    if (!p)
        p = strstr(buf, "scale");

    if (p) {
        p = strchr(p, ':');
        if (p) {
            p++;
            while (*p && !isdigit((unsigned char)*p))
                p++;
            long v = strtol(p, NULL, 10);
            if (v > 1 && v <= 8) {
                grScale = (int)v;
                grHdEnabled = 1;
            }
        }
    }

    grRenderWidth = SCREEN_WIDTH * grScale;
    grRenderHeight = SCREEN_HEIGHT * grScale;

    if (debugMode && grHdEnabled) {
        printf("HD assets enabled (scale=%d, render=%dx%d)\n",
               grScale, grRenderWidth, grRenderHeight);
    }
}


void graphicsInit(void)
{
    platformInit();

    grDetectHDAssets();

    platform_window = platformCreateWindow(
        "Johnny Reborn ...?",
        grRenderWidth,
        grRenderHeight,
        (grWindowed ? 0 : 1)
    );

    if (platform_window == NULL)
        fatalError("Could not create window: %s", platformGetError());

    grScreenOrigin.x = 0;
    grScreenOrigin.y = 0;
    grScreenOrigin.w = grRenderWidth;
    grScreenOrigin.h = grRenderHeight;

    if (!grWindowed)
        platformShowCursor(0);

    platformUpdateWindow(platform_window);

    grLoadPalette(palResources[0]);  // TODO ?

    {
        // srand() takes an unsigned int; time_t may be 64-bit.
        // Fold the time value down to 32 bits in a deterministic way.
        time_t now = time(NULL);
        unsigned long long t = (unsigned long long)now;
        unsigned int seed = (unsigned int)(t ^ (t >> 32));
        srand(seed);
    }

    eventsInit();
}


void graphicsEnd(void)
{
    platformDestroyWindow(platform_window);
    platformShutdown();
}


void grRefreshDisplay(void)
{
    platformUpdateWindow(platform_window);
}


void grToggleFullScreen(void)
{
    grWindowed = !grWindowed;

    platformToggleFullscreen(platform_window);

    if (grWindowed) {
        platformShowCursor(1);
    }
    else {
        platformShowCursor(0);
    }

    platformUpdateWindow(platform_window);
}


void grUpdateDisplay(struct TTtmThread *ttmBackgroundThread,
                     struct TTtmThread *ttmThreads,
                     struct TTtmThread *ttmHolidayThread,
                     struct TTtmThread *ttmCloudsThread)
{
    UNUSED(ttmBackgroundThread);

    PlatformSurface* windowSurface = platformGetWindowSurface(platform_window);

    // Blit the background
    if (grBackgroundSfc != NULL)
        platformBlitSurface(grBackgroundSfc,
                        NULL,
                        windowSurface,
                        &grScreenOrigin);

    // Blit the Clouds
    if (ttmCloudsThread != NULL)
        if (ttmCloudsThread->isRunning)
            platformBlitSurface(ttmCloudsThread->ttmLayer,
                            NULL,
                            windowSurface,
                            &grScreenOrigin);

    // If not NULL, blit the optional layer of saved zones
    if (grSavedZonesLayer != NULL)
        platformBlitSurface(grSavedZonesLayer,
                        NULL,
                        windowSurface,
                        &grScreenOrigin);


    // Blit successively each thread's layer
    for (int i=0; i < MAX_TTM_THREADS; i++)
        if (ttmThreads[i].isRunning)
            platformBlitSurface(ttmThreads[i].ttmLayer,
                            NULL,
                            windowSurface,
                            &grScreenOrigin);

    // Finally, blit the holiday layer
    if (ttmHolidayThread != NULL)
        if (ttmHolidayThread->isRunning)
            platformBlitSurface(ttmHolidayThread->ttmLayer,
                            NULL,
                            windowSurface,
                            &grScreenOrigin);

    // Wait for the tick ...
    eventsWaitTick(grUpdateDelay);

    // ... and refresh the display
    platformUpdateWindow(platform_window);
}
PlatformSurface *grNewLayer(void)
{
    // Layers are drawn over the background, so they need real transparency.
    // We use per-pixel alpha (premultiplied BGRA / PBGRA), not a magenta color-key.
    PlatformSurface *sfc = platformCreateSurface(grRenderWidth, grRenderHeight);
    PlatformRect dest = { 0, 0, grRenderWidth, grRenderHeight };
    platformFillRect(sfc, &dest, 0, 0, 0, 0);  // fully transparent
    return sfc;
}



void grFreeLayer(PlatformSurface *sfc)
{
    platformFreeSurface(sfc);
}


void grSetClipZone(PlatformSurface *sfc, int x1, int y1, int x2, int y2)
{
    x1 += grDx; y1 += grDy;
    x2 += grDx; y2 += grDy;

    int w = x2 - x1;
    int h = y2 - y1;
    if (w < 0) w = 0;
    if (h < 0) h = 0;

    PlatformRect rect = { x1 * grScale, y1 * grScale, w * grScale, h * grScale };
    platformSetClipRect(sfc, &rect);
}


void grCopyZoneToBg(PlatformSurface *sfc, int x, int y, int width, int height)
{
    x += grDx; y += grDy;
    PlatformRect rect = { x * grScale, y * grScale, (width + 2) * grScale, height * grScale };

    if (grSavedZonesLayer == NULL)
        grSavedZonesLayer = grNewLayer();

    platformBlitSurface(sfc, &rect, grSavedZonesLayer, &rect);

    // Note : without the +2 in width+2 above, there would be a graphical
    // glitch (2 unfilled pixels) on the hull of the cargo, caused by an
    // error in coordinates in GJIVS6.TTM
    // Obviously, the original soft rounds the SAVE_IMAGE boundaries on
    // one way or another.
}


void grSaveImage1(PlatformSurface *sfc, int x, int y, int width, int height) // TODO : rename ?
{
    UNUSED(sfc);
    UNUSED(x);
    UNUSED(y);
    UNUSED(width);
    UNUSED(height);
//    ttmSetColors(4,4);
//    ttmDrawRect(arg0,arg1,arg2,arg3);
//    ttmSaveImage0(arg0,arg1,arg2,arg3);
//    ttmUpdate();
}


void grSaveZone(PlatformSurface *sfc, int x, int y, int width, int height)
{
    UNUSED(sfc);
    UNUSED(x);
    UNUSED(y);
    UNUSED(width);
    UNUSED(height);
    // Minimalistic implementation: we don't really save the zone,
    // and let grRestoreZone() simply erase the 'saved zones' layer
}


void grRestoreZone(PlatformSurface *sfc, int x, int y, int width, int height)
{
    UNUSED(sfc);
    UNUSED(x);
    UNUSED(y);
    UNUSED(width);
    UNUSED(height);
    // In Johnny's TTMs, we never have RESTORE_ZONE called
    // while several zones are saved. So we simply free the
    // whole saved zones layer
    grReleaseSavedLayer();
}


void grDrawPixel(PlatformSurface *sfc, int x, int y, uint8 color)
{
    x += grDx; y += grDy;
    grPutPixel(sfc, x, y, color);
}


void grDrawLine(PlatformSurface *sfc, int x1, int y1, int x2, int y2, uint8 color)
{
    x1 += grDx; y1 += grDy;
    x2 += grDx; y2 += grDy;

    platformLockSurface(sfc);

    // Bresenham's line drawing algorithm
    // Note : the code below intends to be pixel-perfect

    int dx, dy, cumul, x, y;
    int xinc, yinc;

    x = x1;
    y = y1;
    dx = abs(x2 - x1);
    dy = abs(y2 - y1);

    xinc = (x2>x1 ? 1 : -1);
    yinc = (y2>y1 ? 1 : -1);

    if (dy < dx) {
        cumul = (dx + 1) >> 1;

        for (int i=0; i <= dx; i++) {

            grPutPixel(sfc, x, y, color);

            x += xinc;
            cumul += dy;

            if (cumul > dx) {
                cumul -= dx;
                y += yinc;
            }
        }
    }
    else {
        cumul = (dy + 1) >> 1;

        for (int i=0; i <= dy; i++) {

            grPutPixel(sfc, x, y, color);

            y += yinc;
            cumul += dx;

            if (cumul > dy) {
                cumul -= dy;
                x += xinc;
            }
        }
    }

    platformUnlockSurface(sfc);
}


void grDrawRect(PlatformSurface *sfc, int x, int y, int width, int height, uint8 color)
{
    if (color >= 16) color = 0;
    x += grDx; y += grDy;
    x *= grScale; y *= grScale;
    width *= grScale; height *= grScale;

    PlatformRect dest = { x, y, width, height };
    platformFillRect(sfc, &dest,
                     ttmPalette[color][2],  // TODO ?
                     ttmPalette[color][1],
                     ttmPalette[color][0],
                     255
    );
}


void grDrawCircle(PlatformSurface *sfc, int x1, int y1, int width, int height, uint8 fgColor, uint8 bgColor)
{
    x1 += grDx; y1 += grDy;

    // We can only draw regular circles
    if (width != height) {
        fprintf(stderr, "Warning : grDrawCircle() : unable to draw ellipse\n");
        return;
    }

    // In original data, every width is even
    if (width % 2) {
        fprintf(stderr, "Warning : grDrawCircle() : unable to process odd diameters\n");
        return;
    }

    // Bresenham's circle drawing algorithm
    // Note : the code below intends to be pixel-perfect

    platformLockSurface(sfc);

    int r = (width >> 1) - 1;
    int xc = x1 + r;
    int yc = y1 + r;
    int x = 0;
    int y = r;
    int d = 1 - r;

    while (1) {

        grDrawHorizontalLine(sfc, xc-x, xc+x+1, yc+y+1, bgColor);
        grDrawHorizontalLine(sfc, xc-x, xc+x+1, yc-y  , bgColor);

        grDrawHorizontalLine(sfc, xc-y, xc+y+1, yc+x+1, bgColor);
        grDrawHorizontalLine(sfc, xc-y, xc+y+1, yc-x  , bgColor);

        if (y-x <= 1)
            break;

        if (d < 0)
            d += (x << 1) + 3;
        else {
            d += ((x - y) << 1) + 5;
            y--;
        }

        x++;
    }

    if (fgColor != bgColor) {

        x = 0;
        y = r;
        d = 1 - r;

        while (1) {

            grPutPixel(sfc, xc-x  , yc+y+1, fgColor);
            grPutPixel(sfc, xc+x+1, yc+y+1, fgColor);

            grPutPixel(sfc, xc-x  , yc-y  , fgColor);
            grPutPixel(sfc, xc+x+1, yc-y  , fgColor);

            grPutPixel(sfc, xc-y  , yc+x+1, fgColor);
            grPutPixel(sfc, xc+y+1, yc+x+1, fgColor);

            grPutPixel(sfc, xc-y  , yc-x  , fgColor);
            grPutPixel(sfc, xc+y+1, yc-x  , fgColor);

            if (y-x <= 1)
                break;

            if (d < 0)
                d += (x << 1) + 3;
            else {
                d += ((x - y) << 1) + 5;
                y--;
            }

            x++;
        }
    }

    platformUnlockSurface(sfc);
}


void grDrawSprite(PlatformSurface *sfc, struct TTtmSlot *ttmSlot, int x, int y, uint16 spriteNo, uint16 imageNo)
{
    if (imageNo >= MAX_BMP_SLOTS || spriteNo >= ttmSlot->numSprites[imageNo]) {
        debugMsg("Warning : grDrawSprite(): sprite #%d requested from bmpSlot %d (%s), but only %d loaded",
                spriteNo, imageNo,
                (imageNo < MAX_BMP_SLOTS && ttmSlot->bmpNames[imageNo]) ? ttmSlot->bmpNames[imageNo] : "empty",
                imageNo < MAX_BMP_SLOTS ? ttmSlot->numSprites[imageNo] : 0);
        return;
    }

    x += grDx; y += grDy;
    x *= grScale; y *= grScale;

    PlatformSurface *srcSfc = ttmSlot->sprites[imageNo][spriteNo];

    PlatformRect dest = { x, y, 0, 0 };
    platformBlitSurface(srcSfc, NULL, sfc, &dest);
}


void grDrawSpriteFlip(PlatformSurface *sfc, struct TTtmSlot *ttmSlot, int x, int y, uint16 spriteNo, uint16 imageNo)
{
    if (imageNo >= MAX_BMP_SLOTS || spriteNo >= ttmSlot->numSprites[imageNo]) {
        debugMsg("Warning : grDrawSpriteFlip(): sprite #%d requested from bmpSlot %d (%s), but only %d loaded",
                spriteNo, imageNo,
                (imageNo < MAX_BMP_SLOTS && ttmSlot->bmpNames[imageNo]) ? ttmSlot->bmpNames[imageNo] : "empty",
                imageNo < MAX_BMP_SLOTS ? ttmSlot->numSprites[imageNo] : 0);
        return;
    }

    x += grDx; y += grDy;
    x *= grScale; y *= grScale;

    PlatformSurface *srcSfc = ttmSlot->sprites[imageNo][spriteNo];
    x += platformGetSurfaceWidth(srcSfc) - 1;

    for (int i=0; i < platformGetSurfaceWidth(srcSfc); i++) {

        PlatformRect src = { i, 0, 1, platformGetSurfaceHeight(srcSfc) };
        PlatformRect dest = { x - i, y, 0, 0 };

        platformBlitSurface(srcSfc, &src, sfc, &dest);
    }
}


void grClearScreen(PlatformSurface *sfc)
{
    PlatformRect rect;

    platformGetClipRect(sfc, &rect);
    platformSetClipRect(sfc, NULL);
    platformFillRect(sfc, NULL, 0, 0, 0, 0);
    platformSetClipRect(sfc, &rect);
}


void grLoadScreen(const char *strArg)
{
    struct TScrResource *scrResource = findScrResource(strArg);

    if (scrResource == NULL) {
        printf("Requested SCR resource not found: %s\n", strArg);
        fatalError("Screen resource not found");
    }

    if (scrResource->width > SCREEN_WIDTH || scrResource->height > SCREEN_HEIGHT)
        fatalError("Screen resource is too big");

    if (scrResource->width % 2)
        printf("Warning: odd-width SCR file %s (engine expects even widths)\n", strArg);

    if (grBackgroundSfc != NULL)
        grReleaseScreen();

    if (grSavedZonesLayer != NULL)
        grReleaseSavedLayer();

    // HD override: data/hd/SCR/<NAME>.png  (e.g. data/hd/SCR/OCEAN00.SCR.png)
    if (grHdEnabled) {
        char path[512];
        snprintf(path, sizeof(path), "data/hd/SCR/%s.png", scrResource->resName);

        size_t pngSize = 0;
        uint8 *pngData = zipvfs_read(path, &pngSize);
        if (pngData) {
            PlatformSurface *pngSfc = platformLoadPNGFromMemory(pngData, pngSize);
            free(pngData);
            if (pngSfc != NULL) {
                grBackgroundSfc = pngSfc;
                return;
            }
        }
    }

    int w = scrResource->width;
    int h = scrResource->height;
    int outW = w * grScale;
    int outH = h * grScale;

    uint8 *outData = safe_malloc((size_t)outW * (size_t)outH * sizeof(uint32));
    uint8 *inPtr = scrResource->uncompressedData;

    int srcIndex = 0;
    for (int y = 0; y < h; y++) {
        for (int x = 0; x < w; x++) {

            uint8 byte = inPtr[srcIndex];
            uint8 index = (x % 2 == 0) ? ((byte & 0xF0) >> 4) : (byte & 0x0F);
            if (x % 2 == 1)
                srcIndex++;

            int rx = x * grScale;
            int ry = y * grScale;

            for (int dy = 0; dy < grScale; dy++) {
                uint8 *row = outData + ((size_t)(ry + dy) * (size_t)outW + (size_t)rx) * 4;
                for (int dx = 0; dx < grScale; dx++) {
                    row[dx * 4 + 0] = ttmPalette[index][0];
                    row[dx * 4 + 1] = ttmPalette[index][1];
                    row[dx * 4 + 2] = ttmPalette[index][2];
                    row[dx * 4 + 3] = 255;
                }
            }
        }
    }

    grBackgroundSfc = platformCreateSurfaceFrom(outData, outW, outH, outW * 4);
}


// Some parts of the engine (ADS script runner) rely on having a valid background
// surface even when no SCR has been loaded yet.
//
// In the HD/scaled pipeline, the background must be allocated at the *render*
// resolution (logical 640x480 multiplied by grScale).
void grInitEmptyBackground(void)
{
    if (grBackgroundSfc != NULL)
        grReleaseScreen();

    if (grSavedZonesLayer != NULL)
        grReleaseSavedLayer();

    int outW = SCREEN_WIDTH * grScale;
    int outH = SCREEN_HEIGHT * grScale;

    uint8 *data = safe_malloc((size_t)outW * (size_t)outH * sizeof(uint32));

    // Opaque black background (alpha=255). This matters now that the blitter
    // supports real alpha blending.
    for (int y = 0; y < outH; y++) {
        uint8 *row = data + ((size_t)y * (size_t)outW * 4);
        for (int x = 0; x < outW; x++) {
            row[x * 4 + 0] = 0;   // B
            row[x * 4 + 1] = 0;   // G
            row[x * 4 + 2] = 0;   // R
            row[x * 4 + 3] = 255; // A
        }
    }

    grBackgroundSfc = platformCreateSurfaceFrom((void*)data, outW, outH, 4 * outW);
}



// Release all sprite images for a given BMP slot.
// Note: sprite surfaces are created with platformCreateSurfaceFrom(), so the
// pixel buffers are owned by the engine and must be freed explicitly.
void grReleaseBmp(struct TTtmSlot *ttmSlot, uint16 bmpSlotNo)
{
    for (int i = 0; i < ttmSlot->numSprites[bmpSlotNo]; i++) {
        if (ttmSlot->sprites[bmpSlotNo][i] != NULL) {
            free(platformGetSurfacePixels(ttmSlot->sprites[bmpSlotNo][i]));
            platformFreeSurface(ttmSlot->sprites[bmpSlotNo][i]);
            ttmSlot->sprites[bmpSlotNo][i] = NULL;
        }
    }

    ttmSlot->numSprites[bmpSlotNo] = 0;
    if (ttmSlot->bmpNames[bmpSlotNo] != NULL) {
        free((void*)ttmSlot->bmpNames[bmpSlotNo]);
        ttmSlot->bmpNames[bmpSlotNo] = NULL;
    }
}


void grLoadBmp(struct TTtmSlot *ttmSlot, uint16 slotNo, const char *strArg)
{
    /* Fast path: slot already holds this exact BMP — skip the full
     * release-decode-reallocate cycle. Prevents a pathological per-frame
     * realloc storm if a TTM ever issues LOAD_IMAGE on an unchanged name
     * inside its animation loop. Normal scene authoring doesn't hit this,
     * but it's cheap defense. */
    if (ttmSlot->numSprites[slotNo] &&
        ttmSlot->bmpNames[slotNo] != NULL &&
        strcmp(ttmSlot->bmpNames[slotNo], strArg) == 0) {
        return;
    }

    if (ttmSlot->numSprites[slotNo])
        grReleaseBmp(ttmSlot, slotNo);

    {
        // strdup the name to avoid dangling pointer if caller's buffer is on the stack
        size_t len = strlen(strArg);
        char *nameCopy = safe_malloc(len + 1);
        memcpy(nameCopy, strArg, len + 1);
        ttmSlot->bmpNames[slotNo] = nameCopy;
    }

    struct TBmpResource *bmpResource = findBmpResource(strArg);
    if (bmpResource == NULL) {
        printf("Requested BMP resource not found: %s\n", strArg);
        fatalError("BMP resource not found");
    }

    uint8 *inPtr = bmpResource->uncompressedData;

    ttmSlot->numSprites[slotNo] = bmpResource->numImages;

    for (int image = 0; image < bmpResource->numImages; image++) {

        uint16 width  = bmpResource->widths[image];
        uint16 height = bmpResource->heights[image];

        if ((width % 2) == 1)
            fatalError("grLoadBmp(): can't manage odd widths");

        int spriteBytes = (width * height) / 2;

        // HD override per-image: data/hd/BMP/<NAME>/<NNN>.png
        if (grHdEnabled) {
            char path[512];
            snprintf(path, sizeof(path), "data/hd/BMP/%s/%03d.png", bmpResource->resName, image);

            size_t hdPngSize = 0;
            uint8 *hdPngData = zipvfs_read(path, &hdPngSize);
            PlatformSurface *pngSfc = hdPngData ? platformLoadPNGFromMemory(hdPngData, hdPngSize) : NULL;
            if (hdPngData) free(hdPngData);
            if (pngSfc != NULL) {
                // New path: keep real alpha from the PNG.
                //
                // Backward compatibility: if the PNG pack still uses the classic
                // "magenta" background (A8-00-A8) with fully-opaque pixels, convert
                // that color to true transparency (alpha=0).
                uint8 *px = platformGetSurfacePixels(pngSfc);
                int pitch = platformGetSurfacePitch(pngSfc);
                int pw = platformGetSurfaceWidth(pngSfc);
                int ph = platformGetSurfaceHeight(pngSfc);

                if (px && platformGetSurfaceBytesPerPixel(pngSfc) == 4) {
                    for (int yy = 0; yy < ph; yy++) {
                        uint8 *row = px + ((size_t)yy * (size_t)pitch);
                        for (int xx = 0; xx < pw; xx++) {
                            uint8 *p = row + ((size_t)xx * 4);

                            // If it's classic magenta and fully opaque, treat it as transparent.
                            if (p[3] == 255 && p[0] == 0xA8 && p[1] == 0x00 && p[2] == 0xA8) {
                                p[0] = 0;
                                p[1] = 0;
                                p[2] = 0;
                                p[3] = 0;
                            }
                        }
                    }
                }

                ttmSlot->sprites[slotNo][image] = pngSfc;

                // still advance the source pointer for subsequent images
                inPtr += spriteBytes;
                continue;
            }
        }

        int outW = width * grScale;
        int outH = height * grScale;

        uint8 *outData = safe_malloc((size_t)outW * (size_t)outH * sizeof(uint32));

        // Decode nibble-packed pixels and scale-up by duplicating pixels.
        int srcIndex = 0;
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {

                uint8 byte = inPtr[srcIndex];
                uint8 index = (x % 2 == 0) ? ((byte & 0xF0) >> 4) : (byte & 0x0F);
                if (x % 2 == 1)
                    srcIndex++;

                int rx = x * grScale;
                int ry = y * grScale;

                for (int dy = 0; dy < grScale; dy++) {
                    uint8 *row = outData + ((size_t)(ry + dy) * (size_t)outW + (size_t)rx) * 4;
                    for (int dx = 0; dx < grScale; dx++) {
                        uint8 b = ttmPalette[index][0];
                        uint8 g = ttmPalette[index][1];
                        uint8 r = ttmPalette[index][2];

                        // In the original assets, the "magenta" color is used as a transparency key.
                        // Convert it to real alpha (0) instead of relying on a color key.
                        uint8 a = 255;
                        if (b == 0xA8 && g == 0x00 && r == 0xA8) {
                            a = 0;
                            b = g = r = 0; // premultiplied alpha: RGB must be 0 when A is 0
                        }

                        row[dx * 4 + 0] = b;
                        row[dx * 4 + 1] = g;
                        row[dx * 4 + 2] = r;
                        row[dx * 4 + 3] = a;
                    }
                }
            }
        }

        inPtr += spriteBytes;

        PlatformSurface *surface = platformCreateSurfaceFrom((void*)outData, outW, outH, 4 * outW);
        ttmSlot->sprites[slotNo][image] = surface;
    }
}



void grFadeOut(void)
{
    static int fadeOutType = 0;
    PlatformSurface *sfc = platformGetWindowSurface(platform_window);
    PlatformSurface *tmpSfc = grNewLayer();

    int centerX = grScreenOrigin.w / 2;
    int centerY = grScreenOrigin.h / 2;

    grDx = grDy = 0;

    switch (fadeOutType) {

        // Circle from center
        case 0:
            // Note: we use tmpSfc to be sure we have a 32bpp surface,
            // which is needed by grDrawCircle()
            for (int radius=20; radius <= 400; radius += 20) {
                grDrawCircle(tmpSfc, centerX / grScale - radius, centerY / grScale - radius,
                    radius << 1, radius << 1, 5, 5);
                platformBlitSurface(tmpSfc, NULL, sfc, &grScreenOrigin);
                eventsWaitTick(1);
                platformUpdateWindow(platform_window);
            }
            break;

        // Rectangle from center
        case 1:
            for (int i=1; i <= 20; i++) {
                grDrawRect(sfc, grScreenOrigin.x + centerX / grScale - i*16, grScreenOrigin.y + centerY / grScale - i*12, i*32, i*24, 5);
                eventsWaitTick(1);
                platformUpdateWindow(platform_window);
            }
            break;

        // Right to left
        case 2:
            for (int i = SCREEN_WIDTH - 40; i >= 0; i -= 40) {
                grDrawRect(sfc, grScreenOrigin.x / grScale + i, grScreenOrigin.y / grScale, 40, SCREEN_HEIGHT, 5);
                eventsWaitTick(1);
                platformUpdateWindow(platform_window);
            }
            break;

        // Left to right
        case 3:
            for (int i=0; i < SCREEN_WIDTH; i += 40) {
                grDrawRect(sfc, grScreenOrigin.x + i, grScreenOrigin.y, 40, SCREEN_HEIGHT, 5);
                eventsWaitTick(1);
                platformUpdateWindow(platform_window);
            }
            break;

        // Middle to left and right
        case 4:
            for (int i=0; i < 320; i += 20) {
                grDrawRect(sfc, grScreenOrigin.x + centerX / grScale + i, grScreenOrigin.y, 20, SCREEN_HEIGHT, 5);
                grDrawRect(sfc, grScreenOrigin.x + centerX / grScale - 20 - i, grScreenOrigin.y, 20, SCREEN_HEIGHT, 5);
                eventsWaitTick(1);
                platformUpdateWindow(platform_window);
            }
            break;
    }

    grFreeLayer(tmpSfc);

    fadeOutType = (fadeOutType + 1) % 5;
}
