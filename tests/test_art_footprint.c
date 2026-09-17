/* Exercise the actual style loader and graphics draw entry points without a
 * display. The byte archive/PNG decoder is a dimension fixture; decoder pixels
 * remain covered by Invoke-ArtStyleTests.ps1 and the portable PNG probe. */
#undef NDEBUG
#include <assert.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "graphics.h"
#include "../src/engine/art_style.c"
#include "../src/engine/island.c"

struct PlatformSurface { int w, h; uint8 *pixels; };
static int haveCartoon = 1, haveHd = 1, cartoonW = 640, cartoonH = 180;
static int hdW = 560, hdH = 104, lastHd, live;
static int waveEntries;
static const char *caseName;
uint8 *zipvfs_read(const char *path, size_t *size)
{
    lastHd = strstr(path, "data/hd/") != NULL;
    if (!(lastHd ? haveHd : haveCartoon)) return NULL;
    uint8 *p = calloc(33, 1);
    memcpy(p, "\211PNG\r\n\032\n", 8);
    memcpy(p + 8, "\0\0\0\15IHDR", 8);
    p[24] = 8; p[25] = 6; *size = 33;
    return p;
}
int zipvfs_exists(const char *path) { (void)path; return waveEntries; }
void *safe_malloc(size_t size) { void *p = malloc(size); assert(p); return p; }
PlatformSurface *platformCreateSurface(int w, int h)
{
    PlatformSurface *p = malloc(sizeof(*p));
    p->w = w; p->h = h; p->pixels = calloc((size_t)w * h, 4); live++;
    return p;
}
PlatformSurface *platformLoadPNGFromMemory(const uint8 *data, size_t size)
{
    assert(data && size == 33);
    return platformCreateSurface(lastHd ? hdW : cartoonW, lastHd ? hdH : cartoonH);
}
void platformFreeSurface(PlatformSurface *p) { free(p); live--; }
uint8 *platformGetSurfacePixels(PlatformSurface *p) { return p->pixels; }
int platformGetSurfaceWidth(PlatformSurface *p) { return p->w; }
int platformGetSurfaceHeight(PlatformSurface *p) { return p->h; }
int platformGetSurfacePitch(PlatformSurface *p) { return p->w * 4; }
int platformGetSurfaceBytesPerPixel(PlatformSurface *p) { (void)p; return 4; }
void platformLockSurface(PlatformSurface *p) { (void)p; }
void platformUnlockSurface(PlatformSurface *p) { (void)p; }
void platformGetClipRect(PlatformSurface *p, PlatformRect *r)
{ *r = (PlatformRect){0, 0, p->w, p->h}; }
void platformBlitSurface(PlatformSurface *s, PlatformRect *sr, PlatformSurface *d, PlatformRect *dr)
{
    PlatformRect r = sr ? *sr : (PlatformRect){0, 0, s->w, s->h};
    for (int y = 0; y < r.h; y++) for (int x = 0; x < r.w; x++) {
        int dx = dr->x + x, dy = dr->y + y;
        if (dx < 0 || dy < 0 || dx >= d->w || dy >= d->h) continue;
        uint8 *a = s->pixels + ((y+r.y)*s->w+x+r.x)*4;
        uint8 *b = d->pixels + (dy*d->w+dx)*4;
        assert(a[3] == 0 || a[3] == 255);
        if (a[3]) memcpy(b, a, 4);
    }
}
void debugMsg(const char *format, ...) { (void)format; }
void fatalError(const char *format, ...)
{
    va_list args; va_start(args, format);
    fprintf(stderr, "REFUSED src/engine/art_style.c: ");
    vfprintf(stderr, format, args); fputc('\n', stderr); va_end(args);
    assert(live == 0 && "invalid loaded surface released");
    exit(1);
}
static void check(int condition, const char *label)
{
    if (!condition) { fprintf(stderr, "FAIL %s: %s\n", caseName, label); exit(2); }
}
static void offset(PlatformSurface *p, const char *name, int image, int flip, int x, int y)
{
    int dx = 99, dy = 99;
    artStyleSpriteOffset(name, image, p->w, p->h, flip, &dx, &dy);
    check(dx == x && dy == y, "registered offset");
}
static void draw(const char *mode)
{
    struct TTtmSlot slot = {0};
    int legacy = !strcmp(mode, "draw-legacy");
    int flip = !strcmp(mode, "draw-flip");
    int atop = !strcmp(mode, "draw-atop");
    int shifted = !strcmp(mode, "draw-offset");
    PlatformSurface *s = platformCreateSurface(legacy ? 560 : 640, legacy ? 104 : 180);
    PlatformSurface *d = platformCreateSurface(1280, 960);
    for (int i = 3; i < d->w*d->h*4; i += 4) d->pixels[i] = 255;
    s->pixels[0] = 93; s->pixels[3] = 255;
    int last = (s->w*s->h-1)*4;
    s->pixels[last+1] = 177; s->pixels[last+3] = 255;
    slot.bmpNames[0] = "BACKGRND.BMP"; slot.numSprites[0] = 1; slot.sprites[0][0] = s;
    grScale = 2; grDx = shifted ? 10 : 0; grDy = shifted ? -4 : 0;
    if (flip) grDrawSpriteFlip(d, &slot, 288, 279, 0, 0);
    else if (atop) grDrawSpriteAtop(d, &slot, 288, 279, 0, 0);
    else grDrawSprite(d, &slot, 288, 279, 0, 0);
    int x = legacy ? 576 : flip ? 532 : shifted ? 560 : 540;
    int y = legacy ? 558 : shifted ? 540 : 548;
    int firstX = flip ? x + 639 : x, lastX = flip ? x : x+s->w-1;
    check(d->pixels[(y*1280+firstX)*4] == 93, "first pixel preserves logical anchor");
    check(d->pixels[((y+s->h-1)*1280+lastX)*4+1] == 177, "extended bottom pixel retained");
    check(d->pixels[((y-1)*1280+x)*4] == 0, "outside footprint untouched");
    releaseLoadedSurface(s); releaseLoadedSurface(d);
}
static void waves(void)
{
    struct TTtmSlot slot = {0};
    slot.bmpNames[0] = "BACKGRND.BMP"; slot.numSprites[0] = 9;
    for (int i = 0; i < 9; i++)
        slot.sprites[0][i] = platformCreateSurface(i >= 6 ? 384 : 1, i >= 6 ? 256 : 1);
    grScale = 2; grDx = grDy = 0; grRenderWidth = 1280; grRenderHeight = 960;
    grBackgroundSfc = platformCreateSurface(1280, 960);
    for (int i = 0; i < 1280*960; i++) {
        grBackgroundSfc->pixels[i*4] = 71;
        grBackgroundSfc->pixels[i*4+3] = 255;
    }
    waveEntries = 1;
    islandSaveWaveBase(&slot);
    check(waveBase && waveBounds.x == 540 && waveBounds.y == 548 &&
          waveBounds.w == 540 && waveBounds.h == 256, "dirty bounds include registered wave offsets");
    uint8 *first = slot.sprites[0][6]->pixels;
    first[0] = 215; first[3] = 255;
    islandDrawWave(&slot, 1, 0);
    check(grBackgroundSfc->pixels[(548*1280+696)*4] == 215, "incoming foam may cover ground");
    islandDrawWave(&slot, 1, 1);
    check(grBackgroundSfc->pixels[(548*1280+696)*4] == 71, "receding foam restores exact static ground");
    islandRelease();
    for (int i = 0; i < 9; i++) releaseLoadedSurface(slot.sprites[0][i]);
    releaseLoadedSurface(grBackgroundSfc); grBackgroundSfc = NULL;
}
int main(int argc, char **argv)
{
    assert(argc == 2); caseName = argv[1];
    printf("WITNESS art footprint %s BEGIN\n", caseName); fflush(stdout);
    artStyleSelect("cartoon"); currentScale = hdScale = 2;
    if (!strcmp(caseName, "wave-restore")) waves();
    else if (!strncmp(caseName, "draw-", 5)) draw(caseName);
    else {
        const char *name = "BACKGRND.BMP"; int frame = 0, w = 280, h = 52;
        if (!strcmp(caseName, "legacy-ground")) { cartoonW = 560; cartoonH = 104; }
        if (!strcmp(caseName, "new-center") || !strcmp(caseName, "legacy-center")) {
            w = 160; h = 25; cartoonW = !strcmp(caseName, "new-center") ? 384 : 320;
            cartoonH = !strcmp(caseName, "new-center") ? 256 : 50;
            for (frame = 6; frame <= 8; frame++) {
                PlatformSurface *p = artStyleLoadSprite(name, frame, w, h);
                check(p && p->h == cartoonH, "center surface loaded");
                offset(p,name,frame,0,cartoonH == 256 ? -32 : 0,cartoonH == 256 ? -90 : 0);
                offset(p,name,frame,1,cartoonH == 256 ? -32 : 0,cartoonH == 256 ? -90 : 0);
                releaseLoadedSurface(p);
            }
            goto done;
        }
        if (!strcmp(caseName, "wrong-ground-height")) cartoonH = 181;
        if (!strcmp(caseName, "wrong-ground-width")) cartoonW = 641;
        if (!strcmp(caseName, "wrong-source")) w = 281;
        if (!strcmp(caseName, "wrong-frame")) frame = 1;
        if (!strcmp(caseName, "wrong-resource")) name = "OTHER.BMP";
        if (!strcmp(caseName, "wrong-center-frame") || !strcmp(caseName, "wrong-center-height")) {
            w = 160; h = 25; cartoonW = 384; cartoonH = 256;
            frame = !strcmp(caseName, "wrong-center-frame") ? 9 : 7;
            if (frame == 7) cartoonH++;
        }
        if (!strcmp(caseName, "hd-fallback") || !strcmp(caseName, "bad-hd-fallback") ||
            !strcmp(caseName, "original-fallback")) haveCartoon = 0;
        if (!strcmp(caseName, "original-fallback")) haveHd = 0;
        if (!strcmp(caseName, "bad-hd-fallback")) { hdW = 640; hdH = 180; }
        if (!strcmp(caseName, "hd-style")) { artStyleSelect("hd"); currentScale = hdScale = 2; hdW = 640; hdH = 180; }
        PlatformSurface *p = artStyleLoadSprite(name, frame, w, h);
        if (!strcmp(caseName,"original-fallback") || !strcmp(caseName,"bad-hd-fallback"))
            check(!p && originalLoads == 1, "HD/original fallback ignores extended size");
        else {
            check(p != NULL, "surface loaded");
            int extended = !strcmp(caseName,"new-ground");
            offset(p,name,frame,0,extended ? -36 : 0,extended ? -10 : 0);
            offset(p,name,frame,1,extended ? -44 : 0,extended ? -10 : 0);
            releaseLoadedSurface(p);
        }
    }
done:
    check(live == 0, "all test surfaces released");
    printf("WITNESS art footprint %s PASS\n", caseName);
    return 0;
}
